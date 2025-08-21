# quapp-braket

Quapp Braket library supporting the Quapp Platform for Quantum Computing with
providers, devices, circuit export, invocation, and job fetching utilities.

## Overview

`quapp-braket` is a Python library that integrates the Quapp Platform with
Amazon
Braket and related quantum backends. It provides common abstractions for
providers and devices, circuit conversion/export helpers, robust job submission
and fetching flows, and consistent, job-scoped logging across components. Recent
improvements focus on cleaner and more consistent logging, better error
handling, and clear separation of concerns between invocation and fetching
flows.

Features

- Provider and device factories for quantum computing platforms (e.g., AWS
  Braket, OQC Cloud, and Quapp simulators).
- Circuit export utilities, including conversion from Braket circuits to Qiskit
  circuits.
- Handlers for job invocation and job result fetching with enhanced,
  context-rich logging.
- Job-scoped, instance-bound logging for improved traceability and debugging.
- Refined log levels and simplified imports to reduce noise and improve clarity.
- Compatibility with Qiskit 1.4.3, pinned for stability.

## Installation

Install via pip:

``` bash
bash pip install quapp-braket
```

## Recently Changes Highlights

- Refactor: Added job-specific, instance-bound loggers and improved log levels
  across handlers and tasks.
- Refactor: Simplified imports and reduced redundant debug logs while keeping
  detailed context where needed.
- Build: Pinned Qiskit to 1.4.3 to ensure compatibility.
- Build: Added dependencies for quantum and AWS-related functionality to broaden
  backend support.
- Enhancement: Clearer handler selection logic for invocation vs. job fetching
  based on provider job IDs.

For detailed usage and API references, please refer to the in-code documentation
or contact the maintainers.
