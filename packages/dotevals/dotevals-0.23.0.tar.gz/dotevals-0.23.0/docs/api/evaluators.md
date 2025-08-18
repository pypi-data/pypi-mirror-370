# Evaluators Module

Built-in evaluators and decorators for creating custom evaluators.

## Built-in Evaluators

Ready-to-use evaluators for common evaluation tasks. These functions can be used directly in your evaluations or as building blocks for custom evaluators.

### exact_match

The most commonly used evaluator for exact string comparisons.

::: dotevals.evaluators.base.exact_match

### numeric_match

Compare numeric values with optional tolerance, handling various formats like commas, spaces, and scientific notation.

::: dotevals.evaluators.base.numeric_match

### valid_json

Validate if response is valid JSON and optionally matches a schema.

::: dotevals.evaluators.base.valid_json

### All Evaluators

::: dotevals.evaluators
    options:
      filters:
        - "!evaluator"
        - "!get_metadata"

## @evaluator Decorator

Create custom evaluators with automatic metric computation and result aggregation.

**Usage**: `@evaluator(metrics=[accuracy(), mean()])`

::: dotevals.evaluators.base.evaluator

## Helper Functions

### get_metadata

Extract metadata from evaluator functions.

::: dotevals.evaluators.base.get_metadata
