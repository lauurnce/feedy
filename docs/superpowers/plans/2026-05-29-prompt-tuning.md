# Prompt Tuning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the existing 2-sentence prompt in `_build_prompt` with a structured 3-sentence prompt that includes an explicit "Why it matters:" developer-impact line.

**Architecture:** Single function change — only `_build_prompt` in `feedy/summarizer.py` is modified. `summarize()` public API and all other behavior stays identical. Two new tests added to verify the new prompt structure.

**Tech Stack:** Python 3.11+ stdlib, pytest, `feedy.summarizer._build_prompt`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `feedy/summarizer.py` | Update `_build_prompt` with structured 3-sentence prompt |
| Modify | `tests/test_summarizer.py` | Add 2 tests for new prompt structure |
| Modify | `ROADMAP.md` | Mark Day 15 complete |

---

### Task 1: Failing tests for new prompt structure

**Files:**
- Modify: `tests/test_summarizer.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/test_summarizer.py`:

```python
def test_summarize_prompt_instructs_why_it_matters():
    entry = {**_ENTRY}
    with patch("feedy.summarizer.complete", return_value="Summary.") as mock_complete:
        summarize([entry])
    prompt = mock_complete.call_args.args[0]
    assert "Why it matters:" in prompt


def test_summarize_prompt_requests_three_sentences():
    entry = {**_ENTRY}
    with patch("feedy.summarizer.complete", return_value="Summary.") as mock_complete:
        summarize([entry])
    prompt = mock_complete.call_args.args[0]
    assert "3 sentences" in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

```
.venv\Scripts\pytest.exe tests/test_summarizer.py -k "why_it_matters or three_sentences" -v
```

Expected:
```
FAILED tests/test_summarizer.py::test_summarize_prompt_instructs_why_it_matters
FAILED tests/test_summarizer.py::test_summarize_prompt_requests_three_sentences
```

- [ ] **Step 3: Commit**

```
git add tests/test_summarizer.py
git commit -m "test(summarizer): add failing tests for tuned prompt structure"
```

---

### Task 2: Update `_build_prompt` in `feedy/summarizer.py`

**Files:**
- Modify: `feedy/summarizer.py`

- [ ] **Step 1: Replace `_build_prompt`**

Replace the existing `_build_prompt` function:

```python
def _build_prompt(entry: FeedEntry) -> str:
    return (
        "Summarize this developer blog post in exactly 2 sentences.\n"
        f"Title: {entry['title']}\n"
        f"URL: {entry['url']}\n"
        f"Source: {entry['source']}\n\n"
        "Focus on what changed or was announced and why it matters to developers."
    )
```

with:

```python
def _build_prompt(entry: FeedEntry) -> str:
    return (
        "Summarize this developer blog post.\n\n"
        f"Title: {entry['title']}\n"
        f"URL: {entry['url']}\n"
        f"Source: {entry['source']}\n\n"
        "Write exactly 3 sentences using this format:\n"
        "Sentence 1: What was announced or changed.\n"
        "Sentence 2: The key technical detail or how it works.\n"
        'Sentence 3: Start with "Why it matters:" followed by the impact for developers.\n\n'
        "Example:\n"
        "Telegram launches Stories API for bots with support for rich media up to 100MB. "
        "Developers can create, schedule, and react to story interactions via a REST endpoint with OAuth scoping. "
        "Why it matters: Bots can now run announcement campaigns and interactive polls previously limited to human accounts."
    )
```

- [ ] **Step 2: Run prompt-structure tests to verify they pass**

```
.venv\Scripts\pytest.exe tests/test_summarizer.py -k "why_it_matters or three_sentences" -v
```

Expected:
```
tests/test_summarizer.py::test_summarize_prompt_instructs_why_it_matters PASSED
tests/test_summarizer.py::test_summarize_prompt_requests_three_sentences PASSED
```

- [ ] **Step 3: Run full summarizer test suite to check for regressions**

```
.venv\Scripts\pytest.exe tests/test_summarizer.py -v
```

Expected: all 8 tests pass (6 existing + 2 new).

- [ ] **Step 4: Run full test suite**

```
.venv\Scripts\pytest.exe -v
```

Expected: all 108 tests pass.

- [ ] **Step 5: Commit**

```
git add feedy/summarizer.py
git commit -m "feat(summarizer): tune prompt for 3-sentence structured output with why-it-matters line"
```

---

### Task 3: Mark Day 15 complete

**Files:**
- Modify: `ROADMAP.md`

- [ ] **Step 1: Update roadmap**

In `ROADMAP.md`, change:

```
- [ ] Day 15 — Prompt tuning: improve summary quality, add "why it matters for devs" line
```

to:

```
- [x] Day 15 — Prompt tuning: improve summary quality, add "why it matters for devs" line
```

- [ ] **Step 2: Commit**

```
git add ROADMAP.md
git commit -m "chore: mark Day 15 complete"
```
