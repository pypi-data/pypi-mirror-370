import logging
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from queue import Queue, Empty
from typing import Any, Dict, List, Optional

import requests

from spacelog.SpaceLogCounter import SpaceLogCounter


class SpaceLogLogLevel(str, Enum):
    Debug = "debug"
    Info = "info"
    Warning = "warning"
    Error = "error"
    Critical = "critical"


@dataclass
class SpaceLogPingInfo:
    id: str
    group: str
    application: str
    is_observed: bool
    last_ping: datetime
    project: str
    is_enabled: bool


class BatchRequestHandler:
    """Batch payloads and post them as a JSON array at a fixed interval."""

    def __init__(
            self,
            base_url: str,
            endpoint: str,
            bearer_token: str,
            batch_interval: float,
            timeout_seconds: int = 5,
            name: str = "batch"
    ):
        self._url = base_url.rstrip("/") + endpoint
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }
        self._queue: "Queue[Dict[str, Any]]" = Queue()
        self._interval = float(batch_interval)
        self._timeout = int(timeout_seconds)
        self._name = name

        self._stop_evt = threading.Event()
        self._thread = threading.Thread(target=self._flush_loop, name=f"SpaceLog-{name}", daemon=True)

    def start(self) -> None:
        if not self._thread.is_alive():
            self._stop_evt.clear()
            self._thread = threading.Thread(target=self._flush_loop, name=f"SpaceLog-{self._name}", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop_evt.set()

    def join(self, timeout: Optional[float] = None) -> None:
        if self._thread.is_alive():
            self._thread.join(timeout=timeout)

    def enqueue(self, payload: Dict[str, Any]) -> None:
        if payload is None:
            raise ValueError("payload is None")
        self._queue.put(payload)

    def flush_now(self) -> None:
        batch = self._drain_all()
        if not batch:
            return
        self._post_batch(batch)

    def _flush_loop(self) -> None:
        next_wake = time.monotonic() + self._interval
        while not self._stop_evt.wait(timeout=max(0.0, next_wake - time.monotonic())):
            next_wake = time.monotonic() + self._interval
            batch = self._drain_all()
            if not batch:
                continue
            self._post_batch(batch)

        # final drain on stop
        final_batch = self._drain_all()
        if final_batch:
            self._post_batch(final_batch)

    def _drain_all(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        while True:
            try:
                item = self._queue.get_nowait()
                items.append(item)
            except Empty:
                break
        return items

    def _post_batch(self, batch: List[Dict[str, Any]]) -> None:
        try:
            resp = requests.post(self._url, json=batch, headers=self._headers, timeout=self._timeout)
        except Exception as ex:
            logging.warning(f"SpaceLog {self._name}: request failed ({ex})")
            return

        if resp.status_code != 200:
            text = resp.text.strip()
            logging.warning(f"SpaceLog {self._name}: server returned {resp.status_code}: {text}")


class SpaceLogClient:
    """SpaceLog client with batching for logs and counters, plus optional heartbeat."""

    DEFAULT_SUPABASE_PROJECT_ID = "qtdiupshceorsdarittk"

    SPACE_LOG_PROJECT_ID_ENV_NAME = "SPACE_LOG_PROJECT_ID"
    SPACE_LOG_APP_ID_ENV_NAME = "SPACE_LOG_APP_ID"
    SPACE_LOG_AUTH_TOKEN_ENV_NAME = "SPACE_LOG_TOKEN"

    def __init__(
            self,
            application_id: str,
            auth_token: Optional[str] = None,
            supabase_project: Optional[str] = None,
            web_timeout: int = 5,
            enable_heartbeat: bool = False,
            heartbeat_interval: float = 60.0,
            log_batch_interval: float = 10.0,
            counter_batch_interval: float = 5.0,
    ):
        # identity and config
        self.application_id = application_id
        self.auth_token = os.environ.get(self.SPACE_LOG_AUTH_TOKEN_ENV_NAME) if auth_token is None else auth_token
        self.supabase_project = (
            os.environ.get(self.SPACE_LOG_PROJECT_ID_ENV_NAME, self.DEFAULT_SUPABASE_PROJECT_ID)
            if supabase_project is None
            else supabase_project
        )
        self.web_timeout = int(web_timeout)

        # info populated by ping
        self._project: Optional[str] = None
        self._group: Optional[str] = None
        self._application: Optional[str] = None
        self._last_ping_str: Optional[str] = None
        self._is_enabled: Optional[bool] = None

        if not self.auth_token:
            logging.error(
                f"SpaceLog: auth token is not set. Set env var {self.SPACE_LOG_AUTH_TOKEN_ENV_NAME} or pass auth_token."
            )

        # batchers
        self._log_batcher = BatchRequestHandler(
            base_url=self.base_url,
            endpoint="/functions/v1/log-event",
            bearer_token=self.auth_token or "",
            batch_interval=log_batch_interval,
            timeout_seconds=self.web_timeout,
            name="logs",
        )
        self._counter_batcher = BatchRequestHandler(
            base_url=self.base_url,
            endpoint="/functions/v1/counter",
            bearer_token=self.auth_token or "",
            batch_interval=counter_batch_interval,
            timeout_seconds=self.web_timeout,
            name="counters",
        )

        self._log_batcher.start()
        self._counter_batcher.start()

        # heartbeat
        self._hb_enabled = bool(enable_heartbeat)
        self._hb_interval = float(heartbeat_interval)
        self._hb_stop_evt = threading.Event()
        self._hb_thread = threading.Thread(target=self._heartbeat_loop, name="SpaceLog-heartbeat", daemon=True)
        if self._hb_enabled:
            self.start_heartbeat(self._hb_interval)

    # properties to mirror C# fields
    @property
    def project(self) -> Optional[str]:
        return self._project

    @property
    def group(self) -> Optional[str]:
        return self._group

    @property
    def application(self) -> Optional[str]:
        return self._application

    @property
    def last_ping(self) -> Optional[str]:
        return self._last_ping_str

    @property
    def is_enabled(self) -> Optional[bool]:
        return self._is_enabled

    @property
    def base_url(self) -> str:
        return f"https://{self.supabase_project}.supabase.co"

    # heartbeat controls
    def start_heartbeat(self, interval: float = 60.0) -> None:
        self._hb_interval = float(interval)
        if not self._hb_thread.is_alive():
            self._hb_stop_evt.clear()
            self._hb_thread = threading.Thread(target=self._heartbeat_loop, name="SpaceLog-heartbeat", daemon=True)
            self._hb_thread.start()

    def stop_heartbeat(self) -> None:
        self._hb_stop_evt.set()

    def _heartbeat_loop(self) -> None:
        self.send_ping()
        while not self._hb_stop_evt.wait(self._hb_interval):
            self.send_ping()

    # ping
    def send_ping(self) -> Optional[SpaceLogPingInfo]:
        url = f"{self.base_url}/functions/v1/send-ping?guid={self.application_id}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=self.web_timeout)
        except Exception as ex:
            logging.warning(f"SpaceLog: could not send ping ({ex})")
            return None

        if resp.status_code != 200:
            logging.warning(f"SpaceLog: ping returned {resp.status_code}: {resp.text.strip()}")
            return None

        try:
            payload = resp.json()
        except Exception:
            logging.warning("SpaceLog: ping returned invalid json")
            return None

        data = payload.get("data") or []
        if not data:
            logging.warning("SpaceLog: ping returned no data")
            return None

        entry = data[0]

        # support both snake and camel keys
        def pick(key_snake: str, key_camel: str, default: Any = None) -> Any:
            if key_snake in entry:
                return entry[key_snake]
            if key_camel in entry:
                return entry[key_camel]
            return default

        last_ping_raw = pick("last_ping", "lastPing")
        try:
            # try iso parse without external deps
            last_ping_dt = datetime.fromisoformat(
                last_ping_raw.replace("Z", "+00:00")) if last_ping_raw else datetime.now(timezone.utc)
        except Exception:
            last_ping_dt = datetime.now(timezone.utc)

        ping_info = SpaceLogPingInfo(
            id=str(pick("id", "id", "")),
            group=str(pick("group", "group", "")),
            application=str(pick("application", "application", "")),
            is_observed=bool(pick("is_observed", "isObserved", False)),
            last_ping=last_ping_dt,
            project=str(pick("project", "project", "")),
            is_enabled=bool(pick("is_enabled", "isEnabled", True)),
        )

        # update cached fields
        self._project = ping_info.project
        self._group = ping_info.group
        self._application = ping_info.application
        self._is_enabled = ping_info.is_enabled
        self._last_ping_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        return ping_info

    # log methods enqueue only
    def log_debug(self, module: str, message: str, metadata: Optional[Dict[str, Any]] = None,
                  occurred_at: Optional[datetime] = None) -> None:
        self._enqueue_log(SpaceLogLogLevel.Debug, module, message, metadata, occurred_at)

    def log_info(self, module: str, message: str, metadata: Optional[Dict[str, Any]] = None,
                 occurred_at: Optional[datetime] = None) -> None:
        self._enqueue_log(SpaceLogLogLevel.Info, module, message, metadata, occurred_at)

    def log_warning(self, module: str, message: str, metadata: Optional[Dict[str, Any]] = None,
                    occurred_at: Optional[datetime] = None) -> None:
        self._enqueue_log(SpaceLogLogLevel.Warning, module, message, metadata, occurred_at)

    def log_error(self, module: str, message: str, metadata: Optional[Dict[str, Any]] = None,
                  occurred_at: Optional[datetime] = None) -> None:
        self._enqueue_log(SpaceLogLogLevel.Error, module, message, metadata, occurred_at)

    def log_critical(self, module: str, message: str, metadata: Optional[Dict[str, Any]] = None,
                     occurred_at: Optional[datetime] = None) -> None:
        self._enqueue_log(SpaceLogLogLevel.Critical, module, message, metadata, occurred_at)

    def _enqueue_log(
            self,
            level: SpaceLogLogLevel,
            module: str,
            message: str,
            metadata: Optional[Dict[str, Any]],
            occurred_at: Optional[datetime],
    ) -> None:
        when = occurred_at or datetime.now(timezone.utc)
        payload: Dict[str, Any] = {
            "guid": self.application_id,
            "level": str(level.value),
            "module": module,
            "message": message,
            "metadata": metadata or {},
            "occurred_at": when.isoformat(),
        }
        self._log_batcher.enqueue(payload)

    # counter methods enqueue only
    def update_counter(self, name: str, value: float, increment: bool) -> None:
        payload = {
            "guid": self.application_id,
            "name": name,
            "value": float(value),
            "increment": bool(increment),
        }
        self._counter_batcher.enqueue(payload)

    def increment_counter_by_one(self, name: str) -> None:
        self.update_counter(name, 1.0, True)

    def set_counter(self, name: str, value: float) -> None:
        self.update_counter(name, float(value), False)

    # lifecycle helpers
    def flush_now(self) -> None:
        self._log_batcher.flush_now()
        self._counter_batcher.flush_now()

    def close(self) -> None:
        try:
            self.stop_heartbeat()
        except Exception:
            pass
        self._log_batcher.stop()
        self._counter_batcher.stop()
        self._log_batcher.join(timeout=5.0)
        self._counter_batcher.join(timeout=5.0)

    def __enter__(self) -> "SpaceLogClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # additional methods for high-level objects
    def create_counter(self, name: str) -> SpaceLogCounter:
        return SpaceLogCounter(name, self)

    # factory from environment
    @staticmethod
    def from_environment(
            application_id: Optional[str] = None,
            auth_token: Optional[str] = None,
            supabase_project: Optional[str] = None,
            **kwargs: Any,
    ) -> Optional["SpaceLogClient"]:
        app_id = os.environ.get(SpaceLogClient.SPACE_LOG_APP_ID_ENV_NAME) if application_id is None else application_id
        token = os.environ.get(SpaceLogClient.SPACE_LOG_AUTH_TOKEN_ENV_NAME) if auth_token is None else auth_token
        project = (
            os.environ.get(SpaceLogClient.SPACE_LOG_PROJECT_ID_ENV_NAME, SpaceLogClient.DEFAULT_SUPABASE_PROJECT_ID)
            if supabase_project is None
            else supabase_project
        )

        if app_id is None:
            logging.warning(f"Spacelog could not find env var {SpaceLogClient.SPACE_LOG_APP_ID_ENV_NAME}")
            return None

        if token is None:
            logging.warning(f"Spacelog could not find env var {SpaceLogClient.SPACE_LOG_AUTH_TOKEN_ENV_NAME}")
            return None

        return SpaceLogClient(app_id, token, project, **kwargs)
