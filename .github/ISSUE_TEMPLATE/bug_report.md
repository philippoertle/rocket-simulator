---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] '
labels: bug, status-triage
assignees: ''
---

## Bug Description

**Summary:**
A clear and concise description of what the bug is.

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened.

## Reproduction Steps

1. Step 1...
2. Step 2...
3. Step 3...
4. See error

**Minimal Code Example:**
```python
# Minimal code to reproduce the issue
from rocket_sim import ...

# Your code here
```

## Environment

**System Information:**
- OS: [e.g., Windows 11, Ubuntu 22.04, macOS 14]
- Python Version: [e.g., 3.11.5]
- rocket-simulator Version: [e.g., 0.1.0]

**Dependencies:**
```bash
# Output of: pip list | grep -E "numpy|scipy|matplotlib|cantera"
numpy==1.24.0
scipy==1.10.0
matplotlib==3.7.0
cantera==3.0.0
```

## Error Output

**Error Message:**
```
Paste the full error traceback here
```

**Log Output (if applicable):**
```
Paste relevant log output here
```

## Additional Context

**Screenshots/Plots:**
If applicable, add screenshots or plots to help explain the problem.

**Related Issues:**
Links to related issues or discussions.

**Possible Solution:**
If you have ideas about what might be causing this or how to fix it.

## Severity Assessment

**Impact:** [Critical / High / Medium / Low]
- Critical: System crashes, data corruption, security issue
- High: Major functionality broken, incorrect results
- Medium: Minor functionality issue, workaround available
- Low: Cosmetic issue, documentation error

**Urgency:** [Immediate / Soon / When possible]

---

**Checklist:**
- [ ] I have searched existing issues to avoid duplicates
- [ ] I have included a minimal code example
- [ ] I have provided my environment details
- [ ] I have included the full error traceback
- [ ] I have described the expected vs actual behavior
