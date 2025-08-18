# quapp-dwave-ocean

Quapp D-Wave Ocean library supporting Quapp Platform for Quantum Computing.

## Overview

`quapp-dwave-ocean` provides providers, devices, factories, and async tasks to
run
Binary Quadratic Models (BQMs) via D-Wave Ocean within the Quapp Platform. It
supports
D-Wave system and hybrid devices as well as a QuaO quantum simulator, featuring
consistent context-rich logging, robust error handling, and standardized
project/workspace
headers for clean integration with backend services.

## Features

- Provider and device factories for:
    - D-Wave System devices
    - D-Wave Hybrid devices
    - Quapp D-Wave Ocean simulator
- Asynchronous circuit export to SVG (BQM visualization) with optional
  compression and upload.
- Consistent, instance-level logging across provider/device creation, job
  invocation, export, and fetching.
- Standardized project/workspace header handling for backend invocations.
- Improved error handling and diagnostics in critical paths (export,
  provider/device creation, job processing).
- Job fetching workflow encapsulated for clarity and maintainability.

## Installation

Install via pip:

```bash
pip install quapp-dwave-ocean
```

## Recently Changes Highlights

- chore: Bump a version to `0.0.1.dev2` and update `quapp-common` dependency to
  `0.0.11.dev6`
- refactor: Replace global logger usage with instance-level logging and enhance
  debug information across D-Wave Ocean modules
- feature: Create `DWaveOceanJobFetching` class for managing job fetching logic in
  D-Wave Ocean backend
- feature: Add `DWaveOceanCircuitExportTask` for exporting and processing D-Wave
  Ocean circuit visualizations
- refactor: Update import paths from `qapp_common` to `quapp_common` for consistency
  across modules

For detailed usage and API references, please refer to the in-code documentation
or contact the maintainers.