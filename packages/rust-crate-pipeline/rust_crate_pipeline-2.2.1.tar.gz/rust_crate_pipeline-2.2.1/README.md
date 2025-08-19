# Rust Crate Pipeline v2.2.0

A comprehensive system for gathering, enriching, and analyzing metadata for Rust crates using AI-powered insights, web scraping, and dependency analysis. This pipeline provides deep analysis of Rust crates with support for multiple LLM providers, advanced web scraping, and the Sigil Protocol for Sacred Chain analysis.

## 🚀 Quick Start

### Option 1: Install via pip (Recommended for users)

```bash
# Install the package
pip install rust-crate-pipeline

# Run with Azure OpenAI (most common)
python run_with_llm.py --provider azure --model gpt-4o

# Or use the module directly
python -m rust_crate_pipeline --llm-provider azure --llm-model gpt-4o
```

### Option 2: Clone and run from repository (Recommended for developers)

```bash
# Clone the repository
git clone https://github.com/Superuser666-Sigil/SigilDERG-Data_Production.git
cd SigilDERG-Data_Production

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Playwright browsers (required for web scraping)
playwright install

# Run the pipeline
python run_with_llm.py --provider azure --model gpt-4o
```

## ✨ Key Features

- **🤖 Multi-Provider LLM Support**: Azure OpenAI, OpenAI, Anthropic, Ollama, LM Studio, Lambda.AI, and all LiteLLM providers
- **🌐 Advanced Web Scraping**: Crawl4AI + Playwright for intelligent content extraction
- **⚡ Auto-Resume Capability**: Automatically skips already processed crates
- **📊 Real-time Progress Tracking**: Comprehensive monitoring and error recovery
- **🔒 Sigil Protocol Support**: Sacred Chain analysis with IRL trust scoring
- **🐳 Docker Support**: Containerized deployment with docker-compose
- **📦 Batch Processing**: Configurable memory optimization and cost control
- **🛡️ Security Analysis**: Privacy and security scanning with Presidio
- **📈 Comprehensive Output**: JSON metadata with detailed crate analysis

## 📋 Requirements

- **Python 3.12+** (required)
- **Git** (for repository operations)
- **Cargo** (for Rust crate analysis)
- **Playwright browsers** (auto-installed via `playwright install`)

## 🔧 Installation & Setup

### For End Users (pip install)

```bash
# Install the package (includes all dependencies)
pip install rust-crate-pipeline

# Install Playwright browsers
playwright install

# Set up environment variables (optional but recommended)
export AZURE_OPENAI_ENDPOINT="your_endpoint"
export AZURE_OPENAI_API_KEY="your_api_key"
export GITHUB_TOKEN="your_github_token"
```

### For Developers (repository clone)

```bash
# Clone the repository
git clone https://github.com/Superuser666-Sigil/SigilDERG-Data_Production.git
cd SigilDERG-Data_Production

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Playwright browsers
playwright install

# Set up environment variables
export AZURE_OPENAI_ENDPOINT="your_endpoint"
export AZURE_OPENAI_API_KEY="your_api_key"
export GITHUB_TOKEN="your_github_token"
```

## 🎯 Usage Examples

### Basic Usage

```bash
# Resume processing with Azure OpenAI (recommended)
python run_with_llm.py --provider azure --model gpt-4o

# Process specific crates with OpenAI
python run_with_llm.py --provider openai --model gpt-4 --api-key YOUR_KEY --crates tokio serde

# Use local Ollama model
python run_with_llm.py --provider ollama --model llama2

# Process from file with custom batch size
python run_with_llm.py --provider azure --model gpt-4o --crates-file data/crate_list.txt --batch-size 5
```

### Advanced Usage

```bash
# Custom configuration with all options
python run_with_llm.py \
  --provider azure \
  --model gpt-4o \
  --batch-size 10 \
  --max-tokens 2048 \
  --checkpoint-interval 5 \
  --log-level DEBUG \
  --output-path ./results \
  --skip-problematic

# Use the module directly (alternative entry point)
python -m rust_crate_pipeline \
  --llm-provider azure \
  --llm-model gpt-4o \
  --limit 50 \
  --batch-size 5 \
  --output-dir ./data \
  --log-level DEBUG

# Enable Sigil Protocol for Sacred Chain analysis (module entry point only)
python -m rust_crate_pipeline --enable-sigil-protocol --crates tokio serde
```

### Docker Usage

```bash
# Build and run with Docker
docker-compose up --build

# Or build manually
docker build -t rust-crate-pipeline .
docker run -e AZURE_OPENAI_API_KEY=your_key rust-crate-pipeline
```

## 🔑 Environment Variables

Configure your LLM providers and API keys:

```bash
# Azure OpenAI (recommended)
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_api_key"
export AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment"

# OpenAI
export OPENAI_API_KEY="your_api_key"

# Anthropic
export ANTHROPIC_API_KEY="your_api_key"

# GitHub (for enhanced metadata)
export GITHUB_TOKEN="your_github_token"

# Lambda.AI
export LAMBDA_API_KEY="your_api_key"
```

## 🏗️ Architecture Overview

### Entry Points

The pipeline provides two main entry points:

1. **`run_with_llm.py`** - Comprehensive script with full LLM provider support
   - Supports all LLM providers (Azure, OpenAI, Anthropic, Ollama, etc.)
   - Advanced configuration options and batch processing
   - Auto-resume capability and progress tracking
   - Recommended for most users

2. **`python -m rust_crate_pipeline`** - Module entry point with Sigil Protocol support
   - Includes Sigil Protocol for Sacred Chain analysis
   - IRL trust scoring and cryptographic audit trails
   - Simplified configuration for focused analysis
   - Use with `--enable-sigil-protocol` flag

### Core Components

- **`UnifiedLLMProcessor`** - Handles all LLM providers uniformly
- **`UnifiedSigilPipeline`** - Core pipeline orchestration with Sigil Protocol support
- **`Crawl4AI Integration`** - Advanced web scraping with AI extraction
- **`ProgressMonitor`** - Real-time progress tracking and auto-resume

### Key Features

- **Auto-resume**: Automatically skips already processed crates
- **Progress tracking**: Real-time monitoring with detailed logging
- **Error recovery**: Robust error handling and retries
- **Memory optimization**: Configurable batch sizes for different environments
- **Cost control**: Budget management and tracking
- **Sigil Protocol**: Sacred Chain analysis with IRL trust scoring

## 📚 Documentation

- **[LLM Provider Guide](docs/README_LLM_PROVIDERS.md)** - Complete LLM provider setup and usage
- **[Configuration Guide](docs/CONFIGURATION_GUIDE.md)** - Detailed configuration options
- **[Performance Optimization](docs/PERFORMANCE_OPTIMIZATION.md)** - Tuning for production use
- **[Lambda.AI Setup](docs/LAMBDA_AI_SETUP.md)** - Lambda.AI specific configuration
- **[Crawl4AI Analysis](docs/CRAWL4AI_TYPE_ANALYSIS.md)** - Web scraping implementation details

## 🛠️ Development

### Building and Testing

```bash
# Build package
python -m build

# Run tests
pytest --cov=rust_crate_pipeline tests/

# Type checking
pyright rust_crate_pipeline/
mypy rust_crate_pipeline/

# Code formatting
black rust_crate_pipeline/
isort rust_crate_pipeline/

# Linting
flake8 rust_crate_pipeline/

# Security checks
bandit -r rust_crate_pipeline/
safety check
```

### Publishing

```bash
# Build and upload to PyPI
python -m build
twine upload dist/*
```

## 📦 Project Structure

```
rust_crate_pipeline/
├── main.py                    # Module entry point
├── unified_llm_processor.py   # Multi-provider LLM support
├── unified_pipeline.py        # Main pipeline orchestration
├── ai_processing.py           # LLM enrichment logic
├── crawl4ai_integration.py    # Web scraping integration
├── progress_monitor.py        # Progress tracking
├── config.py                  # Configuration management
├── core/                      # Core analysis components
│   ├── irl_engine.py         # IRL trust scoring
│   ├── sacred_chain.py       # Sacred Chain analysis
│   └── canon_registry.py     # Canon registry
├── scraping/                  # Web scraping modules
├── utils/                     # Utility functions
└── audits/                    # Audit and validation
```

## 🔄 Version 2.2.0 Changes

- **Fixed Setuptools warnings** - Clean build process with no deprecation warnings
- **Improved requirements management** - Synchronized dependencies across all config files
- **Enhanced error handling** - Better exception handling and logging
- **Updated dependencies** - Latest versions with security fixes
- **Streamlined installation** - Simplified setup for both pip and repository users
- **Sigil Protocol support** - Sacred Chain analysis with IRL trust scoring (via `python -m rust_crate_pipeline --enable-sigil-protocol`)

## 🐳 Docker Support

The project includes full Docker support for containerized deployment:

```bash
# Quick start with docker-compose
docker-compose up --build

# Manual Docker build
docker build -t rust-crate-pipeline .
docker run -e AZURE_OPENAI_API_KEY=your_key rust-crate-pipeline
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔧 Troubleshooting

### Common Issues

**Playwright Installation**
```bash
# If you get Playwright errors, install browsers
playwright install
```

**LLM Provider Issues**
```bash
# Check your API keys and endpoints
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your_api_key"

# Test connection
python -c "from rust_crate_pipeline.unified_llm_processor import UnifiedLLMProcessor; print('✅ LLM processor ready')"
```

**Memory Issues**
```bash
# Reduce batch size for low-memory environments
python run_with_llm.py --provider azure --model gpt-4o --batch-size 2
```

**Permission Issues**
```bash
# On Linux/macOS, ensure proper permissions
chmod +x run_with_llm.py
chmod +x rust_crate_pipeline/main.py
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/issues)
- **Documentation**: [Project Wiki](https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/discussions)
