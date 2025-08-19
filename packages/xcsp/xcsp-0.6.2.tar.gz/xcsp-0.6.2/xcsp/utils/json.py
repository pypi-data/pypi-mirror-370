import enum
import json


class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle enum serialization."""
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        return super().default(obj)