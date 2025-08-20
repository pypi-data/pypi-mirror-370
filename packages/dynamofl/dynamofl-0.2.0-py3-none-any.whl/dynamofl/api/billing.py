""" Module for billing APIs """
import logging
from typing import List

from ..entities.billing import BillingReport
from ..Request import _Request

logger = logging.getLogger("BillingAPI")


# pylint: disable=protected-access
class BillingAPI:
    """Class for billing APIs"""

    def __init__(self, request: _Request):
        self.request = request

    def __convert_billing_response_obj_to_billing_report(
        self, billing_api_response: dict
    ) -> BillingReport:
        return BillingReport(
            id=billing_api_response["id"],
            from_time=billing_api_response["fromTime"],
            to_time=billing_api_response["toTime"],
            data_store_path=billing_api_response["dataStorePath"],
            is_billing_data_corrupted=billing_api_response["isBillingDataCorrupted"],
            job_id=billing_api_response["jobId"],
            status=billing_api_response["status"],
            validation_error=billing_api_response.get("validationError"),
        )

    def generate_report(self, params=None):
        billing_api_response = self.request._make_request("POST", "/billing/reports", params=params)
        if not billing_api_response:
            raise Exception("No response")
        return self.__convert_billing_response_obj_to_billing_report(billing_api_response)

    def get_billing_reports(self) -> List[BillingReport]:
        res = self.request._make_request("GET", "/billing/reports")
        if not res:
            raise Exception("No response")
        return [self.__convert_billing_response_obj_to_billing_report(report) for report in res]

    def get_billing_report(self, report_id: int) -> BillingReport:
        res = self.request._make_request("GET", f"/billing/reports/{report_id}")
        if not res:
            raise Exception("No response")
        return self.__convert_billing_response_obj_to_billing_report(res)

    def get_billing_report_download_url(self, report_id: int) -> str:
        res = self.request._make_request("GET", f"/billing/reports/{report_id}/download")
        if not res:
            raise Exception("No response")
        return res["url"]
