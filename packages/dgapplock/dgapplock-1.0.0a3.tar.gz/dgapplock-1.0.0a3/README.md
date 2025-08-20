# AppLocker - Distributed Application Lock Manager

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Redis Required](https://img.shields.io/badge/requires-Redis-red)

## Overview

AppLocker is a Python library that provides distributed application locking using Redis. It ensures that only one instance of your application can run a critical section of code at a time, even across multiple servers.

Key features:
- **Distributed locking** across multiple application instances
- **Automatic lock renewal** (heartbeat) to prevent premature expiration
- **Lock ownership verification** to prevent accidental release
- **Context manager support** for easy use in `with` statements
- **Stale lock detection** and recovery

## Installation

```bash
pip install your-package-name
```

## Prerequisites

- Python 3.8+
- Redis server
- `dglog` and `dgredis` packages (will be installed automatically if using pip)

## Quick Start

```python
from app_locker import AppLocker

# Configure Redis connection
redis_config = {
    "host": "localhost",
    "port": 6379,
    # Add other Redis parameters as needed
}

# Create a locker instance
locker = AppLocker(redis_config, "my_application")

# Usage example
with locker:
    print("This code is protected by a distributed lock")
    # Only one instance of your application can execute this at a time
```

## Configuration

### Basic Configuration

When creating an `AppLocker` instance, you need to provide:

1. Redis configuration dictionary (host, port, etc.)
2. Your application name (used as part of the lock key)
3. Optional parameters:
   - `ttl`: Lock time-to-live in seconds (default: 60)
   - `logger_`: Custom logger instance

### Advanced Configuration

You can customize the lock behavior by:

1. Setting a specific lock key instead of the default `QUEUE:{application}`
2. Adjusting the stale timeout for force-release operations
3. Providing a custom logger for tracking lock operations

## Usage Examples

### Basic Locking

```python
if locker.acquire():
    try:
        # Critical section
        print("Doing important work")
    finally:
        locker.release()
else:
    print("Could not acquire lock - another instance is running")
```

### Context Manager

```python
with locker.acquired():
    # Critical section
    print("This code is protected")
```

### Checking Lock Status

```python
if locker.is_my_lock():
    print("We currently hold the lock")
    
lock_info = locker.get_lock_info()
if lock_info:
    print(f"Lock held by {lock_info['owner']} since {lock_info['acquired_at']}")
```

### Force Release Stale Lock

```python
if locker.force_release_if_stale(stale_timeout=120):
    print("Released a stale lock")
```

## Best Practices

1. **Keep TTL reasonable** - Set it long enough for your operations but not too long (default 60s is good for most cases)
2. **Always use context managers** when possible for safer lock handling
3. **Check lock ownership** before performing sensitive operations
4. **Monitor lock duration** using `get_lock_duration()` to optimize your TTL
5. **Handle lock acquisition failures** gracefully in your application

## Troubleshooting

### Common Issues

1. **Can't acquire lock**
   - Check if another instance is running
   - Verify Redis connection
   - Check if a stale lock needs to be force-released

2. **Unexpected lock release**
   - Ensure your operations complete within the TTL
   - Check for network issues with Redis

3. **Permission errors**
   - Verify Redis credentials in your configuration

### Logging

AppLocker provides detailed logging about lock operations. If you're not seeing logs:
- Make sure logging is configured properly
- Pass a custom logger to the constructor if needed

## API Reference

See the full [API documentation](API.md) for detailed information about all available methods and parameters.

## License

[MIT License](LICENSE)