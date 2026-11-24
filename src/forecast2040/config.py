"""Configuration objects.

The registry lives in YAML so that adding a source is a data change, not a code
change. This module turns that file into frozen dataclasses and rejects a broken
registry before any request is made.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES = PROJECT_ROOT / "config" / "sources.yaml"
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_MANIFEST = PROJECT_ROOT / "data" / "manifest.csv"

VALID_KINDS = ("worldbank", "eurostat", "stooq", "yahoo", "csv")


class ConfigError(ValueError):
    """Raised when the source registry is not usable."""


@dataclass(frozen=True, slots=True)
class Source:
    """One machine-readable source."""

    id: str
    label: str
    kind: str
    url_template: str
    params: Mapping[str, Any]
    cadence: str
    licence: str
    enabled: bool = True

    def url(self) -> str:
        """Return the base URL with the scalar parameters substituted."""
        scalar = {k: v for k, v in self.params.items() if not isinstance(v, (dict, list))}
        try:
            return self.url_template.format(**scalar)
        except KeyError as exc:
            raise ConfigError(f"{self.id}: missing parameter {exc}") from exc


@dataclass(frozen=True, slots=True)
class Settings:
    """Everything a fetch run needs, resolved to absolute paths."""

    raw_dir: Path
    manifest_path: Path
    user_agent: str
    timeout_s: int
    max_retries: int
    backoff_s: float
    sources: tuple[Source, ...]

    def source(self, source_id: str) -> Source:
        for src in self.sources:
            if src.id == source_id:
                return src
        known = ", ".join(s.id for s in self.sources)
        raise ConfigError(f"unknown source {source_id!r}, known: {known}")


def _parse_sources(payload: Any) -> tuple[Source, ...]:
    if not isinstance(payload, dict) or "sources" not in payload:
        raise ConfigError("registry must be a mapping with a 'sources' key")
    entries = payload["sources"]
    if not isinstance(entries, list) or not entries:
        raise ConfigError("'sources' must be a non-empty list")

    parsed: list[Source] = []
    seen: set[str] = set()
    for raw in entries:
        if not isinstance(raw, dict):
            raise ConfigError("each source must be a mapping")
        missing = {"id", "label", "kind", "url_template", "params"} - raw.keys()
        if missing:
            raise ConfigError(f"source {raw.get('id')!r} misses {sorted(missing)}")
        if raw["kind"] not in VALID_KINDS:
            raise ConfigError(f"{raw['id']}: unknown kind {raw['kind']!r}")
        if raw["id"] in seen:
            raise ConfigError(f"duplicate source id {raw['id']!r}")
        seen.add(raw["id"])
        parsed.append(
            Source(
                id=str(raw["id"]),
                label=str(raw["label"]),
                kind=str(raw["kind"]),
                url_template=str(raw["url_template"]),
                params=dict(raw["params"]),
                cadence=str(raw.get("cadence", "unknown")),
                licence=str(raw.get("licence", "unspecified")),
                enabled=bool(raw.get("enabled", True)),
            )
        )
    return tuple(parsed)


def load_settings(
    registry_path: Path | None = None,
    raw_dir: Path | None = None,
    manifest_path: Path | None = None,
    user_agent: str = "forecast2040 research (contact: armin)",
) -> Settings:
    """Load and validate the registry."""
    path = registry_path or DEFAULT_SOURCES
    if not path.is_file():
        raise ConfigError(f"registry not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return Settings(
        raw_dir=(raw_dir or DEFAULT_RAW_DIR).resolve(),
        manifest_path=(manifest_path or DEFAULT_MANIFEST).resolve(),
        user_agent=user_agent,
        timeout_s=30,
        max_retries=3,
        backoff_s=1.5,
        sources=_parse_sources(payload),
    )


def select(settings: Settings, ids: Sequence[str] | None) -> tuple[Source, ...]:
    """Return the requested sources, or every enabled source when ids is empty.

    An explicitly named source is always honoured, even when it is disabled in
    the registry, because a disabled source is usually disabled for a reason
    that a single manual run may want to override.
    """
    if not ids:
        return tuple(source for source in settings.sources if source.enabled)
    return tuple(settings.source(i) for i in ids)
