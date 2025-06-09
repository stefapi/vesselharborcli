# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of FastAPI Vue Template seriously. If you believe you've found a security vulnerability, please follow these steps:

1. **Do not disclose the vulnerability publicly**
2. **Email the details to [stephane{plus}security{at}apiou{dot}org]**
   - Provide a detailed description of the vulnerability
   - Include steps to reproduce the issue
   - Attach any proof-of-concept code or screenshots if applicable
   - Let us know if you'd like to be credited for the discovery

## What to Expect

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide an initial assessment of the report within 7 days
- We aim to release a fix for verified vulnerabilities within 30 days
- We will keep you informed of our progress throughout the process
- After the issue is resolved, we will publicly acknowledge your responsible disclosure (unless you prefer to remain anonymous)

## Security Best Practices for Deployment

When deploying this application, please follow these security best practices:

1. **Environment Variables**
   - Never commit `.env` files to version control
   - Use strong, unique values for `SECRET_KEY` and other sensitive variables
   - Rotate secrets regularly

2. **Database Security**
   - Use strong passwords for database access
   - Restrict database access to only the application server
   - Enable TLS/SSL for database connections

3. **API Security**
   - Use HTTPS in production
   - Implement rate limiting to prevent abuse
   - Keep dependencies updated to avoid known vulnerabilities

4. **Authentication**
   - Use strong password policies
   - Implement multi-factor authentication where possible
   - Set appropriate token expiration times

## Security Updates

We will announce security updates through:

- GitHub Security Advisories
- Release notes
- (Optional) Security mailing list

Thank you for helping keep FastAPI Vue Template and its users safe!
