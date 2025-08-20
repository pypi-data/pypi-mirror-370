# CABEK Python SDK

Official Python SDK for C.A.B.E.K. biometric authentication.

[![PyPI version](https://badge.fury.io/py/cabek-sdk.svg)](https://pypi.org/project/cabek-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/cabek-sdk.svg)](https://pypi.org/project/cabek-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install cabek-sdk
```

For ECG processing capabilities:
```bash
pip install cabek-sdk[ecg]
```

## Quick Start

```python
import asyncio
from cabek_sdk import CABEK

async def authenticate():
    # Initialize the SDK
    cabek = CABEK(
        api_key="your-api-key",
        environment="production"
    )
    
    # Authenticate a user
    try:
        result = await cabek.authenticate()
        print(f"User authenticated! Session ID: {result.session_id}")
    except Exception as e:
        print(f"Authentication failed: {e}")
    finally:
        await cabek.close()

# Run the authentication
asyncio.run(authenticate())
```

## Features

- 🔐 **Zero-Storage Authentication**: No biometric data stored anywhere
- ⚡ **Async/Await Support**: Built for modern Python applications
- 🛡️ **Type Hints**: Full type annotation support
- 📱 **Multi-Device Support**: Works with various biometric sensors
- 🔄 **Real-time Events**: WebSocket-based event streaming
- 📊 **Signal Quality Monitoring**: Real-time ECG signal analysis

## Documentation

Full documentation available at [https://docs.cabek.io](https://docs.cabek.io)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- Email: support@cabek.io
- GitHub Issues: [https://github.com/alagbefranc/cabek-python-sdk/issues](https://github.com/alagbefranc/cabek-python-sdk/issues)
