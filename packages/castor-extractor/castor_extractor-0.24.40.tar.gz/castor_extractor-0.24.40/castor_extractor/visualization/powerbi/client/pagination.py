from typing import Optional

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from ....utils import (
    FetchNextPageBy,
    PaginationModel,
)


class PowerBiPagination(PaginationModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    fetch_by: FetchNextPageBy = FetchNextPageBy.URL

    activity_event_entities: list
    continuation_uri: Optional[str] = None
    last_result_set: bool = False

    def is_last(self) -> bool:
        return self.last_result_set

    def next_page_payload(self) -> Optional[str]:
        return self.continuation_uri

    def page_results(self) -> list:
        return self.activity_event_entities
