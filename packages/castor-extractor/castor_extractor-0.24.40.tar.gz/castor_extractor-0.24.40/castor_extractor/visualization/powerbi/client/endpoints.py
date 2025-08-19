from datetime import date, datetime
from typing import Optional

from ....utils import at_midnight, clean_path, format_date, yesterday


def _time_filter(day: Optional[date]) -> tuple[datetime, datetime]:
    target_day = day or yesterday()
    start = at_midnight(target_day)
    end = datetime.combine(target_day, datetime.max.time())
    return start, end


class PowerBiEndpointFactory:
    def __init__(self, login_url: str, api_base: str):
        self.app_base = clean_path(login_url)
        self.rest_api_base = clean_path(api_base)

    def activity_events(self, day: Optional[date]) -> str:
        start, end = _time_filter(day)
        url = f"{self.rest_api_base}/admin/activityevents"
        url += "?$filter=Activity eq 'viewreport'"
        url += f"&startDateTime='{format_date(start)}'"
        url += f"&endDateTime='{format_date(end)}'"
        return url

    def authority(self, tenant_id: str) -> str:
        return f"{self.app_base}/{tenant_id}"

    def dashboards(self) -> str:
        return f"{self.rest_api_base}/admin/dashboards"

    def datasets(self) -> str:
        return f"{self.rest_api_base}/admin/datasets"

    def groups(self) -> str:
        return f"{self.rest_api_base}/admin/groups"

    def metadata_create_scan(self) -> str:
        return f"{self.rest_api_base}/admin/workspaces/getInfo"

    def metadata_scan_result(self, scan_id: int) -> str:
        return f"{self.rest_api_base}/admin/workspaces/scanResult/{scan_id}"

    def metadata_scan_status(self, scan_id: int) -> str:
        return f"{self.rest_api_base}/admin/workspaces/scanStatus/{scan_id}"

    def pages(self, report_id: str) -> str:
        return f"{self.rest_api_base}/admin/reports/{report_id}/pages"

    def reports(self) -> str:
        return f"{self.rest_api_base}/admin/reports"

    def workspace_ids(self) -> str:
        return f"{self.rest_api_base}/admin/workspaces/modified"
