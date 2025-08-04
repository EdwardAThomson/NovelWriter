# Don't Build Chatbots — Build Agents With Jobs

**Author:** Sean Falconer  
**Published:** July 7th, 2025 8:00am  
**Source:** [The New Stack](https://thenewstack.io/dont-build-chatbots-build-agents-with-jobs/)

---

LLMs are most effective when they're scoped, structured and grounded in clear context. Predictability is what makes AI reliable at scale. If you want AI that delivers real results, design for control and purpose, not open-ended freedom.

The promise of AI agents is compelling: autonomous systems that can reason, plan and execute complex workflows without constant human oversight. But most agent implementations today are essentially expensive chatbots with access to APIs. They're built for open-ended conversation rather than focused execution, and they fail when deployed in production environments that demand reliability and measurable outcomes.

The difference isn't technical — it's architectural. Instead of building agents that can do anything, build agents with specific jobs. Focus on closed-world problems where success is defined by clear criteria, and design your agent architecture around purpose-built tools and workflows rather than general-purpose reasoning.

## Focus on Closed-World Problems

The key to reliable AI systems is choosing problems where you can define clear boundaries, success criteria and constraints. Open-world problems — like "help me plan my vacation" or "analyze this document" — have infinite solution spaces and vague success criteria. Closed-world problems have defined parameters, clear inputs and outputs, and measurable criteria for success. Think about things like:

* Processing an insurance claim
* Troubleshooting an IT ticket
* Onboarding a new customer or employee

These are bounded tasks with rules, constraints and measurable outcomes. That's what makes them suitable for LLM-based systems, not just because they're easier to automate, but because they're easier to trust.

It's no coincidence that code generation has been one of the most successful LLM use cases so far. The inputs are clear, the outputs are testable and correctness is verifiable. You can run the code. That same pattern, clear expectations and tight feedback loops are exactly what make closed-world business use cases viable.

When you focus on closed-world problems, you get:

* **Better testability:** You can write test cases and know what a good response looks like.
* **More explainability:** It's easier to debug or audit the system when things go wrong.
* **Tighter guardrails:** You can limit what the AI is allowed to see, say or do.

The more you can reduce ambiguity, the more reliable your AI systems become. It's all about designing with intent. Solve problems where the path is clear, the scope is defined and the stakes are known. Add as much determinism to the inherently nondeterministic process as you can. That's how you build AI that delivers results instead of surprises.

## Purpose-Built Agents, Not General Chatbots

Once you've narrowed the problem space, the next step is to break it down.

Trying to build a single, all-knowing AI that handles everything from customer service to sales forecasting is a fast track to complexity and chaos. Instead, treat AI like software: modular, composable and scoped to specific jobs.

That's where purpose-built agents come in.

A purpose-built agent is an AI system with a clearly defined responsibility, like triaging support tickets, monitoring system logs or generating weekly sales reports. Each agent is optimized to do one thing well.

And just like in software, the power comes from composition.

Take a closed-world problem like processing an insurance claim. It's not just one step. It's a series of structured, interconnected tasks: validating inputs, checking eligibility, fetching relevant policy details, summarizing the case and escalating exceptions. Instead of building one monolithic agent to handle all of it, you can design atomic agents, each handling a specific piece, and orchestrate them into a multiagent system.

This kind of decomposition makes your AI systems more reliable, more secure and easier to evolve. And just like with software microservices, the magic happens not just within each agent but in the way they work together.

## Build Tools for LLMs, Not People

Once you've broken down your system into purpose-built agents, the next step is giving them the right tools, just like you would for any team.

With LLMs, they rely entirely on what you expose them to and how well it's described. So if you want your agents to behave predictably, your tools need to be designed with that in mind.

And it's not just a matter of exposing your existing API endpoints. A generic tool, like an open-ended SQL interface to your production database, might seem powerful, but it's incredibly hard for an LLM to use safely.

Imagine what it takes for an agent to write a query with a generic SQL tool:

1. Ask for the schema.
2. Parse a large, potentially messy schema response.
3. Infer the right table to use.
4. Guess at the necessary joins across related tables.
5. Construct the correct SELECT statement.
6. Try to decide how much data to return.
7. Format the result in a useful way.
8. Handle edge cases or ambiguous fields.

Each of those steps introduces risks like wrong assumptions, incomplete context, ambiguous naming and high potential for hallucination. Worse, if the query fails, most agent frameworks will retry the entire sequence, often with slight prompt tweaks. That leads to token bloat, cascading retries and increased cost without improving the result.

You end up with all the downsides of open-world problems: unclear intent, wide decision space, unpredictable behavior. Like agents, tools should be purpose-built. They should be designed specifically to help the agent solve a well-scoped task. Think "fetch today's unshipped orders" instead of "run any query you want."

The more you reduce ambiguity, the more reliably the model can get the job done.

That means building tools that are:

* **Strongly typed:** No ambiguity in what goes in or what comes out.
* **Constrained:** Small, focused tools are easier for agents to reason about and harder to misuse.
* **Self-describing:** Tools should include metadata, examples and descriptions to help the model know when and how to use them.
* **Access-controlled:** Just like with users, not every agent should have access to every tool. Scope matters.

This is where protocols like the Model Context Protocol (MCP) come in. MCP helps standardize the way tools are defined and described so agents can reason about them more effectively. If you do this right, you're giving LLMs the right context to use tools safely and correctly.

When you design tools correctly, you can force reliability. The model stops improvising and starts operating more like software should: with clear rules, defined behavior and predictable outcomes.

## Governance, Testing and the Need for AI Testers

In traditional software, testing is about whether the output is correct. With AI agents, that's just the beginning. You also need to test how the agent discovers tools, how it decides to use them and whether it uses them correctly.

That means spending real time on evaluations.

If you've built your agents and tools to be purpose-built and scoped, then writing good evals should be straightforward. You know the inputs, you know the expected outputs, and you can run consistent checks across edge cases and common workflows. This isn't something you can just eyeball. You need repeatable, deterministic tests, just like any other production system.

And for many use cases, human-in-the-loop should be part of the system. You should think through what can be fully autonomous and what requires human oversight. You may need people involved for escalation, validation and learning. Let AI handle the routine, predictable tasks, and let humans step in when things get messy.

## Control Is a Feature, Not a Limitation

LLMs are most effective when they're scoped, structured and grounded in clear context. Predictability is what makes AI reliable at scale. If you want AI that delivers real results, design for control and purpose, not open-ended freedom.

---

*Sean Falconer is an AI Entrepreneur in Residence at Confluent where he works on AI strategy and thought leadership. Sean's been an academic, startup founder and Googler. He has published works covering a wide range of topics from AI to technology entrepreneurship.*

*Confluent sponsored this post.* 