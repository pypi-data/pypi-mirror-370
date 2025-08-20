"""DynamoFL Model"""
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class BillingReport:
    """Data class for billing report"""

    id: int
    from_time: str
    to_time: str
    data_store_path: Optional[str]
    is_billing_data_corrupted: bool
    job_id: str
    status: str
    validation_error: Optional[str] = None
