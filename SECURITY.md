# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

**Note:** We maintain security updates for the latest minor version only. Please upgrade to the latest version to receive security patches.

---

## Reporting a Vulnerability

**⚠️ DO NOT report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please report it privately to help us address it before public disclosure.

### How to Report

**Preferred Method: GitHub Security Advisory**

1. Go to the [Security tab](https://github.com/philippoertle/rocket-simulator/security) of this repository
2. Click "Report a vulnerability"
3. Fill out the security advisory form with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

**Alternative Method: Email**

If you cannot use GitHub Security Advisories, email security details to:
- **Email:** security@rocket-simulator.org (or open a GitHub Security Advisory)
- **Subject:** [SECURITY] Vulnerability in rocket-simulator

### What to Include

Please include the following information:

1. **Description:** Clear description of the vulnerability
2. **Impact:** What could an attacker do with this vulnerability?
3. **Affected Components:** Which modules/files are affected?
4. **Reproduction Steps:** Detailed steps to reproduce the issue
5. **Proof of Concept:** Code demonstrating the vulnerability
6. **Suggested Fix:** If you have ideas on how to fix it
7. **Your Details:** Name/handle for credit (optional)

### What to Expect

**Response Timeline:**

- **Initial Response:** Within 48 hours
- **Status Update:** Within 5 business days
- **Fix Timeline:** Depends on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next release

**Our Process:**

1. **Acknowledge:** We confirm receipt of your report
2. **Assess:** We evaluate the severity and impact
3. **Develop:** We develop a fix in a private branch
4. **Test:** We thoroughly test the fix
5. **Coordinate:** We coordinate disclosure with you
6. **Release:** We release a patch and publish an advisory
7. **Credit:** We credit you in the security advisory (if desired)

---

## Security Considerations

### Scope of Security Issues

**In Scope:**
- Code execution vulnerabilities
- Denial of service attacks
- Data integrity issues
- Dependency vulnerabilities with actual impact
- Injection vulnerabilities (if applicable)

**Out of Scope:**
- Simulation accuracy issues (these are bugs, not security issues)
- Performance problems
- Missing input validation that doesn't lead to code execution
- Issues requiring physical access to the machine
- Social engineering attacks

### Known Limitations

**This is a simulation tool, not safety-critical software:**

1. **Educational Purpose Only**
   - This software is for educational and research purposes
   - NOT certified for safety-critical applications
   - NOT a substitute for professional engineering analysis

2. **Simulation Limitations**
   - Results depend on model accuracy
   - Real-world behavior may differ
   - User responsible for validation

3. **Safety Disclaimer**
   - See LICENSE file for full disclaimer
   - Working with H₂/O₂ is inherently dangerous
   - Consult professionals before physical testing

### Dependency Security

We monitor dependencies for known vulnerabilities using:

- **GitHub Dependabot:** Automated dependency updates
- **Safety:** Python package vulnerability scanning
- **Manual Reviews:** Periodic security audits

**Dependency Update Policy:**
- Critical security updates: Immediate patch release
- High security updates: Within 1 week
- Medium security updates: Next minor release
- Low security updates: Next planned release

---

## Security Best Practices for Users

### Installation Security

1. **Verify Package Integrity**
   ```bash
   # Install from official PyPI only
   pip install rocket-simulator
   
   # Verify checksums if provided
   ```

2. **Use Virtual Environments**
   ```bash
   # Isolate dependencies
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install rocket-simulator
   ```

3. **Keep Dependencies Updated**
   ```bash
   # Regular updates
   pip install --upgrade rocket-simulator
   ```

### Usage Security

1. **Input Validation**
   - Validate all user inputs
   - Use reasonable bounds for parameters
   - Don't execute untrusted simulation configurations

2. **Output Handling**
   - Review simulation results before physical testing
   - Understand uncertainty and limitations
   - Apply conservative safety factors

3. **Data Privacy**
   - Simulation data stays on your machine
   - No telemetry or data collection
   - Control what you share publicly

---

## Security Disclosure Policy

### Coordinated Disclosure

We follow responsible disclosure practices:

1. **Private Development:** Fixes developed in private
2. **Coordinated Timing:** Disclosure coordinated with reporter
3. **Advance Notice:** Users notified before public disclosure
4. **Patch Release:** Fix released before advisory publication
5. **Public Advisory:** Details published after fix is available

### Security Advisories

Published security advisories include:

- **Severity:** Critical / High / Medium / Low
- **Impact:** What attackers could do
- **Affected Versions:** Which versions are vulnerable
- **Fixed Version:** Version with the fix
- **Workarounds:** Temporary mitigations (if any)
- **Credits:** Recognition of reporter
- **Timeline:** Key dates in the disclosure process

### CVE Assignment

For significant vulnerabilities, we may request a CVE identifier through GitHub or MITRE.

---

## Security Updates

### How to Stay Informed

- **GitHub Watch:** Watch the repository for security advisories
- **Release Notes:** Check CHANGELOG.md for security fixes
- **GitHub Releases:** Subscribe to release notifications
- **Security Tab:** Monitor the Security tab on GitHub

### Security Patch Versioning

Security patches are released as patch versions (0.1.x):

- `0.1.0` → `0.1.1`: Security fix
- `0.1.1` → `0.1.2`: Another security fix

Version numbers don't reveal vulnerability severity (to avoid tipping off attackers before users update).

---

## Contact

**Security Issues:** Use GitHub Security Advisories (preferred)  
**General Questions:** GitHub Issues (for non-security topics only)  
**Project Maintainer:** @philippoertle (GitHub)

---

## Acknowledgments

We appreciate the security research community's efforts to keep software secure. Security researchers who responsibly disclose vulnerabilities will be:

- Credited in security advisories (if desired)
- Listed in a Security Hall of Fame (if we create one)
- Thanked publicly in release notes

Thank you for helping keep rocket-simulator and its users safe!

---

**Last Updated:** January 25, 2026  
**Version:** 1.0
