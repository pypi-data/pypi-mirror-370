# -*- coding: utf-8 -*-

"""
Configuration Merge Pattern for Secure Configuration Management

This module solves a critical security problem in configuration management: 
**separating sensitive data from non-sensitive data** while maintaining a 
unified configuration structure for application consumption.

**The Security Problem**

In production applications, you need to store:
- **Non-sensitive config**: Database hosts, timeouts, feature flags (safe to version control)
- **Sensitive config**: Passwords, API keys, certificates (must NOT be in version control)

**Traditional Problems**

Without proper separation, developers often:

1. 🚨 **Accidentally commit secrets** to version control
2. 🔄 **Duplicate config structure** between files (maintenance nightmare)
3. 🐛 **Manual config assembly** (error-prone, inconsistent)
4. 🚀 **Complex deployment** (hard to automate, environment-specific)

**The Solution: Structural Merging**

This module provides **recursive, structure-aware merging** that:

- ✅ **Preserves data types**: Handles dicts, lists, and nested structures
- ✅ **Maintains relationships**: Merges corresponding list items by position
- ✅ **Validates structure**: Ensures configs have compatible schemas
- ✅ **Prevents corruption**: Immutable operations (returns new objects)

**Example Use Case**

.. code-block:: python

    # config.json (safe to commit)
    {
        "database": {
            "host": "prod-db.com",
            "port": 5432
        },
        "users": [
            {"username": "admin"},
            {"username": "app"}
        ]
    }

    # secrets.json (encrypted, never committed)
    {
        "database": {
            "password": "secret123"
        },
        "users": [
            {"password": "admin-pwd"},
            {"password": "app-pwd"}
        ]
    }

    # Result after merging
    {
        "database": {
            "host": "prod-db.com",
            "port": 5432,
            "password": "secret123"
        },
        "users": [
            {"username": "admin", "password": "admin-pwd"},
            {"username": "app", "password": "app-pwd"}
        ]
    }

**When to Use This Pattern**

- ✅ **Multi-environment deployments** with sensitive config
- ✅ **Microservices** with shared config structure
- ✅ **CI/CD pipelines** that inject secrets at deployment time
- ✅ **Configuration templates** that need runtime data injection
- ✅ **Compliance scenarios** requiring secret/non-secret separation
"""

import typing as T
import copy


def deep_merge(
    data1: dict,
    data2: dict,
    _fullpath: T.Optional[str] = None,
) -> dict:
    """
    Intelligently merge two configuration dictionaries while preserving structure and relationships.
    
    This function solves the critical problem of **safely combining configuration files**
    without losing data or breaking relationships between configuration elements.
    
    **Why Use This Instead of Simple Dict Updates?**
    
    Standard dict.update() operations are **shallow** and **destructive**:
    - ❌ Overwrites entire nested dictionaries
    - ❌ Replaces entire lists (losing relationships)
    - ❌ No validation of structural compatibility
    
    This function provides **deep, intelligent merging**:
    - ✅ **Recursive**: Merges nested dictionaries at any depth
    - ✅ **Positional**: Merges list items by position (maintains relationships)
    - ✅ **Immutable**: Returns new objects (original data unchanged)
    - ✅ **Validated**: Ensures structural compatibility between inputs
    
    **Common Use Cases:**
    
    1. **Secret Injection**: Merge non-sensitive config with secrets
    2. **Environment Overrides**: Combine base config with environment-specific values
    3. **Modular Config**: Assemble configuration from multiple sources
    4. **Template Expansion**: Fill configuration templates with runtime data
    
    **Examples:**
    
    Basic merging::
    
        >>> base_config = {
        ...     "database": {"host": "localhost", "port": 5432},
        ...     "features": {"logging": True}
        ... }
        >>> secrets = {
        ...     "database": {"password": "secret123"},
        ...     "features": {"analytics": False}
        ... }
        >>> result = deep_merge(base_config, secrets)
        >>> # Result: {
        >>> #     "database": {"host": "localhost", "port": 5432, "password": "secret123"},
        >>> #     "features": {"logging": True, "analytics": False}
        >>> # }
    
    List merging (by position)::
    
        >>> user_config = {
        ...     "users": [
        ...         {"username": "alice", "role": "admin"},
        ...         {"username": "bob", "role": "user"}
        ...     ]
        ... }
        >>> password_config = {
        ...     "users": [
        ...         {"password": "alice-secret"},
        ...         {"password": "bob-secret"}
        ...     ]
        ... }
        >>> result = deep_merge(user_config, password_config)
        >>> # Result: {
        >>> #     "users": [
        >>> #         {"username": "alice", "role": "admin", "password": "alice-secret"},
        >>> #         {"username": "bob", "role": "user", "password": "bob-secret"}
        >>> #     ]
        >>> # }

    :param data1: Base configuration dictionary (typically non-sensitive config)
    :param data2: Override configuration dictionary (typically secrets or environment-specific)
    :param _fullpath: Internal parameter for error reporting (do not use)

    :raises ValueError: When lists have different lengths (structural mismatch)
    :raises TypeError: When attempting to merge incompatible data types

    :return: New dictionary containing the intelligently merged configuration

    .. note::

        **This operation is immutable** - original dictionaries are not modified.
        The function creates deep copies before merging to prevent side effects.
    """
    # 🛡️ Create deep copies to ensure immutability (prevent side effects on original data)
    # This is critical for config safety - we never want to accidentally modify source configs
    data1 = copy.deepcopy(data1)
    data2 = copy.deepcopy(data2)
    
    # 📍 Track current path for meaningful error messages during recursive merging
    if _fullpath is None:
        _fullpath = ""

    # 🔍 Analyze key relationships between the two dictionaries
    # This set-based approach efficiently categorizes keys for different merge strategies
    difference = data2.keys() - data1.keys()      # Keys only in data2 (new additions)
    intersection = data1.keys() & data2.keys()   # Keys in both (potential conflicts/merges)

    # ➕ Handle new keys: Simple addition to result (no conflicts possible)
    # Example: data1={"host": "db.com"}, data2={"password": "secret"}
    # Result gets password without any complexity
    for key in difference:
        data1[key] = data2[key]

    # 🤝 Handle overlapping keys: This is where intelligent merging happens
    # We need to decide how to combine values that exist in both dictionaries
    for key in intersection:
        value1, value2 = data1[key], data2[key]
        
        # 📂 CASE 1: Both values are dictionaries → Recursive merge
        # Why recursive? Nested configs are common (database.host, database.port, database.password)
        # We want to preserve the nested structure while combining all properties
        if isinstance(value1, dict) and isinstance(value2, dict):
            data1[key] = deep_merge(value1, value2, f"{_fullpath}.{key}")
            
        # 📋 CASE 2: Both values are lists → Positional merge
        # Critical for maintaining relationships: user[0] password must match user[0] username
        elif isinstance(value1, list) and isinstance(value2, list):
            # 🚨 Length validation: Structural mismatch indicates config error
            # Example: 3 users but 2 passwords = undefined behavior
            if len(value1) != len(value2):
                raise ValueError(f"list length mismatch: path = '{_fullpath}.{key}'")
                
            # 🔄 Merge corresponding list items by position
            # zip() ensures we process pairs: (user[0], password[0]), (user[1], password[1])
            merged_list = []
            for item1, item2 in zip(value1, value2):
                # 🎯 Only merge dictionaries - other types would lose data or create ambiguity
                if isinstance(item1, dict) and isinstance(item2, dict):
                    merged_list.append(deep_merge(item1, item2, f"{_fullpath}.{key}"))
                else:
                    # 💥 Fail fast on type mismatches - better than silent data corruption
                    raise TypeError(
                        f"items in '{_fullpath}.{key}' are not dict, so you cannot merge them!"
                    )
            data1[key] = merged_list
            
        # 💥 CASE 3: Incompatible types → Error
        # We can't safely merge different types without data loss or ambiguity
        # Examples: string + dict, int + list, etc.
        else:
            raise TypeError(
                f"type of value at '{_fullpath}.{key}' in data1 and data2 "
                f"has to be both dict or list of dict to merge! "
                f"they are {type(value1)} and {type(value2)}."
            )

    # 🎉 Return the fully merged configuration
    # At this point: all new keys added, all compatible keys merged, all conflicts resolved
    return data1
