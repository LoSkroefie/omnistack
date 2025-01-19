# OmniStack API Reference

## Overview

The OmniStack API provides RESTful endpoints for accessing AI-powered software development tools. All endpoints are available via HTTP/HTTPS and follow REST conventions.

## Base URL

```
http://localhost:8000
```

For production, use your deployed domain:
```
https://api.yourdomain.com
```

## Authentication

### JWT Authentication

All API requests require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

To obtain a token, use the authentication endpoint:

```http
POST /auth/token
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

## Rate Limiting

Rate limits are enforced based on subscription tiers:

| Tier | Requests/Minute | Burst Size |
|------|----------------|------------|
| Free | 60 | 10 |
| Pro | 300 | 50 |
| Enterprise | 1000 | 100 |

Rate limit headers in responses:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 60
```

## Endpoints

### AI Services

#### Code Analysis

```http
POST /api/v1/analyze
Content-Type: application/json
Authorization: Bearer <token>

{
    "code": "def example():\n    print('hello')",
    "context": {
        "language": "python",
        "project_type": "web"
    },
    "use_cache": true
}
```

Response:
```json
{
    "status": "success",
    "data": {
        "quality_score": 0.85,
        "suggestions": [
            {
                "type": "style",
                "message": "Add function docstring",
                "severity": "low"
            }
        ],
        "context_analysis": {
            "complexity": "low",
            "maintainability": "high"
        }
    },
    "timestamp": "2025-01-19T01:56:02+02:00"
}
```

#### Code Optimization

```http
POST /api/v1/optimize
Content-Type: application/json
Authorization: Bearer <token>

{
    "code": "for i in range(len(items)):\n    print(items[i])",
    "context": {
        "performance_priority": "high"
    }
}
```

Response:
```json
{
    "status": "success",
    "data": {
        "suggestions": [
            {
                "type": "performance",
                "message": "Use enumerate() instead of range(len())",
                "severity": "medium",
                "improved_code": "for i, item in enumerate(items):\n    print(item)"
            }
        ]
    },
    "timestamp": "2025-01-19T01:56:02+02:00"
}
```

### Monitoring

#### Health Check

```http
GET /health
```

Response:
```json
{
    "status": "healthy",
    "timestamp": "2025-01-19T01:56:02+02:00",
    "services": {
        "ai_services": {
            "status": "healthy",
            "models_loaded": true
        },
        "config": "healthy",
        "telemetry": "healthy"
    },
    "metrics": {
        "cpu_usage": 45.2,
        "memory_usage": 1024576,
        "request_count": {
            "/api/v1/analyze": 150,
            "/api/v1/optimize": 75
        }
    }
}
```

#### Metrics

```http
GET /metrics
```

Response:
```text
# HELP omnistack_requests_total Total number of requests
# TYPE omnistack_requests_total counter
omnistack_requests_total{endpoint="/api/v1/analyze",status="success"} 150
omnistack_requests_total{endpoint="/api/v1/optimize",status="success"} 75

# HELP omnistack_request_latency_seconds Request latency in seconds
# TYPE omnistack_request_latency_seconds histogram
omnistack_request_latency_seconds_bucket{endpoint="/api/v1/analyze",le="0.1"} 120
omnistack_request_latency_seconds_bucket{endpoint="/api/v1/analyze",le="0.5"} 145
```

## Error Handling

### Error Responses

All errors follow this format:
```json
{
    "detail": "Error message",
    "code": "ERROR_CODE",
    "timestamp": "2025-01-19T01:56:02+02:00"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### Common Error Codes

| Code | Description |
|------|-------------|
| INVALID_TOKEN | Authentication token is invalid |
| RATE_LIMIT_EXCEEDED | Too many requests |
| INVALID_INPUT | Invalid request parameters |
| SERVICE_ERROR | Internal service error |

## Versioning

The API uses URL versioning:
- Current version: `v1`
- Format: `/api/v{version_number}/`

## Best Practices

1. **Rate Limiting**
   - Implement exponential backoff
   - Cache responses when possible
   - Monitor rate limit headers

2. **Error Handling**
   - Always check error responses
   - Implement proper retry logic
   - Log error details for debugging

3. **Performance**
   - Use compression for large requests
   - Implement request caching
   - Monitor response times

4. **Security**
   - Store tokens securely
   - Use HTTPS in production
   - Validate all inputs

## SDK Examples

### Python

```python
from omnistack import OmniStackClient

client = OmniStackClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

# Analyze code
result = client.analyze_code(
    code="def example(): pass",
    context={"language": "python"}
)

# Get optimization suggestions
suggestions = client.optimize_code(
    code="for i in range(len(items)): print(items[i])"
)
```

### JavaScript

```javascript
import { OmniStackClient } from 'omnistack-js';

const client = new OmniStackClient({
    apiKey: 'your_api_key',
    baseUrl: 'http://localhost:8000'
});

// Analyze code
const result = await client.analyzeCode({
    code: 'function example() {}',
    context: { language: 'javascript' }
});

// Get optimization suggestions
const suggestions = await client.optimizeCode({
    code: 'for (let i = 0; i < items.length; i++) console.log(items[i]);'
});
```

## Support

For API support:
- Email: api@jvrsoftware.com
- Documentation: https://docs.jvrsoftware.com
- Status: https://status.jvrsoftware.com
