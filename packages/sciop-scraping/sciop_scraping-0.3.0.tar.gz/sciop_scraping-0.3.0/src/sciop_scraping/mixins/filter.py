"""
Mixins for filtering urls, pages, files, etc.
"""

import re
from collections.abc import Iterable
from typing import TypeAlias

PatternArgType: TypeAlias = str | re.Pattern | list[str] | list[re.Pattern] | None


class URLFilterMixin:
    """
    Filter urls according to include/exclude patterns.

    Like scrapy's Link extractors, except works on sets of urls as strings,
    rather than scrapy's `Response` objects and HTML responses only.

    Written using `classmethods` for use as a mixin,
    to use by composition as a an independent object,
    use :class:`URLFilter`

    `include` and `exclude` are regex patterns, or lists of regex patterns,
    and urls are filtered such that
    - If neither include or exclude are provided, no filtration is done
    - If only `include` is provided, only urls that match one of the patterns are included.
    - If only `exclude` is provided, all urls *except* those that match one of the patterns
      are excluded.
    - If both are provided, all urls that match one of the `include` patterns
      and do not match any of the `exclude` patterns are included.

    Both sets of filters are `OR`'d - urls match against *any* of them, rather than *all* of them.
    Both sets of filters are matched with a *full match* -
    the entire string must match the pattern for a hit.
    For partial matching, use wildcards and string start/end anchors.
    """

    @classmethod
    def matches_pattern(cls, value: str, pattern: PatternArgType, flags: int | None = None) -> bool:
        """Check if a string matches a pattern or set of patterns"""
        if pattern is None:
            return True
        if not isinstance(pattern, list):
            pattern = [pattern]
        pattern = [p if isinstance(p, re.Pattern) else re.compile(p, flags=flags) for p in pattern]
        return any([p.fullmatch(value) for p in pattern])

    @classmethod
    def url_valid(
        cls,
        url: str,
        include: PatternArgType = None,
        exclude: PatternArgType = None,
        flags: int | None = None,
    ) -> bool:
        """Check if a string is valid given a set of include and exclude patterns"""
        if not exclude:
            # if exclude is None, the string always trivially matches it,
            # which is the opposite of what we want for excludes.
            return cls.matches_pattern(url, include, flags)
        else:
            return cls.matches_pattern(url, include, flags) and not cls.matches_pattern(
                url, exclude, flags
            )

    @classmethod
    def filter_urls(
        cls,
        urls: list[str],
        include: PatternArgType = None,
        exclude: PatternArgType = None,
        flags: int | None = None,
    ) -> list[str]:
        """Filter a list of urls according to include and exclude patterns"""
        return [url for url in urls if cls.url_valid(url, include, exclude, flags)]

    @classmethod
    def iter_filtered_urls(
        cls,
        urls: Iterable[str],
        include: PatternArgType = None,
        exclude: PatternArgType = None,
        flags: int | None = None,
    ) -> Iterable[str]:
        """Iterate over some iterable of urls, yielding only valid urls"""
        for url in urls:
            if cls.url_valid(url, include, exclude, flags):
                yield url


class URLFilter:
    """
    Independent version of :class:`URLFilterMixin`,
    that accepts include/exclude patterns as params,
    and uses the URLFilterMixin class when parsing urls.
    """

    def __init__(
        self,
        include: PatternArgType = None,
        exclude: PatternArgType = None,
        flags: int | None = None,
    ):
        self.include: list[re.Pattern] | None = _pattern_input_to_pattern_list(include, flags)
        self.exclude: list[re.Pattern] | None = _pattern_input_to_pattern_list(exclude, flags)
        self.flags = flags

    def url_valid(self, url: str) -> bool:
        return URLFilterMixin.url_valid(url, self.include, self.exclude, self.flags)

    def filter_urls(self, urls: list[str]) -> list[str]:
        return URLFilterMixin.filter_urls(urls, self.include, self.exclude, self.flags)

    def iter_filtered_urls(self, urls: Iterable[str]) -> Iterable[str]:
        yield from URLFilterMixin.iter_filtered_urls(urls, self.include, self.exclude, self.flags)


def _pattern_input_to_pattern_list(
    pattern: PatternArgType, flags: int | None = None
) -> list[re.Pattern] | None:
    if pattern is None:
        return pattern
    if not isinstance(pattern, list):
        pattern = [pattern]
    pattern = [p if isinstance(p, re.Pattern) else re.compile(p, flags=flags) for p in pattern]
    return pattern
