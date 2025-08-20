from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar


class CrawlStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    TIMED_OUT = "timed_out"
    FAILED = "failed"
    ABORTED = "aborted"
    ERROR = "error"


class EngineType(str, Enum):
    PLAYWRIGHT = "playwright"
    CHEERIO = "cheerio"
    AUTO = "auto"


@dataclass
class StartCrawlPayload:
    startUrl: str
    maxResults: int
    maxDepth: Optional[int] = None
    includeLinks: Optional[bool] = None
    useSitemap: Optional[bool] = None
    timeout: Optional[int] = None
    engineType: Optional[EngineType] = None
    useStaticIps: Optional[bool] = None


@dataclass
class QueryCrawlsPayload:
    status: Optional[List[CrawlStatus]] = None
    startUrls: Optional[List[str]] = None
    page: int


@dataclass
class CrawlResult:
    crawlId: str
    brandId: Optional[str]
    url: str
    title: str
    markdown: str
    depthOfUrl: Optional[int]
    createdAt: Optional[str] = None
    anonymousUserId: Optional[str] = None
    isSuccess: Optional[bool] = None
    error: Optional[str] = None
    isDeleted: Optional[bool] = None


@dataclass
class Crawl:
    id: str
    status: CrawlStatus
    startUrls: List[str]
    includeLinks: bool
    maxDepth: int
    maxResults: int
    brandId: str
    createdAt: str
    completedAt: Optional[str]
    durationInSeconds: int
    numberOfResults: int
    useSitemap: bool
    timeout: int
    useStaticIps: bool
    engineType: EngineType


T = TypeVar("T")


@dataclass
class PaginationResult(Generic[T]):
    results: List[T]
    page: int
    limit: int
    totalPages: int
    totalResults: int


def _from_dict(model_cls, data: Dict[str, Any]):
    return model_cls(**data)


