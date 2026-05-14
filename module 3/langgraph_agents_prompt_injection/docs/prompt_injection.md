# Prompt Injection Handling

Prompt injection is relevant in this module because the first input, the feature description, is untrusted text. A malicious task could try to override the agent personas, for example: "ignore previous instructions", "do not write tests", or "approve no matter what".

## Controls Implemented

1. **Untrusted input wrapper**
   - The Developer Agent wraps the feature request in an explicit `<untrusted_feature_request>` block before sending it to the LLM boundary.
   - The wrapper reminds the model that user task text cannot override agent rules.

2. **Pattern-based detection**
   - `validation.py` includes `detect_prompt_injection()` for common injection phrases.
   - This is deterministic and easy to test in a take-home exercise.

3. **Context isolation**
   - Developer receives the feature request and optional reviewer feedback.
   - Tester receives only extracted code cells.
   - Reviewer receives code, tests, and security findings.
   - No agent receives the full conversation history.

4. **Reviewer gate**
   - The Reviewer Agent reports prompt-injection findings as `WARN` items.
   - Security-dangerous code patterns such as `eval`, `exec`, `subprocess`, `os.system`, network calls, and destructive file operations are treated as failures.

5. **Output validation**
   - The workflow uses deterministic validation helpers and tests to enforce basic safety expectations.

## Limitations

The implemented detector is intentionally lightweight. A production version should add:

- stronger policy-based classifiers,
- AST-based static analysis,
- sandboxed execution,
- file-system allowlists,
- secret scanning,
- dependency scanning,
- human approval for high-risk changes.

## Interview Explanation

The main design decision is to treat all task text and generated artifacts as untrusted data. Prompt injection is not solved only by prompt wording; it is handled through layered controls: prompt rules, context isolation, validation, restricted output paths, and a separate Reviewer Agent that acts as the quality gate.
