# CloudSense

An interactive tool for AWS cost tracking.

## Features

- **Secure AWS cost tracking** using Cost Explorer API with comprehensive authentication
- **Complete cost visibility** - entire account and per-service usage analysis
- **Intelligent caching** - cost data cached for 1 hour (by default, customizable) to minimize API costs
- **Flexible time ranges** (7, 14, 30, 90 days, current month, previous month, custom month, specific day)
- **Interactive visualizations** - daily cost trends with dynamic charts
- **Detailed breakdowns** - service-by-service cost analysis 
- **Performance optimized** - AWS session caching and efficient API usage
- **Enterprise features** - rate limiting, input validation, security headers
- **Health monitoring** - built-in health check endpoint for monitoring
- **Comprehensive logging** - structured logging with configurable levels

## Caching cost data to reduce cost 

AWS Cost Explorer API calls are $.01 for each call.

- CloudSense caches cost data for **1 hour** to reduce cost
- Cache status displayed in the interface with last update timestamp
- Click **"Update Cost Data"** button to force refresh cached data

## Installation

**Recommended: Use a virtual environment**
```bash
# Create virtual environment
python -m venv cloudsense-env

# Activate virtual environment
source cloudsense-env/bin/activate
```

1. **Install CloudSense:**
   ```bash
   pip install cloudsense
   ```

2. **Configure AWS credentials (Required):**
   ```bash
   aws configure
   # or set environment variables:
   export AWS_ACCESS_KEY_ID=<your-key>
   export AWS_SECRET_ACCESS_KEY=<your-secret>
   export AWS_DEFAULT_REGION=us-east-1
   ```
   
   **Authentication Required**: CloudSense requires valid AWS credentials to access cost data.

3. **Run CloudSense:**
   ```bash
   cloudsense
   ```
   
   **Security Note**: By default, CloudSense binds to `127.0.0.1` (localhost only) for security.

4. **Access the interface:**
   Open http://localhost:8080 in your browser

## Command Line Options

### Basic Usage
```bash
cloudsense                          # Start with default settings
cloudsense --help                   # Show comprehensive help
cloudsense --version                # Show version information
```

### Server Configuration
```bash
cloudsense --port 5000              # Custom port (default: 8080)
cloudsense --host 127.0.0.1         # Bind to specific host (default: localhost)
cloudsense --debug                  # Enable debug mode (development only)
cloudsense --config production      # Use production configuration
```

### AWS Configuration
```bash
cloudsense --aws-region eu-west-1   # Override AWS region (default: us-east-1)
cloudsense --aws-profile myprofile  # Use specific AWS profile
cloudsense --hide-acct               # Hide AWS account number in interface
```

### Security & Performance
```bash
cloudsense --rate-limit "50 per hour"     # Custom rate limiting
cloudsense --cache-duration 7200          # Cache duration in seconds (default: 3600)
cloudsense --log-level DEBUG              # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

### Environment Configuration
```bash
# Copy environment template and customize
cp .env.example .env

# Available environment variables:
export AWS_REGION=us-east-1
export LOG_LEVEL=INFO
export CACHE_DURATION=3600
export RATELIMIT_DEFAULT="100 per hour"
export HIDE_ACCOUNT=false
```

**Security Options:**
- `--host 127.0.0.1` (default): Localhost only - most secure
- `--host 0.0.0.0`: All interfaces - **Use with caution** - requires firewall protection
- Rate limiting protects against abuse and DoS attacks
- Input validation prevents injection attacks
- Security headers protect against common web vulnerabilities

## Health Check & Monitoring

CloudSense includes a built-in health check endpoint for monitoring and load balancer integration:

```bash
# Health check endpoint
curl http://localhost:8080/health

# Example response:
{
  "status": "healthy",
  "aws": "connected", 
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "0.1.0"
}
```

## Rate Limiting & Security

CloudSense implements comprehensive security measures:

- **Rate Limiting**: API endpoints are protected with configurable rate limits
  - `/api/billing`: 30 requests per minute
  - `/api/service/*`: 60 requests per minute  
  - `/api/regions`: 10 requests per minute
- **Input Validation**: All parameters are validated and sanitized
- **Security Headers**: Protection against XSS, clickjacking, and content sniffing
- **Error Handling**: Structured error responses without sensitive information leakage
- **Logging**: Comprehensive request and error logging for security monitoring

## AWS Permissions Required

Your AWS credentials need the following permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ce:GetUsageReport",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

**Note**: `sts:GetCallerIdentity` is required for authentication validation and account ID display.

## Architecture & Code Quality

### Enhanced Architecture (v1.0.0)

CloudSense has been completely refactored with enterprise-grade architecture:

```
cloudsense/
├── app.py              # Main Flask application (enhanced with security)
├── cli.py              # Enhanced CLI with rich options
├── config/             # Configuration management
│   ├── __init__.py
│   └── config.py       # Environment-based configuration
├── utils/              # Utility modules
│   ├── __init__.py
│   ├── validators.py   # Input validation and sanitization
│   └── helpers.py      # Helper functions and utilities
├── static/             # Static assets (new)
│   ├── css/
│   │   └── main.css    # Extracted stylesheets
│   └── js/
│       └── main.js     # Extracted JavaScript
└── templates/
    ├── index.html      # Main template (28 lines, 96% reduction!)
    └── components/     # Reusable components
        ├── header.html
        ├── metrics.html
        ├── chart.html
        ├── services.html
        └── breakdowns.html
```

### Key Improvements

- **Modular Design**: Clean separation of concerns with utility modules
- **Security First**: Input validation, rate limiting, security headers
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Error Handling**: Structured error handling with proper HTTP status codes
- **Monitoring**: Built-in health checks and comprehensive logging
- **Performance**: Optimized imports, threading support, efficient caching
- **Maintainability**: 96% reduction in template size, component-based UI

### Code Quality Features

- **Zero Linting Errors**: Clean, properly formatted code
- **Comprehensive Documentation**: Detailed docstrings and comments
- **Environment Configuration**: Flexible configuration via environment variables
- **Production Ready**: Separate development and production configurations
- **Testing Ready**: Modular structure enables easy unit testing

## Development & Contributing

### Local Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd cloudsense

# Create virtual environment
python -m venv cloudsense-env
source cloudsense-env/bin/activate  # On Windows: cloudsense-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run in development mode
cloudsense --debug --log-level DEBUG
```

### Configuration Options

Create a `.env` file for local development:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Application Configuration  
FLASK_DEBUG=true
LOG_LEVEL=DEBUG
CACHE_DURATION=3600

# Security Configuration
RATELIMIT_DEFAULT=1000 per hour  # More lenient for development
HIDE_ACCOUNT=false

# Server Configuration
HOST=127.0.0.1
PORT=8080
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
cloudsense --port 8081  # Use different port
```

**AWS credentials not found:**
```bash
aws configure  # Configure AWS CLI
# or set environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

**Permission denied errors:**
```bash
cloudsense --port 8080  # Use port > 1024
# or run with appropriate permissions
```

**Rate limit exceeded:**
```bash
cloudsense --rate-limit "200 per hour"  # Increase rate limit
```

### Logging

View detailed logs:
```bash
cloudsense --log-level DEBUG  # Enable debug logging
tail -f cloudsense.log        # Monitor log file
```

## License

MIT License - see LICENSE file for details.

## Support

For issues, feature requests, or contributions, please visit the GitHub repository.
