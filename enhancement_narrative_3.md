# Enhancement Narrative 3

## 1. Artifact Description

**Artifact:** Enhanced Stock Market Backtesting Engine

**What is it?**
This artifact is a Python-based backtesting engine for historical equity data that now includes structured logging, a YAML configuration framework, input validation, multiple position sizing strategies, risk management logic, and database resilience.

**When was it created?**
The latest enhancement was completed in June 2026 as part of the capstone project work on this repository.

## 2. Justification for Inclusion

I chose this artifact because it captures the transition from a basic proof-of-concept backtester to a professional-quality software system. The enhancements are not just feature additions; they embody key software engineering practices:

- **Structured logging** replaces ad hoc output and supports audit trails, debugging, and operational visibility.
- **Configuration management** centralizes all parameters in YAML files, which allows the system to run multiple experiments without code changes.
- **Input validation and type hints** make the code more robust, maintainable, and self-documenting.
- **Performance metrics** turn raw trade results into actionable analytics.
- **Database resilience and pooling** make the system suitable for repeated runs and larger datasets.

These improvements demonstrate my ability to build systems that are maintainable, configurable, and production-ready, which is why this artifact is appropriate for the ePortfolio.

## 3. Course Outcomes Reflection

### Planned outcomes
The enhancements were intended to address these course outcomes:

- **Course Outcome 1:** Apply software design principles through strategy abstraction and modular architecture.
- **Course Outcome 2:** Build professional-quality applications with logging, configuration, and defensive programming.
- **Course Outcome 3:** Implement complex algorithmic logic and performance measurement in a real system.
- **Course Outcome 4:** Design scalable data storage and database access patterns.
- **Course Outcome 5:** Communicate technical work clearly through documentation and narrative.

### Outcome coverage updates
The artifact now supports these outcomes even more strongly than planned:

- The strategy and position sizing modules now demonstrate polymorphism, clean interfaces, and extensibility.
- The configuration layer shows professional separation of code and data.
- The logging and validation improvements support software quality and operational reliability.
- The database module provides connection pooling and schema migration logic, which strengthens the application’s scalability.
- The documentation and narrative are designed to communicate the implementation and the learning process.

## 4. Reflection on the Process

### What I learned

Working on this enhancement taught me the value of building systems that are easy to change. Moving configuration out of code made the engine far more flexible, which is especially important in backtesting where parameter sweeps are common.

I also learned that professional engineering is not just about writing code that works. It is about writing code that other people can understand, or that I can revisit months later and still make sense of. The logging upgrade and the YAML configuration framework both contribute heavily to that.

### Challenges faced

The most significant challenge was balancing mathematical correctness with practical robustness. For example, the Kelly criterion is mathematically elegant, but using a full Kelly allocation is too aggressive for most trading scenarios. Learning to include a fractional Kelly option showed me how engineering judgement complements theory.

Another challenge was database compatibility. I had to design schema initialization and migration logic that works for both new tables and older deployments, which required careful handling of `ALTER TABLE` operations and index creation.

### Process insights

- I found it useful to make one improvement at a time and verify it with tests.
- Writing the narrative helped me step back from the code and identify what I actually learned versus what I simply implemented.
- The project became more rewarding when I shifted focus from "adding features" to "improving the system’s architecture and reliability."

## Final Thoughts

This artifact is included in my ePortfolio because it represents a meaningful step toward building a real engineering-grade system. It is not just a trading model—it is a software product with configuration, logging, validation, metrics, and storage.

Those qualities make it a strong example of my growth in both software development and systems thinking.
