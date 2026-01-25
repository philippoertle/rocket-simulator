# Maintenance Runbook

**Project:** PET Rocket Simulator  
**Purpose:** Operational procedures for ongoing maintenance  
**Audience:** Project maintainers  
**Last Updated:** January 25, 2026

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Weekly Tasks](#weekly-tasks)
3. [Monthly Tasks](#monthly-tasks)
4. [Quarterly Reviews](#quarterly-reviews)
5. [Issue Triage](#issue-triage)
6. [Release Procedures](#release-procedures)
7. [Emergency Procedures](#emergency-procedures)
8. [Common Tasks](#common-tasks)

---

## Daily Operations

### Morning Check (5 minutes)

```bash
# 1. Check GitHub notifications
# - New issues
# - New PRs
# - Comments/mentions

# 2. Review CI/CD status
# - Check if any builds are failing
# - Review any security alerts

# 3. Quick triage
# - Label new issues
# - Respond to critical items
```

**Action Items:**
- [ ] Respond to critical (P0) issues within 24 hours
- [ ] Acknowledge new issues/PRs
- [ ] Check for security alerts

---

## Weekly Tasks

### Monday: Planning (30 minutes)

```bash
# 1. Review open issues
gh issue list --state open

# 2. Review open PRs
gh pr list --state open

# 3. Plan week's work
# - Identify issues to work on
# - Set weekly goals
```

**Checklist:**
- [ ] Triage all new issues from last week
- [ ] Review all open PRs
- [ ] Update project board
- [ ] Identify priorities for the week

### Wednesday: Code Review (1 hour)

```bash
# 1. Review pending PRs
gh pr list --state open

# 2. Test PR locally if needed
gh pr checkout <PR-number>
pytest -v
```

**Checklist:**
- [ ] Review all open PRs
- [ ] Provide constructive feedback
- [ ] Merge ready PRs
- [ ] Update PR status

### Friday: Maintenance (1 hour)

```bash
# 1. Check dependency updates
pip list --outdated

# 2. Review security advisories
# Check GitHub Security tab

# 3. Update documentation if needed
```

**Checklist:**
- [ ] Review dependency updates
- [ ] Check for security vulnerabilities
- [ ] Update docs if needed
- [ ] Close completed issues
- [ ] Update CHANGELOG if changes merged

---

## Monthly Tasks

### First Monday of Month (2 hours)

#### 1. Dependency Review

```bash
# Check for outdated dependencies
pip list --outdated

# Security scan
pip install safety
safety check

# Update dependencies (testing)
pip install --upgrade numpy scipy matplotlib cantera

# Run full test suite
pytest -v --cov=rocket_sim

# If all tests pass, update requirements.txt
pip freeze > requirements.txt
```

#### 2. Metrics Review

**Gather metrics:**
- PyPI download stats (if published)
- GitHub stars/forks
- Open vs closed issues
- PR merge rate
- Test coverage
- Code quality scores

**Document in:**
`docs/development/metrics/YYYY-MM.md`

#### 3. Issue Cleanup

```bash
# Close stale issues
# - No response for 30+ days
# - Resolved but not closed

# Update labels
# - Priority changes
# - Status updates
```

#### 4. Documentation Review

**Check for:**
- Broken links
- Outdated information
- Missing documentation
- User confusion patterns (from issues)

**Update as needed:**
- README.md
- QUICKSTART.md
- INSTALL.md
- API docs

---

## Quarterly Reviews

### Quarter Planning Session (4 hours)

#### 1. Performance Review

**Metrics to analyze:**
- Issues: Opened vs closed trend
- Response times: Average time to first response
- Resolution times: Average time to close
- User satisfaction: Based on feedback
- Code quality: Test coverage, lint scores
- Community: Contributors, engagement

#### 2. Roadmap Update

**Review:**
- Feature requests
- User needs
- Technical debt
- Performance issues
- Competition/alternatives

**Plan:**
- Next quarter priorities
- Major features to implement
- Technical debt to address
- Documentation improvements

#### 3. Process Improvement

**Evaluate:**
- What's working well?
- What's not working?
- Bottlenecks?
- Community feedback?

**Improve:**
- Update processes
- Improve documentation
- Enhance automation
- Streamline workflows

---

## Issue Triage

### Triage Process (for each new issue)

```bash
# 1. Read and understand the issue

# 2. Apply labels
# Type: bug, enhancement, question, documentation
# Priority: priority-critical, priority-high, priority-medium, priority-low
# Component: module-combustion, module-system, module-fem, etc.
# Status: status-triage (initially)

# 3. Request clarification if needed
# - Ask for reproduction steps
# - Request environment details
# - Ask for code examples

# 4. Reproduce if bug
# - Try to reproduce locally
# - Confirm the issue

# 5. Update status
# - status-confirmed: Issue confirmed
# - status-wontfix: Won't address
# - status-duplicate: Duplicate of another

# 6. Assign priority
# Based on severity and impact

# 7. Assign or add to backlog
```

### Priority Guidelines

**Critical (P0):**
- Security vulnerabilities
- Data corruption
- System crashes
- Incorrect results (safety-critical)

**High (P1):**
- Major functionality broken
- Performance regression
- Installation failures

**Medium (P2):**
- Minor bugs
- Usability issues
- Missing features (requested)

**Low (P3):**
- Cosmetic issues
- Documentation typos
- Nice-to-have features

---

## Release Procedures

### Patch Release (0.1.x)

**When:** Bug fixes, minor updates

```bash
# 1. Create release branch
git checkout -b release/0.1.x

# 2. Update version
# Edit setup.py: version='0.1.x'

# 3. Update CHANGELOG.md
# Add entry for this version

# 4. Run full test suite
pytest -v --cov=rocket_sim
# Ensure >90% coverage, ~96% pass rate

# 5. Build package
python -m build

# 6. Test package locally
pip install dist/rocket_simulator-0.1.x.tar.gz
python -c "import rocket_sim; print(rocket_sim.__version__)"

# 7. Merge to main
git checkout main
git merge release/0.1.x

# 8. Tag release
git tag -a v0.1.x -m "Release version 0.1.x"
git push origin main --tags

# 9. Upload to PyPI
twine upload dist/*

# 10. Create GitHub Release
# Go to Releases > Draft a new release
# - Tag: v0.1.x
# - Title: Version 0.1.x
# - Description: From CHANGELOG.md
# - Attach: dist files

# 11. Announce
# - Update README if needed
# - Post in Discussions (if enabled)
```

### Minor Release (0.x.0)

**When:** New features, enhancements

```bash
# Follow same process as patch release, but:
# - More extensive testing
# - Update documentation for new features
# - Possibly update QUICKSTART.md
# - Announce more prominently
```

### Major Release (x.0.0)

**When:** Breaking changes, major overhaul

```bash
# Follow release process, plus:
# - Create migration guide
# - Extensive testing
# - Beta release first (optional)
# - Coordinated announcement
# - Update all documentation
```

---

## Emergency Procedures

### Critical Security Vulnerability

```bash
# 1. IMMEDIATELY - Assess severity
# - Can users be exploited?
# - What's the impact?
# - Are users at risk right now?

# 2. If severe:
# - Draft security advisory (keep private)
# - Disable affected functionality if possible
# - Notify known users (if applicable)

# 3. Develop fix (PRIVATE BRANCH)
git checkout -b security/CVE-YYYY-XXXXX

# 4. Test fix thoroughly
pytest -v

# 5. Create hotfix release
# Follow patch release process

# 6. Publish security advisory
# On GitHub Security tab

# 7. Notify users
# - GitHub Release notes
# - Pin issue to repository
# - Email if applicable

# Time Target: Fix within 7 days for critical
```

### Critical Bug (System Crash/Data Loss)

```bash
# 1. Reproduce the issue
# - Verify it's actually critical
# - Document reproduction steps

# 2. Create hotfix branch
git checkout -b hotfix/critical-bug-name

# 3. Fix and test
# - Implement fix
# - Add regression test
# - Run full test suite

# 4. Emergency release
# Follow patch release process (expedited)

# 5. Notify users
# GitHub release notes

# Time Target: Fix within 1 week
```

---

## Common Tasks

### Adding a New Contributor

```bash
# 1. Merge their first PR

# 2. Update CONTRIBUTORS.md
# Add their name/handle

# 3. Thank them in PR comments

# 4. Mention in next release notes
```

### Handling Stale Issues

```bash
# If issue has no activity for 30 days:

# 1. Comment asking for update
"Is this still an issue? If there's no response in 14 days, we'll close this. Please reopen if needed."

# 2. Wait 14 days

# 3. If no response, close with comment
"Closing due to inactivity. Please reopen if this is still relevant."

# 4. Label: status-stale
```

### Updating Dependencies

```bash
# 1. Check for updates
pip list --outdated

# 2. Update one at a time (in dev environment)
pip install --upgrade <package>

# 3. Run tests
pytest -v

# 4. If tests pass, update requirements.txt
pip freeze > requirements.txt

# 5. Commit
git commit -am "deps: Update <package> to <version>"

# 6. Create PR
gh pr create --title "deps: Update <package>" --body "Updates <package> to <version> for bug fixes/features"
```

### Code Review Checklist

**For each PR:**
- [ ] Code follows style guidelines (PEP 8)
- [ ] Tests added/updated
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No security issues
- [ ] No performance regressions
- [ ] Breaking changes justified
- [ ] Commit messages clear

---

## Tools & Commands

### GitHub CLI Commands

```bash
# List issues
gh issue list --state open
gh issue list --label bug

# View issue
gh issue view <number>

# Create issue
gh issue create --title "..." --body "..."

# Close issue
gh issue close <number>

# List PRs
gh pr list --state open

# Review PR
gh pr view <number>
gh pr checkout <number>
gh pr review <number> --approve
gh pr merge <number> --squash

# Create release
gh release create v0.1.x --title "Version 0.1.x" --notes "..."
```

### Python Package Management

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI (testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*

# Install from local build
pip install dist/rocket_simulator-0.1.0.tar.gz
```

### Testing Commands

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=rocket_sim --cov-report=html

# Run specific module
pytest rocket_sim/combustion/tests/

# Run specific test
pytest rocket_sim/combustion/tests/test_cantera_wrapper.py::test_basic_combustion

# Run validation tests
pytest tests/test_phase5_validation.py
```

---

## Contact & Escalation

**Primary Maintainer:** [Your Name]  
**Backup Maintainer:** [If applicable]  
**Security Contact:** See SECURITY.md  

**Response Times:**
- Critical issues: 24 hours
- High priority: 3 days  
- General: 1 week (best effort)

---

**Remember:** This is an open-source project. Set realistic expectations and maintain work-life balance!

**Last Updated:** January 25, 2026
