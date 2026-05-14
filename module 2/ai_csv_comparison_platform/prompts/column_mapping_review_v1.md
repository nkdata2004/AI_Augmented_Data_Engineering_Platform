# Prompt: Column Mapping Human Review v1

You are reviewing proposed column mappings between two CSV files.

Input JSON contains:
- source_column
- target_column
- levenshtein score
- embedding score
- heuristic score
- final confidence
- sample source values
- sample target values

Task:
1. Decide whether the proposed mapping is valid.
2. Return strict JSON only.
3. Do not invent columns that are not present.
4. Flag ambiguous mappings for human review instead of guessing.

Output schema:
```json
{
  "is_valid_mapping": true,
  "confidence_adjustment": 0.0,
  "reason": "short explanation",
  "needs_human_review": false
}
```

Few-shot example:
Input: cust_id -> CustomerID, high overlap in integer values
Output: {"is_valid_mapping": true, "confidence_adjustment": 0.05, "reason": "Both columns represent customer identifiers and values overlap.", "needs_human_review": false}

Input: status -> loyalty_tier, low semantic overlap, different value distribution
Output: {"is_valid_mapping": false, "confidence_adjustment": -0.25, "reason": "Account status and loyalty tier are different business concepts.", "needs_human_review": true}
```
