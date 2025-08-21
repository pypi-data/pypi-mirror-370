# Metis Agent Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
   - [SingleAgent](#singleagent)
   - [Intent Router](#intent-router)
   - [Planner](#planner)
   - [Task Manager](#task-manager)
   - [Scheduler](#scheduler)
   - [LLM Interface](#llm-interface)
3. [LLM Providers](#llm-providers)
   - [OpenAI](#openai)
   - [Groq](#groq)
   - [Anthropic](#anthropic)
   - [HuggingFace](#huggingface)
4. [Memory Systems](#memory-systems)
   - [SQLite Memory](#sqlite-memory)
   - [Titans Memory](#titans-memory)
5. [Tools](#tools)
   - [Code Generation](#code-generation)
   - [Content Generation](#content-generation)
   - [Google Search](#google-search)
   - [Firecrawl](#firecrawl)
   - [Custom Tools](#custom-tools)
6. [Authentication](#authentication)
   - [API Key Management](#api-key-management)
   - [Secure Storage](#secure-storage)
7. [Interfaces](#interfaces)
   - [Python API](#python-api)
   - [Command Line Interface](#command-line-interface)
   - [Web Server](#web-server)
8. [Advanced Usage](#advanced-usage)
   - [Session Management](#session-management)
   - [Tool Selection](#tool-selection)
   - [Memory Insights](#memory-insights)
9. [Deployment](#deployment)
   - [Installation](#installation)
   - [Configuration](#configuration)
   - [Environment Variables](#environment-variables)
10. [Development](#development)
    - [Testing](#testing)
    - [Contributing](#contributing)

## Architecture Overview

Metis Agent is built with a modular architecture that separates concerns into specialized components. This design allows for flexibility, extensibility, and maintainability.

The high-level architecture consists of:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  User Interface │────▶│  SingleAgent    │────▶│  Intent Router  │
│  (CLI/Web/API)  │     │                 │     │                 │
│                 │     └────────┬────────┘     └────────┬────────┘
└─────────────────┘              │                       │
                                 │                       │
                                 ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Memory System  │◀───▶│  Task Manager   │◀───▶│  Planner        │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └────────┬────────┘
                                 │                       │
                                 │                       │
                                 ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  LLM Interface  │◀───▶│  Tools Registry │◀───▶│  Scheduler      │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Core Components

### SingleAgent

The `SingleAgent` class is the main entry point for the Metis Agent framework. It orchestrates all other components and provides a simple interface for processing user queries.

**Key Responsibilities:**
- Initialize and coordinate all components
- Process user queries
- Manage session context
- Handle task execution
- Combine results into coherent responses

**Usage:**

```python
from metis_agent import SingleAgent

agent = SingleAgent(
    use_titans_memory=False,  # Enable/disable Titans memory
    tools=None,               # Custom tools (uses all available if None)
    llm_provider="openai",    # LLM provider
    llm_model=None,           # LLM model (uses default if None)
    memory_path=None,         # Path to memory database
    task_file=None            # Path to task file
)

response = agent.process_query(
    "Write a Python function to calculate Fibonacci numbers",
    session_id="user123",     # Optional session ID for context
    tool_name=None            # Optional tool name to use
)
```

### Intent Router

The `IntentRouter` class determines whether a user query is a simple question or a complex task that requires planning and execution.

**Key Responsibilities:**
- Classify user queries as questions or tasks
- Use rule-based heuristics for common patterns
- Fall back to LLM for ambiguous cases

**Usage:**

```python
from metis_agent.core.intent_router import IntentRouter

router = IntentRouter()
intent = router.classify("What is the capital of France?")  # Returns "question"
intent = router.classify("Create a Python script to sort a list")  # Returns "task"
```

### Planner

The `Planner` class breaks down complex tasks into smaller, manageable subtasks.

**Key Responsibilities:**
- Analyze complex tasks
- Create a plan with subtasks
- Store plans in a task file

**Usage:**

```python
from metis_agent.core.planner import Planner

planner = Planner("tasks.md")
tasks = planner.create_plan("Build a simple web server in Python")
```

### Task Manager

The `TaskManager` class manages tasks and their status.

**Key Responsibilities:**
- Add new tasks
- Mark tasks as complete
- Track task status
- Store tasks in a task file

**Usage:**

```python
from metis_agent.core.task_manager import TaskManager

task_manager = TaskManager("tasks.md")
task_manager.add_task("Write a function to calculate Fibonacci numbers")
task_manager.mark_complete("Write a function to calculate Fibonacci numbers")
tasks = task_manager.get_all_tasks()
```

### Scheduler

The `Scheduler` class prioritizes tasks for execution.

**Key Responsibilities:**
- Determine task priority
- Optimize task execution order
- Handle dependencies between tasks

**Usage:**

```python
from metis_agent.core.scheduler import Scheduler

scheduler = Scheduler()
prioritized_tasks = scheduler.prioritize_tasks(tasks)
```

### LLM Interface

The LLM interface provides a unified API for interacting with different LLM providers.

**Key Responsibilities:**
- Configure LLM settings
- Provide a consistent interface for LLM interactions
- Handle API key management

**Usage:**

```python
from metis_agent.core.llm_interface import configure_llm, get_llm

# Configure LLM
configure_llm("openai", "gpt-4o", "your-api-key")

# Get configured LLM
llm = get_llm()
response = llm.chat([{"role": "user", "content": "Hello!"}])
```

## LLM Providers

Metis Agent supports multiple LLM providers through a unified interface.

### OpenAI

```python
from metis_agent.llm.openai_llm import OpenAILLM

llm = OpenAILLM(model="gpt-4o", api_key="your-api-key")
response = llm.chat([{"role": "user", "content": "Hello!"}])
```

### Groq

```python
from metis_agent.llm.groq_llm import GroqLLM

llm = GroqLLM(model="llama-3.1-8b-instant", api_key="your-api-key")
response = llm.chat([{"role": "user", "content": "Hello!"}])
```

### Anthropic

```python
from metis_agent.llm.anthropic_llm import AnthropicLLM

llm = AnthropicLLM(model="claude-3-opus-20240229", api_key="your-api-key")
response = llm.chat([{"role": "user", "content": "Hello!"}])
```

### HuggingFace

```python
from metis_agent.llm.huggingface_llm import HuggingFaceLLM

llm = HuggingFaceLLM(model="mistralai/Mixtral-8x7B-Instruct-v0.1", api_key="your-api-key")
response = llm.chat([{"role": "user", "content": "Hello!"}])
```

## Memory Systems

Metis Agent provides two memory systems: a simple SQLite-based memory and a more advanced Titans-inspired adaptive memory.

### SQLite Memory

The `SQLiteMemory` class provides a simple, persistent memory system using SQLite.

**Key Features:**
- Store user inputs and agent outputs
- Retrieve conversation context
- Track clarification context
- Store and update tasks

**Usage:**

```python
from metis_agent.memory.sqlite_store import SQLiteMemory

memory = SQLiteMemory("memory.db")
memory.store_input("user123", "What is machine learning?")
memory.store_output("user123", "Machine learning is...")
context = memory.get_context("user123")
```

### Titans Memory

The `TitansInspiredMemory` class provides an advanced adaptive memory system inspired by the Titans approach.

**Key Features:**
- Lightweight embedding without requiring PyTorch
- Short-term and long-term memory
- Surprise detection
- Attentional context mechanisms
- Memory adaptation based on user interactions

**Usage:**

```python
from metis_agent.memory.titans.titans_memory import TitansInspiredMemory

memory = TitansInspiredMemory("memory_dir")
memory.store_memory("Machine learning is...", "ai_concepts")
relevant_memories = memory.retrieve_relevant_memories("What is deep learning?")
```

## Tools

Metis Agent includes several built-in tools and supports custom tools.

### Code Generation

The `CodeGenerationTool` generates code based on requirements.

**Usage:**

```python
from metis_agent.tools.code_generation import CodeGenerationTool

tool = CodeGenerationTool()
result = tool.execute("Write a Python function to calculate Fibonacci numbers")
```

### Content Generation

The `ContentGenerationTool` creates various types of content.

**Usage:**

```python
from metis_agent.tools.content_generation import ContentGenerationTool

tool = ContentGenerationTool()
result = tool.execute("Write a blog post about AI ethics")
```

### Google Search

The `GoogleSearchTool` performs web searches.

**Usage:**

```python
from metis_agent.tools.google_search import GoogleSearchTool

tool = GoogleSearchTool(api_key="your-api-key")
result = tool.execute("Search for recent advances in quantum computing")
```

### Firecrawl

The `FirecrawlTool` scrapes and analyzes web content.

**Usage:**

```python
from metis_agent.tools.firecrawl import FirecrawlTool

tool = FirecrawlTool(api_key="your-api-key")
result = tool.execute("Analyze the content of https://example.com")
```

### Custom Tools

You can create custom tools by extending the `BaseTool` class.

**Usage:**

```python
from metis_agent.tools.base import BaseTool
from metis_agent.tools.registry import register_tool

class MyTool(BaseTool):
    name = "my_tool"
    description = "Custom tool for specific tasks"
    
    def can_handle(self, task):
        # Determine if this tool can handle the task
        return "specific task" in task.lower()
        
    def execute(self, task):
        # Execute the task
        return f"Task executed: {task}"

# Register the tool
register_tool("my_tool", MyTool)
```

## Authentication

Metis Agent provides secure API key management.

### API Key Management

The `APIKeyManager` class provides secure storage and retrieval of API keys.

**Usage:**

```python
from metis_agent.auth.api_key_manager import APIKeyManager

key_manager = APIKeyManager()
key_manager.set_key("openai", "your-api-key")
api_key = key_manager.get_key("openai")
services = key_manager.list_services()
```

### Secure Storage

The `SecureStorage` class provides secure storage for sensitive information.

**Usage:**

```python
from metis_agent.auth.secure_storage import SecureStorage

storage = SecureStorage("secure_data")
storage.store("api_key", "your-api-key")
api_key = storage.retrieve("api_key")
```

## Interfaces

Metis Agent provides multiple interfaces for interaction.

### Python API

The Python API is the most flexible way to interact with Metis Agent.

**Usage:**

```python
from metis_agent import SingleAgent

agent = SingleAgent()
response = agent.process_query("Write a Python function to calculate Fibonacci numbers")
```

### Command Line Interface

The command-line interface provides quick access to Metis Agent functionality.

**Usage:**

```bash
# Run a query
metis run "Write a Python function to calculate Fibonacci numbers"

# Start the web server
metis serve

# List available tools
metis tools list
```

### Web Server

The web server provides API access to Metis Agent.

**Usage:**

```bash
# Start the web server
metis serve
```

Then make requests to the API:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Write a Python function to calculate Fibonacci numbers"}'
```

## Advanced Usage

### Session Management

Maintain context across multiple interactions:

```python
agent = SingleAgent()

# First query
response1 = agent.process_query(
    "What are the main types of machine learning?",
    session_id="user123"
)

# Follow-up query (uses context from first query)
response2 = agent.process_query(
    "Can you explain supervised learning in more detail?",
    session_id="user123"
)
```

### Tool Selection

Specify which tool to use for a query:

```python
agent = SingleAgent()

# Use a specific tool
response = agent.process_query(
    "Generate a Python function to sort a list",
    tool_name="CodeGenerationTool"
)
```

### Memory Insights

Get insights about the agent's memory:

```python
agent = SingleAgent(use_titans_memory=True)

# Process some queries
agent.process_query("What is machine learning?", session_id="user123")
agent.process_query("Explain neural networks", session_id="user123")

# Get memory insights
insights = agent.get_memory_insights()
print(insights)
```

## Deployment

### Installation

```bash
pip install metis-agent
```

### Configuration

Create a configuration file (`.env`) with your API keys:

```
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key
GOOGLE_API_KEY=your-google-api-key
FIRECRAWL_API_KEY=your-firecrawl-api-key
```

### Environment Variables

Metis Agent uses the following environment variables:

- `OPENAI_API_KEY`: API key for OpenAI
- `GROQ_API_KEY`: API key for Groq
- `ANTHROPIC_API_KEY`: API key for Anthropic
- `HUGGINGFACE_API_KEY`: API key for HuggingFace
- `GOOGLE_API_KEY`: API key for Google Search
- `FIRECRAWL_API_KEY`: API key for Firecrawl
- `FLASK_SECRET_KEY`: Secret key for Flask web server

## Development

### Testing

Run the comprehensive test suite:

```bash
# Run system tests
python metis_agent/test_system.py

# Run CLI tests
python metis_agent/test_cli.py
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request