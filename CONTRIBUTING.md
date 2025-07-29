# Contributing to NewsTrader

Thank you for your interest in contributing to NewsTrader! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your feature or bugfix
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 16+
- PostgreSQL 15+
- Redis 7+
- Docker/Podman (optional)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Database Setup
```bash
# Using Docker/Podman
podman run -d --name newsdb -e POSTGRES_DB=newstrader -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15
podman run -d --name newsredis -p 6379:6379 redis:7-alpine
```

## Making Changes

### Branch Naming Convention
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates

### Commit Message Format
```
type(scope): brief description

Detailed description if necessary

- List any breaking changes
- Reference issues: Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

## Submitting Changes

1. Ensure your code follows the style guidelines
2. Add tests for new functionality
3. Update documentation if needed
4. Make sure all tests pass
5. Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots if UI changes

## Style Guidelines

### Python (Backend)
- Follow PEP 8
- Use Black for code formatting
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable and function names

```bash
# Format code
black .
flake8 .
mypy .
```

### TypeScript/React (Frontend)
- Use TypeScript for all new code
- Follow React hooks patterns
- Use functional components
- Use meaningful component and variable names
- Follow Ant Design conventions

```bash
# Format code
npm run lint
npm run type-check
```

### Database
- Use descriptive table and column names
- Create migrations for schema changes
- Add proper indexes for queries
- Document complex queries

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Tests
```bash
# Start all services
docker-compose up -d

# Run integration tests
pytest tests/integration/
```

## API Documentation

- Document all endpoints using FastAPI/OpenAPI
- Include request/response examples
- Document error responses
- Update API documentation when making changes

## Database Changes

1. Create migration files using Alembic
2. Test migrations up and down
3. Document schema changes in CHANGELOG.md

```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Adding New Features

1. Check existing issues for similar requests
2. Create an issue to discuss the feature
3. Wait for approval before starting development
4. Follow the development workflow
5. Include comprehensive tests
6. Update documentation

## Reporting Bugs

1. Check if the bug already exists in issues
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Screenshots if applicable

## Performance Considerations

- Use async/await for I/O operations
- Implement proper caching strategies
- Optimize database queries
- Consider rate limiting for external APIs
- Monitor memory usage

## Security Guidelines

- Never commit API keys or sensitive data
- Use environment variables for configuration
- Validate all user inputs
- Follow security best practices
- Report security issues privately

## Documentation

- Update README.md for setup changes
- Update API documentation for endpoint changes
- Add code comments for complex logic
- Update PROJECT_OVERVIEW.md for architectural changes

## Questions?

If you have questions about contributing, please:
1. Check existing documentation
2. Search closed issues
3. Create a new issue with the "question" label
4. Join our community discussions

Thank you for contributing to NewsTrader!