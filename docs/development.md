# OmniStack Development Guide

## Development Environment Setup

### Prerequisites

1. Python 3.13+
2. Docker and Docker Compose
3. Git
4. Redis
5. PostgreSQL
6. MongoDB

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/jvrsoftware/omnistack.git
cd omnistack
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. Set up pre-commit hooks:
```bash
pre-commit install
```

5. Start development services:
```bash
docker-compose up -d redis prometheus
```

### Environment Configuration

Create `.env` file:
```bash
cp .env.example .env
```

Required environment variables:
```env
# API Settings
API_HOST=localhost
API_PORT=8000
DEBUG=true

# Authentication
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
POSTGRES_URL=postgresql://user:pass@localhost:5432/omnistack
MONGODB_URL=mongodb://localhost:27017/omnistack

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
MODEL_CACHE_SIZE=1000
MODEL_BATCH_SIZE=32

# Monitoring
PROMETHEUS_PORT=9090
SENTRY_DSN=your-sentry-dsn
```

## Project Structure

```
omnistack/
├── ai_core/               # AI service implementations
│   ├── context_analyzer.py
│   ├── predictive_debugger.py
│   ├── code_optimizer.py
│   └── service_manager.py
├── api/                   # API endpoints and routing
│   ├── main.py
│   ├── routes/
│   └── middleware/
├── auth/                  # Authentication services
│   ├── auth_service.py
│   └── models.py
├── config/               # Configuration management
│   ├── config_manager.py
│   └── feature_flags.py
├── monitoring/           # Monitoring and telemetry
│   ├── metrics_collector.py
│   └── telemetry.py
├── tests/               # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── docker/             # Docker configurations
```

## Development Workflow

### 1. Code Style

We use:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run formatters:
```bash
# Format code
black .

# Sort imports
isort .

# Run linter
flake8 .

# Type checking
mypy .
```

### 2. Testing

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=omnistack tests/

# Run specific test file
pytest tests/unit/test_context_analyzer.py

# Run tests matching pattern
pytest -k "test_analyze"
```

#### Writing Tests

Example test:
```python
from omnistack.ai_core.context_analyzer import ContextAnalyzer

def test_context_analysis():
    analyzer = ContextAnalyzer()
    result = analyzer.analyze_code(
        code="def example(): pass",
        context={"language": "python"}
    )
    
    assert result.quality_score >= 0.0
    assert result.quality_score <= 1.0
    assert "suggestions" in result.__dict__
```

### 3. Git Workflow

1. Create feature branch:
```bash
git checkout -b feature/your-feature
```

2. Make changes and commit:
```bash
git add .
git commit -m "feat: add new feature"
```

3. Push changes:
```bash
git push origin feature/your-feature
```

4. Create Pull Request

### 4. Documentation

We use MkDocs for documentation:

1. Install MkDocs:
```bash
pip install mkdocs mkdocs-material
```

2. Serve documentation locally:
```bash
mkdocs serve
```

3. Build documentation:
```bash
mkdocs build
```

## Debugging

### 1. Logging

```python
import structlog

logger = structlog.get_logger()

# Log with context
logger.info(
    "Processing request",
    user_id=user.id,
    endpoint="/api/v1/analyze"
)

# Log error with traceback
try:
    raise ValueError("Example error")
except Exception as e:
    logger.error(
        "Error occurred",
        error=str(e),
        exc_info=True
    )
```

### 2. Debugging Tools

- VS Code debugger configuration:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "api.main:app",
                "--reload"
            ],
            "jinja": true
        }
    ]
}
```

### 3. Performance Profiling

```python
import cProfile
import pstats

def profile_code():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Code to profile
    result = expensive_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()
```

## Deployment

### 1. Local Development

```bash
uvicorn api.main:app --reload
```

### 2. Docker Development

```bash
docker-compose up --build
```

### 3. Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring

### 1. Metrics

Access Prometheus metrics:
```bash
curl http://localhost:8000/metrics
```

### 2. Logging

View structured logs:
```bash
docker-compose logs -f api
```

### 3. Tracing

View traces in Jaeger UI:
```
http://localhost:16686
```

## Security

### 1. Security Checks

Run security scan:
```bash
bandit -r omnistack/
```

### 2. Dependency Scanning

Check dependencies:
```bash
safety check
```

## Contributing

1. Check existing issues or create a new one
2. Fork the repository
3. Create feature branch
4. Make changes following our guidelines
5. Write tests
6. Update documentation
7. Submit Pull Request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)
