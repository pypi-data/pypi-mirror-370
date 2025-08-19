# 🎯 Results Parser Agent

A powerful, intelligent agent for extracting metrics from raw result files using LangGraph and AI-powered parsing. The agent automatically analyzes unstructured result files and extracts specific metrics into structured JSON output with high accuracy.

## 🚀 Features

- **🤖 AI-Powered Parsing**: Uses advanced LLMs (OpenAI GPT-4o, GROQ, Anthropic, Google Gemini, Ollama) for intelligent metric extraction
- **📁 Flexible Input**: Process single files or entire directories of result files
- **🎯 Pattern Recognition**: Automatically detects and adapts to different file formats and structures
- **⚙️ Simple Configuration**: Environment variable-based configuration with sensible defaults
- **📊 Structured Output**: Direct output in Pydantic schemas for easy integration
- **🛠️ Professional CLI**: Simple, intuitive command-line interface
- **🔧 Python API**: Easy integration into existing Python applications
- **🔄 Error Recovery**: Robust error handling and retry mechanisms

## 📦 Installation

### Quick Install (Recommended)

```bash
pip install result-parser-agent
```

### Development Install

```bash
# Clone the repository
git clone https://github.com/Infobellit-Solutions-Pvt-Ltd/result-parser-agent.git
cd result-parser-agent

# Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv pip install -e .

# Or install with pip
pip install -e .
```

## 📋 Configuration

### Environment Variables

Create a `.env` file in your project directory:

```bash
# API Keys - Set only the one you need
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Override default LLM settings
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
```

## 🎯 Quick Start

### 1. Set up your API key

```bash
# For OpenAI (default - recommended)
export OPENAI_API_KEY="your-openai-api-key-here"

# For GROQ
export GROQ_API_KEY="your-groq-api-key-here"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# For Google Gemini
export GOOGLE_API_KEY="your-google-api-key-here"
```

### 2. Use the CLI

```bash
# Parse all files in a directory (uses default metrics)
result-parser ./benchmark_results

# Parse with specific metrics
result-parser ./benchmark_results --metrics "RPS,latency,throughput"

# Parse a single file
result-parser ./results.txt --metrics "accuracy,precision"

# Custom output file
result-parser ./results/ --output my_results.json

# Verbose output
result-parser ./results/ --verbose

# Show setup instructions
result-parser setup
```

### 3. Use the Python API

```python
from result_parser_agent import ResultsParserAgent, settings
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Get default configuration
config = settings

# Initialize agent
agent = ResultsParserAgent(config)

# Parse results (file or directory)
results = await agent.parse_results(
    input_path="./benchmark_results",  # or "./results.txt"
    metrics=["RPS", "latency", "throughput"]
)

# Output structured data
print(results.json(indent=2))
```