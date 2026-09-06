"""Local, revision-safe HTTP surface for the Visual Director workbench."""

from __future__ import annotations

import json
import mimetypes
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from director_plan import LockConflict, PatchError, RevisionConflict, apply_patch, atomic_write_json, load_json, plan_metrics, validate_plan


MAX_BODY = 1_000_000


class WorkbenchStore:
    def __init__(self, project: Path, catalog_path: Path | None = None):
        self.project = project.resolve()
        self.plan_path = self.project / "director-plan.json"
        self.catalog_path = catalog_path.resolve() if catalog_path else None
        self._lock = threading.RLock()
        if not self.plan_path.is_file():
            raise FileNotFoundError(self.plan_path)

    def _catalog(self) -> dict[str, Any] | None:
        return load_json(self.catalog_path) if self.catalog_path and self.catalog_path.is_file() else None

    def read(self) -> dict[str, Any]:
        with self._lock:
            plan = load_json(self.plan_path)
            catalog = self._catalog()
            return {
                "plan": plan,
                "metrics": plan_metrics(plan),
                "catalog": catalog or {"schemaVersion": "hyperframes-shared-catalog/v1", "entries": []},
                "errors": validate_plan(plan, catalog),
            }

    def patch(self, value: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            current = load_json(self.plan_path)
            catalog = self._catalog()
            updated = apply_patch(current, value, "human", catalog)
            atomic_write_json(self.plan_path, updated)
            return {"plan": updated, "metrics": plan_metrics(updated), "errors": validate_plan(updated, catalog)}


def handler_factory(store: WorkbenchStore, assets: Path):
    assets = assets.resolve()

    class Handler(BaseHTTPRequestHandler):
        server_version = "HyperFramesVisualDirector/1"

        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _json(self, status: int, value: Any) -> None:
            payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/api/plan":
                self._json(HTTPStatus.OK, store.read())
                return
            relative = "index.html" if path == "/" else unquote(path.lstrip("/"))
            candidate = (assets / relative).resolve()
            if assets not in candidate.parents or not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            payload = candidate.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mimetypes.guess_type(candidate.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/api/patch":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            if length <= 0 or length > MAX_BODY:
                self._json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"ok": False, "error": "invalid body size"})
                return
            try:
                value = json.loads(self.rfile.read(length))
                result = store.patch(value)
            except RevisionConflict as error:
                self._json(HTTPStatus.CONFLICT, {"ok": False, "error": "RevisionConflict", "message": str(error)})
                return
            except LockConflict as error:
                self._json(HTTPStatus.LOCKED, {"ok": False, "error": "LockConflict", "message": str(error)})
                return
            except (PatchError, ValueError, json.JSONDecodeError) as error:
                self._json(HTTPStatus.UNPROCESSABLE_ENTITY, {"ok": False, "error": type(error).__name__, "message": str(error)})
                return
            self._json(HTTPStatus.OK, {"ok": True, **result})

    return Handler


def create_server(project: Path, catalog: Path | None, host: str, port: int) -> ThreadingHTTPServer:
    store = WorkbenchStore(project, catalog)
    assets = Path(__file__).resolve().parents[1] / "assets" / "workbench"
    return ThreadingHTTPServer((host, port), handler_factory(store, assets))
