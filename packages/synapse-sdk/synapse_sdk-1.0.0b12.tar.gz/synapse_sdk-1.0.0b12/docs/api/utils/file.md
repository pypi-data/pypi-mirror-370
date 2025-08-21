---
id: file
title: File Utilities
sidebar_position: 1
---

# File Utilities

File operations and handling utilities.

## File Operations

### Archive Functions

Functions for creating and extracting plugin archives.

### Download Functions

Utilities for downloading files from URLs.

```python
from synapse_sdk.utils.file import download_file

local_path = download_file(url, destination)
```

### Upload Functions

File upload utilities with chunked upload support.

## Path Utilities

Functions for path manipulation and validation.

## Temporary Files

Utilities for managing temporary files and cleanup.