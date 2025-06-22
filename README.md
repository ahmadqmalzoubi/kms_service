# KMS Service (Python Frontend)

A high-performance, secure Key Management Service frontend built with FastAPI, providing a RESTful API for cryptographic operations with comprehensive security, monitoring, and rate limiting features.

## Features

### 🔐 Security
- API key authentication
- Rate limiting per client
- CORS protection
- Request validation and sanitization
- Secure error handling (no sensitive data leakage)

### 📊 Monitoring & Observability
- Structured logging (JSON/Text formats)
- Request tracking with unique IDs
- Performance monitoring
- Health checks with backend status
- Prometheus metrics support

### 🚀 Performance
- Async/await architecture
- Connection pooling
- Retry logic with exponential backoff
- Request caching support
- Optimized response handling

### 🛠️ Operations
- Docker containerization
- Health checks and readiness probes
- Graceful shutdown handling
- Configuration management
- Environment-based settings

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   KMS Service   │    │   KMS Backend   │
│                 │    │   (Python)      │    │   (Rust)        │
│ - Web Apps      │───▶│ - FastAPI       │───▶│ - Axum          │
│ - Mobile Apps   │    │ - Rate Limiting │    │ - Crypto Ops    │
│ - Microservices │    │ - Auth          │    │ - Key Storage   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │ - Rate Limiting │
                       │ - Caching       │
                       └─────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Redis (optional, for enhanced rate limiting)

### Local Development

1. **Clone and setup:**
```bash
git clone <repository>
cd kms_service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start the backend KMS service first:**
```bash
# From the kms_crypto directory
cargo run
```

4. **Run the Python service:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

1. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

2. **Or run individual services:**
```bash
# Build the image
docker build -t kms-service .

# Run with environment variables
docker run -p 8000:8000 \
  -e API_KEY=your-secret-key \
  -e KMS_BACKEND_URL=http://host.docker.internal:9000 \
  kms-service
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | Required | API key for authentication |
| `KMS_BACKEND_URL` | `http://localhost:9000` | Backend KMS service URL |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `json` | Log format (json/text) |
| `RATE_LIMIT_PER_MINUTE` | `100` | Rate limit per client |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

### Configuration File

Create a `.env` file:
```env
API_KEY=your-super-secret-api-key
KMS_BACKEND_URL=http://localhost:9000
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=100
CORS_ORIGINS=*
```

## API Documentation

### Authentication

All API endpoints require authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/kms/generate_key
```

### Endpoints

#### Health Check
```http
GET /health
```

#### Symmetric Operations

**Generate Key:**
```http
POST /api/kms/generate_key
```

**Encrypt:**
```http
POST /api/kms/encrypt
Content-Type: application/json

{
  "key_id": "key-123",
  "plaintext": "Hello, World!"
}
```

**Decrypt:**
```http
POST /api/kms/decrypt
Content-Type: application/json

{
  "key_id": "key-123",
  "ciphertext": "base64-encoded-ciphertext",
  "nonce": "base64-encoded-nonce"
}
```

#### Asymmetric Operations

**Generate Key Pair:**
```http
POST /api/kms/generate_keypair
```

**Asymmetric Encrypt:**
```http
POST /api/kms/encrypt_asymmetric
Content-Type: application/json

{
  "key_id": "keypair-123",
  "plaintext": "Hello, World!"
}
```

**Asymmetric Decrypt:**
```http
POST /api/kms/decrypt_asymmetric
Content-Type: application/json

{
  "key_id": "keypair-123",
  "ciphertext": "base64-encoded-ciphertext"
}
```

### Response Format

All responses follow a consistent format:

```json
{
  "key_id": "key-123",
  "ciphertext": "base64-encoded-data",
  "nonce": "base64-encoded-nonce",
  "algorithm": "AES-256-GCM",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Handling

Errors are returned with consistent formatting:

```json
{
  "error": "Validation Error",
  "detail": "Invalid key_id format",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "uuid-123",
  "status_code": 400
}
```

## Monitoring

### Logs

The service uses structured logging. In JSON format:
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "info",
  "logger": "app.api.v1.endpoints.kms_proxy",
  "message": "Data encrypted successfully",
  "request_id": "uuid-123",
  "key_id": "key-123",
  "algorithm": "AES-256-GCM",
  "data_length": 13
}
```

### Health Checks

Monitor service health:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "uptime": 3600,
  "backend_status": "healthy",
  "backend_latency": 15.5
}
```

### Metrics

Prometheus metrics are available at `/metrics` (when enabled):
```bash
curl http://localhost:8000/metrics
```

## Security Considerations

### API Key Management
- Use strong, randomly generated API keys
- Rotate keys regularly
- Store keys securely (environment variables, secret management)
- Never commit keys to version control

### Rate Limiting
- Configure appropriate rate limits for your use case
- Monitor rate limit violations
- Consider different limits for different endpoints

### Network Security
- Use HTTPS in production
- Configure proper CORS origins
- Use reverse proxies for additional security layers
- Implement IP whitelisting if needed

### Logging Security
- Avoid logging sensitive data
- Use structured logging for better analysis
- Implement log rotation and retention policies
- Consider log encryption for sensitive environments

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Quality
```bash
# Install development dependencies
pip install black isort mypy flake8

# Format code
black .
isort .

# Type checking
mypy .

# Linting
flake8 .
```

### Adding New Endpoints

1. Create request/response models in `app/models/`
2. Add endpoint in `app/api/v1/endpoints/`
3. Update client methods in `app/services/kms_client.py`
4. Add tests
5. Update documentation

## Deployment

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Configure proper `API_KEY`
- [ ] Set appropriate `CORS_ORIGINS`
- [ ] Configure `LOG_LEVEL` and `LOG_FORMAT`
- [ ] Set up monitoring and alerting
- [ ] Configure backup and disaster recovery
- [ ] Set up SSL/TLS certificates
- [ ] Configure reverse proxy (nginx/traefik)
- [ ] Set up log aggregation
- [ ] Configure rate limiting policies

### Kubernetes Deployment

Example deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kms-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kms-service
  template:
    metadata:
      labels:
        app: kms-service
    spec:
      containers:
      - name: kms-service
        image: kms-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: kms-secrets
              key: api-key
        - name: KMS_BACKEND_URL
          value: "http://kms-backend:9000"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Troubleshooting

### Common Issues

1. **Backend Connection Errors**
   - Verify backend KMS service is running
   - Check `KMS_BACKEND_URL` configuration
   - Ensure network connectivity

2. **Rate Limiting Issues**
   - Check rate limit configuration
   - Monitor client IP addresses
   - Adjust limits if needed

3. **Authentication Errors**
   - Verify API key is correct
   - Check `X-API-Key` header format
   - Ensure key is not expired

4. **Performance Issues**
   - Monitor backend latency
   - Check resource usage
   - Review rate limiting settings
   - Consider caching strategies

### Debug Mode

Enable debug mode for detailed error information:
```bash
export DEBUG=true
uvicorn app.main:app --reload
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure code quality checks pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the logs for error details 