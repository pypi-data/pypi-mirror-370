import json
from decimal import Decimal
from typing import Any, Union


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Union[float, str, Any]:
        if isinstance(obj, Decimal):
            return float(obj)
        # Handle other non-serializable objects by converting to string
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
