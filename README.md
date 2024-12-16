# github-repo-searcher
DoD: Развернуто локальное решение с простым frontend. Система должна позволять загрузить ссылку на GitHub-репозиторий, по которому в дальнейшем можно будет задавать вопросы по коду

```mermaid
flowchart TD
    A[Clone GitHub Repository] --> B[Read data]
    B --> C[Chunk data]
    C --> D[Embedding Model]
    D -->|Ingestion| E[Elasticsearch Vector Database]
    E -->|Query| D
    E -->|Context/Prompt| F[LLM]
    F --> G[Answer the question]
    G -->D
```
