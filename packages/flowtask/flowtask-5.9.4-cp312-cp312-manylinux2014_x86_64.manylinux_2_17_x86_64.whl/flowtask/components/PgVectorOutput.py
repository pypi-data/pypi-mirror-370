from collections.abc import Callable
import asyncio
from typing import List
from sqlalchemy import text
from langchain_core.documents import Document
from parrot.stores.postgres import PgvectorStore
from .flow import FlowComponent
from ..exceptions import DataNotFound, ComponentError, ConfigError
from ..conf import default_sqlalchemy_pg
from ..interfaces.credentials import CredentialsInterface


class PgVectorOutput(CredentialsInterface, FlowComponent):
    """
    Saving Langchain Documents on a Postgres Database using PgVector.


    This component is designed to save documents into a PostgreSQL database using PgVector extension

    Example:

    ```yaml
    PgVectorOutput:
        credentials:
            dsn:
        table: lg_products
        schema: lg
        embedding_model:
            model: thenlper/gte-base
            model_type: transformers
        id_column: "id"
        vector_column: 'embedding'
        pk: source_type
        create_table: true
        upsert: true
    ```

    """
    _credentials: dict = {
        "dsn": str,
    }

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        self.upsert: bool = kwargs.pop('upsert', True)
        self.pk: str = kwargs.pop('pk', 'source_type')
        self._embedding_model: dict = kwargs.get('embedding_model', None)
        self.vector_column: str = kwargs.pop('vector_column', 'embedding')
        self.table: str = kwargs.pop('table', 'documents')
        self.schema: str = kwargs.pop('schema', 'public')
        self.id_column: str = kwargs.pop('id_column', 'id')
        self.dimension: int = kwargs.pop('dimension', 768)
        self.create_table: dict = kwargs.pop('create_table', {})
        self.prepare_columns: bool = kwargs.pop('prepare_columns', True)
        self._pk: List[str] = kwargs.pop('pk', ['source_type'])
        super().__init__(loop=loop, job=job, stat=stat, **kwargs)

    async def start(self, **kwargs):
        if self.previous:
            self.data = self.input
        await super().start(**kwargs)
        self.processing_credentials()
        # DSN
        if not self.credentials:
            self._dsn = default_sqlalchemy_pg
        else:
            self._dsn = self.credentials.get('dsn', default_sqlalchemy_pg)
        if not self.data:
            raise DataNotFound(
                "List of Documents is Empty."
            )
        if not isinstance(self.data, list):
            raise ComponentError(
                f"Incompatible kind of data received, expected a *list* of documents, receives {type(self.data)}"
            )
        return True

    async def close(self):
        pass

    async def _create_table(self, store: PgvectorStore):
        """
        Create the table in the PostgreSQL database if it does not exist.
        """
        creation = self.create_table.get('create', True)
        if not creation:
            return
        tablename = f"{self.schema}.{self.table}"
        if not await store.table_exists(table=self.table, schema=self.schema):
            print(f"Creating table {tablename}...")
            post_creation = ""
            if self.create_table.get('use_uuid', True):
                pk_type = 'UUID'
                # Postgres UUID generation, add a DEFAULT generation for uuid
                post_creation = f"""
                ALTER TABLE {tablename}
                ALTER COLUMN {self.id_column} SET DEFAULT uuid_generate_v4();
                """
            elif self.create_table.get('use_serial', False):
                pk_type = 'SERIAL'
            else:
                pk_type = 'VARCHAR'
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {tablename} (
                {self.id_column} {pk_type} PRIMARY KEY,
                text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            try:
                await store.execute_sql(
                    create_table_sql
                )
                if post_creation:
                    await store.execute_sql(
                        post_creation
                    )
            except Exception as e:
                raise ConfigError(
                    f"Error creating table {tablename}: {e}"
                )

    async def _prepare_columns(self, store: PgvectorStore):
        """
        Prepare the columns in the PostgreSQL database if they do not exist.
        """
        tablename = f"{self.schema}.{self.table}"
        async with store.engine().begin() as conn:
            await store.prepare_embedding_table(
                tablename=tablename,
                conn=conn,
                embedding_column=self.vector_column,
                id_column=self.id_column,
                dimension=self.dimension
            )

    async def run(self):
        """
        Saving Langchain Documents on a Postgres Database.
        """
        # Connecting to PostgreSQL:
        _store = PgvectorStore(
            embedding_model=self._embedding_model,
            dsn=self._dsn,
            dimension=768,
            table=self.table,
            schema=self.schema,
            id_column=self.id_column,
            embedding_column=self.vector_column
        )
        # TODO: add Collection creation:
        self._result = None
        async with _store as store:
            print('Connecting to PostgreSQL...', store.is_connected())
            print(f"Preparing Table {self.schema}.{self.table}...")
            if self.create_table:
                await self._create_table(store)
            if self.prepare_columns:
                await self._prepare_columns(store)
            if await store.table_exists(table=self.table, schema=self.schema):
                # if upsert: we need to delete existing documents with the pk:
                if hasattr(self, 'upsert') and self.upsert:
                    await store.delete_documents(
                        values=self.pk
                    )
                auto_uuid = self.create_table.get('use_uuid', False)
                # Load documents into the store:
                added_ids = await store.add_documents(
                    self.data,
                    use_uuid=auto_uuid
                )
                result = {
                    "vectorstore": f"{store!r}",
                    "table": f"{self.schema}.{self.table}",
                    "ids": added_ids,
                    "documents": self.data
                }
            else:
                raise DataNotFound(
                    f"Table {self.schema}.{self.table} does not exist."
                )
            self._result = result
        self.add_metric('DOCUMENTS_LOADED', len(self.data))
        return result
