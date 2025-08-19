import json
from datetime import datetime

from dataclasses import dataclass
from typing import Any, Literal

from polars_hist_db.utils import to_ipc_b64


@dataclass
class NatsPayload:
    type: Literal["json", "ipc", "epoch_ms", "error"]
    data: Any

    def as_bytes(self) -> bytes:
        encodable_result: str | int | bytes
        if self.type == "ipc":
            encodable_result = to_ipc_b64(self.data, "zlib").decode()
        elif self.type == "epoch_ms":
            if isinstance(self.data, datetime):
                encodable_result = int(self.data.timestamp() * 1000)
            else:
                assert isinstance(self.data, int), (
                    "Data must be a integer object (milliseconds since epoch)"
                )
                encodable_result = self.data
        else:
            # its a json-encodable object
            encodable_result = self.data

        json_result = json.dumps(
            {
                "data": encodable_result,
                "type": self.type,
            }
        )

        result = json_result.encode("utf-8")
        return result

    def __str__(self) -> str:
        match self.type:
            case "json":
                return f"Response(type={self.type}, len={len(self.data)})"
            case "ipc":
                return f"Response(type={self.type}, rowcount={len(self.data)})"
            case _:
                return f"Response(type={self.type})"
