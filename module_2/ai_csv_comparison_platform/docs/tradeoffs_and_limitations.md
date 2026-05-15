# Tradeoffs and Limitations

## Simplifying assumptions

- Demo files are read into memory with pandas.
- The default semantic matcher is deterministic and local. It behaves like a lightweight embedding vector built from normalized tokens, synonyms, and character n-grams.
- Key detection is automatic but not magic. For critical datasets, users should pass `--key-column`.
- Duplicate keys are not deeply reconciled in this demo; the first matching row is used.

## Edge cases

- Two columns can be semantically close but operationally different, such as `account_status` and `loyalty_tier`.
- Numeric values may differ because of formatting, rounding, currency conversion, or units.
- Dates may differ because of timezone or formatting. Production code should normalize date/time types per domain.
- Very wide schemas may need bipartite matching instead of greedy matching.

## Why not hardcode an LLM call?

The exercise values LLM best practices, not uncontrolled dependency on an external service. Prompts are versioned in `prompts/`, and the architecture supports an optional LLM review stage for ambiguous mappings. The default implementation remains deterministic, testable, and runnable offline.
