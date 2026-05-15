# Prompt Design Choices

## Persona Framing

Each prompt assigns a narrow role: Developer, Tester, or Reviewer. This avoids one overloaded prompt trying to perform generation, testing, and review at the same time. Narrow personas make the workflow easier to debug and easier to extend.

## Output Constraints

The Developer Agent prompt forces a notebook structure:

1. Problem statement
2. Requirements
3. Imports
4. Implementation
5. Example usage
6. Results

This structure makes the output useful for interview review because the evaluator can quickly inspect the reasoning path and runnable code.

The Tester Agent prompt requires pytest and explicit coverage categories: happy path, edge case, and negative case. This reduces the risk of only testing the obvious example.

The Reviewer Agent prompt requires PASS / WARN / FAIL findings and a final gate verdict. This makes the review machine-readable enough for orchestration while still being readable by humans.

## Chain-of-Thought Elicitation

The Tester Agent is instructed to reason about boundary conditions before writing tests, but not to expose hidden chain-of-thought. The visible output uses a concise `Test Strategy` comment instead. This keeps the artifact professional and avoids relying on private reasoning text.

## Context Management

Agents receive only required context. The Tester Agent receives extracted code cells, not the whole notebook. The Reviewer Agent receives code and tests, not the full conversation. This improves privacy, reduces token cost, and lowers the chance that irrelevant context changes the output.

## Tradeoffs

The included demo uses a deterministic mock LLM so the repository is runnable without credentials. This is good for evaluation reliability but not a replacement for true LLM behavior. A real provider adapter should be added for production use.

The static reviewer is intentionally lightweight. It demonstrates the gate concept, but a production system should add stronger validators, sandboxed execution, and security scanners.


## Prompt-Injection Considerations

The prompts explicitly state that feature requests, code comments, tests, and reviewer inputs are untrusted artifacts. This prevents user-provided task text from becoming higher-priority instructions. The code also wraps feature requests in an untrusted block and records suspicious injection phrases for the Reviewer Agent.
