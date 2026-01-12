# Contributing to SkyMind

Thank you for considering contributing to SkyMind! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs
- Use GitHub Issues
- Include detailed reproduction steps
- Include your environment (OS, Python version, etc.)

### Suggesting Features
- Open a GitHub Issue with the "enhancement" label
- Describe the feature and its use case
- Explain why it would be valuable

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests** if applicable
5. **Ensure tests pass**:
   ```bash
   pytest
   ```
6. **Commit your changes**:
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/Iqbalsofi/skymind.git
cd skymind

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run server
uvicorn app.main:app --reload
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep functions focused and small

## Areas We Need Help

1. **Provider Integrations**: Adding more flight APIs
2. **Frontend**: React/Vue UI
3. **Testing**: Increasing test coverage
4. **Documentation**: Improving guides and examples
5. **AI Features**: NLP-based search improvements

## Questions?

Open an issue or reach out to the maintainers.

Thank you for contributing! 🚀
