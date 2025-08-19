# types/workers.py

import asyncio
import math
from typing import List, Dict, Any
import pandas as pd

from .base import WorkdayTypeBase
from ..models import Worker
from ..parsers import (
    parse_personal_data,
    parse_contact_data,
    parse_worker_organization_data,
    parse_compensation_data,
    parse_identification_data,
    parse_benefits_and_roles,
    parse_employment_data,
    parse_worker_status,
    parse_business_site,
    parse_management_chain_data,
    parse_position_management_chain_data,
    parse_payroll_and_tax_data,
)
from ..utils import safe_serialize


class WorkerType(WorkdayTypeBase):
    """Handler for the Workday Get_Workers operation, batching pages
       so that no more than `max_parallel` requests run concurrently."""

    def __init__(self, component: Any, max_retries: int = 5, retry_delay: float = 0.2):
        """
        Initialize WorkerType with more robust retry settings for connection issues.
        
        :param component: Component instance
        :param max_retries: Maximum retry attempts (default: 5 for connection resilience)
        :param retry_delay: Base delay between retries in seconds (default: 0.5 for exponential backoff)
        """
        super().__init__(component, max_retries=max_retries, retry_delay=retry_delay)

    def _get_default_payload(self) -> Dict[str, Any]:
        """
        Default payload for Get_Workers operation with worker-specific response groups.
        """
        return {
            "Response_Filter": {},
            "Response_Group": {
                "Include_Personal_Information": True,
                "Include_Compensation": True,
                "Include_Worker_Documents": True,
                "Include_Photo": True,
                "Include_Roles": True,
                "Include_Employment_Information": True,
                "Include_Management_Chain_Data": True,
                "Include_Organizations": True,
            },
        }

    async def execute(self, **kwargs) -> pd.DataFrame:
        """
        Execute the Get_Workers operation and return a pandas DataFrame.

        If `worker_id` is provided, fetches only that one; otherwise
        fetches all pages in batches of at most `max_parallel` concurrent requests.
        """
        worker_id = kwargs.pop("worker_id", None)

        if worker_id:
            # Single‐worker request
            payload = {
                **self.request_payload,
                "Request_References": {
                    "Worker_Reference": [
                        {"ID": {"type": "Employee_ID", "_value_1": worker_id}}
                    ]
                },
            }
            
            # Use retry for single worker request
            raw = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    raw = await self.component.run(operation="Get_Workers", **payload)
                    break
                except Exception as exc:
                    self._logger.warning(
                        f"[Get_Workers] Error fetching worker {worker_id} "
                        f"(attempt {attempt}/{self.max_retries}): {exc}"
                    )
                    if attempt == self.max_retries:
                        self._logger.error(
                            f"[Get_Workers] Failed to fetch worker {worker_id} after "
                            f"{self.max_retries} attempts."
                        )
                        raise
                    await asyncio.sleep(self.retry_delay)
            
            data = self.component.serialize_object(raw)
            items = data.get("Response_Data", {}).get("Worker", [])
            workers_raw = [items] if isinstance(items, dict) else items or []

        else:
            # 1) Fetch page 1 to get total_pages
            first_payload = {
                **self.request_payload,
                "Response_Filter": {"Page": 1, "Count": 100},
            }
            
            # Use retry for first page as well
            raw1 = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    raw1 = await self.component.run(operation="Get_Workers", **first_payload, **kwargs)
                    break
                except Exception as exc:
                    self._logger.warning(
                        f"[Get_Workers] Error on first page "
                        f"(attempt {attempt}/{self.max_retries}): {exc}"
                    )
                    if attempt == self.max_retries:
                        self._logger.error(
                            f"[Get_Workers] Failed first page after "
                            f"{self.max_retries} attempts."
                        )
                        raise
                    await asyncio.sleep(self.retry_delay)
            
            data1 = self.component.serialize_object(raw1)
            page1 = data1.get("Response_Data", {}).get("Worker", [])
            if isinstance(page1, dict):
                page1 = [page1]
            total_pages = int(float(data1.get("Response_Results", {}).get("Total_Pages", 1)))

            all_workers: List[dict] = list(page1)

            # 2) If more pages, batch them so we never exceed max_parallel
            max_parallel = 10
            if total_pages > 1:
                pages = list(range(2, total_pages + 1))
                # calculate how many batches we need
                num_batches = math.ceil(len(pages) / max_parallel)
                batches = self.component.split_parts(pages, num_parts=num_batches)

                for batch in batches:
                    self._logger.info(f"Processing batch of {len(batch)} pages: {batch}")
                    tasks = [self._fetch_page(p, kwargs) for p in batch]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for res in results:
                        if isinstance(res, Exception):
                            self._logger.error(f"Error fetching page: {res}")
                        else:
                            all_workers.extend(res)

            workers_raw = all_workers

        # 3) Parse into Pydantic models
        parsed: List[Worker] = []
        for w in workers_raw:
            wd = w.get("Worker_Data", {}) or {}
            
            # Try position management chain first (has manager names), fallback to worker management chain
            position_chain_data = parse_position_management_chain_data(wd)
            worker_chain_data = parse_management_chain_data(wd)
            
            # Use position chain data if it has data, otherwise use worker chain data
            management_chain_data = position_chain_data if position_chain_data.get("management_chain") else worker_chain_data
            
            # Parse payroll and tax data
            payroll_data = parse_payroll_and_tax_data(wd)
            
            # If we have management chain data and last_detected_manager_id but no name, try to find it in the chain
            if (management_chain_data.get("management_chain") and 
                payroll_data.get("last_detected_manager_id") and 
                not payroll_data.get("last_detected_manager_name")):
                
                last_detected_manager_id = payroll_data["last_detected_manager_id"]
                
                # Look for the manager in the management chain
                for level in management_chain_data["management_chain"]:
                    if level.get("manager_id") == last_detected_manager_id:
                        payroll_data["last_detected_manager_name"] = level.get("manager_name")
                        break
            
            record = {
                "worker_id": wd.get("Worker_ID"),
                "user_id": wd.get("User_ID"),
                **parse_personal_data(wd),
                **parse_contact_data(wd),
                **parse_worker_organization_data(wd),
                **parse_compensation_data(wd),
                **parse_identification_data(wd),
                **parse_benefits_and_roles(wd),
                **parse_employment_data(wd),
                **parse_worker_status(wd),
                **parse_business_site(wd),
                **management_chain_data,
                **payroll_data,
                "raw_data": w,
            }
            parsed.append(Worker(**record))

        # 4) Build DataFrame and serialize complex columns
        df = pd.DataFrame([w.dict() for w in parsed])
        for col in [
            "emails",
            "roles",
            "worker_documents",
            "benefit_enrollments",
            "custom_ids",
            "compensation_guidelines",
            "compensation_summary",
            "salary_and_hourly",
            "reason_references",
            "custom_id_shared_references",
            "management_chain",
            "matrix_management_chain",
            "organizations",
        ]:
            if col in df.columns:
                df[col] = df[col].apply(safe_serialize)

        # 5) Metric
        self.component.add_metric("NUM_WORKERS", len(parsed))
        return df

    async def _fetch_page(self, page_num: int, base_kwargs: dict) -> List[dict]:
        """
        Fetch a single page of Get_Workers. Returns list of worker dicts.
        """
        self._logger.debug(f"Starting fetch for page {page_num}")
        payload = {
            **self.request_payload,
            "Response_Filter": {"Page": page_num, "Count": 100},
        }
        
        # Use the retry mechanism from base class with exponential backoff
        raw = None
        for attempt in range(1, self.max_retries + 1):
            try:
                raw = await self.component.run(operation="Get_Workers", **payload, **base_kwargs)
                break
            except Exception as exc:
                self._logger.warning(
                    f"[Get_Workers] Error on page {page_num} "
                    f"(attempt {attempt}/{self.max_retries}): {exc}"
                )
                if attempt == self.max_retries:
                    self._logger.error(
                        f"[Get_Workers] Failed page {page_num} after "
                        f"{self.max_retries} attempts."
                    )
                    raise
                # Use exponential backoff: 0.5s, 1s, 2s, 4s, 8s
                delay = min(self.retry_delay * (2 ** (attempt - 1)), 8.0)
                await asyncio.sleep(delay)
        
        data = self.component.serialize_object(raw)
        items = data.get("Response_Data", {}).get("Worker", [])
        if isinstance(items, dict):
            return [items]
        return items or []
