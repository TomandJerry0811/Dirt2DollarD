# Run the 189 listed cases through Playwright

This patch adds one normal Playwright test for every spreadsheet ID, TC01 through
TC189, grouped by the 16 feature names. It applies on top of the Full50 project.
The original 40 frontend and 10 controlled-backend scenarios remain unchanged.
There are now 239 registered scenarios across the three configurations.

## Windows PowerShell setup

From the project root, reuse the existing controlled-test environment:

```powershell
.\.venv-playwright\Scripts\python.exe -m pip install -r requirements-playwright.txt
cd frontend
$env:PLAYWRIGHT_PYTHON = (Resolve-Path "..\.venv-playwright\Scripts\python.exe").Path
npm run test:e2e:typecheck
npm run test:nodes:ui
```

If the Python environment does not exist, create it from the project root first:

```powershell
python -m venv .venv-playwright
```

The new suite needs the existing frontend npm dependencies (`npm ci` if they are
not installed). No new npm dependency, browser installation, Vite/FastAPI server,
model download, service credential, or live database is needed for these 189 cases.

In UI Mode, expand a feature and select an ID such as `TC35`. Its steps show the
source expectation and fixture, actual Python-node execution, and assertions.
The browser preview can be empty: these are backend contracts, not browser clicks.
The `sheet-case-and-fixtures` and `actual-node-output` JSON attachments explain
the inputs, provider/repository calls, node outputs, and original exception type.

## Commands

```powershell
npm run test:nodes
npm run test:nodes:ui
npm run test:nodes:report
npm run test:nodes -- --grep "TC35"
npm run test:complete
```

`test:complete` runs the existing frontend/integration suites, then these node
contracts. Each suite exits nonzero on an unexpected failure; it does not silently
continue or relabel failures. The existing `test:all` still runs the original 50.
Close UI Mode with Ctrl+C before another run of the same suite so their output
directories do not collide. New evidence is written to ignored directories
`frontend/test-results-nodes` and `frontend/playwright-report-nodes`.

## How it works

1. `tests/playwright_node_cases.json` preserves all eight original sheet columns
   and supplies explicit fixtures and independently specified assertions per ID.
2. `frontend/e2e/node-contracts/listed-cases.spec.ts` registers those 189 tests.
   `playwright.nodes.config.ts` selects only this suite and starts no web servers.
3. Each test uses `execFile` (not a shell command) to run the selected Python case
   with `python -m tests.playwright_nodes TC35`, from the project root. Interpreter
   paths containing spaces are supported through PLAYWRIGHT_PYTHON.
4. The CLI adapter constructs the real allowlisted node and invokes its real
   `execute`, `validate`, `process`, prompt, parser, and calculation methods.
   Only external provider/repository constructors are replaced by strict recorded
   dependencies. Application methods and observed outputs are never mocked.
5. Calls, context fields, error class/message and lifecycle status return as JSON.
   Playwright performs the assertions. Every invocation has a fresh process and
   outbound socket connections are disabled. Unconfigured dependency calls fail.

This adapter is CLI-only. It adds no FastAPI route and never changes src.main.
No production source file is modified by this patch. Python setup/protocol errors
are distinct from expected node exceptions and cannot count as a passing case.

## Source contract and assumptions

Source: https://docs.google.com/spreadsheets/d/1k_IIwfYcFEGcCsAd93Kmlt7EfEDVQoenvKQlXAthTe8/edit

The manifest uses the 2026-10-19 snapshot: 189 rows, originally 181 Pass and 8 Fail.
Those historical sheet results are retained as source data and are not assertions
or expected-failure flags. All 189 tests run normally, with no skip/fixme/test.fail.
The result is measured against the sheet's Expected Result, not Actual Result.

The sheet is not a complete machine-readable fixture specification. Assumptions
are exposed in each case's input and fixture_note rather than being hidden:

- TC37/38/49 use campaign weights 0.6 updates and 0.4 KPI. TC39/40/42 use 0.5/0.5.
  The sheet omits the stage/weight records; these are controlled fixture choices,
  not assertions about the live campaign configuration. Unknown campaign status
  is also supplied as program_stage because the current node looks up that field.
- TC49 retains expected 60.0 exactly. A result of 59.99 is a visible disagreement,
  not rounded away by a tolerant assertion. The expected rounding needs review.
- Summary-batch cases use a configurable 1500-character batch limit and explicit
  updates: twelve 240-character bodies fit into three batches of four. The actual
  batching algorithm and format_update method are not patched.
- TC111/112 supply separate zero lead/appointment counts with improving, nonzero
  costs. Current code detects zero cost instead of these activity counts. The
  sheet's intended metric semantics need review before changing either contract.
- TC109 returns a deliberately unrelated High Risk AI interpretation for missing
  KPIs, reproducing the listed failure condition. This checks how the node handles
  that controlled response; it is not a claim about live model accuracy.
- Embedding vectors and provider JSON are fixtures, as expected for unit-level
  contracts. The real node still builds content, extracts vectors, validates JSON,
  updates context and chooses save/update operations. Network providers and
  repository internals themselves are outside this node suite's scope.
- When the sheet explicitly requires ValueError or RuntimeError, the test keeps
  that exact class. Current ValidationException/ServiceException wrappers may
  therefore fail even if the error message and validation behaviour are correct.
  Such failures require contract review, not automatic removal of error handling.

See LISTED_NODE_TEST_RESULTS.md for the measured results and all failing IDs.
The original five pending UI scenarios are unaffected by this new suite.
