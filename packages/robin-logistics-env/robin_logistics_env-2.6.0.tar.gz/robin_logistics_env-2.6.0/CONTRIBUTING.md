# Contributing to Robin Logistics Environment

Thank you for your interest in contributing to the Robin Logistics Environment! This document provides guidelines for developers and contributors.

## Development Setup

### Prerequisites

- Python 3.8+
- pip or conda for package management

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Environment

# Install in development mode
pip install -e .
```

## Project Structure

```
robin_logistics/
├── environment.py          # Main environment interface
├── solvers.py             # Base skeleton solver for testing
├── dashboard.py           # Streamlit dashboard
├── headless.py            # Headless execution
└── core/                  # Core components
    ├── models/            # Data models
    ├── state/             # State management
    ├── network/           # Network management
    ├── validation/        # Validation engine
    ├── metrics/           # Metrics calculation
    └── utils/             # Utilities
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m tests.test_environment_mock
python -m tests.test_environment_with_mock_solvers

# Test dashboard functionality
python main.py
```

### Testing Your Solver

1. **Create a test file** (e.g., `my_solver_test.py`):
```python
#!/usr/bin/env python3
from robin_logistics import LogisticsEnvironment
from my_solver import my_solver

def main():
    env = LogisticsEnvironment()
    env.set_solver(my_solver)
    env.launch_dashboard()

if __name__ == "__main__":
    main()
```

2. **Run your solver**:
```bash
python my_solver_test.py
```

### Mock Data

The project includes comprehensive mock data for testing:
- `tests/mock_data.py` - Mock environment and solution creation
- `tests/mock_solvers.py` - Example solver implementations

## Development Workflow

### 1. Environment Testing

Test the environment without a solver:
```bash
python -m tests.test_environment_mock
```

### 2. Solver Integration Testing

Test environment with mock solvers:
```bash
python -m tests.test_environment_with_mock_solvers
```

### 3. Dashboard Testing

Test the dashboard with base solver:
```bash
python main.py
```

### 4. Headless Testing

Test headless execution:
```bash
python main.py --headless
```

## Code Quality Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write clear, descriptive docstrings
- Keep functions focused and single-purpose

### Architecture Principles

- **Separation of Concerns**: Keep environment logic separate from solving logic
- **Single Responsibility**: Each class/module has one clear purpose
- **Dependency Injection**: Pass dependencies rather than creating them
- **Error Handling**: Use meaningful error messages and proper exception handling

### Testing Requirements

- All new features must include tests
- Maintain test coverage above 90%
- Use descriptive test names
- Test both success and failure scenarios

## Areas for Contribution

### High Priority

- **Performance Optimization**: Improve distance calculations and state management
- **Validation Rules**: Add new business logic validation rules
- **Metrics**: Enhance cost calculation and performance metrics
- **Documentation**: Improve API documentation and examples

### Medium Priority

- **Dashboard Features**: Add new visualization capabilities
- **Headless Mode**: Enhance result saving and analysis
- **Error Handling**: Improve error messages and debugging
- **Configuration**: Add more environment configuration options

### Low Priority

- **Data Formats**: Support additional input/output formats
- **CLI Tools**: Add command-line utilities
- **Examples**: Create more solver examples and tutorials

## Pull Request Process

### Before Submitting

1. **Test Locally**: Ensure all tests pass
2. **Check Style**: Verify code follows style guidelines
3. **Update Documentation**: Update relevant documentation
4. **Test Integration**: Test with main.py and dashboard

### PR Guidelines

- **Title**: Clear, descriptive title
- **Description**: Explain what and why (not how)
- **Tests**: Include tests for new functionality
- **Documentation**: Update relevant docs
- **Breaking Changes**: Clearly mark and explain

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: At least one maintainer review required
3. **Testing**: PR must pass all tests
4. **Documentation**: Ensure documentation is updated

## Common Issues and Solutions

### Dashboard Won't Launch

```bash
# Check Streamlit installation
pip install streamlit

# Verify environment setup
python -c "from robin_logistics import LogisticsEnvironment; print('OK')"
```

### Tests Failing

```bash
# Check mock data setup
python -m tests.test_environment_mock

# Verify package installation
pip install -e .
```

### Import Errors

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Verify package structure
ls robin_logistics/
```

## Getting Help

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and ideas
- **Documentation**: Check README.md and API_REFERENCE.md first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
