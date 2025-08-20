import hashlib
import json
from typing import TYPE_CHECKING, Literal, get_args, get_type_hints

from pydantic import BaseModel

if TYPE_CHECKING:
    from parameter import Parameter


class Config(BaseModel):
    parameter: "Parameter"

    def model_post_init(self, __context):
        """
        Validate that `parameter` matches its type annotations.
        """
        param_cls = type(self.parameter)
        hints = get_type_hints(param_cls)

        for field, expected_type in hints.items():
            value = getattr(self.parameter, field, None)

            # Handle Literal
            if getattr(expected_type, "__origin__", None) is Literal:
                allowed_values = get_args(expected_type)
                if value not in allowed_values:
                    raise TypeError(
                        f"Parameter field '{field}' expects one of {allowed_values}, "
                        f"got {value!r}"
                    )
            else:
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"Parameter field '{field}' expects {expected_type}, "
                        f"got {type(value)} with value {value!r}"
                    )

    def write_to_json_file(self, file_path: str) -> None:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.model_dump_json(indent=2))
            print(f"Successfully wrote config to {file_path}")
        except Exception as e:
            print("Error writing file:", e)

    def stable_config_hash(self) -> str:
        data = self.parameter.model_dump()
        json_repr = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(bytes(json_repr, "utf-8")).hexdigest()
