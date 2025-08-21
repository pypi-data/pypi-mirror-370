# Authentication and Login System Documentation

## Overview
The authentication system in Exponent is built around API keys and GraphQL-based authentication. The system supports multiple environments (development, staging, production) with different API endpoints and authentication mechanisms.

## Key Components

### 1. Configuration and Settings
**Location**: `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/core/config.py`

The settings system manages:
- API keys for different environments (development, staging, production)
- Base URLs for different services
- Configuration storage in `~/.config/exponent/config.json`

### 2. Login Command
**Location**: `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/commands/config_commands.py`

The login command:
- Accepts an API key via `indent login --key <API-KEY>`
- Verifies the API key with the server
- Stores the verified key in the config file

### 3. Authentication Flow

#### Initial Authentication
1. When a command is run, the system checks for an API key
2. If no API key is found:
   - In SSH session: Shows message to run `indent login --key <API-KEY>`
   - Otherwise: Redirects to `<base_url>/cli` for web-based login

#### API Key Verification
**Location**: `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/commands/common.py`

The system verifies API keys through:
1. GraphQL mutation `SET_LOGIN_COMPLETE_MUTATION`
2. Verification of returned API key matching the provided key

#### API Key Refresh
**Location**: `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/commands/config_commands.py`

Users can refresh their API key using:
- Command: `exponent config refresh-key`
- Uses `REFRESH_API_KEY_MUTATION` GraphQL mutation
- Automatically updates the stored API key

### 4. GraphQL Authentication

#### Client Setup
**Location**: `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/core/graphql/client.py`

The GraphQL client:
- Adds API key to HTTP headers for REST calls
- Includes API key in WebSocket init payload
- Handles both HTTP and WebSocket connections

#### Key Mutations and Subscriptions
**Location**: `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/core/graphql/mutations.py`

Important GraphQL operations:
```graphql
SET_LOGIN_COMPLETE_MUTATION
REFRESH_API_KEY_MUTATION
AUTHENTICATED_USER_SUBSCRIPTION
```

### 5. Environment Support
**Location**: `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/core/config.py`

Supports multiple environments:
- Development: `localhost:3000` (API), `localhost:8000` (WebSocket)
- Staging: `staging.exponent.run`
- Production: `exponent.run`

## Security Considerations

1. API Key Storage
   - Keys stored in `~/.config/exponent/config.json`
   - Separate keys for different environments

2. SSL/TLS Security
   - System checks for SSL certificates
   - Can install certificates if missing (macOS specific)
   - Uses `certifi` for certificate verification

## Error Handling

The system handles various authentication errors:
- Invalid API keys
- Network connection issues
- SSL certificate problems
- Environment-specific configuration issues

## Related Files (Absolute Paths)

1. `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/core/config.py`
   - Core configuration and settings management

2. `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/commands/config_commands.py`
   - Login and API key management commands

3. `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/commands/common.py`
   - Authentication helpers and utilities

4. `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/core/graphql/client.py`
   - GraphQL client implementation

5. `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/core/graphql/mutations.py`
   - Authentication-related GraphQL mutations

6. `/Users/dkzlv/Projects/exponent-wrapper/exponent/python_modules/exponent/exponent/core/graphql/subscriptions.py`
   - Authentication-related GraphQL subscriptions