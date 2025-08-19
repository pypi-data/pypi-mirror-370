# unified_llm_processor.py
import logging
from typing import TYPE_CHECKING, Any, Dict

from .config import CrateMetadata, EnrichedCrate, PipelineConfig
from .llm_factory import create_llm_client_from_config

if TYPE_CHECKING:
    pass


class UnifiedLLMProcessor:
    """
    Unified LLM processor that supports multiple providers with a consistent interface.

    This processor replaces the old litellm-based approach with a more robust,
    provider-agnostic implementation that supports:
    - Ollama (local models)
    - OpenAI (cloud models)
    - Azure OpenAI (enterprise models)
    - llama-cpp-python (direct model loading)
    - LiteLLM (fallback for complex scenarios)
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Create LLM client from config
        self.llm_client = create_llm_client_from_config(config)

        # Processing configuration
        self.processing_config = self._load_processing_config()

    def _load_processing_config(self) -> Dict[str, Any]:
        """Load processing configuration from config loader"""
        try:
            from .config_loader import get_config_loader

            config_loader = get_config_loader()
            return config_loader.get_processing_config()
        except Exception as e:
            self.logger.warning(f"Could not load processing config: {e}")
            return {}

    async def process_crate(self, crate: CrateMetadata) -> EnrichedCrate:
        """Process a crate through the unified LLM pipeline"""
        try:
            # Create enriched crate with original data
            enriched = EnrichedCrate(
                name=crate.name,
                version=crate.version,
                description=crate.description,
                repository=crate.repository,
                keywords=crate.keywords,
                categories=crate.categories,
                readme=crate.readme,
                downloads=crate.downloads,
                github_stars=crate.github_stars,
                dependencies=crate.dependencies,
                features=crate.features,
                code_snippets=crate.code_snippets,
                readme_sections=crate.readme_sections,
                librs_downloads=crate.librs_downloads,
                source=crate.source,
                enhanced_scraping=crate.enhanced_scraping,
                enhanced_features=crate.enhanced_features,
                enhanced_dependencies=crate.enhanced_dependencies,
            )

            # Perform AI enrichment
            await self._enrich_crate(enriched)
            return enriched

        except Exception as e:
            self.logger.error(f"Error processing crate {crate.name}: {e}")
            # Return basic enriched crate with error info
            return EnrichedCrate(
                name=crate.name,
                version=crate.version,
                description=crate.description,
                repository=crate.repository,
                keywords=crate.keywords,
                categories=crate.categories,
                readme=crate.readme,
                downloads=crate.downloads,
                github_stars=crate.github_stars,
                dependencies=crate.dependencies,
                features=crate.features,
                code_snippets=crate.code_snippets,
                readme_sections=crate.readme_sections,
                librs_downloads=crate.librs_downloads,
                source=crate.source,
                enhanced_scraping=crate.enhanced_scraping,
                enhanced_features=crate.enhanced_features,
                enhanced_dependencies=crate.enhanced_dependencies,
                readme_summary="Error during processing",
                feature_summary="Error during processing",
                use_case="unknown",
                score=0.0,
                factual_counterfactual="Error during processing",
                source_analysis={"error": str(e)},
                user_behavior={"error": str(e)},
                security={"error": str(e)},
            )

    async def _enrich_crate(self, enriched: EnrichedCrate) -> None:
        """Enrich crate with AI analysis"""

        # Build context for analysis
        context = self._build_context(enriched)

        # Generate summaries
        enriched.readme_summary = await self._generate_readme_summary(enriched)
        enriched.feature_summary = await self._generate_feature_summary(enriched)

        # Perform comprehensive analysis
        analysis_result = await self._perform_comprehensive_analysis(context)

        # Update enriched crate with analysis results
        enriched.source_analysis = analysis_result.get("analysis", {})
        enriched.score = analysis_result.get("quality_score", 0.0)
        enriched.use_case = analysis_result.get("use_case", "unknown")
        enriched.factual_counterfactual = analysis_result.get("factual_pairs", "")
        enriched.user_behavior = analysis_result.get("user_behavior", {})
        enriched.security = analysis_result.get("security", {})

    def _build_context(self, enriched: EnrichedCrate) -> str:
        """Build comprehensive context for LLM analysis"""
        context_parts = []

        # Basic information
        context_parts.append(f"Crate: {enriched.name} v{enriched.version}")
        if enriched.description:
            context_parts.append(f"Description: {enriched.description}")

        # Repository and metadata
        if enriched.repository:
            context_parts.append(f"Repository: {enriched.repository}")
        if enriched.keywords:
            context_parts.append(f"Keywords: {', '.join(enriched.keywords)}")
        if enriched.categories:
            context_parts.append(f"Categories: {', '.join(enriched.categories)}")

        # Dependencies and features
        if enriched.dependencies:
            deps = [f"{dep.get('name', 'unknown')} {dep.get('version', '')}" for dep in enriched.dependencies]
            context_parts.append(f"Dependencies: {', '.join(deps)}")

        if enriched.features:
            context_parts.append(f"Features: {', '.join(enriched.features.keys())}")

        # Metrics
        if enriched.downloads is not None:
            context_parts.append(f"Downloads: {enriched.downloads}")
        if enriched.github_stars is not None:
            context_parts.append(f"GitHub Stars: {enriched.github_stars}")

        # README content (truncated)
        if enriched.readme:
            readme_preview = (
                enriched.readme[:1500] + "..." if len(enriched.readme) > 1500 else enriched.readme
            )
            context_parts.append(f"README: {readme_preview}")

        return "\n".join(context_parts)

    async def _generate_readme_summary(self, enriched: EnrichedCrate) -> str:
        """Generate README summary"""
        if not enriched.readme:
            return "No README available"

        prompt = f"""Summarize the key aspects of this Rust crate from its README:

Crate: {enriched.name}
Description: {enriched.description}

        README Content:
{enriched.readme[:2000]}

Provide a concise summary (2-3 sentences) focusing on:
- Main purpose and functionality
- Key features and capabilities
- Target use cases

Summary:"""

        try:
            response = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3,
            )
            return response.strip()
        except Exception as e:
            self.logger.error(f"Error generating README summary: {e}")
            return "README summary generation failed"

    async def _generate_feature_summary(self, enriched: EnrichedCrate) -> str:
        """Generate feature summary"""
        if not enriched.features:
            return "No features defined"

        prompt = f"""Summarize the features of this Rust crate:

Crate: {enriched.name}
Features: {enriched.features}
Description: {enriched.description}

Provide a concise summary of the key features and their purposes.

Feature Summary:"""

        try:
            response = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.2,
            )
            return response.strip()
        except Exception as e:
            self.logger.error(f"Error generating feature summary: {e}")
            return "Feature summary generation failed"

    async def _perform_comprehensive_analysis(self, context: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of the crate"""
        prompt = (
            f"Analyze this Rust crate comprehensively and provide structured analysis in JSON format:\n\n"
            f"{context}\n\n"
            f"Provide analysis in this JSON format:\n"
            f"{{\n"
            f'    "analysis": {{\n'
            f'        "maintenance_status": "active|inactive|unknown",\n'
            f'        "community_health": "high|medium|low",\n'
            f'        "code_quality": "high|medium|low",\n'
            f'        "documentation_quality": "high|medium|low",\n'
            f'        "security_concerns": ["list", "of", "concerns"],\n'
            f'        "performance_characteristics": "description",\n'
            f'        "use_case_suitability": ["list", "of", "use", "cases"]\n'
            f"    }},\n"
            f'    "quality_score": 0.0-1.0,\n'
            f'    "use_case": "primary use case category",\n'
            f'    "factual_pairs": "3 factual statements and 3 counterfactual statements",\n'
            f'    "user_behavior": {{\n'
            f'        "target_audience": "description",\n'
            f'        "adoption_patterns": "description"\n'
            f"    }},\n"
            f'    "security": {{\n'
            f'        "risk_level": "low|medium|high",\n'
            f'        "vulnerabilities": ["list", "of", "concerns"]\n'
            f"    }}\n"
            f"}}"
        )

        try:
            response = await self.llm_client.chat_json(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.2,
            )
            return response
        except Exception as e:
            self.logger.error(f"Error performing comprehensive analysis: {e}")
            return {
                "analysis": {"error": str(e)},
                "quality_score": 0.5,
                "use_case": "unknown",
                "factual_pairs": "Analysis failed",
                "user_behavior": {"error": str(e)},
                "security": {"error": str(e)},
            }

    async def close(self) -> None:
        """Close LLM client resources"""
        await self.llm_client.aclose()
