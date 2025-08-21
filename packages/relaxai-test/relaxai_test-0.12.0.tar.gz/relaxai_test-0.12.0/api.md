# Shared Types

```python
from relaxai.types import OpenAICompletionTokensDetails, OpenAIPromptTokensDetails, OpenAIUsage
```

# Relaxai

Types:

```python
from relaxai.types import HealthResponse
```

Methods:

- <code title="get /v1/health">client.<a href="./src/relaxai/_client.py">health</a>() -> str</code>

# Chat

Types:

```python
from relaxai.types import (
    ChatCompletionMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ContentFilterResults,
    FunctionCall,
    FunctionDefinition,
    StreamOptions,
)
```

Methods:

- <code title="post /v1/chat/completions">client.chat.<a href="./src/relaxai/resources/chat.py">create_completion</a>(\*\*<a href="src/relaxai/types/chat_create_completion_params.py">params</a>) -> <a href="./src/relaxai/types/chat_completion_response.py">ChatCompletionResponse</a></code>

# Embeddings

Types:

```python
from relaxai.types import EmbeddingRequest, EmbeddingResponse
```

Methods:

- <code title="post /v1/embeddings">client.embeddings.<a href="./src/relaxai/resources/embeddings.py">create_embedding</a>(\*\*<a href="src/relaxai/types/embedding_create_embedding_params.py">params</a>) -> <a href="./src/relaxai/types/embedding_response.py">EmbeddingResponse</a></code>

# Models

Types:

```python
from relaxai.types import Model, ModelList
```

Methods:

- <code title="get /v1/models">client.models.<a href="./src/relaxai/resources/models.py">list_models</a>() -> <a href="./src/relaxai/types/model_list.py">ModelList</a></code>
- <code title="get /v1/models/{model}">client.models.<a href="./src/relaxai/resources/models.py">retrieve_model</a>(model) -> <a href="./src/relaxai/types/model.py">Model</a></code>
