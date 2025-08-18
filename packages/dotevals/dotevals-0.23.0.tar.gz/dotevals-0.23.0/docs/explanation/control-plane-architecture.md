# Control Plane Architecture

How dotevals separates evaluation orchestration from compute provisioning.

## Control vs Compute

dotevals keeps orchestration simple while letting compute scale through Model Provider plugins. The core of the library is a control plane that orchestrates evaluations, tracks progress, and stores results. The compute plane comes in the form of fixtures or Model Provider plugin and runs model inference, handles GPU resources, and scales as needed.

The control plane stays single-machine. The compute plane can be anything - local, cloud, distributed. This separation is what makes dotevals both simple and scalable.

## How It Works

Your evaluation code stays the same regardless of where compute happens:

```python
@foreach("prompt,expected", dataset)
def eval_accuracy(prompt, expected, model):
    response = model.generate(prompt)  # Could be local, OpenAI, Modal, SageMaker
    return exact_match(response, expected)
```

The model fixture determines where compute happens. Use a local model, compute runs on your machine. Use OpenAI, compute runs on their infrastructure. Use the cloud, it spawns GPU instances on demand. The control plane doesn't know or care - it just sends requests and collects results.

```
┌─────────────────────┐
│  dotevals (local)    │
│                     │
│  Progress tracking  │
│  Result storage     │
│  Concurrency        │
│  Error handling     │
└─────────────────────┘
         │
         ├──────────────┬────────────────┬──────────────┐
         ▼              ▼                ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Local GPU   │ │ OpenAI API  │ │Modal Cloud  │ │ SageMaker   │
│ vLLM server │ │ GPT-4       │ │ A100 fleet  │ │ Auto-scaling│
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

One control plane, many compute backends.

## Why Not Distribute Control?

You might think distributed control would help. It doesn't.

The bottleneck in LLM evaluation is model inference, not sending requests. A single Python process can easily send thousands of concurrent HTTP requests. Adding more control plane instances doesn't make models respond faster.

Distributed control gives you logs scattered across machines, non-deterministic failures, state synchronization problems, and the joy of debugging distributed systems. A single control plane sending 1000 concurrent requests to distributed compute is simpler and just as fast as 10 distributed controllers each sending 100 requests.

When you hit an error, you know exactly where to look. When you need to debug, you set one breakpoint. When you check progress, there's one place to check.

## Scaling Patterns

The scalability comes from how *fixtures* and *Model Provider plugins* handle compute scaling.

We could have chosen to forego Model Provider plugins entirely and let users handle scaling themselves. Just write a fixture that returns a client, done. And that's exactly what you can do if you have custom infrastructure needs.

But there are common patterns - spinning up local vLLM instances, spawning cloud GPU instances, managing connection pools - that get reimplemented over and over. Model Provider plugins capture these patterns once, correctly, and make them available to everyone. The community can contribute new patterns as plugins without waiting for the core framework to change.

## What This Means in Practice

This architecture gives you distributed compute power without distributed system complexity. You can develop on a laptop with a local model, test against OpenAI, then run production evaluations on Modal with 100 GPUs. Same code, different model fixture.

When something goes wrong, you have one log stream to check. When you need to debug, you run the same code locally with the same control flow. When you need to scale, you change the compute backend, not your evaluation logic.

The framework handles orchestration. Plugins handle compute. You focus on what actually matters: defining good evaluations for your AI system.

Evaluation orchestration and compute provisioning are different problems that deserve different solutions. By keeping them separate, both stay simple.
