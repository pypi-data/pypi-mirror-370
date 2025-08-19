import logging
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
from zeep import Settings
from zeep.helpers import serialize_object

from ...interfaces.SOAPClient import SOAPClient
from ...components.flow import FlowComponent
from ...conf import (
    WORKDAY_CLIENT_ID,
    WORKDAY_CLIENT_SECRET,
    WORKDAY_TOKEN_URL,
    WORKDAY_WSDL_PATH,
    WORKDAY_WSDL_TIME,
    WORKDAY_WSDL_HUMAN_RESOURCES,
    WORKDAY_REFRESH_TOKEN,
)
from .types import WorkerType, TimeBlockType, LocationType, TimeRequestType, OrganizationType
from .types.organization_single import GetOrganization
from .types.location_hierarchy_assignments import LocationHierarchyAssignmentsType

# Configure Zeep logging
logging.getLogger("zeep").setLevel(logging.INFO)

class Workday(SOAPClient, FlowComponent):
    """
    Workday Component

    Overview:
        The Workday class is a Flowtask component for the Workday SOAP API.
        It encapsulates all Workday-specific logic, including authentication,
        request/response handling, and data normalization.

    Properties:
        type (str): Operation type to perform (e.g. 'get_workers', 'get_time_blocks')
        worker_id (str): Optional worker ID to fetch a specific worker
        use_storage (bool): Enable data storage functionality
        storage_path (str): Path where to store the data files
        
    Returns:
        Returns a pandas DataFrame with the requested data.
        
    Examples:
        ```yaml
        # Basic usage
        Workday:
          type: get_workers 
          worker_id: "72037046323885"
        
        # With storage enabled
        Workday:
          type: get_workers
          use_storage: true
          storage_path: "/data/workday"
        
        # Location hierarchy assignments with storage
        Workday:
          type: get_location_hierarchy_assignments
          use_storage: true
          storage_path: "/data/workday"
        
        # Organizations with storage
        Workday:
          type: get_organizations
          organization_type: "Cost_Center"
          use_storage: true
          storage_path: "/data/workday"
        ```
    """
    
    def __init__(self, *, loop=None, job=None, stat=None, **kwargs):
        # Get kwargs first to determine operation type
        self.type = kwargs.get('type', 'get_workers')
        self.worker_id = kwargs.get('worker_id')
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        
        # Storage parameters
        self.use_storage: bool = kwargs.get('use_storage', False)
        self.storage_path: str = kwargs.get('storage_path')
        if self.use_storage and not self.storage_path:
            raise ValueError(
                "Workday: storage_path is required when use_storage is True"
            )
        
        # Location parameters
        self.location_id = kwargs.get('location_id')
        self.location_name = kwargs.get('location_name')
        self.location_type = kwargs.get('location_type')
        self.location_usage = kwargs.get('location_usage')
        self.inactive = kwargs.get('inactive')
        
        # Time Request parameters
        self.time_request_id = kwargs.get('time_request_id')
        self.supervisory_organization_id = kwargs.get('supervisory_organization_id')
        
        # Organization parameters
        self.organization_id = kwargs.get('organization_id')
        self.organization_id_type = kwargs.get('organization_id_type', 'Organization_Reference_ID')
        self.organization_type = kwargs.get('organization_type')
        self.include_inactive = kwargs.get('include_inactive')
        self.enable_transaction_log_lite = kwargs.get('enable_transaction_log_lite')
        
        # Select WSDL based on operation type
        wsdl_mapping = {
            'get_time_blocks': WORKDAY_WSDL_TIME,
            'get_workers': WORKDAY_WSDL_PATH,
            'get_locations': WORKDAY_WSDL_HUMAN_RESOURCES,
            'get_time_requests': WORKDAY_WSDL_TIME,
            'get_organizations': WORKDAY_WSDL_PATH,
            'get_organization': WORKDAY_WSDL_HUMAN_RESOURCES,
            'get_location_hierarchy_assignments': WORKDAY_WSDL_HUMAN_RESOURCES,
            # Add more mappings as needed
        }
        wsdl_path = wsdl_mapping.get(self.type, WORKDAY_WSDL_PATH)
        
        # Configure credentials with appropriate WSDL
        creds = {
            "client_id": WORKDAY_CLIENT_ID,
            "client_secret": WORKDAY_CLIENT_SECRET,
            "token_url": WORKDAY_TOKEN_URL,
            "wsdl_path": wsdl_path,
            "refresh_token": WORKDAY_REFRESH_TOKEN,
        }
        
        # Configure SOAP settings
        settings = Settings(strict=False, xml_huge_tree=True)
        
        super().__init__(credentials=creds, settings=settings, loop=loop, job=job, stat=stat, **kwargs)
        
        # Component configuration
        self._logger = logging.getLogger("flowtask.workday")
        
        # Log which WSDL is being used
        self._logger.info(f"Using WSDL: {wsdl_path} for operation type: {self.type}")
        
        # Log storage information after logger is initialized
        if self.use_storage:
            self._logger.info(
                f"Storage enabled. Data will be saved in: {self.storage_path}"
            )
        
        # Register available types
        self._type_handlers = {
            # Original handlers
            "get_workers": WorkerType(self),
            "get_time_blocks": TimeBlockType(self),
            "get_locations": LocationType(self),
            "get_time_requests": TimeRequestType(self),
            "get_organizations": OrganizationType(self),
            "get_organization": GetOrganization(self),
            "get_location_hierarchy_assignments": LocationHierarchyAssignmentsType(self)
        }
        
        # Initialize metrics
        self.metrics = {}
        self._result = None

    def _get_storage_file(self) -> str:
        """Get the storage file path for the current execution."""
        today = datetime.now().strftime('%Y%m%d')
        filename = f"workday_{self.type}_{today}.csv"
        storage_dir = Path(self.storage_path)
        storage_dir.mkdir(parents=True, exist_ok=True)
        return str(storage_dir / filename)

    def _get_wsdl_path(self, operation_type: str) -> str:
        """
        Get the appropriate WSDL path based on operation type.
        
        Args:
            operation_type: The type of operation ('get_workers', 'get_time_blocks', etc.)
            
        Returns:
            The WSDL path to use for the operation
        """
        wsdl_mapping = {
            'get_time_blocks': WORKDAY_WSDL_TIME,
            'get_workers': WORKDAY_WSDL_PATH,
            'get_locations': WORKDAY_WSDL_HUMAN_RESOURCES,
            'get_time_requests': WORKDAY_WSDL_TIME,
            'get_organizations': WORKDAY_WSDL_PATH,
            'get_organization': WORKDAY_WSDL_PATH,
            # Add more mappings as needed
        }
        
        return wsdl_mapping.get(operation_type, WORKDAY_WSDL_PATH)

    def add_metric(self, key: str, value: any) -> None:
        """Add a metric to track"""
        self.metrics[key] = value

    def serialize_object(self, obj):
        """Helper to serialize SOAP objects"""
        return serialize_object(obj)

    async def start(self, **kwargs) -> None:
        """Initialize the component"""
        await super().start()

    async def run(self, operation: str = None, **kwargs):
        """Execute the component's main operation"""
        if operation:
            # If operation is provided, this is a SOAP call
            return await super().run(operation=operation, **kwargs)
            
        # Try to load from storage first
        if self.use_storage:
            storage_file = self._get_storage_file()
            if os.path.exists(storage_file):
                self._logger.info(
                    f"Found existing data file: {storage_file}. Using stored data."
                )
                try:
                    self._result = pd.read_csv(storage_file)
                    return self._result
                except Exception as e:
                    self._logger.error(f"Error loading storage file: {e}")
            else:
                self._logger.info(
                    f"No existing data file found. Will generate new file: {storage_file}"
                )
            
        # Otherwise this is a component operation
        self._logger.info(f"Starting Workday operation: {self.type}")

        # Get the appropriate handler for the operation type
        handler = self._type_handlers.get(self.type)
        if not handler:
            raise ValueError(f"Unknown operation type: {self.type}")
            
        # Add parameters to kwargs if specified
        if self.worker_id:
            kwargs['worker_id'] = self.worker_id
        
        # Add date parameters if they exist in the component
        if hasattr(self, 'start_date') and self.start_date:
            kwargs['start_date'] = self.start_date
        if hasattr(self, 'end_date') and self.end_date:
            kwargs['end_date'] = self.end_date
        
        # Add location parameters if they exist in the component (only for locations type)
        if self.type == 'get_locations':
            if hasattr(self, 'location_id') and self.location_id:
                kwargs['location_id'] = self.location_id
            if hasattr(self, 'location_name') and self.location_name:
                kwargs['location_name'] = self.location_name
            if hasattr(self, 'location_type') and self.location_type:
                kwargs['location_type'] = self.location_type
            if hasattr(self, 'location_usage') and self.location_usage:
                kwargs['location_usage'] = self.location_usage
            if hasattr(self, 'inactive') and self.inactive is not None:
                kwargs['inactive'] = self.inactive
            
        # Add time request parameters if they exist in the component (only for time_requests type)
        if self.type == 'get_time_requests':
            if hasattr(self, 'time_request_id') and self.time_request_id:
                kwargs['time_request_id'] = self.time_request_id
            if hasattr(self, 'supervisory_organization_id') and self.supervisory_organization_id:
                kwargs['supervisory_organization_id'] = self.supervisory_organization_id
            
        # Add organization parameters if they exist in the component (only for organizations type)
        if self.type == 'get_organizations':
            if hasattr(self, 'organization_id') and self.organization_id:
                kwargs['organization_id'] = self.organization_id
            if hasattr(self, 'organization_id_type') and self.organization_id_type:
                kwargs['organization_id_type'] = self.organization_id_type
            if hasattr(self, 'organization_type') and self.organization_type:
                kwargs['organization_type'] = self.organization_type
            if hasattr(self, 'include_inactive') and self.include_inactive is not None:
                kwargs['include_inactive'] = self.include_inactive
            if hasattr(self, 'enable_transaction_log_lite') and self.enable_transaction_log_lite is not None:
                kwargs['enable_transaction_log_lite'] = self.enable_transaction_log_lite
            
        # Add organization parameters if they exist in the component (only for get_organization type)
        if self.type == 'get_organization':
            if hasattr(self, 'organization_id') and self.organization_id:
                kwargs['organization_id'] = self.organization_id
            if hasattr(self, 'organization_id_type') and self.organization_id_type:
                kwargs['organization_id_type'] = self.organization_id_type
            
        # Execute the operation
        result = None
        try:
            result = await handler.execute(**kwargs)
            
            # Save to storage after successful execution
            if self.use_storage and result is not None and isinstance(result, pd.DataFrame):
                try:
                    storage_file = self._get_storage_file()
                    result.to_csv(storage_file, index=False)
                    self._logger.info(
                        f"Successfully saved data to: {storage_file}"
                    )
                except Exception as e:
                    self._logger.error(f"Error saving to storage: {e}")
                    
        except Exception as exc:
            self._logger.error(f"Error during Workday operation: {exc}")
            raise
        
        # Add metrics if result is a DataFrame
        if isinstance(result, pd.DataFrame):
            self.add_metric("NUMROWS", len(result.index))
            self.add_metric("NUMCOLS", len(result.columns))
            
        # Store and return result
        self._result = result
        
        if getattr(self, '_debug', False):
            self._print_data("Workday Result", result)
            
        self._logger.info("Workday operation finished successfully")
        return self._result

    def _print_data(self, title: str, data_df: pd.DataFrame) -> None:
        """Debug helper to print DataFrame information"""
        print(f"::: Printing {title} === ")
        print("Data: ", data_df)
        for column, t in data_df.dtypes.items():
            print(f"{column} -> {t} -> {data_df[column].iloc[0] if not data_df.empty else None}") 

    async def close(self) -> None:
        """Cleanup resources"""
        await super().close() 