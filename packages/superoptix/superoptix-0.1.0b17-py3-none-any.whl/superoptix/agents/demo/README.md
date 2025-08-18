# SuperOptiX Demo Agents

This directory contains comprehensive demo agents that showcase all the major features and capabilities of the SuperOptiX framework. Each demo agent is designed to demonstrate specific aspects of the framework and help users understand how to leverage different features.

## 🚀 Available Demo Agents

### 🤖 **Model Backend Demos**

#### 1. **MLX Demo** (`mlx_demo_playbook.yaml`)
- **Purpose**: Demonstrates MLX local model capabilities
- **Features**: Code assistance, concept explanation, problem solving
- **Model**: `mlx-community/Llama-3.2-3B-Instruct-4bit`
- **Pull Command**: `super agent pull mlx-demo`
- **Use Case**: Local development with Apple Silicon optimization

#### 2. **Ollama Demo** (`ollama_demo_playbook.yaml`)
- **Purpose**: Demonstrates Ollama local model capabilities
- **Features**: Creative writing, conversation, knowledge assistance
- **Model**: `llama3.2:3b`
- **Pull Command**: `super agent pull ollama-demo`
- **Use Case**: Local development with easy model management

#### 3. **HuggingFace Demo** (`huggingface_demo_playbook.yaml`)
- **Purpose**: Demonstrates HuggingFace model capabilities
- **Features**: Text generation, language understanding, NLP tasks
- **Model**: `microsoft/Phi-4`
- **Pull Command**: `super agent pull huggingface-demo`
- **Use Case**: Advanced NLP and transformer model usage

#### 4. **LM Studio Demo** (`lmstudio_demo_playbook.yaml`)
- **Purpose**: Demonstrates LM Studio local model capabilities
- **Features**: Logical reasoning, data analysis, research assistance
- **Model**: `llama3.2:3b`
- **Pull Command**: `super agent pull lmstudio-demo`
- **Use Case**: Local development with GUI model management

### 🔍 **RAG (Retrieval-Augmented Generation) Demos**

#### 5. **RAG ChromaDB Demo** (`rag_chroma_demo_playbook.yaml`)
- **Purpose**: Demonstrates RAG capabilities with ChromaDB
- **Features**: Knowledge retrieval, document analysis, semantic search
- **Vector DB**: ChromaDB (default, lightweight)
- **Pull Command**: `super agent pull rag-chroma-demo`
- **Use Case**: Development and small to medium datasets

#### 6. **RAG LanceDB Demo** (`rag_lancedb_demo_playbook.yaml`)
- **Purpose**: Demonstrates high-performance RAG with LanceDB
- **Features**: High-speed retrieval, large-scale analysis, Apache Arrow integration
- **Vector DB**: LanceDB (high performance)
- **Pull Command**: `super agent pull rag-lancedb-demo`
- **Use Case**: Production applications with large datasets

### 🛠️ **Framework Feature Demos**

#### 7. **Tools Demo** (`tools_demo_playbook.yaml`)
- **Purpose**: Demonstrates comprehensive tool ecosystem
- **Features**: Core tools, development tools, industry-specific tools
- **Tool Categories**: 20+ categories including finance, healthcare, education
- **Pull Command**: `super agent pull tools-demo`
- **Use Case**: Understanding the complete tool ecosystem

#### 8. **Memory Demo** (`memory_demo_playbook.yaml`)
- **Purpose**: Demonstrates multi-layered memory system
- **Features**: Short-term, long-term, and episodic memory
- **Memory Types**: Context retention, persistent storage, episode recall
- **Pull Command**: `super agent pull memory-demo`
- **Use Case**: Building agents with persistent memory

#### 9. **Observability Demo** (`observability_demo_playbook.yaml`)
- **Purpose**: Demonstrates monitoring and debugging capabilities
- **Features**: Tracing, monitoring, debugging, analytics
- **Observability**: Performance metrics, error tracking, dashboard
- **Pull Command**: `super agent pull observability-demo`
- **Use Case**: Production monitoring and debugging

## 📋 **Quick Start Guide**

### 1. **Setup Your Environment**

```bash
# Initialize a new SuperOptiX project
super init my_demo_project
cd my_demo_project

# Install dependencies
pip install -e .
```

### 2. **Choose Your Model Backend**

#### For MLX (Apple Silicon):
```bash
# Install MLX
pip install mlx

# Start MLX server
super model server mlx mlx-community/Llama-3.2-3B-Instruct-4bit --port 8000

# Pull and run MLX demo
super agent pull mlx-demo
super agent compile mlx-demo
super agent run mlx-demo --goal "Explain recursion with examples"
```

#### For Ollama:
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.2:3b

# Pull and run Ollama demo
super agent pull ollama-demo
super agent compile ollama-demo
super agent run ollama-demo --goal "Write a creative story about AI"
```

#### For HuggingFace:
```bash
# Start HuggingFace server
super model server huggingface microsoft/Phi-4 --port 8001

# Pull and run HuggingFace demo
super agent pull huggingface-demo
super agent compile huggingface-demo
super agent run huggingface-demo --goal "Explain transformers architecture"
```

### 3. **Explore RAG Capabilities**

```bash
# Pull RAG demo with ChromaDB
super agent pull rag-chroma-demo
super agent compile rag-chroma-demo
super agent run rag-chroma-demo --goal "What is the SuperOptiX framework?"

# Pull RAG demo with LanceDB
super agent pull rag-lancedb-demo
super agent compile rag-lancedb-demo
super agent run rag-lancedb-demo --goal "Explain vector database performance"
```

### 4. **Test Framework Features**

```bash
# Test tools ecosystem
super agent pull tools-demo
super agent compile tools-demo
super agent run tools-demo --goal "Demonstrate calculator and text analysis tools"

# Test memory system
super agent pull memory-demo
super agent compile memory-demo
super agent run memory-demo --goal "Remember my name is Alice and my favorite color is blue"

# Test observability
super agent pull observability-demo
super agent compile observability-demo
super agent run observability-demo --goal "Calculate factorial of 5 with tracing"
```

## 🔧 **Configuration Examples**

### Model Configuration
Each demo agent is pre-configured with optimal settings for its specific use case:

```yaml
# Example: MLX Demo Configuration
language_model:
  location: local
  provider: mlx
  model: mlx-community/Llama-3.2-3B-Instruct-4bit
  api_base: http://localhost:8000
  temperature: 0.7
  max_tokens: 2048
```

### RAG Configuration
Different vector databases have optimized configurations:

```yaml
# ChromaDB (Development)
rag:
  enabled: true
  retriever_type: chroma
  config:
    top_k: 5
    chunk_size: 512
    chunk_overlap: 50

# LanceDB (Production)
rag:
  enabled: true
  retriever_type: lancedb
  config:
    top_k: 10
    chunk_size: 1024
    chunk_overlap: 100
```

### Memory Configuration
Multi-layered memory system configuration:

```yaml
memory:
  enabled: true
  short_term:
    enabled: true
    max_tokens: 2000
    window_size: 10
  long_term:
    enabled: true
    storage_type: local
    max_entries: 500
    persistence: true
  episodic:
    enabled: true
    max_episodes: 100
    episode_retention: 30
```

## 🎯 **Demo Scenarios**

### **Scenario 1: Code Assistant with MLX**
```bash
super agent run mlx-demo --goal "Write a Python function to implement quicksort and explain the algorithm"
```

### **Scenario 2: Creative Writing with Ollama**
```bash
super agent run ollama-demo --goal "Create a short story about a robot learning to paint"
```

### **Scenario 3: RAG Knowledge Retrieval**
```bash
super agent run rag-chroma-demo --goal "Explain how DSPy integrates with RAG systems"
```

### **Scenario 4: Tool Integration**
```bash
super agent run tools-demo --goal "Calculate compound interest for $1000 at 5% for 3 years and analyze the results"
```

### **Scenario 5: Memory Persistence**
```bash
# First session
super agent run memory-demo --goal "Remember that I prefer coffee over tea"

# Second session (memory should persist)
super agent run memory-demo --goal "What's my drink preference?"
```

### **Scenario 6: Observability and Debugging**
```bash
super agent run observability-demo --goal "Analyze this code for potential issues: def divide(a, b): return a / b"
```

## 📊 **Performance Comparison**

| Demo Agent | Best For | Performance | Setup Complexity |
|------------|----------|-------------|------------------|
| MLX Demo | Apple Silicon development | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Ollama Demo | Local development | ⭐⭐⭐⭐ | ⭐ |
| HuggingFace Demo | Advanced NLP | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| LM Studio Demo | GUI model management | ⭐⭐⭐ | ⭐⭐ |
| RAG ChromaDB | Development/testing | ⭐⭐⭐ | ⭐ |
| RAG LanceDB | Production/large scale | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Tools Demo | Tool ecosystem exploration | ⭐⭐⭐⭐ | ⭐ |
| Memory Demo | Memory system testing | ⭐⭐⭐⭐ | ⭐ |
| Observability Demo | Monitoring/debugging | ⭐⭐⭐⭐ | ⭐⭐ |

## 🔍 **Troubleshooting**

### Common Issues

1. **Model Server Not Running**
   ```bash
   # Check if server is running
   curl http://localhost:8000/health  # MLX
   curl http://localhost:11434/api/tags  # Ollama
   ```

2. **RAG Not Working**
   ```bash
   # Check RAG status
   super agent inspect <agent_name>
   # Look for RAG configuration in the output
   ```

3. **Tools Not Available**
   ```bash
   # Verify tools are enabled in playbook
   # Check tool categories and specific_tools sections
   ```

4. **Memory Not Persisting**
   ```bash
   # Check memory configuration
   # Ensure persistence is enabled for long_term memory
   ```

### Getting Help

- **Documentation**: `super docs`
- **Model Management**: `super model list --help`
- **Agent Management**: `super agent list --help`
- **Observability**: `super observe dashboard`

## 🚀 **Next Steps**

After exploring the demo agents:

1. **Customize Agents**: Modify playbooks to suit your specific needs
2. **Combine Features**: Create agents that use multiple features together
3. **Scale Up**: Use production-ready configurations for larger deployments
4. **Build Your Own**: Use the demo agents as templates for your custom agents

## 📚 **Additional Resources**

- [SuperOptiX Website](https://superoptix.ai)
- [SuperOptiX GitHub](https://github.com/SuperagenticAI/superoptix-ai)
- [RAG Guide](../docs/RAG_GUIDE.md)
- [Memory System Overview](../docs/MEMORY_SYSTEM_OVERVIEW.md)
- [Observability Guide](../docs/TRACING_GUIDE.md)
- [Tools Documentation](../tools/README.md)

---

**Happy exploring with SuperOptiX! 🎉** 