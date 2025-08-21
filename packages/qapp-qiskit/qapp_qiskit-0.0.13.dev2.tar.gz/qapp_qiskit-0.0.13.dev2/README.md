# quapp-qiskit

Quapp qiskit library supporting Quapp Platform for Quantum Computing.

## Overview

`quapp-qiskit` provides the providers, devices, factories, and tasks to
run quantum circuits via Qiskit within the Quapp Platform. It integrates with
IBM Quantum, IBM Cloud, OQC Cloud, and Qiskit simulators (Aer), with a strong
focus on clean, consistent logging, robust error handling, and standardized
header management using project/workspace context to improve maintainability and
clarity.

## Features

- Provider and device factories for IBM Quantum, IBM Cloud, OQC Cloud, and
  Qiskit Aer simulators.
- Circuit export and transpilation pipeline with asynchronous job submission.
- Consistent, context-rich logging across provider/device creation,
  transpilation, job submission, and job fetching.
- Standardized header handling using project and workspace headers for backend
  invocations.
- Improved error handling and diagnostics in critical execution paths.

## Installation

Install via pip:

```bash
pip install quapp-qiskit
```

## Recently Changes Highlights

- refactor: Remove unused timing logs and import from InvocationHandler.
- refactor: Replace set/map usage with set comprehension and enhance logging for
  unsupported devices.
- refactor: Add support for project and workspace headers in backend invocation.
- refactor: Update logging to handle missing jobId gracefully.
- refactor: Improve logging across device and provider classes, enhance error
  handling in key methods.
- chore: Bump a library version and update quapp-common dependency to the latest
  development release.

For detailed usage and API references, please refer to the in-code documentation
or contact the maintainers.