# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** Open a Public Issue

Security vulnerabilities should not be disclosed publicly until a fix is available.

### 2. Report Privately

Send a detailed report to: **[your-email@example.com]** or use GitHub's private vulnerability reporting feature.

### 3. Include in Your Report

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)
- Your contact information

### 4. What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Status Updates**: Regular updates as we work on a fix
- **Resolution**: Depending on severity, typically within 30 days

### 5. Disclosure Timeline

- We will work with you to understand and fix the issue
- Once fixed, we'll coordinate disclosure timing
- Credit will be given to reporters (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

1. **Environment Variables**: Never commit `.env` files
2. **Secrets**: Use strong, unique values for `JWT_SECRET_KEY` and `POSTGRES_PASSWORD`
3. **Database**: Don't expose PostgreSQL port to the internet
4. **HTTPS**: Always use HTTPS in production
5. **Dependencies**: Keep dependencies up to date
6. **Monitoring**: Set up logging and monitoring

### For Developers

1. **Input Validation**: All user input is validated via Pydantic schemas
2. **SQL Injection**: Use SQLAlchemy ORM (never raw SQL)
3. **Password Storage**: Passwords are hashed with Argon2
4. **JWT Tokens**: Access tokens expire in 15 minutes
5. **Authentication**: Protected endpoints require valid JWT
6. **Authorization**: Role-based access control enforced at service layer
7. **Dependencies**: Regularly audit with `uv pip list --outdated`

## Known Security Considerations

### Rate Limiting
**Status**: Not implemented  
**Recommendation**: Add rate limiting middleware for production (e.g., slowapi)

### CORS
**Status**: Not configured  
**Recommendation**: Configure CORS for your frontend origin in production

### Input Size Limits
**Status**: Default FastAPI limits  
**Recommendation**: Configure appropriate limits for your use case

### Session Management
**Status**: Refresh token rotation implemented  
**Note**: Refresh tokens are stored in database and can be revoked

## Security Updates

We will announce security updates through:
- GitHub Security Advisories
- Release notes
- README updates

## Scope

This security policy applies to:
- The ProjectHub codebase
- Official Docker images
- Documentation

It does NOT apply to:
- Third-party dependencies (report to their maintainers)
- Forks and derivatives
- Your deployment infrastructure

## Contact

For security concerns, contact: **[your-email@example.com]**

For general questions, open a GitHub issue.

---

Thank you for helping keep ProjectHub secure!
