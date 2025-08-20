"""
NextStop Agent.

Run queries using the NextStop Agent.
"""
from typing import Optional, Any
from collections.abc import Callable
import asyncio
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
import pandas as pd
# Parrot AI Agent:
from parrot.bots.nextstop import NextStop
# Tools:
from parrot.tools.nextstop import (
    StoreInfo,
    EmployeeToolkit
)
# Inherited interfaces:
from ..interfaces.parrot import AgentBase
from .flow import FlowComponent

class NextStopResponse(BaseModel):
    """
    NextStopResponse is a model that defines the structure of the response
    for the NextStop agent.
    """
    user_id: str = Field(..., description="Unique identifier for the user")
    agent_name: str = Field(
        required=False,
        description="Name of the agent that processed the request"
    )
    program_slug: str = Field(default="hisense", description="Program slug for the agent")
    kind: Optional[str] = Field(
        default=None,
        description="Kind of response, e.g., 'visit_report'"
    )
    content: str = Field(
        default="",
        description="Description of Generated Report."
    )
    data: str = Field(..., description="Data returned by the agent")
    status: str = Field(default="success", description="Status of the response")
    output: str = Field(default=None)
    transcript: Optional[str] = Field(
        default=None,
        description="Transcript of the conversation with the agent"
    )
    attributes: dict = Field(
        default_factory=dict,
        description="Additional attributes related to the response"
    )
    store_id: Optional[str] = Field(
        default=None,
        description="ID of the store associated with the session"
    )
    employee_id: Optional[str] = Field(
        default=None,
        description="ID of the employee associated with the session"
    )
    manager_id: Optional[str] = Field(
        default=None,
        description="ID of the manager associated with the session"
    )
    created_at: datetime = Field(default=datetime.now)
    podcast_path: Optional[str] = Field(
        default=None,
        description="Path to the podcast associated with the session"
    )
    script_path: Optional[str] = Field(
        default=None,
        description="Path to the script associated with the session"
    )
    pdf_path: Optional[str] = Field(
        default=None,
        description="Path to the PDF associated with the session"
    )
    document_path: Optional[str] = Field(
        default=None,
        description="Path to document generated during session"
    )
    documents: list[Path] = Field(
        default_factory=list,
        description="List of documents associated with the session"
    )


class NextStopAgent(AgentBase, FlowComponent):
    """NextStopAgent.

    Overview:
        The NextStopAgent class is a FlowComponent that integrates with the Parrot AI Agent framework to run queries
        using the NextStop Agent. It extends the AgentBase class and provides methods for creating and managing the
        agent's lifecycle within a FlowTask.

    """
    _agent_class: type = NextStop
    _agent_name: str = 'NextStopAgent'
    agent_id: str = 'nextstop_agent'
    _use_llm: str = 'openai'
    _use_model: str = 'gpt-4.1-mini'
    _agent_response: type = NextStopResponse  # Default response type

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        # Method to be executed by agent:
        self._report = kwargs.get('report', 'for_employee')
        super().__init__(loop=loop, job=job, stat=stat, **kwargs)

    def _define_tools(self, base_dir: Path):
        """Define tools for the NextStop Agent."""
        program = getattr(self, '_program', 'hisense')
        tools = StoreInfo(program=program).get_tools()
        tools.extend(EmployeeToolkit(program=program).get_tools())
        return tools

    async def start(self, **kwargs):
        """
        start.

            Initialize (if needed) a task
        """
        if self.previous:
            self.data = self.input
        # check if previous data is an iterable:
        if isinstance(self.data, pd.DataFrame):
            self._iterable = self.data.iterrows()
        await super().start(**kwargs)

    async def close(self):
        pass

    async def _process_row(self, row, report):
        """
        Process each row with the report.

        Args:
            row: A single row from the DataFrame.
            report: The report to be processed.
        """
        # Here you would implement the logic to process each row with the report
        # For example, you might call a method on the agent to handle the row
        self.logger.info(f"Processing row: {row} with report: {report}")
        try:
            data = row.to_dict()
            response = await self._agent.report(
                prompt_file=report,
                program_slug=self._program,
                **data
            )
            response.manager_id = row.get('manager_id', None)
            response.employee_id = row.get('employee_id', None)
            response.program_slug = self._program
        except Exception as e:
            self.logger.error(
                f"Error processing row {row}: {e}"
            )
            return None
        self.logger.info(f"Processed row successfully: {response}")
        return response

    async def run(self):
        """
        run.

            Run the NextStop Agent with the provided data.
        """
        try:
            # calling a report for every row in the DataFrame:
            results = []
            if isinstance(self.data, pd.DataFrame):
                for _, row in self.data.iterrows():
                    report = f"{self._report}.txt"
                    # Process each row with the report
                    result = await self._process_row(row, report)
                    if result:
                        # Define the kind and content:
                        if self._report == 'for_employee':
                            result.kind = "_nextstop_employee"
                            result.content = f"Employee: {row.get('employee_id', '')}"
                        elif self._report == 'team_performance':
                            result.kind = "_team_performance"
                            result.content = f"Team Performance for: {row.get('manager_id', '')}"
                        results.append(result)
            # Convert results to a DataFrame if needed
            if results:
                # responses: list[NextStopResponse]
                self._result = pd.DataFrame(
                    [r.model_dump(mode="json", exclude_none=True) for r in results]
                )
                # Add Column "request_date" with today's date:
                self._result['request_date'] = datetime.now().isoformat()
            self._print_data_(
                self._result,
                title="NextStop Agent Results"
            )
            return self._result
        except Exception as e:
            self.logger.error(
                f"Error occurred while running NextStopAgent: {e}"
            )
            return None
