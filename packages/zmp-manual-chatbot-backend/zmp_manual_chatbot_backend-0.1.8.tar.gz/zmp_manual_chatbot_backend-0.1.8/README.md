# ZMP Manual Chatbot Backend

A production-ready FastAPI backend for the ZMP Manual Chatbot with OAuth2 authentication, multi-agent workflow, and MCP Server integration for intelligent document retrieval and response generation.

## Features

- **🔐 OAuth2 Authentication**: Secure authentication with Keycloak integration
- **🤖 Multi-Agent Workflow**: Intelligent planning, research, and response generation
- **📚 MCP Server Integration**: Async integration with MCP Server for knowledge retrieval
- **📖 OpenAPI Documentation**: Complete API documentation with Swagger UI
- **🔄 Streaming Responses**: Real-time streaming of multi-agent workflow progress
- **🏗️ Production-Ready**: Logging, error handling, health checks, session management
- **🐳 Containerization-Ready**: Docker/Kubernetes deployment support
- **🧪 Comprehensive Testing**: Test suite for API and core logic

## Getting Started

### Prerequisites

- Python 3.12+
- MCP Server running and accessible (see `MCP_SERVER_URL` in config)
- Keycloak server configured for OAuth2 authentication

### Installation

Clone this repository:

```bash
# Clone the repo
cd /path/to/your/workspace
git clone <your-repo-url>
cd zmp-manual-chatbot-backend
```

Set up a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
poetry install
```

### Configuration

#### Environment Variables

Create a `.env` file or set the following environment variables:

```bash
# MCP Server Configuration
export MCP_SERVER_URL='http://localhost:5371/mcp'

# Keycloak OAuth2 Configuration
export KEYCLOAK_SERVER_URL='https://keycloak.ags.cloudzcp.net/auth'
export KEYCLOAK_REALM='ags'
export KEYCLOAK_CLIENT_ID='zmp-client'
export KEYCLOAK_CLIENT_SECRET='your-client-secret'
export KEYCLOAK_REDIRECT_URI='http://localhost:5370/api/manual-chatbot/v1/auth/callback'

# Server Configuration
export HOST='0.0.0.0'
export PORT='5370'
export LOG_LEVEL='info'
```

#### Keycloak Setup

1. Configure your Keycloak client with:
   - **Valid Redirect URIs**: `http://localhost:5370/api/manual-chatbot/v1/auth/callback`
   - **Web Origins**: `http://localhost:5370`
   - **Client Protocol**: `openid-connect`
   - **Access Type**: `confidential`

### Running Locally

Start the FastAPI app with Uvicorn:

```bash
poetry run uvicorn src.zmp_manual_chatbot_backend.main:app --reload --host 0.0.0.0 --port 5370
```

- **API Documentation**: http://localhost:5370/api/manual-chatbot/v1/api-docs
- **Health Check**: http://localhost:5370/health
- **OAuth2 Callback**: http://localhost:5370/api/manual-chatbot/v1/auth/callback

## API Usage

### Authentication System

The ZMP Manual Chatbot Backend now uses the **zmp_authentication_provider** package for comprehensive OAuth2 authentication with Keycloak integration.

#### 🔐 Authentication Overview

The authentication system provides:
- **OAuth2 with Keycloak**: Enterprise-grade authentication
- **Session Management**: Secure session handling and persistence
- **Token Management**: Access token and refresh token lifecycle
- **User Profile Access**: Authenticated user information retrieval

#### 📋 Available Authentication Endpoints

| Endpoint | Method | Description | Usage |
|----------|--------|-------------|-------|
| `/auth/home` | GET | Authentication home page | Entry point for authentication flow |
| `/auth/authenticate` | GET | Initiate OAuth2 authentication | Redirects to Keycloak login |
| `/auth/oauth2/callback` | GET | OAuth2 callback handler | Handles Keycloak response |
| `/auth/access_token` | GET | Retrieve current access token | Get token for API calls |
| `/auth/refresh_token` | PATCH | Refresh expired access token | Renew authentication |
| `/auth/logout` | GET | Logout and clear session | End authentication session |
| `/auth/profile` | GET | Get authenticated user profile | Retrieve user information |

#### 🚀 Client Authentication Flow

##### Step 1: Initiate Authentication
```bash
# Navigate user to authentication endpoint
GET /api/manual-chatbot/v1/auth/authenticate
```
This will redirect to Keycloak for user login.

##### Step 2: Handle OAuth2 Callback
After successful login, Keycloak redirects to:
```
/api/manual-chatbot/v1/auth/oauth2/callback?code=AUTH_CODE&state=STATE
```

##### Step 3: Retrieve Access Token
```bash
# Get access token for API calls
curl -X GET \
  'http://localhost:5370/api/manual-chatbot/v1/auth/access_token' \
  -H 'Cookie: session_id=YOUR_SESSION_COOKIE'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

##### Step 4: Use Token for API Calls
```bash
# Make authenticated API calls
curl -X POST \
  'http://localhost:5370/api/manual-chatbot/v1/chat/query' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Your question here",
    "chat_history": []
  }'
```

#### 🔄 Token Management

##### Refresh Expired Tokens
```bash
# Refresh access token when expired
curl -X PATCH \
  'http://localhost:5370/api/manual-chatbot/v1/auth/refresh_token' \
  -H 'Cookie: session_id=YOUR_SESSION_COOKIE'
```

##### Check User Profile
```bash
# Get authenticated user information
curl -X GET \
  'http://localhost:5370/api/manual-chatbot/v1/auth/profile' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

**Response:**
```json
{
  "sub": "user-id",
  "preferred_username": "username",
  "email": "user@example.com",
  "name": "User Name",
  "roles": ["user", "admin"]
}
```

#### 🖥️ Web Client Integration

##### JavaScript/Frontend Integration

```javascript
// 1. Initiate authentication
window.location.href = '/api/manual-chatbot/v1/auth/authenticate';

// 2. After callback, get access token
async function getAccessToken() {
  const response = await fetch('/api/manual-chatbot/v1/auth/access_token', {
    credentials: 'include' // Include session cookies
  });
  
  if (response.ok) {
    const data = await response.json();
    return data.access_token;
  }
  throw new Error('Authentication required');
}

// 3. Make authenticated API calls
async function chatQuery(question, accessToken) {
  const response = await fetch('/api/manual-chatbot/v1/chat/query', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      question: question,
      chat_history: []
    })
  });
  
  return response.json();
}

// 4. Handle token refresh
async function refreshToken() {
  const response = await fetch('/api/manual-chatbot/v1/auth/refresh_token', {
    method: 'PATCH',
    credentials: 'include'
  });
  
  if (response.ok) {
    return await response.json();
  }
  // Redirect to authentication if refresh fails
  window.location.href = '/api/manual-chatbot/v1/auth/authenticate';
}

// 5. Logout
async function logout() {
  await fetch('/api/manual-chatbot/v1/auth/logout', {
    credentials: 'include'
  });
  // Redirect to home or login page
}
```

#### 📱 Mobile/Native App Integration

```javascript
// React Native / Mobile app example
class AuthService {
  constructor() {
    this.baseURL = 'http://your-api-domain.com/api/manual-chatbot/v1';
    this.accessToken = null;
  }

  // Open web view for authentication
  async authenticate() {
    const authURL = `${this.baseURL}/auth/authenticate`;
    // Open WebView or browser for OAuth flow
    // Handle redirect to get session
  }

  // Get access token after authentication
  async getAccessToken(sessionCookie) {
    const response = await fetch(`${this.baseURL}/auth/access_token`, {
      headers: {
        'Cookie': sessionCookie
      }
    });
    
    const data = await response.json();
    this.accessToken = data.access_token;
    return this.accessToken;
  }

  // Make authenticated requests
  async makeAuthenticatedRequest(endpoint, options = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.accessToken}`
      }
    });

    if (response.status === 401) {
      // Token expired, try refresh
      await this.refreshToken();
      // Retry request
      return this.makeAuthenticatedRequest(endpoint, options);
    }

    return response;
  }
}
```

#### 🔒 Security Best Practices for Clients

1. **Secure Token Storage**
   - Store tokens securely (Keychain/Keystore for mobile)
   - Never log tokens in production
   - Use secure HTTP-only cookies when possible

2. **Token Lifecycle Management**
   - Implement automatic token refresh
   - Handle token expiration gracefully
   - Clear tokens on logout

3. **Error Handling**
   - Handle 401 responses appropriately
   - Implement retry logic for network failures
   - Provide clear authentication error messages

4. **Session Management**
   - Include credentials/cookies for session-based requests
   - Handle session timeouts
   - Implement proper logout functionality

#### 🧪 Testing Authentication

You can test the authentication flow using:

1. **Swagger UI**: Visit http://localhost:5370/api/manual-chatbot/v1/api-docs
2. **Browser**: Navigate to authentication endpoints directly
3. **cURL**: Use the examples provided above
4. **Automated Tests**: Run the comprehensive test suite (see Testing section)

#### 🛠️ Authentication Methods

You can authenticate using any of these methods:

1. **Web Browser Flow**: Complete OAuth2 flow in browser
2. **API Token**: Use a Bearer token in the Authorization header  
3. **Session Cookies**: Maintain session after initial authentication
4. **Swagger UI**: Built-in authentication for API testing

### Chat Query Endpoint

**Endpoint**: `POST /api/manual-chatbot/v1/chat/query`

**Request Schema**:
```json
{
  "question": "Your question here",
  "chat_history": [],
  "image_url": null,
  "thread_id": null
}
```

**Example cURL**:
```bash
curl -X 'POST' \
  'http://localhost:5370/api/manual-chatbot/v1/chat/query' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_OAUTH2_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Kubernetes에 대해 알려줘",
    "chat_history": [],
    "image_url": null
  }'
```

**Response**: Streaming JSON with multi-agent workflow progress:
```json
{"plan": [], "final_answer": null, "doc_urls": null, "citation_map": null}
{"plan": ["Step 1", "Step 2"], "final_answer": null, "doc_urls": null, "citation_map": null}
{"plan": [], "final_answer": "Complete answer with citations", "doc_urls": ["url1"], "citation_map": {...}}
```

### Complete Authentication API Reference

The authentication system provides a full suite of endpoints for client integration:

| Endpoint | Method | Description | Authentication Required |
|----------|--------|-------------|------------------------|
| `/auth/home` | GET | Authentication home page | No |
| `/auth/authenticate` | GET | Initiate OAuth2 flow | No |
| `/auth/oauth2/callback` | GET | Handle OAuth2 callback | No |
| `/auth/access_token` | GET | Get current access token | Session |
| `/auth/refresh_token` | PATCH | Refresh access token | Session |
| `/auth/logout` | GET | Logout and clear session | Session |
| `/auth/profile` | GET | Get user profile | Bearer Token |

**Base URL**: `http://localhost:5370/api/manual-chatbot/v1`

For detailed client integration examples, see the Authentication System section above.

## Project Structure

```
zmp-manual-chatbot-backend/
├── src/
│   └── zmp_manual_chatbot_backend/
│       ├── __init__.py
│       ├── main.py              # FastAPI app entrypoint with OAuth2 config
│       ├── config.py            # Global settings (MCP, Keycloak, etc.)
│       ├── mcp_client.py        # Async client for MCP Server
│       ├── service.py           # Business logic/multi-agent workflow
│       ├── schemas.py           # Pydantic models for API
│       ├── router.py            # Chat API endpoints
│       ├── auth_router.py       # OAuth2 authentication endpoints
│       ├── auth_service.py      # Authentication service layer
│       ├── oauth2_keycloak.py  # Keycloak OAuth2 integration
│       ├── auth_models.py       # Authentication Pydantic models
│       ├── session.py           # Session management
│       └── agents.py            # Multi-agent workflow definitions
├── tests/
│   ├── __init__.py
│   ├── test_chat.py            # Tests for chat API
│   └── outputs/
│       └── __init__.py
├── k8s/                        # Kubernetes deployment files
├── pyproject.toml
├── README.md
├── logging.conf
└── .env                        # Environment configuration
```

### Key Components

- **`main.py`**: FastAPI app with OAuth2 security schemes and custom OpenAPI schema
- **`router.py`**: Chat query endpoint with authentication requirements
- **`auth_router.py`**: OAuth2 callback and authentication endpoints
- **`service.py`**: Multi-agent workflow orchestration
- **`agents.py`**: Individual agent implementations (planner, researcher, etc.)
- **`schemas.py`**: Pydantic models for API requests/responses
- **`oauth2_keycloak.py`**: Keycloak integration and JWT validation

## Multi-Agent Workflow

The chatbot uses a sophisticated multi-agent workflow:

1. **Planner Agent**: Breaks down user queries into actionable steps
2. **Research Agent**: Searches knowledge base using MCP Server
3. **Answer Agent**: Synthesizes information into comprehensive responses
4. **Citation Agent**: Provides proper document references and citations

## Docker Usage

```bash
# Build the Docker image
docker build -t zmp-manual-chatbot-backend .

# Run the container
docker run -e MCP_SERVER_URL=http://localhost:5371/mcp \
  -e KEYCLOAK_SERVER_URL=https://keycloak.ags.cloudzcp.net/auth \
  -e KEYCLOAK_CLIENT_SECRET=your-secret \
  -p 5370:5370 zmp-manual-chatbot-backend
```

## Kubernetes Deployment

See the `k8s/` directory for Kubernetes deployment configurations:

- `backend-deployment.yaml` - Main application deployment
- `ingress.yaml` - Ingress configuration
- `namespace.yaml` - Namespace setup
- `monitoring.yaml` - Monitoring and logging

## Documentation

### 📚 Complete Documentation Suite

For comprehensive information about the ZMP Manual Chatbot Backend:

#### For Developers
- **[Configuration Guide](docs/CONFIGURATION.md)** - Environment setup and configuration options
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation with examples
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and components

#### For Administrators  
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Security Documentation](docs/SECURITY.md)** - Security implementation and best practices

### 🔧 Advanced Features

#### Multi-Agent Workflow System
The chatbot uses a sophisticated multi-agent architecture:

1. **Query Processing Agents**: Query rewriter, anonymization, language detection
2. **Planning Agents**: Intelligent task breakdown, context-aware routing
3. **Information Retrieval Agents**: MCP server integration, chat history search
4. **Response Generation Agents**: LLM-powered synthesis, citation generation

#### LLM Provider Support
- **Ollama Integration**: Local model deployment with automatic model management
- **OpenAI Integration**: Cloud-based LLM services with intelligent fallback
- **Automatic Provider Detection**: Seamless switching between available providers

#### Security Features
- **OAuth2 with Keycloak**: Enterprise-grade authentication and authorization
- **JWT Validation**: Secure token-based API access
- **RBAC Support**: Role-based access control for granular permissions
- **Security Hardening**: Comprehensive security headers and validation

### 🚀 Deployment Options

#### Development Environment
```bash
# Quick start for development
poetry install
poetry run uvicorn src.zmp_manual_chatbot_backend.main:app --reload
```

#### Docker Deployment
```bash
# Optimized container deployment
docker build -t zmp-manual-chatbot-backend .
docker run -p 5370:5370 zmp-manual-chatbot-backend
```

#### Kubernetes Production
Complete production-ready Kubernetes manifests available in `k8s/` directory with:
- High availability deployment
- Auto-scaling configuration
- Security policies and network isolation
- Monitoring and observability integration

## Testing

### Test Suite
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/zmp_manual_chatbot_backend

# Run specific test categories
pytest tests/test_chat.py -v
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint and workflow testing
- **Security Tests**: Authentication and authorization validation
- **Performance Tests**: Load testing and performance benchmarks

## Development

### Development Workflow
1. **Setup Environment**: Follow installation and configuration guides
2. **Code Development**: Use provided development tools and standards
3. **Testing**: Ensure comprehensive test coverage
4. **Documentation**: Update relevant documentation for changes
5. **Quality Checks**: Run linting, type checking, and security scans

### Development Tools
- **Poetry**: Dependency management and packaging
- **Ruff**: Fast Python linter and code formatter
- **mypy**: Static type checking
- **pytest**: Testing framework with fixtures and mocking
- **Black**: Code formatting (integrated with Ruff)

### Adding New Features

#### Multi-Agent Extensions
1. Define new agent in `agents.py` with proper typing
2. Integrate with workflow in `service.py`
3. Add comprehensive tests and documentation
4. Update API documentation if needed

#### Authentication Extensions
- OAuth2 configuration: `oauth2_keycloak.py`
- Authentication endpoints: `auth_router.py` 
- Security schemes: `main.py` (custom OpenAPI)
- RBAC extensions: Role-based access patterns

## Monitoring & Observability

### Application Metrics
- Request count, duration, and error rates
- Multi-agent workflow performance metrics
- External service health and response times
- Resource utilization and performance trends

### Health Monitoring
- **Health Endpoint**: `/health` for basic health checks
- **Dependency Checks**: MCP server, Keycloak, LLM provider status
- **Performance Monitoring**: Response time tracking and alerting
- **Security Monitoring**: Authentication events and suspicious activity

## Troubleshooting

### Common Issues

#### Authentication Problems
- **Issue**: OAuth2 authentication failures
- **Solution**: Verify Keycloak client configuration, check redirect URIs, review token validation logs
- **Debug**: Enable debug logging and check JWT token structure

#### LLM Provider Issues  
- **Issue**: "No valid LLM provider available"
- **Solution**: Ensure Ollama service is running OR OpenAI API key is configured
- **Debug**: Check provider connectivity and model availability

#### Performance Issues
- **Issue**: Slow response times or high resource usage
- **Solution**: Monitor resource limits, optimize model selection, review query complexity
- **Debug**: Enable performance metrics and analyze bottlenecks

#### Integration Problems
- **Issue**: MCP server connection failures
- **Solution**: Test MCP server connectivity, verify network configuration
- **Debug**: Check logs for connection errors and timeout issues

### Getting Help

1. **Documentation**: Comprehensive guides available in `docs/` directory
2. **Logs**: Check application logs with `tail -f logs/app.log`
3. **Health Checks**: Use `/health` endpoint for service diagnostics
4. **Configuration Validation**: Built-in validation catches common configuration errors

For detailed troubleshooting guides and advanced configuration options, see the [complete documentation](docs/README.md).

## Contributing

### Development Standards
- Follow PEP 8 Python style guidelines  
- Include comprehensive docstrings for all functions and classes
- Maintain high test coverage (>80%)
- Use type hints throughout the codebase
- Update documentation for all changes

### Pull Request Process
1. Fork the repository and create a feature branch
2. Implement changes with appropriate tests
3. Run quality checks: `ruff check`, `mypy`, `pytest`
4. Update relevant documentation
5. Submit pull request with clear description and testing evidence

### Code Review Criteria
- Functionality and correctness
- Security considerations and best practices
- Performance implications
- Test coverage and quality
- Documentation completeness and accuracy

## Authors

SK inc. C&C. Modern Tech. Team

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For more detailed information about any aspect of the system, please refer to the comprehensive [documentation suite](docs/README.md).
