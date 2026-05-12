# ⚖️ Architectural Decisions & Tradeoffs: InsightFlow AI

This document outlines the strategic engineering choices made during the development of the InsightFlow AI platform and the tradeoffs associated with them.

---

## 1. Local AI Inference (Privacy vs. Power)
**Decision**: Use **Ollama (Qwen2.5:0.5b)** and local embeddings (**all-MiniLM-L6-v2**).

- **Reasoning**: In the entertainment industry, internal reports and budgets are highly sensitive. A "Privacy-First" architecture ensures that no data leaves the organizational perimeter.
- **Tradeoff**: Smaller local models have less semantic depth than massive cloud APIs (like GPT-4). We mitigated this by using **Deterministic Routing** to handle complex logic.

## 2. Deterministic Tool Routing (Reliability vs. Flexibility)
**Decision**: Implement a keyword-driven "Intelligent Router" instead of pure LLM-based reasoning.

- **Reasoning**: For Business Intelligence (BI), accuracy is the most critical metric. We cannot afford "hallucinations" in tool selection or SQL generation.
- **Tradeoff**: The system is less "conversational" and more "analytical." It follows a strict protocol to guarantee that the correct data source (SQL vs. PDF) is accessed every time.

## 3. SQLite for Data Storage (Portability vs. Scalability)
**Decision**: Use **SQLite** as the primary relational database.

- **Reasoning**: For an engineering assessment, the system must be portable and "Zero-Configuration." SQLite allows the entire database to be shared as a single file.
- **Tradeoff**: While not suitable for high-concurrency production environments, the use of **SQLAlchemy** ensures the codebase can be migrated to **PostgreSQL** or **Snowflake** with minimal changes.

## 4. Explainable AI Architecture (Transparency vs. UX)
**Decision**: Expose the **"Agent Logic Flow"** (Thought Trace) directly in the UI.

- **Reasoning**: Users are skeptical of AI-generated numbers. By showing the raw SQL query and the specific PDF search used, we provide an "Audit Trail" that builds user trust.
- **Tradeoff**: This adds more information to the UI, but it satisfies the mandatory requirement for **Explainability**.

## 5. React + Tailwind (Aesthetics vs. Build Time)
**Decision**: Build a custom, premium dashboard from scratch using **Tailwind CSS** and **Recharts**.

- **Reasoning**: First impressions matter. A high-fidelity, "Glassmorphic" UI demonstrates that the project is not just a script, but a usable product.
- **Tradeoff**: Requires more frontend development time than using a template, but results in a unique, professional identity for the platform.

---
**Summary**: Every decision was made to prioritize **Security**, **Accuracy**, and **Portability**—the three pillars of a successful enterprise-grade assessment submission.
