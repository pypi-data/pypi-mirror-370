# Koel Authentication Example

This directory contains an example implementation of a custom authentication class for the [Koel](https://koel.dev/) music streaming application.

## Usage

1. Install the required dependencies:
```bash
pip install requests
```

2. Create a Python script to use the Koel authentication:
```python
from specphp_scanner.auth.factory import AuthFactory
from examples.koel.auth import KoelAuth

# Register the Koel auth class
AuthFactory.register("koel", KoelAuth)

# Create an auth instance
auth = AuthFactory.create("koel", email="admin@koel.dev", password="KoelIsCool")

# Use the auth instance
base_url = "http://localhost:8080"
auth.authenticate(base_url)
headers = auth.get_headers(base_url)
cookies = auth.get_cookies(base_url)
```

3. Or use it directly with the scanner:
```bash
python -m specphp_scanner spec.json \
    --auth-type koel \
    --auth-module examples.koel.auth \
    --auth-params '{"email": "admin@koel.dev", "password": "KoelIsCool"}' \
    --host localhost \
    --port 8080
```

## Implementation Details

This example demonstrates:
- How to implement a custom authentication class
- Token-based authentication
- Automatic token refresh
- Integration with the scanner's authentication system

## Notes

- This is just an example implementation
- In a real-world scenario, you should handle token expiration and refresh
- Consider adding error handling for network issues
- Store sensitive information (like passwords) securely
