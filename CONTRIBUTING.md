# Contributing to Gemini Screen Navigator

Thank you for your interest in contributing to Gemini Screen Navigator! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Node.js 22+
- Python 3.11+
- Git
- Docker (for testing deployment)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/gemini-screen-navigator.git
cd gemini-screen-navigator

# Install Node dependencies
pnpm install

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start development server
pnpm dev
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, readable code
- Follow the existing code style
- Add comments for complex logic
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pnpm test

# Check TypeScript
pnpm check

# Format code
pnpm format
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: description of your changes"
```

Use conventional commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `style:` for code style changes
- `refactor:` for code refactoring
- `test:` for test additions
- `chore:` for maintenance

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what was changed and why
- Reference to any related issues
- Screenshots if UI changes

## Code Style

### TypeScript/JavaScript

- Use TypeScript for type safety
- Follow the existing code structure
- Use meaningful variable names
- Add JSDoc comments for functions

### Python

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to functions and classes
- Use descriptive variable names

### CSS/Tailwind

- Use Tailwind utility classes
- Follow the design system in `index.css`
- Avoid inline styles
- Use CSS variables for colors

## Testing

### Adding Tests

- Write tests for new features
- Update tests when modifying existing code
- Aim for >80% code coverage

```bash
# Run tests
pnpm test

# Run with coverage
pnpm test:coverage
```

### Test Structure

```typescript
describe('Feature Name', () => {
  it('should do something', () => {
    // Arrange
    const input = ...;
    
    // Act
    const result = ...;
    
    // Assert
    expect(result).toBe(...);
  });
});
```

## Documentation

### Update Documentation When

- Adding new features
- Changing API endpoints
- Modifying configuration
- Updating dependencies

### Documentation Files

- **README.md**: Setup and basic usage
- **ARCHITECTURE.md**: System design
- **DEPLOYMENT.md**: Deployment instructions
- **API.md**: API reference (if applicable)

## Reporting Issues

### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Node version, Python version)
- Screenshots if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use cases and benefits
- Possible implementation approach
- Any related issues or discussions

## Pull Request Process

1. **Ensure tests pass**: `pnpm test`
2. **Check code style**: `pnpm format && pnpm check`
3. **Update documentation**: Update README or ARCHITECTURE if needed
4. **Request review**: Ask for feedback from maintainers
5. **Address feedback**: Make requested changes
6. **Merge**: Maintainers will merge when approved

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

## Questions?

- Check existing issues and discussions
- Ask in GitHub Discussions
- Email the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Gemini Screen Navigator!
