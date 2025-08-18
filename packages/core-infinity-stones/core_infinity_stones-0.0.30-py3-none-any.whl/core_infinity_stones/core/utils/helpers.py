import re
from typing import Any, Optional, TypeVar


def build_url(*url_components: Optional[str]) -> str:
    """
    Builds a URL from the provided components, removing any unintended extra slashes and ignoring
    components that are None.
    """
    compacted_url_components = [
        component for component in url_components if component is not None
    ]
    components_joined_by_slash = "/".join(compacted_url_components)

    url = _remove_double_slashes_not_preceded_by_columns(components_joined_by_slash)

    return url


def _remove_double_slashes_not_preceded_by_columns(url):
    if url.startswith("https:"):
        return re.sub(r"(?<!https:)/+", "/", url)
    elif url.startswith("http:"):
        return re.sub(r"(?<!http:)/+", "/", url)


T = TypeVar("T")


def get_all_missing_keys_in_dict(dict_: dict[T, Any], keys: list[T]) -> list[T]:
    """Returns a list of keys that are missing from the provided dictionary."""
    missing_keys = [key for key in keys if key not in dict_]
    return missing_keys
