# ai_processing.py
import logging
from typing import Dict

from .config import CrateMetadata, EnrichedCrate, PipelineConfig
from .config_loader import get_config_loader
from .llm_factory import create_llm_client_from_config

import tiktoken


class LLMEnricher:
    def __init__(self, config: PipelineConfig) -> None:
        """Initialize LLMEnricher with new LLM client"""
        self.config = config
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.config_loader = get_config_loader()

        # Use new LLM client
        self.llm_client = create_llm_client_from_config(config)
        self.logger = logging.getLogger(__name__)

    async def enrich_crate(self, crate: CrateMetadata) -> EnrichedCrate:
        """Enrich crate metadata using LLM analysis"""
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
            await self._perform_ai_enrichment(enriched)

            return enriched

        except Exception as e:
            self.logger.error(f"Error enriching crate {crate.name}: {e}")
            # Return basic enriched crate without AI data
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
                readme_summary="Error during enrichment",
                feature_summary="Error during enrichment",
                use_case="unknown",
                score=0.0,
                factual_counterfactual="Error during enrichment",
                source_analysis={"error": str(e)},
                user_behavior={"error": str(e)},
                security={"error": str(e)},
            )

    async def _perform_ai_enrichment(self, enriched: EnrichedCrate) -> None:
        """Perform AI-based enrichment of crate data"""

        # Create context for LLM
        context = self._build_crate_context(enriched)

        # Generate summaries
        enriched.readme_summary = await self._generate_summary(context)
        enriched.feature_summary = await self._generate_feature_summary(enriched)

        # Perform analysis
        analysis_result = await self._perform_analysis(context)
        enriched.source_analysis = analysis_result.get("analysis", {})
        enriched.score = analysis_result.get("quality_score", 0.0)
        enriched.use_case = analysis_result.get("use_case", "unknown")
        enriched.factual_counterfactual = analysis_result.get("factual_pairs", "")
        enriched.user_behavior = analysis_result.get("user_behavior", {})
        enriched.security = analysis_result.get("security", {})

    def _build_crate_context(self, enriched: EnrichedCrate) -> str:
        """Build context string for LLM analysis"""
        context_parts = []

        # Basic info
        context_parts.append(f"Crate: {enriched.name} v{enriched.version}")
        if enriched.description:
            context_parts.append(f"Description: {enriched.description}")

        # Repository
        if enriched.repository:
            context_parts.append(f"Repository: {enriched.repository}")

        # Keywords and categories
        if enriched.keywords:
            context_parts.append(f"Keywords: {', '.join(enriched.keywords)}")
        if enriched.categories:
            context_parts.append(f"Categories: {', '.join(enriched.categories)}")

        # Dependencies
        if enriched.dependencies:
            deps = [f"{dep.get('name', 'unknown')} {dep.get('version', '')}" for dep in enriched.dependencies]
            context_parts.append(f"Dependencies: {', '.join(deps)}")

        # Features
        if enriched.features:
            context_parts.append(f"Features: {', '.join(enriched.features.keys())}")

        # Downloads and stars
        if enriched.downloads is not None:
            context_parts.append(f"Downloads: {enriched.downloads}")
        if enriched.github_stars is not None:
            context_parts.append(f"GitHub Stars: {enriched.github_stars}")

        # README (truncated)
        if enriched.readme:
            readme_preview = (
                enriched.readme[:1000] + "..." if len(enriched.readme) > 1000 else enriched.readme
            )
            context_parts.append(f"README Preview: {readme_preview}")

        return "\n".join(context_parts)

    async def _generate_summary(self, context: str) -> str:
        """Generate AI summary of the crate"""
        prompt = (
            f"Analyze this Rust crate and provide a concise summary "
            f"(2-3 sentences):\n\n"
            f"{context}\n\n"
            f"Summary:"
        )

        try:
            response = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3,
            )
            return response.strip()
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return "Summary generation failed"

    async def _generate_feature_summary(self, enriched: EnrichedCrate) -> str:
        """Generate feature summary"""
        if not enriched.features:
            return "No features defined"

        prompt = f"""Summarize the key features of this Rust crate:

Crate: {enriched.name}
Features: {enriched.features}
Description: {enriched.description}

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

    async def _perform_analysis(self, context: str) -> Dict:
        """Perform comprehensive AI analysis of the crate"""
        prompt = (
            f"Analyze this Rust crate and provide a structured analysis in JSON format:\n\n"
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
                max_tokens=800,
                temperature=0.2,
            )
            return response
        except Exception as e:
            self.logger.error(f"Error performing analysis: {e}")
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
