"""Ahrefs API：使用官方 Python SDK（与 ahrefs-api-skills / ahrefs-python 一致）。"""

from __future__ import annotations

import os
from typing import Any, Sequence

from ahrefs import AhrefsClient


def _load_dotenv_if_present() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in ("../../../..", ".."):
        p = os.path.abspath(os.path.join(here, rel, ".env"))
        if os.path.isfile(p):
            load_dotenv(p)
            return


def get_client() -> AhrefsClient:
    """从环境变量读取 AHREFS_API_KEY；可选 AHREFS_API_BASE。"""
    _load_dotenv_if_present()
    base = os.environ.get("AHREFS_API_BASE")
    if base:
        return AhrefsClient(base_url=base.rstrip("/"))
    return AhrefsClient()


def rows_to_jsonable(rows: Sequence[Any]) -> list[dict[str, Any]]:
    """将 SDK 返回的 Pydantic 行转为可 JSON 序列化的 dict。"""
    out: list[dict[str, Any]] = []
    for row in rows:
        if hasattr(row, "model_dump"):
            out.append(row.model_dump(mode="json"))
        else:
            out.append(dict(row))  # type: ignore[arg-type]
    return out
