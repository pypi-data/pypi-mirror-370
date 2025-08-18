# Robin Logistics Environment

A comprehensive logistics optimization environment for hackathons and competitions. This package provides all the infrastructure needed to build and test logistics solvers without implementing the solving logic itself.

## 🚀 Quick Start

### For Developers (Testing)

```bash
# Test with base skeleton solver
python main.py

# Test headless mode
python main.py --headless
```

### For Contestants

```python
from robin_logistics import LogisticsEnvironment
from my_solver import my_solver

# Create environment
env = LogisticsEnvironment()

# Set your solver
env.set_solver(my_solver)

# Launch dashboard
env.launch_dashboard()

# Or run headless
results = env.run_headless("my_run")
```

## 🏗️ Architecture

The environment is designed with a clear separation of concerns:

- **Environment**: Provides data access, validation, and execution
- **Solver**: Implements the optimization logic (provided by contestants)
- **Dashboard**: Visualizes solutions and metrics
- **Headless Mode**: Runs simulations and saves results

## 📦 Package Structure

```
robin_logistics/
├── environment.py          # Main interface for contestants
├── solvers.py             # Base skeleton solver for testing
├── dashboard.py           # Streamlit-based visualization
├── headless.py            # Headless execution and result saving
└── core/                  # Core components
    ├── models/            # Data models (Node, SKU, Order, Vehicle, Warehouse)
    ├── state/             # State management and orchestration
    ├── network/           # Road network and distance calculations
    ├── validation/        # Solution validation
    ├── metrics/           # Cost and performance calculations
    └── utils/             # Helper utilities
```

## 🔧 Key Features

- **Multi-warehouse logistics**: Support for complex scenarios where vehicles visit multiple warehouses
- **Item-level operations**: Handle individual SKUs and quantities
- **Real-time validation**: Comprehensive constraint checking during execution
- **Centralized metrics**: All cost and performance calculations in one place
- **Flexible execution**: Dashboard mode for visualization, headless mode for automation

## 📊 Dashboard Features

- Problem visualization (nodes, warehouses, orders)
- Solution analysis and validation
- Route visualization with pickup/delivery operations
- Performance metrics and cost analysis
- Order fulfillment tracking

## 🚛 Headless Mode

Run simulations without the dashboard and save detailed results:

```python
results = env.run_headless("run_001")
# Results saved to 'results/custom_solver_run_001/'
```

Generated files include:
- Solution summary and validation
- Route details and metrics
- Fulfillment analysis
- Raw data for further processing

## 🧪 Testing

Test the environment with mock data:

```bash
# Run mock tests
python -m tests.test_environment_mock

# Test with mock solvers
python -m tests.test_environment_with_mock_solvers
```

## 📚 Documentation

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Contributing](CONTRIBUTING.md) - Development guidelines
- [Changelog](CHANGELOG.md) - Version history

## 🚀 Installation

```bash
pip install -e .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.