from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class StreamConfig:
    name: str
    options: Dict[str, Any]
    recreate_if_exists: bool = False


@dataclass
class NatsConfig:
    servers: List[str]
    options: Dict[str, Any]
    streams: List[StreamConfig]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NatsConfig":
        return cls(
            streams=[
                StreamConfig(**stream)
                for stream in data["streams"]
                if isinstance(stream, dict)
            ],
            options=data.get("options", {}),
            servers=data.get("servers", []),
        )
