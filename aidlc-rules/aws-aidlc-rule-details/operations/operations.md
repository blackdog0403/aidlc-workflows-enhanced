# Operations Phase

**Purpose**: Post-construction codebase health, entropy management, and continuous improvement

**Status**: Extended from placeholder with Harness Engineering patterns for entropy management and operational readiness.

## Scope

The Operations phase covers activities **after Construction completes**:

1. **Entropy Management** — detect and fix codebase degradation (see `operations/entropy-management.md`)
2. **Deployment Planning** — build and deployment instructions (generated in Build and Test)
3. **Harness Evolution** — improve AI-DLC rules based on execution traces
4. **Health Monitoring** — periodic codebase health scans

## When to Execute

- **After Build and Test completes successfully**
- **Periodically** — after significant code changes or new Construction cycles
- **On-demand** — when quality degradation is suspected

## Steps

### Step 1: Run Gardener Scan

Load `operations/entropy-management.md` and execute:
- [ ] Doc-Code drift scan
- [ ] Architecture violation check
- [ ] Dead code detection
- [ ] Style consistency review
- [ ] Test coverage validation
- [ ] Dependency health check

### Step 2: Generate Health Report

Create `aidlc-docs/operations/health-report.md` with:
- Health score (0-100)
- Critical issues, warnings, auto-fixes applied
- Entropy metrics (duplication, dead code, coverage, etc.)

### Step 3: Trace-Based Harness Improvement

Analyze execution traces from the latest Construction cycle:
- [ ] Categorize failures (misunderstanding, missing context, repeated mistake, architecture violation)
- [ ] Propose rule file updates
- [ ] Apply Feedback Encoding Ladder (escalate repeated issues to stronger enforcement)

### Step 4: Update State

Update `aidlc-docs/aidlc-state.md`:
- Mark Operations scan as complete
- Record health score and findings count
- Log harness changes in audit.md

### Step 5: Present Results

```markdown
# 🏥 Codebase Health Report Complete

> **📋 <u>**REVIEW REQUIRED:**</u>**
> Please examine the health report at: `aidlc-docs/operations/health-report.md`

> **🔧 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Address Critical Issues** - Fix issues identified in the health report
> 📝 **Update Rules** - Improve AI-DLC rules based on trace analysis
> ✅ **Acknowledge** - Mark health scan as reviewed

---
```

## Future Scope

Still planned for future versions:
- CI/CD pipeline integration
- Production monitoring and alerting setup
- Incident response procedures
- Automated rollback procedures
