import base64
from typing import Tuple


def from_base64(value: str) -> Tuple[str, str]:
    """
    FROM:
    https://github.com/strawberry-graphql/strawberry/blob/main/strawberry/relay/utils.py#L16C1-L40C1

    Parse the base64 encoded relay value.

    Args:
        value:
            The value to be parsed

    Returns:
        A tuple of (TypeName, NodeID).

    Raises:
        ValueError:
            If the value is not in the expected format

    """
    try:
        res = base64.b64decode(value.encode()).decode().split(":", 1)
    except Exception as e:
        raise ValueError(str(e)) from e

    if len(res) != 2:
        raise ValueError(f"{res} expected to contain only 2 items")

    return res[0], res[1]
