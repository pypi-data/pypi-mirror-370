# Changelog

All notable changes to this project will be documented in this file.

## [2.6.0] - 2025-08-17

### Added
- **New Environment Architecture**: `set_solver()`, `launch_dashboard()`, `run_headless()` methods
- **Simplified Main.py**: Super simple orchestrator that imports env and solver, passes solver to env
- **Enhanced Solver Integration**: Environment now handles solver execution and mode selection
- **Improved Dashboard Launch**: Proper Streamlit subprocess launching with error handling

### Changed
- **Main.py Refactored**: Now imports environment and solver, passes solver to environment
- **Environment Orchestration**: Environment handles launching dashboard or running headless
- **Architecture Flow**: Main.py → Environment → Solver → Dashboard/Headless execution
- **Usage Patterns**: Cleaner API for developers and contestants

### Fixed
- **Dashboard Launch**: Fixed Streamlit launching issues with proper subprocess handling
- **Environment Methods**: All new methods properly integrated and tested
- **Documentation**: Updated all docs to reflect new architecture

## [2.5.2] - 2025-08-17

### Added
- New environment methods: `set_solver()`, `launch_dashboard()`, `run_headless()`
- Simplified main.py architecture for easy solver testing
- Enhanced headless execution with comprehensive result saving

### Changed
- Refactored main.py to be super simple: import env, import solver, pass solver to env, run mode
- Updated headless runner to use only existing environment methods
- Streamlined environment API for better contestant experience

### Fixed
- Removed Unicode encoding issues in headless result saving
- Fixed indentation errors in headless runner
- Corrected mock data initialization for consistent testing

## [2.5.1] - 2025-08-17

### Added
- `unload_sku_to_warehouse()` method for multi-warehouse scenarios
- Enhanced multi-warehouse logistics support

### Changed
- Consolidated route execution methods into single `execute_route()` method
- Simplified environment API by removing redundant methods
- Updated dashboard to show item counts instead of SKU counts

### Removed
- Redundant properties and methods for cleaner API
- Unused distance calculation wrappers
- Overly complex live tracking methods

## [2.5.0] - 2025-08-17

### Added
- Multi-warehouse logistics environment
- Item-level operations and inventory tracking
- Centralized state management with atomic operations
- Comprehensive validation and metrics calculation
- Interactive dashboard and headless execution modes

### Changed
- Clean architecture with separation of concerns
- Centralized distance calculations and network management
- Streamlined API for contestant use

## [2.4.0] - 2025-08-17

### Added
- Basic logistics environment structure
- Core models for warehouses, vehicles, orders, and SKUs
- Network management and distance calculations

## [2.3.0] - 2025-08-17

### Added
- Initial project setup
- Basic package structure
- Development environment configuration
