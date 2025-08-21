# FastAPI CLI Tool

A powerful CLI tool for generating production-ready FastAPI applications with multiple template options.

## Overview

This CLI tool provides three different templates to quickly bootstrap FastAPI applications:

- **Minimal**: A basic FastAPI application with minimal dependencies
- **API Only**: A modular API structure with authentication, database, and testing
- **Full-Stack**: A complete production-ready application with all features

## Installation

### From PyPI (when published)
```bash
pip install fastapi-template-cli
```

### From Source
```bash
git clone https://github.com/Sohail342/fastapi-template
cd cli-tool
pip install -e .
```

## Usage

### Basic Usage
```bash
# Create a new FastAPI project
fastapi-template create my-project

# Create with specific template
fastapi-template create my-project --template fullstack

# List available templates
fastapi-template templates
```

### Available Templates

#### 1. Minimal Template
- Basic FastAPI application
- Single file structure
- Perfect for learning and simple projects

```bash
fastapi-template create my-minimal-app --template minimal
```

#### 2. API Only Template
- Modular project structure
- Authentication with JWT
- Database integration with SQLAlchemy
- Testing setup
- API documentation

```bash
fastapi-template create my-api-app --template api_only
```

#### 3. Full-Stack Template
- Everything in API Only template plus:
- Production Docker setup
- Database migrations with Alembic
- Redis integration
- Email support
- Monitoring and logging
- Pre-commit hooks
- CI/CD ready

```bash
fastapi-template create my-fullstack-app --template fullstack
```

### CLI Commands

```bash
# Create new project
fastapi-template create <project-name> [--template TEMPLATE]

# List available templates
fastapi-template templates

# Show version
fastapi-template --version

# Show help
fastapi-template --help
```

## Template Details

### Minimal Template Features
- Single `main.py` file
- Basic FastAPI setup
- Health check endpoint
- Uvicorn development server

### API Only Template Features
- **Project Structure**:
  ```
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── api/
  │   ├── core/
  │   ├── crud/
  │   ├── db/
  │   ├── models/
  │   └── schemas/
  ├── tests/
  ├── requirements.txt
  ├── .env.example
  └── README.md
  ```

- **Features**:
  - JWT Authentication
  - SQLAlchemy ORM
  - Pydantic models
  - CRUD operations
  - Testing with pytest
  - Environment configuration

### Full-Stack Template Features
- **Complete Production Setup**:
  - PostgreSQL database
  - Redis caching
  - Docker & Docker Compose
  - Alembic migrations
  - Email support
  - Security headers
  - CORS configuration
  - Monitoring endpoints
  - Comprehensive testing
  - Development tools

- **Development Tools**:
  - Black formatting
  - Ruff linting
  - MyPy type checking
  - Pre-commit hooks
  - Makefile commands

## Development

### Setup Development Environment
```bash
git clone <repository-url>
cd cli-tool
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Running Tests
```bash
pytest
```

### Building Package
```bash
python -m build
```

## Project Structure

```
cli-tool/
├── fastapi_template/
│   ├── __init__.py
│   ├── cli.py                    # CLI interface
│   └── templates/                # Template directories
│       ├── minimal/
│       ├── api_only/
│       └── fullstack/
├── tests/                        # CLI tool tests
├── pyproject.toml               # Package configuration
└── README.md                    # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new features
5. Run tests (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Template Customization

Each template can be customized by modifying the template files in the `templates/` directory. The templates are designed to be:

- **Extensible**: Easy to add new features
- **Configurable**: Environment-based configuration
- **Maintainable**: Clean code structure
- **Testable**: Comprehensive test coverage

## Requirements

- Python 3.11+
- For Full-Stack template:
  - PostgreSQL
  - Redis (optional)
  - Docker (optional)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Join our community discussions

## Roadmap

- [ ] Additional template options (GraphQL, microservices)
- [ ] Plugin system for custom templates
- [ ] Interactive CLI wizard
- [ ] Database initialization scripts
- [ ] Deployment configurations (AWS, GCP, Azure)
- [ ] Frontend integration templates (React, Vue, Angular)