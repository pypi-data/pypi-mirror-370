import logging

from typing import Dict


log = logging.getLogger(__name__)


threading_local = None
try:
    from log_request_id import local

    threading_local = local
except ImportError:
    log.warning("Can't check request_id", exc_info=True)


def get_request_id_header() -> Dict[str, str]:
    if not threading_local:
        return {}
    request_id = getattr(threading_local, "request_id", None)
    if not request_id or request_id == "none":
        return {}
    return {"X-Request-Id": request_id}
