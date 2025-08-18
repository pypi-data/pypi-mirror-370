# Design Principles

## Evaluations Are Tests for AI Systems

Building AI systems is building software. You test your code; you should test your AI systems.

Many frameworks offer YAML configurations for "simplicity". But YAML breaks down quickly when you need RAG pipelines, structured generation, tool use, or multi-step reasoning - which is most production AI systems.

Other frameworks go the opposite direction with complex DSLs and orchestration layers. You end up fighting the framework instead of solving your problem.

We chose Python and pytest. Evaluations are just tests:

```python
# Simple case
@foreach("text,expected", dataset)
def eval_sentiment(text, expected):
    prediction = model.classify(text)
    return exact_match(prediction, expected)

# Real system with RAG
@foreach("query,expected", dataset)
def eval_rag_system(query, expected):
    docs = retriever.search(query)
    context = reranker.rerank(docs, query)
    response = generator.generate(query, context)

    return Result(
        exact_match(response, expected),
        prompt=query,
        metadata={"docs_retrieved": len(docs)}
    )
```

The execution is complex - managing API calls, handling failures, tracking progress. The declaration stays simple. No new DSL to learn, no YAML limitations to work around. Just Python functions that test your AI system.

## Why pytest?

We don't use pytest to be clever. We use it because it solves the exact problems evaluations have:

- **Discovery** - pytest's discovery mechanism finds and runs evaluations across files and directories. No manifest files, no registration, no boilerplate.
- **Fixtures** - Model clients, database connections, and other resources are naturally shared through fixtures. The pattern proven for test resources works perfectly for evaluation resources.
- **Parametrization** - Running the same evaluation with different models or parameters? pytest parametrization handles it.
- **Plugins** - Thousands of pytest plugins for reporting, parallelization, and CI/CD integration work out of the box.
- **Debugging** - Set breakpoints, use --pdb, filter specific evaluations. Standard Python debugging just works.

Your evaluations integrate with existing test infrastructure. No new CI/CD pipelines, no new monitoring, no new workflows. The test runner you already use becomes your evaluation runner.

This comes with a tradeoff. To run evaluations concurrently, we had to reimplement pytest's fixture lifecycle. pytest runs tests sequentially by design; we need concurrent execution for API-heavy evaluations. So we built our own fixture handling that works with async evaluation loops. It's extra complexity in our codebase, and its weakest point. But we came to the conclusion that the alternative, not using pytest at all, would be worse. The convenience of pytest's ecosystem is worth the implementation cost.

## Everything is a Plugin

dotevals has a small core and everything else is a plugin:

- **Evaluators** - Plugin for custom scoring functions
- **Metrics** - Plugin for custom aggregations
- **Storage** - Plugin for where results go (JSON, SQLite, PostgreSQL)
- **Datasets** - Plugin for data sources (HuggingFace, custom formats)
- **Model Providers** - Plugin for model clients (OpenAI, Anthropic, vLLM)

The plugin system uses standard Python entry points - no custom registry or framework-specific patterns. You can replace any part without breaking the others.

Why plugins instead of expanding the core? Every team has different infrastructure. Some use OpenAI, others use self-hosted models. Some store in S3, others in PostgreSQL. Some need custom metrics specific to their domain. Adding all these to the core would create a bloated library with dependencies you don't need. With plugins the package stays lean, your dependencies minimal.

More importantly, the community can build what they need without waiting for maintainers. Need a Snowflake storage backend? Write it. Need domain-specific evaluators for medical text? Ship them. The ecosystem grows without bottlenecks.

This matters for production use. We've seen too many teams fork evaluation libraries just to add their internal storage system or custom metrics. Forks diverge, maintenance becomes a nightmare, updates get missed. With plugins, you extend without forking. Your custom code stays separate, the core stays updatable.

## Resumability by Default

Evaluations get interrupted. Rate limits hit. APIs timeout. Connections drop. Your laptop goes to sleep.

Most frameworks treat this as exceptional. You lose progress, restart from scratch, waste time and API credits.

dotevals makes every evaluation resumable by default. No special mode, no configuration flag. Run your evaluation, get interrupted at sample 8,543, run the same command again - it picks up at 8,544.

This isn't an optimization. It's acknowledging reality: long-running evaluations against production APIs will get interrupted. The framework should handle it, not you.
