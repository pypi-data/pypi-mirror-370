# Soika Memory - Long-term Memory for AI Agents

Soika Memory is a comprehensive memory management system that provides long-term memory capabilities for AI agents and applications. It enables storage, retrieval, and semantic search of conversation history and contextual information using vector databases and graph networks.

## Features

### 🧠 Core Memory Management
- **Create memories**: Store conversation messages and context for users, agents, or runs
- **Retrieve memories**: Get all memories with flexible filtering options
- **Search memories**: Semantic search through stored memories using vector similarity
- **Update memories**: Modify existing memories with new information
- **Delete memories**: Remove specific memories or bulk delete with filters

### 🔗 Graph Memory
- **Knowledge Graph**: Extract entities and relationships from conversations
- **Graph Search**: Find related information through entity relationships
- **Multiple Graph Stores**: Support for Neo4j, Memgraph, and AWS Neptune

### 🚀 Multiple LLM Providers
- **OpenAI**: GPT models with structured output support
- **Azure OpenAI**: Enterprise-grade OpenAI integration
- **Anthropic**: Claude models
- **Google Gemini**: Gemini Pro models
- **Groq**: High-speed inference
- **DeepSeek**: Cost-effective models
- **XAI**: Grok models
- **SoikaStack**: Integrated AI framework with multi-model support

### 📊 Vector Store Support
- **Qdrant**: Default vector database
- **Pinecone**: Managed vector database
- **Chroma**: Open-source vector database
- **Weaviate**: Enterprise vector search
- **Google Vertex AI**: Vector search
- **Baidu**: Chinese market support
- **LangChain**: Framework integration

### 🌐 Flexible Deployment
- **REST API**: FastAPI-based server with OpenAPI documentation
- **Python Client**: Sync and async client libraries
- **Proxy Integration**: Memory-enhanced OpenAI API proxy
- **Docker Support**: Container deployment

## Quick Start

### Installation

```bash
pip install ai-memory
```

Or with optional dependencies:

```bash
# With graph support
pip install memory[graph]

# With all vector stores
pip install memory[vector_stores]

# Full installation
pip install memory[graph,vector_stores]
```

### Basic Usage

```python
from memory import Memory

# Initialize memory with SoikaStack provider
m = Memory(
    config={
        "llm": {
            "provider": "soikastack",
            "config": {
                "api_key": "your-soikastack-api-key",
                "model": "llama3.3",
                "base_url": "http://localhost:4141/v1"
            }
        },
        "embedder": {
            "provider": "soikastack", 
            "config": {
                "api_key": "your-soikastack-api-key",
                "model": "bge-m3"
            }
        }
    }
)

# Alternative: Use OpenAI provider
# m = Memory(
#     config={
#         "llm": {
#             "provider": "openai",
#             "config": {
#                 "api_key": "your-openai-api-key",
#                 "model": "gpt-4"
#             }
#         },
#         "embedder": {
#             "provider": "openai", 
#             "config": {
#                 "api_key": "your-openai-api-key",
#                 "model": "text-embedding-3-large"
#             }
#         }
#     }
# )

# Add memories
messages = [
    {"role": "user", "content": "I'm John, a software engineer from San Francisco"},
    {"role": "assistant", "content": "Nice to meet you John!"}
]

result = m.add(messages, user_id="john_doe")
print(result)

# Search memories
search_results = m.search("software engineer", user_id="john_doe")
print(search_results)

# Get all memories
all_memories = m.get_all(filters={"user_id": "john_doe"})
print(all_memories)
```

### REST API Server

Start the memory server:

```bash
cd server
python main.py
```

The API will be available at `http://localhost:8000` with documentation at `/docs`.

#### API Examples

**Create Memory:**
```bash
curl -X POST "http://localhost:8000/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I love pizza"},
      {"role": "assistant", "content": "Great! I will remember that."}
    ],
    "user_id": "user123"
  }'
```

**Search Memories:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "food preferences",
    "user_id": "user123"
  }'
```

**Get All Memories:**
```bash
curl "http://localhost:8000/memories?user_id=user123"
```

## Configuration

Memory supports extensive configuration options:

```python
config = {
    "llm": {
        "provider": "openai",  # openai, azure_openai, anthropic, gemini, etc.
        "config": {
            "api_key": "your-api-key",
            "model": "gpt-4",
            "temperature": 0.1
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": "your-api-key",
            "model": "text-embedding-3-large"
        }
    },
    "vector_store": {
        "provider": "qdrant",  # qdrant, pinecone, chroma, weaviate, etc.
        "config": {
            "host": "localhost",
            "port": 6333
        }
    },
    "graph_store": {
        "provider": "neo4j",  # neo4j, memgraph, neptune
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "password"
        }
    }
}
```

## Advanced Features

### Graph Memory

Enable graph memory to extract and store entity relationships:

```python
# Enable graph memory
m = Memory(config=config, enable_graph=True)

# Add complex information
messages = [
    {"role": "user", "content": "Alice works at Google as a software engineer and lives in Mountain View"}
]

result = m.add(messages, user_id="user123")

# Access extracted relationships
relations = result.get("relations", {})
entities = relations.get("added_entities", [])
```

### Space-based Isolation

Organize memories by workspace or project:

```python
# Add memories to different spaces
m.add(messages, user_id="user123", space_id="project_alpha")
m.add(messages, user_id="user123", space_id="project_beta")

# Search within specific space
results = m.search("query", user_id="user123", space_id="project_alpha")
```

### Async Operations

Use async client for high-performance applications:

```python
from memory import AsyncMemory

async def main():
    m = AsyncMemory(config=config)
    
    # Async operations
    result = await m.add(messages, user_id="user123")
    search_results = await m.search("query", user_id="user123")
    all_memories = await m.get_all(filters={"user_id": "user123"})
```

## Docker Deployment

### Using Docker Compose

```yaml
version: '3.8'
services:
  memory-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=your-openai-api-key
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    depends_on:
      - qdrant
  
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client SDK    │    │   REST API      │    │   Proxy Server  │
│  (Sync/Async)   │    │   (FastAPI)     │    │   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Memory Core    │
                    │   (Engine)      │
                    └─────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   LLM       │    │   Vector    │    │   Graph     │
│ Providers   │    │   Stores    │    │   Stores    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Testing

Run the test suite:

```bash
# Basic functionality test
cd server
python simple_test.py

# Advanced scenarios
python advanced_test.py

# API endpoint testing
python test_endpoints.py

# Space isolation demo
bash final_demo.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Real-time memory synchronization
- [ ] Multi-modal memory support (images)
- [ ] Advanced graph analytics
- [ ] Memory compression and archival
- [ ] Federated memory networks

---

**Memory** - Making AI agents truly intelligent with persistent, searchable, and contextual memory.