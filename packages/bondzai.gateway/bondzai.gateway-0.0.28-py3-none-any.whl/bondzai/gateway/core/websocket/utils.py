import json
from typing import Any


def ws_client_serialize(o: Any) -> str:
    return json.dumps(o)


def ws_client_deserialize(o: str) -> Any:
    return json.loads(o)
