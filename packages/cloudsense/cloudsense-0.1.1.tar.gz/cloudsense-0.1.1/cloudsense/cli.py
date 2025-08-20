#!/usr/bin/env python3
"""CloudSense CLI entry point with enhanced configuration options"""

import argparse
import sys
import os
import logging
from .app import create_app
from .config.config import config
from . import __version__

def setup_logging(log_level: str):
    """Setup logging configuration"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('cloudsense.log') if log_level.upper() in ['DEBUG', 'INFO'] else logging.NullHandler()
        ]
    )
    
    # Reduce AWS SDK logging noise unless in DEBUG mode
    if log_level.upper() != 'DEBUG':
        logging.getLogger('botocore').setLevel(logging.WARNING)
        logging.getLogger('boto3').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

def main():
    """Enhanced CLI entry point with better configuration options"""
    parser = argparse.ArgumentParser(
        description='CloudSense - AWS Cost Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic Usage:
    cloudsense                          # Start with default settings
    cloudsense --help                   # Show comprehensive help
    cloudsense --version                # Show version information

  Server Configuration:
    cloudsense --port 5000              # Custom port (default: 8080)
    cloudsense --host 0.0.0.0           # Bind to all interfaces (use with caution)
    cloudsense --debug                  # Debug mode with verbose logging
    cloudsense --config production      # Use production configuration

  AWS Configuration:
    cloudsense --aws-region eu-west-1    # Override AWS region
    cloudsense --aws-profile myprofile   # Use specific AWS profile
    cloudsense --hide-acct               # Hide AWS account number

  Security & Performance:
    cloudsense --rate-limit "50 per hour"     # Custom rate limiting
    cloudsense --cache-duration 7200          # Cache duration in seconds
    cloudsense --log-level DEBUG              # Set logging level

  Advanced Examples:
    cloudsense --config production --log-level WARNING --port 80
    cloudsense --aws-region us-west-2 --cache-duration 1800 --hide-acct
    cloudsense --debug --rate-limit "200 per hour" --log-level DEBUG

Security Notes:
  --host 127.0.0.1 (default): Localhost only - most secure
  --host 0.0.0.0: All interfaces - requires firewall protection
  Rate limiting protects against abuse and DoS attacks
  Input validation prevents injection attacks

Environment Variables:
  Copy .env.example to .env and customize configuration
  AWS_REGION, LOG_LEVEL, CACHE_DURATION, RATELIMIT_DEFAULT, etc.
        """
    )
    
    # Server configuration
    parser.add_argument('--host', default='127.0.0.1', 
                       help='Host to bind to (default: 127.0.0.1 for security)')
    parser.add_argument('--port', type=int, default=8080, 
                       help='Port to bind to (default: 8080)')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode (development only)')
    
    # Application configuration
    parser.add_argument('--config', default='default',
                       choices=['development', 'production', 'default'],
                       help='Configuration environment (default: default)')
    parser.add_argument('--hide-acct', action='store_true', 
                       help='Hide AWS account number in interface')
    
    # AWS configuration
    parser.add_argument('--aws-region', default=None,
                       help='Override AWS region (default: us-east-1)')
    parser.add_argument('--aws-profile', default=None,
                       help='AWS profile to use (default: default)')
    
    # Logging configuration
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Set logging level (default: INFO)')
    
    # Cache configuration
    parser.add_argument('--cache-duration', type=int, default=3600,
                       help='Cache duration in seconds (default: 3600)')
    
    # Rate limiting configuration
    parser.add_argument('--rate-limit', default=None,
                       help='Rate limit (e.g., "100 per hour", default: varies by config)')
    
    # Version
    parser.add_argument('--version', action='version', version=f'CloudSense {__version__}')
    
    args = parser.parse_args()

    # Setup logging
    try:
        setup_logging(args.log_level)
        logger = logging.getLogger(__name__)
        logger.info(f"Starting CloudSense with config: {args.config}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Set environment variables if provided
    if args.aws_region:
        os.environ['AWS_REGION'] = args.aws_region
    if args.aws_profile:
        os.environ['AWS_PROFILE'] = args.aws_profile
    if args.rate_limit:
        os.environ['RATELIMIT_DEFAULT'] = args.rate_limit
    
    os.environ['CACHE_DURATION'] = str(args.cache_duration)
    os.environ['LOG_LEVEL'] = args.log_level

    # Validate host for security
    if args.host == '0.0.0.0':
        logger.warning("WARNING: Binding to all interfaces (0.0.0.0) - ensure firewall is configured!")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted for security.")
            sys.exit(1)

    try:
        app = create_app(config_name=args.config, hide_account=args.hide_acct)
        logger.info(f"CloudSense application created successfully (config: {args.config})")
    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        print(f"Error: Missing dependencies - {e}")
        print("Try: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error creating app: {e}")
        print(f"Error creating app: {e}")
        sys.exit(1)
    
    try:
        logger.info(f"Starting CloudSense server on {args.host}:{args.port} (cache duration: {args.cache_duration}s)")
        print(f"Starting CloudSense on http://{args.host}:{args.port}")
        print(f"Configuration: {args.config}")
        print(f"AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
        print(f"Cache Duration: {args.cache_duration}s")
        print(f"Log Level: {args.log_level}")
        if args.hide_acct:
            print("Account number will be hidden")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 50)
        
        app.run(debug=args.debug, host=args.host, port=args.port, threaded=True)
        
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"Port {args.port} is already in use")
            print(f"Error: Port {args.port} is already in use. Try a different port with --port")
        elif "Permission denied" in str(e):
            logger.error(f"Permission denied for {args.host}:{args.port}")
            print(f"Error: Permission denied. Try a different port or run as administrator")
        else:
            logger.error(f"OS error starting server: {e}")
            print(f"Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        print("\n👋 Shutting down CloudSense...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error running server: {e}")
        print(f"Error running server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()