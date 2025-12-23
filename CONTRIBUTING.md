# Contributing to FFC Static Site Capture Tools

Thank you for your interest in contributing to the FFC Static Site Capture Tools! This project helps charities recover and migrate their website content.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion for improvement:

1. Check if the issue already exists in the [issue tracker](https://github.com/FreeForCharity/FFC-Static-Site-Capture-Tools/issues)
2. If not, create a new issue with:
   - A clear, descriptive title
   - Detailed description of the problem or suggestion
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Your environment (Python version, OS, etc.)

### Submitting Changes

1. Fork the repository
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes following our coding standards
4. Test your changes thoroughly
5. Commit your changes with clear, descriptive messages
6. Push to your fork and submit a pull request

### Coding Standards

- Follow PEP 8 style guidelines for Python code
- Include docstrings for all functions and classes
- Add comments for complex logic
- Keep functions focused and modular
- Write descriptive variable and function names

### Testing

Before submitting a pull request:

1. Test your code with various websites
2. Ensure existing functionality isn't broken
3. Test edge cases (empty sites, large sites, missing resources, etc.)

### Adding New Features

When adding new capture sources or features:

1. Create a new module following the pattern of existing ones:
   - Include a class with `__init__`, capture methods, and utilities
   - Implement proper error handling
   - Add command-line interface in `main()`
2. Update the unified CLI tool (`ffc_capture.py`) if applicable
3. Update the README with usage instructions
4. Add examples to `examples.py`

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Update CONTRIBUTING.md if adding new development processes
- Include examples for new features

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/FreeForCharity/FFC-Static-Site-Capture-Tools.git
   cd FFC-Static-Site-Capture-Tools
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Pull Request Process

1. Update documentation as needed
2. Follow the existing code style
3. Ensure your PR description clearly describes the changes
4. Link any related issues
5. Be responsive to feedback and questions

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community and charities we serve
- Accept constructive criticism gracefully

## Questions?

Feel free to open an issue for questions or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
