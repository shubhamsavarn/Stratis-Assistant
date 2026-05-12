# 🏗️ System Architecture: InsightFlow AI

This document provides a detailed technical overview of the InsightFlow AI platform, focusing on the data flow, component interactions, and the "Secure AI" orchestration layer.

---

## 1. High-Level System Architecture (HLD)

The system is designed as a secure, decoupled micro-architecture where the AI model is isolated within a local boundary to ensure zero data leakage.

```mermaid
graph TD
    %% User Layer
    User((User/Analyst)) -->|HTTPS / X-API-KEY| Frontend[React Dashboard]

    %% Frontend Layer
    subgraph "Frontend Layer (Vite + React)"
        Frontend -->|API Requests| API_Client[Axios Service]
        UI_Dash[Recharts Visualization] --- Frontend
    end

    %% Security & Gateway Layer
    subgraph "Backend Gateway (FastAPI)"
        API_Client -->|POST /query| Router_Endpoint[Main Router]
        Router_Endpoint -->|Auth Check| Security[Security Gateway]
    end

    %% Agentic Intelligence Layer
    subgraph "AI Intelligence (Local Inference)"
        Security -->|Validated Query| Agent[Robust Agent Engine]
        Agent -->|Keyword Routing| LLM_Orch{Ollama: Qwen2.5}
    end

    %% Data Orchestration Layer
    subgraph "Trusted Data Sources"
        Agent -->|SQL Tool| SQL_Store[(SQLite: Structured Data)]
        Agent -->|RAG Tool| Chroma_Store[(ChromaDB: Vector Context)]
    end

    %% Response Flow
    SQL_Store -->|JSON Records| Agent
    Chroma_Store -->|Text Chunks| Agent
    Agent -->|Synthesis| Router_Endpoint
    Router_Endpoint -->|Typed Response| Frontend

    %% Styling
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style LLM_Orch fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:3px
    style SQL_Store fill:#2ecc71,stroke:#27ae60
    style Chroma_Store fill:#e67e22,stroke:#d35400
```

---

## 2. Intelligence Logic & Routing Flow

InsightFlow uses a **Deterministic Routing Engine** to minimize hallucinations and ensure that the most accurate data source is selected for every user query.

```mermaid
graph LR
    A[User Query] --> B{Intelligence Router}
    
    %% SQL Path
    B -->|Keywords: Revenue, Top, Best, Vs| C[SQL Generation Tool]
    C --> D[(SQLite: movies.csv)]
    D --> E[Data Transformation]
    
    %% RAG Path
    B -->|Keywords: Why, Strategy, Roadmap, Policy| F[Vector RAG Tool]
    F --> G[(ChromaDB: internal_reports)]
    G --> H[Context Extraction]
    
    %% Synthesis
    E --> I[LLM Synthesis & Synthesis]
    H --> I
    I --> J[Final Answer + Source Trace]

    style B fill:#f1c40f,stroke:#f39c12
    style I fill:#3498db,color:#fff
```

---

## 3. Data Ingestion Pipeline (ETL)

The ingestion pipeline transforms raw business assets into queryable intelligence stores.

```mermaid
flowchart TD
    subgraph "Source Assets"
        CSV[Raw CSV Data]
        PDF[Internal TXT/PDF Reports]
    end

    subgraph "ETL Process (ingest.py)"
        P1[Pandas Transformer]
        P2[Text Chunker]
        P3[SentenceTransformer Embeddings]
    end

    CSV --> P1
    P1 -->|Table Mapping| SQLite[(SQLite DB)]

    PDF --> P2
    P2 --> P3
    P3 -->|Vector Indexing| Chroma[(ChromaDB)]

    style SQLite fill:#2ecc71
    style Chroma fill:#e67e22
```

---

## 4. Security Framework
1.  **Isolation**: The LLM (Ollama) runs entirely on the host machine; no data is transmitted to external endpoints.
2.  **Tool-Based Access**: The LLM never writes directly to the database. It only generates queries that are executed by a validated Python wrapper.
3.  **Audit Trail**: Every interaction is logged with the specific "Tool" used, ensuring transparency in AI decision-making.
