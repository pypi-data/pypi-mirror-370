# Models Module

Core data types and classes used throughout dotevals.

## Result Class

Return type for evaluation functions. Use this when you need to return multiple scores or metadata alongside your primary evaluation result.

**Usage**: `return Result(primary_score, prompt=prompt, response=response, scores={...})`

::: dotevals.Result

## Data Models

All data models for sessions, experiments, and evaluation results.

::: dotevals.models
