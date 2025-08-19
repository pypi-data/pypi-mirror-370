"""Version information for rust-crate-pipeline."""

__version__ = "2.2.0"
__version_info__ = tuple(int(x) for x in __version__.split("-")[0].split("."))
__author__ = "SigilDERG Team"
__email__ = "sigilderg@example.com"

# Release history
# 2.2.0 - Sigil Protocol Integration Fix Release
#         - Fixed Sigil Protocol integration to properly use UnifiedSigilPipeline
#         - Added IRL trust scoring with 0-10 scale for each crate
#         - Implemented trust verdicts: ALLOW/DENY/DEFER/FLAG
#         - Added Sacred Chain analysis with cryptographically signed audit trails
#         - Enhanced output format with individual Sacred Chain JSON files
#         - Fixed pipeline selection logic for --enable-sigil-protocol flag
#         - Resolved missing Sigil Protocol implementation issue
# 2.1.0 - Code Review and Quality Improvements Release
#         - Fixed schema aliases to use underscores instead of dots for better
#           serialization
#         - Enhanced ValidationError handling with detailed field-level error reporting
#         - Improved security with path traversal protection in tar extraction
#         - Added comprehensive test coverage for all modules
#         - Enhanced error messages and debugging capabilities
#         - Fixed linter issues and improved code quality
#         - Updated dependencies and project structure
# 2.0.0 - Major Cleanup and Refactoring Release
#         - Comprehensive project cleanup and reorganization
#         - Consolidated redundant run scripts into single entry point
#           (run_with_llm.py)
#         - Eliminated code duplication: unified RustCodeAnalyzer implementations
#         - Removed redundant AzureOpenAIEnricher in favor of
#           UnifiedLLMProcessor
#         - Organized files into logical directory structure
#           (configs/, scripts/, data/, docs/)
#         - Enhanced repository hygiene with proper .gitignore for build
#           artifacts
#         - Improved project maintainability and code quality
#         - Streamlined architecture with unified LLM processing approach
# 1.5.6 - Dependency Management and Lambda.AI Integration Release
#         - Complete dependency audit and update across all requirements files
#         - Added missing Azure AI Services dependencies
#           (azure-ai-inference, azure-core, azure-identity)
#         - Added data validation dependencies (pydantic, toml)
#         - Added privacy analysis dependencies (presidio-analyzer, spacy)
#         - Added async HTTP client (aiohttp) and data serialization utilities
#           (dataclasses-json)
#         - Integrated Lambda.AI support with unified LLM processor
#         - Enhanced pyproject.toml with proper version constraints and optional
#           dependency groups
#         - Updated setup.py with new optional dependency groups (privacy, async)
#         - Comprehensive clean build validation with all dependencies resolved
#         - Fixed linter errors and improved code quality across core modules
#         - Enhanced documentation with Lambda.AI setup guide and provider
#           support
# 1.5.0 - GPU/3.11 Compatibility Release
#         - Lowered Python requirement to >=3.11 for GPU builds
#         - Fully supports llama-cpp-python with CUDA/cuBLAS on Python 3.11
#         - PyPI and build system now compatible with GPU-accelerated DeepSeek
#           and Llama models
#         - All previous local model optimizations included
# 1.4.9 - Local Model Optimization Release
#         - Added local model optimization settings
#         - Reduced token limits for local models (2048 vs 4096)
#         - Smaller chunk sizes (800 vs 2000) for better performance
#         - Lower temperature (0.1 vs 0.3) for more consistent outputs
#         - Added LOCAL_MODEL_MODE environment variable support
#         - Created run_local_optimized.py script for easy local model usage
# 1.4.8 - Bug Fix Release: Package Distribution Fix - Final
#         - Fixed utils module inclusion in pip package distribution
#         - Updated setup.py to include utils module in packages
#         - Updated MANIFEST.in to include utils module files
#         - Resolved ModuleNotFoundError for utils.serialization_utils
#         - Ensured proper package installation via pip
# 1.4.5 - Feature Release
#         - Sanitizer now disabled by default; optional via `enabled=True`.
#         - Robust JSON serialization for MarkdownGenerationResult and others.
#         - Removed default PII stripping; crate data preserved.
# 1.4.4 - Security Release
#         - Added PII and secret sanitization to the pipeline.
# 1.4.3 - In-progress
#         - Implemented full crate analysis (cargo check, clippy, audit)
# 1.4.2 - Maintenance Release
#         - Updated project to version 1.4.2
#         - General maintenance and dependency updates
# 1.2.5-dev.20250621 - Dev branch: experimental, not a formal
# release. Originated from v1.2.5.
# 1.2.5 - Last official release.
# 1.5.1 - Configuration Standardization Release: Model Path Consistency
#         - Standardized all configuration to use GGUF model paths
#         - Updated CLI defaults for --crawl4ai-model to
#           ~/models/deepseek/deepseek-coder-6.7b-instruct.Q4_K_M.gguf
#         - Enhanced Rule Zero alignment with transparent configuration practices
#         - Updated all test files to use consistent GGUF model path references
#         - Comprehensive documentation updates for proper model configuration
#         - Removed inconsistent Ollama references in favor of llama-cpp-python
#         - Ensured CLI help text and JSON examples reflect correct model paths
# 1.5.0 - Major Release: Enhanced Web Scraping with Crawl4AI Integration
#         - Integrated Crawl4AI for advanced web scraping capabilities
#         - Added JavaScript-rendered content extraction via Playwright
#         - Enhanced README parsing with LLM-powered content analysis
#         - New CLI options: --enable-crawl4ai, --disable-crawl4ai, --crawl4ai-model
#         - Enhanced configuration with local GGUF model paths and crawl4ai_timeout
#         - Comprehensive test coverage for all Crawl4AI features
#         - Rule Zero compliant with full transparency and audit trails
# 1.4.0 - Major Release: Rule Zero Compliance Audit Complete
#         - Completed comprehensive Rule Zero alignment audit
#         - Eliminated all code redundancy and dead code
#         - Achieved 100% test coverage (22/22 tests passing)
#         - Refactored to pure asyncio architecture (thread-free)
#         - Suppressed Pydantic deprecation warnings
#         - Full production readiness with Docker support
#         - Enhanced documentation with PyPI cross-references
#         - Certified Rule Zero compliance across all four principles
# 1.3.1 - Bug Fix Release: Crawl4AI Integration Cleanup
#         - Fixed CSS selector syntax errors in Crawl4AI integration
#         - Cleaned up duplicate and obsolete test files
#         - Resolved import conflicts between workspace and integration configs
#         - Improved error handling in enhanced scraping module
#         - Standardized on direct llama.cpp approach (removed Ollama dependencies)
#         - Enhanced Rule Zero compliance with transparent cleanup process
#         - Fixed type annotation compatibility issues
#         - Fixed Python 3.9 compatibility for type annotations
#         - Updated dict[str, Any] to "dict[str, Any]" format
#         - Fixed Union type expressions in conditional imports
#         - Resolved IDE linter errors in network.py, pipeline.py, and
#           production_config.py
#         - Improved code quality and maintainability
# 1.3.0 - Quality & Integration Release: Comprehensive code quality improvements
#         - Fixed all critical PEP 8 violations (F821, F811, E114)
#         - Enhanced error handling with graceful dependency fallbacks
#         - Improved module integration and import path resolution
#         - Added comprehensive test validation (21/21 tests passing)
#         - Enhanced async support and Unicode handling
#         - Production-ready CLI interfaces with robust error handling
#         - Full Rule Zero compliance validation
# 1.2.0 - Major release: Production-ready, cleaned codebase
#         - Unified documentation into single comprehensive README
#         - Removed all non-essential development and test files
#         - Optimized for PyPI distribution and Docker deployment
#         - Enhanced GitHub token integration and setup
# 1.1.2 - Production release: Cleaned up non-essential files
#         - Unified documentation into single README
#         - Optimized for PyPI distribution
# 1.1.1 - Bug fix: Added missing python-dateutil dependency
#         - Fixed relativedelta import error
# 1.1.0 - Updated author and contact information
#         - Enhanced package configuration
# 0.1.0 - Initial release
#         - Core pipeline functionality
#         - AI-powered metadata enrichment
#         - Dependency analysis
#         - PyPI package setup
