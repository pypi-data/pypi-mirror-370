# -*- coding: utf-8 -*-

"""
Hierarchical Configuration Inheritance Pattern

This module provides a DRY (Don't Repeat Yourself) solution for configuration 
management by implementing inheritance patterns similar to object-oriented 
programming, but for JSON-like data structures.

**Problem It Solves**

When managing configurations for multiple environments (dev, staging, prod), 
you often need to repeat common settings across environments. This leads to 
duplication and maintenance overhead.

**Solution**

Use a special ``_shared`` section to define default values that automatically
inherit to other sections, while allowing environment-specific overrides.

**How It Works**

The ``_shared`` section contains JSON path patterns that specify where default
values should be applied. Values are only set if they don't already exist 
(no overwriting).

**Basic Example**

Input configuration::

    {
        "_shared": {
            "*.username": "root",       # Apply to all environments
            "*.memory": 2               # Default memory allocation
        },
        "dev": {
            "password": "dev123"        # Dev-specific setting
        },
        "prod": {
            "password": "prod456",      # Prod-specific setting
            "memory": 8                 # Override default memory
        }
    }

After applying inheritance, becomes::

    {
        "dev": {
            "username": "root",         # Inherited from _shared
            "password": "dev123",       # Original value
            "memory": 2                 # Inherited from _shared
        },
        "prod": {
            "username": "root",         # Inherited from _shared
            "password": "prod456",      # Original value
            "memory": 8                 # Override (not replaced)
        }
    }

**JSON Path Patterns**

- ``*.field``: Apply to all top-level keys (except _shared)
- ``env.field``: Apply to specific environment
- ``*.db.*.port``: Apply to nested structures with wildcards
- ``env.services.port``: Apply to specific nested path

**Key Features**

- Non-destructive: Existing values are never overwritten
- Recursive: Supports nested _shared sections for fine-grained control
- Flexible: Works with dictionaries and lists of dictionaries
- Order-aware: Evaluation order matters for overlapping patterns
"""

import typing as T

SHARED = "_shared"
"""
Special key used to define shared inheritance rules in configuration data.
"""

_error_tpl = (
    "node at JSON path {_prefix!r} is not a dict or list of dict! "
    "cannot set node value '{prefix}.{key}' = ...!"
)


def make_type_error(prefix: str, key: str) -> TypeError:
    """
    Create a descriptive TypeError when trying to set a value on incompatible data types.

    This helper creates user-friendly error messages when the inheritance process
    encounters data that isn't a dict or list of dicts, which are the only
    structures that support key assignment.

    :param prefix: The JSON path prefix where the error occurred
    :param key: The key we were trying to set

    :raises TypeError: with descriptive message about the invalid operation
    """
    if prefix == "":
        _prefix = "."
    else:
        _prefix = prefix
    return TypeError(_error_tpl.format(_prefix=_prefix, prefix=prefix, key=key))


def inherit_value(
    path: str,
    value: T.Any,
    data: T.Union[T.Dict[str, T.Any], T.List[T.Dict[str, T.Any]]],
    _prefix: T.Optional[str] = None,
) -> None:
    """
    Apply a default value to a JSON path pattern, preserving existing values.

    This is the core inheritance mechanism that implements setdefault-like behavior
    for nested configuration structures. Like dict.setdefault(), it only sets values
    where keys don't already exist, never overwriting existing configuration.

    **What it does**

    - Follows JSON path patterns like ``"*.username"`` or ``"dev.database.port"``
    - Sets values only where they're missing (non-destructive)
    - Handles wildcards (*) to apply to multiple targets
    - Works with nested dicts and lists of dicts

    **Examples**

    - Path ``"*.memory"`` -> Sets ``memory=2`` in all top-level environments
    - Path ``"dev.db.port"`` -> Sets ``port=5432`` only in ``dev.db``
    - Path ``"*.servers.*.cpu"`` -> Sets ``cpu=1`` in all servers across all environments

    :param path: JSON path pattern (e.g., ``"*.username"``, ``"dev.db.port"``)
    :param value: The default value to set
    :param data: Configuration dict/list to modify in-place
    :param _prefix: Internal recursion parameter (do not use)

    :raises ValueError: If path ends with "*" (incomplete path)
    :raises TypeError: If trying to set values on incompatible data types

    :return: None

    .. important::
        The input param ``data`` will be modified in-place. If you want to keep
        the original data, do this before calling this function:

        .. code-block:: python

            import copy

            new_data = copy.deepcopy(data)
            inherit_value(path, value, new_data)
    """
    # print(f"{path = }, {value = }, {_prefix = }") # for debug only
    if path.endswith("*"):
        raise ValueError("json path cannot ends with *!")
    if _prefix is None:
        _prefix = ""

    parts = path.split(".")

    if len(parts) == 1:
        if isinstance(data, dict):
            data.setdefault(parts[0], value)
        elif isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    raise make_type_error(_prefix, parts[0])
                item.setdefault(parts[0], value)
        else:
            raise make_type_error(_prefix, parts[0])
        return

    key = parts[0]
    if key == "*":
        for k, v in data.items():
            if k != SHARED:
                inherit_value(
                    path=".".join(parts[1:]),
                    value=value,
                    data=v,
                    _prefix=f"{_prefix}.{key}",
                )
    else:
        if isinstance(data, dict):
            inherit_value(
                path=".".join(parts[1:]),
                value=value,
                data=data[key],
                _prefix=f"{_prefix}.{key}",
            )
        elif isinstance(data, list):
            for item in data:
                inherit_value(
                    path=".".join(parts[1:]),
                    value=value,
                    data=item[key],
                    _prefix=f"{_prefix}.{key}",
                )
        else:
            raise make_type_error(_prefix, key)


def apply_inheritance(
    data: dict[str, T.Any],
) -> None:
    """
    Transform configuration data by applying all ``_shared`` inheritance rules.

    This is the main entry point that processes an entire configuration structure,
    finding all _shared sections and applying their inheritance rules to create
    the final resolved configuration.

    **What it does:**

    1. Recursively processes nested _shared sections (deeper ones override shallower ones)
    2. Applies each JSON path pattern in the _shared section in definition order
    3. Removes all _shared sections from the final output
    4. Modifies the input data in-place

    **Path Execution Order Within Same _shared:**

    Within a single _shared section, paths are processed from top to bottom.
    If multiple paths affect the same node, the earlier path takes effect due to
    setdefault behavior. This enables powerful exception-then-default patterns.

    Example - setting defaults with specific exceptions::

        {
            "_shared": {
                "*.servers.blue.cpu": 4,    # Exception: blue gets 4 CPU
                "*.servers.*.cpu": 2        # Default: all others get 2 CPU  
            },
            "env": {
                "servers": {
                    "blue": {},             # Gets cpu=4 (from first rule)
                    "green": {}             # Gets cpu=2 (from second rule)
                }
            }
        }

    The exception must be defined before the wildcard pattern to take effect.

    **Child _shared Overrides Parent _shared:**

    Each nested object can have its own _shared section. When both parent and
    child _shared sections would affect the same node, the child wins due to
    processing order (children processed before parents).

    Example - nested inheritance hierarchy::

        {
            "_shared": {
                "*.servers.*.memory": 1024  # Parent default
            },
            "env": {
                "servers": {
                    "_shared": {
                        "*.memory": 2048    # Child override
                    },
                    "web": {}               # Gets memory=2048 (child wins)
                }
            }
        }

    This design allows fine-grained control where specific sections can override
    broader defaults while maintaining the inheritance hierarchy.

    **Basic Example**:

    >>> data = {
    ...     "_shared": {
    ...         "*.memory": 2
    ...     },
    ...     "dev": {},
    ...     "prod": {
    ...         "memory": 8
    ...     }
    ... }
    >>> apply_inheritance(data)
    >>> data
    {
        "dev": {"memory": 2},     # Inherited default
        "prod": {"memory": 8}     # Kept existing value
    }

    :param data: Configuration dictionary with _shared sections to process

    .. important::
        The input param ``data`` will be modified in-place, all _shared sections
        will be removed and their rules applied. If you want to keep the original data,
        do this before calling this function:

        .. code-block:: python

            import copy

            new_data = copy.deepcopy(data)
            apply_inheritance(new_data)
    """
    # implement recursion pattern
    for key, value in data.items():
        if key == SHARED:
            continue
        if isinstance(value, dict):
            apply_inheritance(value)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    apply_inheritance(item)

    # try to set shared value
    has_shared = SHARED in data
    if has_shared is False:
        return

    # pop the shared data, it is not needed in the final result
    shared_data = data.pop(SHARED)
    for path, value in shared_data.items():
        inherit_value(path=path, value=value, data=data)
