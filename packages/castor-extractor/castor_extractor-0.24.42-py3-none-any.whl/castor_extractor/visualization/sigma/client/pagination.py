from typing import Optional

from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

from ....utils import PaginationModel

SIGMA_API_LIMIT = 200  # default number of records per page
SIGMA_QUERIES_PAGINATION_LIMIT = 50


class SigmaPagination(PaginationModel):
    next_page: Optional[str] = "0"
    entries: list = Field(default_factory=list)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    def is_last(self) -> bool:
        return self.next_page is None

    def next_page_payload(self) -> dict:
        return {"page": self.next_page}

    def page_results(self) -> list:
        return self.entries
