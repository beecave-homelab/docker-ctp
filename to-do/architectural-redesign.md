# To-Do: Refactor docker_ctp for Improved Modularity and Testability

This plan outlines the steps to refactor the `docker_ctp` package by applying modern design patterns to improve maintainability, testability, and code clarity. The core of this redesign is to decouple the business logic from the command-line interface.

## Overview

The `docker_ctp` package is currently a well-structured CLI application. However, the core workflow logic is orchestrated directly within the `cli` module (`docker_ctp/cli/__init__.py`), which calls individual functions from `docker_ctp/core/docker_ops.py`. This creates a tight coupling between the user interface and the application's business logic, making it more difficult to test the core functionality in isolation or to potentially offer a different interface (e.g., a library API) in the future.

This refactoring will introduce a **Service Layer** to encapsulate the core logic, using **Dependency Injection** to manage its dependencies.

## Tasks

- [ ] **Analysis Phase:**
  - [ ] Review current implementation and supporting modules
    - Path: `docker_ctp/cli/__init__.py`, `docker_ctp/core/docker_ops.py`
    - Action: Analyze the existing structure, where `cli` directly calls `docker_ops` functions, creating and managing dependencies like `Runner` and `CleanupManager`.
    - Analysis Results:
      - Key issue: The CLI module is doing too much: parsing arguments, creating configurations, managing dependencies, and orchestrating the main workflow. This violates the Single Responsibility Principle.
      - Major responsibilities to split: UI (Click CLI) vs. Core Business Logic (Docker Operations).
    - **Design Pattern Candidates:**
      - **Service Layer**: To encapsulate the business logic into a cohesive unit.
      - **Dependency Injection**: To provide the service with its dependencies, inverting control and improving testability.
    - Accept Criteria: A clear plan to separate the CLI from the core application workflow.
    - Status: Completed

- [ ] **Implementation Phase:**
  - [x] **Step 1: Create a new `DockerService`**
    - Path: `docker_ctp/core/service.py` (new file)
    - Action: Create a `DockerService` class that encapsulates the logic currently in `run_pipeline`. This service will take its dependencies (`Config`, `Runner`, `CleanupManager`) in its constructor. The `docker_ops` functions can be turned into private methods of this service or kept in `docker_ops` and called by the service.
    - **Design Patterns Applied:**
      - **Service Layer**: The `DockerService` acts as a service layer that exposes the application's main functionality (`execute_workflow`).
      - **Dependency Injection**: Dependencies are passed into the constructor, not created internally.
    - Status: Completed
  - [x] **Step 2: Refactor the CLI to use the `DockerService`**
    - Path: `docker_ctp/cli/__init__.py`
    - Action: Modify the `cli` function to instantiate the `Runner` and `CleanupManager`, then create an instance of `DockerService` with all its required dependencies (`Config`, `Runner`, `CleanupManager`). The `run_pipeline` function will be replaced by a single call to a method on the service object, e.g., `service.execute_workflow()`.
    - Status: Completed

- [x] **Testing Phase:**
  - [x] Write unit tests for the new `DockerService`
    - Path: `tests/test_service.py` (new file)
    - Action: Create focused unit tests for `DockerService`. Use mock objects for the `Runner` and `CleanupManager` to test the service's logic in complete isolation from the Docker daemon or filesystem.
    - Accept Criteria: Core workflow logic is tested independently of the CLI.

- [x] **Documentation Phase:**
  - [x] Update `project-overview.md`
    - Describe the new architecture, specifically mentioning the `DockerService` and the use of Dependency Injection to decouple the core logic from the CLI.
    - Accept Criteria: Documentation reflects the new, more modular structure.

- [x] **Review Phase:**
  - [ ] Validate the new structure for clarity, maintainability, and adherence to the proposed design patterns. (Ready for user review)

## Architectural Overview

The new architecture will be structured as follows:

**CLI (`__init__.py`) -> Service (`service.py`) -> Core Operations (`docker_ops.py`)**

- **New Component**: `docker_ctp.core.service.DockerService`
  - **Responsibility**: To orchestrate the entire build, tag, and push workflow. It is the heart of the application's business logic.
  - **Design Pattern Applied**:
    - **Service Layer**: This class acts as a clear, reusable service that contains a set of related operations.
    - **Dependency Injection**: The service receives its dependencies (`Config`, `Runner`, etc.) through its constructor. This inverts control, as the service is no longer responsible for creating its own dependencies. This makes it highly configurable and easy to test with mocks.

- **Modified Component**: `docker_ctp.cli.__init__.py`
  - **Responsibility**: Reduced to handling user interaction only. Its job is to parse CLI arguments, create the configuration and other dependency objects, and then hand them off to the `DockerService` to execute the workflow.

## Integration Points

- `docker_ctp/cli/__init__.py`: This is the primary consumer of the new `DockerService`. It will be responsible for instantiating the service with the correct dependencies based on user input.

## Related Files

- `docker_ctp/cli/__init__.py` (to be refactored)
- `docker_ctp/core/docker_ops.py` (logic to be encapsulated by the service)
- `docker_ctp/core/runner.py` (dependency to be injected)
- `docker_ctp/utils/cleanup.py` (dependency to be injected)
- `docker_ctp/config/__init__.py` (dependency to be injected)

## Future Enhancements

- **AppContext Class**: A future improvement could be to create a single `AppContext` object that holds all shared application state (`Config`, `Runner`, etc.) and pass that single context object into the service.
- **Multiple Services**: If the application grows, more services (e.g., `ReportingService`, `NotificationService`) could be added, all taking the `AppContext` as a dependency.
