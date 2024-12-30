# github-repo-searcher
**DoD**: Развернуто локальное решение с простым frontend. Система должна позволять загрузить ссылку на GitHub-репозиторий, по которому в дальнейшем можно будет задавать вопросы по коду

### Схема работы
```mermaid
flowchart TD
    A[Clone GitHub Repository] --> B[Read data]
    B --> C[Chunk data]
    C --> D[Embedding Model]
    D -->|Ingestion| E[Elasticsearch Vector Database]
    E -->|Query| D
    E -->|Context/Prompt| F[LLM]
    F --> G[Answer the question]
    G -->|Query| D
```

### Запуск и тестирование

Система работает как расширение vscode. Чтобы его запустить, склонируйте репозиторий и откройте его в VS Code.
Далее в терминале

```
npm install
npm run compile
```

Затем,

```
ctrl+shift+p
Debug: Start debugging
```

После этого откроется новое окно VS Code. Это окно, в котором работает расширение. В новом окне откройте git репозиторий.

```
ctrl+shift+p
Open chat
```

