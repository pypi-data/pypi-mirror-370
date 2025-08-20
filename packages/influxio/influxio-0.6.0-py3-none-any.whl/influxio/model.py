import dataclasses
import sys
import typing as t
from enum import auto

from yarl import URL

from influxio.util.common import AutoStrEnum, url_fullpath, url_or_path


@dataclasses.dataclass
class CommandResult:
    exitcode: int
    stderr: str


class DataFormat(AutoStrEnum):
    """
    Manage data formats implemented by `FileAdapter`.
    """

    LINE_PROTOCOL_UNCOMPRESSED = auto()
    LINE_PROTOCOL_COMPRESSED = auto()
    ANNOTATED_CSV = auto()

    @classmethod
    def from_name(cls, path: str) -> "DataFormat":
        path = path.rstrip("/")
        if path.endswith(".lp"):
            return cls.LINE_PROTOCOL_UNCOMPRESSED
        elif path.endswith(".lp.gz"):
            return cls.LINE_PROTOCOL_COMPRESSED
        elif path.endswith(".csv"):
            return cls.ANNOTATED_CSV
        else:
            raise ValueError(f"Unable to derive data format from file name: {path}")

    @classmethod
    def from_url(cls, url: t.Union[URL, str]) -> "DataFormat":
        if isinstance(url, str):
            url: URL = URL(url)
        if format_ := url.query.get("format"):
            if format_ == "lp":
                return cls.LINE_PROTOCOL_UNCOMPRESSED
            elif format_ == "lp.gz":
                return cls.LINE_PROTOCOL_COMPRESSED
            elif format_ == "csv":
                return cls.ANNOTATED_CSV
            else:
                raise NotImplementedError(f"Invalid data format: {format_}")
        try:
            return cls.from_name(url_fullpath(url))
        except ValueError as ex:
            raise ValueError(f"Unable to derive data format from URL filename or query parameter: {url}") from ex


@dataclasses.dataclass
class OutputFile:
    """
    Manage output file and format for `FileAdapter`.
    """

    path: str
    format: DataFormat  # noqa: A003

    @classmethod
    def from_url(cls, url: t.Union[URL, str]) -> "OutputFile":
        if isinstance(url, str):
            url: URL = URL(url)
        if url.scheme == "file":
            return cls(path=url_or_path(url), format=DataFormat.from_url(url))
        else:
            raise NotImplementedError(f"Unknown file output scheme: {url.scheme}")

    @property
    def stream(self) -> t.IO:
        if self.path == "-":
            return sys.stdout
        else:
            return open(self.path, "w")
