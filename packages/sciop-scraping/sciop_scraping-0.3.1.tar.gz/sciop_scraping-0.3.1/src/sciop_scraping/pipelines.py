import re
from typing import Any

from scrapy import Request
from scrapy.http import Response
from scrapy.pipelines.files import FilesPipeline


class URLPathFilesPipeline(FilesPipeline):
    """Save files named according to their full URL path."""

    def file_path(
        self,
        request: Request,
        response: Response | None = None,
        info: Any | None = None,
        *,
        item: Any | None = None,
    ) -> str:
        return re.sub("^https?://", "", request.url)
