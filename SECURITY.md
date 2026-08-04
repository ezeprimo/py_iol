# Security Policy

## Supported Versions

Security fixes are considered for the latest published version of `pyiol-client`.
Older versions may not receive fixes; upgrade before reporting or evaluating an issue.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately. Do not open a public issue, pull request,
discussion, or forum post containing exploitable details.

Use GitHub's private vulnerability reporting feature from the repository Security tab when it
is available. If private reporting is not enabled, contact the repository maintainers through
the private channel configured here:

> **Security contact: [TO BE CONFIGURED BY REPOSITORY MAINTAINERS]**

Do not send credentials or other secrets in a report. Redact tokens, passwords, API keys,
account identifiers, personal data, and any request or response fields that contain them.

## Information to Include

Include enough information to reproduce and assess the issue safely:

- A short description of the vulnerability and its potential impact.
- The affected `pyiol-client` version, Python version, and operating system.
- The relevant endpoint, client method, or configuration area.
- Minimal reproduction steps or a proof of concept that does not use real credentials or funds.
- Expected behavior and actual behavior.
- Any logs, tracebacks, HTTP status codes, or sanitized request/response excerpts.
- Your preferred contact details for follow-up, if the private reporting channel does not provide them.

## Scope

This policy covers security issues in the `pyiol-client` package, including authentication,
credential handling, request construction, response handling, and documentation that could
cause unsafe use of the library.

The following are generally outside the project's control and should not be reported as
vulnerabilities in this repository:

- Vulnerabilities in the Invertir Online service or its infrastructure.
- Vulnerabilities in Python, `httpx`, `cachetools`, or other third-party dependencies without a
  demonstrated impact through this package.
- Issues requiring access to credentials or systems that the reporter is not authorized to use.
- Denial-of-service testing, automated high-volume requests, or testing against production accounts.

Do not perform testing that could execute trades, alter account data, or disrupt the IOL service.
Use a controlled environment and authorized test accounts only.

## Response Process

Maintainers will acknowledge a private report when possible, investigate its impact, and
coordinate a fix or mitigation. Please allow reasonable time for assessment and disclosure
coordination before making details public.
