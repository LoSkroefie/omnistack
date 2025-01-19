# OmniStack AI Framework

![OmniStack Logo](docs/images/omnistack-logo.png)

> Advanced AI-powered software development framework by JVR Software

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

OmniStack is a cutting-edge AI framework that enhances software development through:
- Context-aware code analysis
- Predictive debugging
- Performance optimization
- Intelligent deployment tools
- Decentralized marketplace

## Features

### AI Services
- **Context Analysis**: Understand code in its full context using transformer models
- **Predictive Debugging**: Detect potential bugs before runtime
- **Code Optimization**: Get intelligent performance improvement suggestions
- **Service Manager**: Coordinate AI services with caching and monitoring

### Infrastructure
- **Authentication**: JWT-based with role-based access control
- **Caching**: Redis-based caching for model predictions
- **Monitoring**: Prometheus metrics and OpenTelemetry tracing
- **Logging**: Structured JSON logging with context
- **Rate Limiting**: Token bucket algorithm with tier-based limits

### Development Tools
- **API**: RESTful endpoints using FastAPI
- **Testing**: Comprehensive pytest suite
- **Documentation**: OpenAPI/Swagger specs
- **Containerization**: Docker and Kubernetes support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jvrsoftware/omnistack.git
cd omnistack
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Quick Start

1. Start required services:
```bash
docker-compose up -d redis prometheus
```

2. Run the API server:
```bash
python -m uvicorn api.main:app --reload
```

3. Access the services:
- API Documentation: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics
- Health Check: http://localhost:8000/health

## Documentation

Detailed documentation is available in the [/docs](docs/) directory:
- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guide](docs/contributing.md)

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=omnistack tests/
```

## Security

- [Security Policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [License](LICENSE)

## Contributing

Please read our [Contributing Guide](docs/contributing.md) for details on our code of conduct and development process.

## Issues and Feature Requests

Please file issues and feature requests on our [GitHub Issues](https://github.com/jvrsoftware/omnistack/issues) page.

## License

OmniStack is MIT licensed. See [LICENSE](LICENSE) for details.

## Acknowledgments

- [JVR Software](https://github.com/jvrsoftware) - Creator and maintainer
- All our [contributors](https://github.com/jvrsoftware/omnistack/graphs/contributors)

## Contact

- Website: [jvrsoftware.co.za](https://jvrsoftware.co.za)
- Email: jvrsoftware@gmail.com or jan@jvrsoftware.co.za

---
Made with ❤️ by JVR Software
