# HDT Unit Test Authoring Guide (for LLM Agents)
**Version:** 1.0  
**Audience:** LLM agents that *author or modify* unit tests in the HDT style  
**Source Prompt Cards:** Generator + Refactorer modes  

---

## 1) Purpose and Non‑Negotiables
When you decide you must **write new unit tests** or **modify existing tests**, this document is the single reference for *how* to do so.

All HDT unit tests MUST be:

- **Deterministic**: 100% reproducible across runs and environments.
- **Isolated**: no real network / filesystem / database / clock / unseeded randomness.
- **Dependency‑aware**: tests are organized and executed by **levels** (Level 0 → Level N) derived from the call graph.
- **Framework‑native**: no custom gating logic embedded in test bodies.
- **CI‑gated**: higher levels are blocked if lower levels fail (via CI stages, not `if/return` in tests).
- **Signal‑rich for developers**: support dev runs that collect multiple failures when useful.

Guiding principle: **maximize diagnostic value and maintainability without proceduralizing the suite.**

---

## 2) Choose the Mode: Generator vs Refactorer
You MUST explicitly choose one of these modes before authoring.

### Mode A — **Generator** (Create New Tests)
Use **Generator** when:
- No tests exist for the target scope, OR
- You are adding coverage for **new units** / **new behavior**, OR
- You are building a suite from source code (or a new module) and need a baseline.

Primary deliverable shape:
1) Static analysis (UUTs + call graph + levels + deps)
2) Test matrix (happy/boundary/error)
3) New test code (level‑ordered)
4) Execution plan (CI gating + dev signal)
5) Quality checklist

### Mode B — **Refactorer** (Improve Existing Tests)
Use **Refactorer** when:
- A test suite already exists, and you must **fix flakiness**, **reduce brittleness**, **restructure levels**, or **improve coverage**.
- You are modifying tests to align with HDT rules (determinism, isolation, leveling, CI gating).

Primary deliverable shape:
1) Audit (what’s wrong & why)
2) Static analysis (UUTs + call graph + levels + deps)
3) Refactor plan (stepwise)
4) Updated test matrix
5) Refactored test code (or patches)
6) Execution plan (CI gating + dev signal)
7) Quality checklist

---

## 3) Mode Selection Heuristic (Decision Checklist)
If ANY of the following is true, pick **Refactorer**:
- Tests exist for the scope.
- Failures are flaky/intermittent.
- Tests touch real I/O or time.
- Tests rely on order or shared state.
- Assertions are brittle (implementation details, snapshots that break frequently).

Pick **Generator** only when you are genuinely producing **new tests** from source (or for uncovered code).

If ambiguous, default to **Refactorer** (changing existing suites is higher risk; start by auditing).

---

## 4) Universal HDT Test Principles (apply in BOTH modes)

### 4.1 Determinism Requirements
Tests MUST NOT depend on:
- Real wall clock time (use time freezing, dependency injection, or fakes)
- Unseeded randomness (seed or inject deterministic generators)
- Unordered collection iteration (normalize or compare as sets where appropriate)
- Locale/timezone/environment (explicitly set or normalize)
- Global mutable state shared across tests

### 4.2 Isolation Requirements
You MUST isolate:
- **Network** calls (mock/stub)
- **Filesystem** access (use temp fakes or mock; never touch real user paths)
- **Databases** (use in‑memory fakes or mocks; never real DB)
- **External services** (always mock)
- **OS / process** state (env vars, cwd, etc.) where relevant

No test may rely on state left behind by another test.

### 4.3 Behavior over Implementation
- Prefer **behavioral assertions** (inputs → outputs / observable effects).
- Avoid asserting internal calls unless that is the behavior contract.
- Avoid brittle snapshot asserts unless the snapshot is *truly* a stable contract.
- Prefer explicit expected values/exceptions.

### 4.4 AAA Structure
Use **Arrange – Act – Assert** in every test. Make the Act step obvious.

### 4.5 Explicit Expected Outcomes
Every test MUST declare either:
- `expected_output`, OR
- `expected_exception` (type; message only if stable and intentional)

---

## 5) Dependency Awareness: Levels and the Call Graph
HDT uses levels to ensure fast, reliable diagnosis and CI gating.

### 5.1 Definitions
- **UUT (Unit Under Test):** a function/class/module boundary you are testing.
- **Level 0 (Atomic):** leaf units with no internal dependencies (or only trivial pure helpers).
- **Level 1..N (Composed):** units that depend on lower-level units (directly or indirectly).

### 5.2 Required Static Analysis Artifact
Before writing or refactoring tests, you MUST produce:
1) **UUT list**
2) **Call graph** (approximate is acceptable; must be explicit)
3) **Level classification table**
4) **External dependencies to isolate**

### 5.3 Leveling Rules of Thumb
- If a unit calls another project unit: it is *higher level* than the callee.
- If a unit calls an external dependency: it is higher level, and that dependency must be isolated.
- Keep Level 0 tests small and precise; they are your CI gate.

---

## 6) Repo Layout and Naming Conventions
### 6.1 Recommended Layout
```
tests/
  unit/
    atomic/
    composed/
    module/        # optional; only if your project meaningfully benefits
```

### 6.2 Naming Convention
Use clear test names:
- `test_<scenario>_<expected_behavior>`
- Prefer descriptive scenario labels (happy/boundary/error).

---

## 7) Generator Mode: Required Workflow and Output Contract
When in **Generator** mode, you MUST deliver the following artifacts **in this exact order**.

### 7.1 Static Analysis Artifact
Include:
- UUT list
- Call graph
- Levels table
- External deps to isolate

### 7.2 Test Matrix Artifact (minimum cases per UUT)
For each UUT, define at least:
- **Happy path**
- **Boundary case(s)**
- **Error case(s)** (if applicable)

Matrix columns SHOULD include:
- UUT, Level, Scenario, Arrange (inputs), Act, Assert (expected), Mocks

### 7.3 Test Code (Framework‑Native)
- Write tests starting from **Level 0**, then Level 1..N.
- Use AAA.
- No real I/O.
- Explicit expected outcomes.
- Use per-framework best practices (fixtures, parametrization, setup/teardown) *without* creating cross-test coupling.

### 7.4 Execution Plan
Provide:
- **CI plan**: staged gating (atomic → composed → module)
- **Dev plan**: how to run signal‑rich (collect multiple failures)

### 7.5 Quality Checklist
At minimum:
- Deterministic
- Isolated
- Explicit expected outcomes
- Correct levels (atomic first)
- Happy + boundary + error coverage
- Non‑brittle asserts
- Clear naming

---

## 8) Refactorer Mode: Required Workflow and Output Contract
When in **Refactorer** mode, you MUST deliver the following artifacts **in this exact order**.

### 8.1 Audit Artifact (what’s wrong & why)
Identify:
1) **Flakiness sources** (time, random, I/O, shared state, order dependence)
2) **Brittleness sources** (over-mocking, impl-detail asserts, fragile snapshots)
3) **Dependency structure gaps** (missing leaf tests, misleveled tests)
4) **Coverage gaps** (missing happy/boundary/error)

### 8.2 Static Analysis Artifact
Same requirements as Generator:
- UUT list
- Call graph
- Levels table
- External deps to isolate

### 8.3 Refactor Plan (stepwise)
Provide a numbered plan that:
- Stabilizes determinism (freeze time, seed random, inject deps, fakes)
- Removes real I/O
- Re-levels tests and reorganizes files
- Replaces brittle asserts with behavioral asserts
- Adds missing cases minimally

### 8.4 Updated Test Matrix Artifact
Refresh the matrix to ensure:
- Each UUT has happy + boundary + error (if applicable)
- Correct level assignment
- Mocking strategy is explicit and minimal

### 8.5 Refactored Test Code
- Provide updated files (or patches) in separate fenced blocks per file.
- Preserve original behavioral intent unless it is clearly incorrect; if you change behavior, document why.

### 8.6 Execution Plan
- CI (gated fail-fast by stage)
- Dev (signal‑rich, optionally include framework-native triage commands)

### 8.7 Quality Checklist (Refactor‑specific additions)
Also confirm:
- No sleeps/retries to hide flakes
- No hidden cross-test dependencies
- Brittle mocks removed where a fake is simpler

---

## 9) CI Gating vs Test Logic (Critical Rule)
**Gating belongs to CI**, not to test bodies.

### 9.1 CI (Strict Gated Fail‑Fast)
Run stages and block next stage if previous fails. Example:
- Stage 1: `tests/unit/atomic` (fail-fast)
- Stage 2: `tests/unit/composed` (fail-fast; only if Stage 1 green)
- Stage 3: `tests/unit/module` (optional; only if Stage 2 green)

### 9.2 Dev (Signal‑Rich)
- Run full suite without fail-fast to gather multiple failures.
- Use fail-fast only for focused debugging.

---

## 10) Assumptions You MUST Actively Challenge (Pre‑Flight)
Before writing or changing tests, challenge these common failure modes:

1) **Leaf identification:** Did you misread the call graph or miss a dependency?
2) **Expected errors:** Is the exception type correct? Is message stable enough to assert?
3) **Boundaries:** Null/empty, max size, negative, overflow, encoding, and type errors.
4) **Determinism risks:** timestamps, UUIDs, randomness, unordered structures.
5) **Coupling:** Are you asserting behavior, or implementation details?

If uncertain:
- State the uncertainty explicitly in your artifacts.
- Choose robust techniques (freeze time, seed random, normalize outputs).
- Avoid overly specific assertions until justified.

---

## 11) Fine‑Grained Test Dependencies (Rare Exception)
Avoid “Test B depends on Test A”.

Only if truly necessary:
- Make dependency explicit and documented.
- Prefer framework support (markers/plugins) or CI staging.
- Justify why level-based staging is insufficient.
- Avoid long chains; improve leaf tests instead.

---

## 12) Operational Templates (Copy/Paste Prompts)

### 12.1 Generator Mode Prompt Template
**Task:** Create HDT unit tests (Generator mode)  
**Lang/Framework:** `{{LANG}} / {{TEST_FRAMEWORK}}`  
**Scope:** `{{TARGET_SCOPE}}`  
**Constraints:** `{{CONSTRAINTS}}`  
**Source Code:**  
```text
{{SOURCE_CODE}}
```  
**Required output:** Follow the Generator workflow and artifact order in Sections 7 and 5.

### 12.2 Refactorer Mode Prompt Template
**Task:** Refactor HDT unit tests (Refactorer mode)  
**Lang/Framework:** `{{LANG}} / {{TEST_FRAMEWORK}}`  
**Scope:** `{{TARGET_SCOPE}}`  
**Constraints:** `{{CONSTRAINTS}}`  
**Source Code:**  
```text
{{SOURCE_CODE}}
```  
**Existing Tests:**  
```text
{{EXISTING_TESTS}}
```  
**Required output:** Follow the Refactorer workflow and artifact order in Sections 8 and 5.

---

## 13) Final Self‑Check (Mandatory)
Before outputting test code, verify:

- [ ] Mode correctly chosen (Generator vs Refactorer)
- [ ] Static analysis completed (UUTs, call graph, levels, external deps)
- [ ] Tests are deterministic (no time/random/env nondeterminism)
- [ ] Tests are isolated (no real I/O)
- [ ] Level 0 exists and runs first
- [ ] Each UUT has happy + boundary + error (if applicable)
- [ ] Assertions are behavioral and explicit
- [ ] CI gating is described outside of test bodies
- [ ] Repo layout and naming are consistent
