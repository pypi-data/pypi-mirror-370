"""
DuckDuckGo Search with 3-Step Processing
1. Query Optimization: Convert user prompt to search query
2. Search Execution: Use DuckDuckGo to find relevant content
3. Result Integration: Feed search results + original prompt to LLM
"""

import logging
import time
from typing import Type, TypeVar, Dict, Any, List
from pydantic import BaseModel
import json

T = TypeVar("T", bound=BaseModel)


class SearchResult(BaseModel):
    """Represents a single search result"""

    title: str
    url: str
    snippet: str
    relevance_score: float = 0.0


class OptimizedQuery(BaseModel):
    """Optimized search query from LLM"""

    search_query: str
    reasoning: str
    language: str = "en"


class DuckDuckGoSearch:
    """
    Handles DuckDuckGo search with 3-step processing for any LLM model.
    """

    def __init__(self, config: Dict[str, Any], llm_client):
        self.config = config
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        # Initialize with bootstrap config or fallback to defaults
        try:
            from ..config import get_config

            bootstrap_config = get_config()
            self.max_results = bootstrap_config.get("search_duckduckgo_max_results", 5)
            self.search_timeout = bootstrap_config.get("search_duckduckgo_timeout", 10)
        except Exception:
            # Fallback to defaults if bootstrap config is not available
            self.max_results = 5
            self.search_timeout = 10

    def _optimize_search_query(self, original_prompt: str, model: str) -> OptimizedQuery:
        """
        Step 1: Use LLM to convert user prompt to optimized search query
        """
        # Check if this is a smaller model that might need simpler prompts
        is_small_model = any(indicator in model.lower() for indicator in ["0.6b", "1b", "3b", "mini", "small"])

        if is_small_model:
            # Simpler, more direct prompt for smaller models
            optimization_prompt = f"""Convert this prompt to a search query:

"{original_prompt}"

Return JSON with:
- search_query: short search terms
- reasoning: why these terms
- language: "en" or "zh"

Example:
{{"search_query": "tennis players", "reasoning": "key terms", "language": "en"}}"""
        else:
            # More detailed prompt for larger models
            optimization_prompt = (
                f"You need to create an optimized search query for DuckDuckGo based on the user's prompt.\n\n"
                f"User's original prompt: {original_prompt}\n\n"
                f"Please provide:\n"
                f"1. search_query: A concise search query (under 200 characters) with key terms "
                f"optimized for web search engines\n"
                f"2. reasoning: Brief explanation of why you chose these search terms\n"
                f"3. language: The language code (default \"en\" for English, \"zh\" for Chinese, etc.)\n\n"
                f"Example response format:\n"
                f"{{\n"
                f'  "search_query": "tennis player rankings ATP",\n'
                f'  "reasoning": "Focused on key terms for finding current tennis player information",\n'
                f'  "language": "en"\n'
                f"}}\n\n"
                f"Now create your optimized search query:"
            )

        try:
            # Use the LLM client to optimize the query
            # Extract schema for logging
            try:
                schema_json = json.dumps(OptimizedQuery.model_json_schema(), default=str)
            except Exception:
                schema_json = None

            result = self.llm_client._generate_standard(
                optimization_prompt,
                OptimizedQuery,
                model,
                temperature=0.1,
                max_retries=1,  # Reduced retries to fail faster and use fallback
                schema=schema_json,
            )

            # Validate the result has meaningful content
            if not result.search_query or len(result.search_query.strip()) < 3:
                raise ValueError("Generated search query is too short or empty")

            self.logger.info(f"Optimized search query: '{result.search_query}'")
            self.logger.info(f"Optimization reasoning: {result.reasoning}")

            return result

        except Exception as e:
            self.logger.warning(f"Query optimization failed: {e}. Using fallback.")
            # Fallback: extract key terms from original prompt
            fallback_query = self._extract_key_terms(original_prompt)
            return OptimizedQuery(
                search_query=fallback_query,
                reasoning="Fallback extraction due to optimization failure",
                language="auto",
            )

    def _extract_key_terms(self, text: str) -> str:
        """
        Fallback method to extract key terms from text
        """
        # Simple keyword extraction (can be enhanced)
        import re

        # Remove common stop words and punctuation
        stop_words = {
            "the",
            "is",
            "at",
            "which",
            "on",
            "and",
            "a",
            "to",
            "are",
            "as",
            "was",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "can",
            "may",
            "might",
            "must",
            "shall",
            "in",
            "of",
            "for",
            "with",
            "by",
            "generate",
            "create",
            "make",
            "find",
            "get",
            "show",
            "tell",
            "give",
            "provide",
        }

        # Extract words (alphanumeric sequences)
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter out stop words and short words
        key_words = [w for w in words if len(w) > 2 and w not in stop_words]

        # Prioritize nouns and important terms (simple heuristic)
        # Keep words that are likely to be important search terms
        important_words = []
        for word in key_words:
            # Skip very common words that might have slipped through
            if word not in {"top", "best", "good", "great", "new", "old", "big", "small"}:
                important_words.append(word)

        # Take first 8 most relevant words and join
        search_query = " ".join(important_words[:8])

        # Limit to 200 characters
        if len(search_query) > 200:
            search_query = search_query[:197] + "..."

        return search_query or text[:200]  # Fallback to truncated original

    def _perform_duckduckgo_search(self, query: str) -> List[SearchResult]:
        """
        Step 2: Execute DuckDuckGo search
        """
        try:
            # Try to import duckduckgo_search
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                self.logger.error("duckduckgo_search package not found. Install with: pip install duckduckgo-search")
                return []

            results = []

            with DDGS() as ddgs:
                search_results = ddgs.text(
                    keywords=query,
                    max_results=self.max_results,
                    safesearch="moderate",
                    timelimit="m",  # Last month for more current results
                )

                for i, result in enumerate(search_results):
                    # Calculate simple relevance score based on position
                    relevance_score = 1.0 - (i * 0.1)

                    search_result = SearchResult(
                        title=result.get("title", ""),
                        url=result.get("href", ""),
                        snippet=result.get("body", ""),
                        relevance_score=max(0.1, relevance_score),
                    )
                    results.append(search_result)

            self.logger.info(f"Found {len(results)} search results for query: '{query}'")
            return results

        except Exception as e:
            self.logger.error(f"DuckDuckGo search failed: {e}")
            return []

    def _format_search_context(self, results: List[SearchResult], original_prompt: str) -> str:
        """
        Format search results into context for the LLM
        """
        if not results:
            return (
                f"No search results found. Please answer based on your training data.\n\n"
                f"Original question: {original_prompt}"
            )

        context = "Based on the following search results, please provide a comprehensive structured response:\n\n"
        context += "SEARCH RESULTS:\n"

        for i, result in enumerate(results, 1):
            context += f"\n{i}. {result.title}\n"
            context += f"   URL: {result.url}\n"
            context += f"   Content: {result.snippet}\n"
            context += f"   Relevance: {result.relevance_score:.2f}\n"

        context += f"\n\nORIGINAL QUESTION: {original_prompt}\n\n"
        context += (
            "Please synthesize the search results to provide an accurate, comprehensive, and well-structured response. "
        )
        context += "Cite relevant sources when applicable and indicate if information is current as of the search date."

        return context

    def _retry_search_with_strategies(self, original_query: str, max_attempts: int = 3) -> List[SearchResult]:
        """
        Retry search with different strategies if initial search fails
        """
        strategies = [
            original_query,  # Original query
            original_query.replace('"', ""),  # Remove quotes
            " ".join(original_query.split()[:5]),  # First 5 words only
            original_query.split()[0] if original_query.split() else original_query,  # Single most important term
        ]

        for attempt, query in enumerate(strategies[:max_attempts]):
            self.logger.info(f"Search attempt {attempt + 1} with query: '{query}'")
            results = self._perform_duckduckgo_search(query)

            if results:
                return results

            # Wait before retry
            if attempt < max_attempts - 1:
                time.sleep(1)

        return []

    def _generate_with_search_logging(
        self, prompt: str, output_model: Type[T], model: str, temperature: float, max_retries: int, search_type: str
    ) -> T:
        """Generate with search type logging"""
        # Track timing
        start_time = time.time()
        response_obj = None
        token_details = None
        error_info_str = None

        try:
            # Get client and provider info
            client = self.llm_client._get_client_for_model(model, enable_anthropic_search=False)
            provider, model_name = self.llm_client.determine_provider(model)

            messages = [{"role": "user", "content": prompt}]
            kwargs = {"messages": messages, "response_model": output_model, "max_retries": max_retries}

            if provider != "google":
                kwargs["model"] = model_name
                kwargs["temperature"] = temperature

                if provider == "anthropic":
                    kwargs["max_tokens"] = 1024
            else:
                if temperature != 0.0:
                    kwargs["generation_config"] = {"temperature": temperature}

            if provider == "google":
                response_obj = self.llm_client._handle_google_rate_limit_retry(
                    lambda: client.chat.completions.create(**kwargs), max_retries=max(max_retries, 3)
                )
            else:
                response_obj = client.chat.completions.create(**kwargs)

            # Extract token usage
            if (
                hasattr(response_obj, "_raw_response")
                and hasattr(response_obj._raw_response, "usage")
                and response_obj._raw_response.usage
            ):
                raw_usage = response_obj._raw_response.usage
                if hasattr(raw_usage, "input_tokens"):
                    token_details = {
                        "prompt_tokens": raw_usage.input_tokens,
                        "completion_tokens": raw_usage.output_tokens,
                        "total_tokens": raw_usage.input_tokens + raw_usage.output_tokens,
                    }
                else:
                    token_details = {
                        "prompt_tokens": raw_usage.prompt_tokens,
                        "completion_tokens": raw_usage.completion_tokens,
                        "total_tokens": raw_usage.total_tokens,
                    }
            elif hasattr(response_obj, "usage") and response_obj.usage:
                raw_usage = response_obj.usage
                if hasattr(raw_usage, "input_tokens"):
                    token_details = {
                        "prompt_tokens": raw_usage.input_tokens,
                        "completion_tokens": raw_usage.output_tokens,
                        "total_tokens": raw_usage.input_tokens + raw_usage.output_tokens,
                    }
                else:
                    token_details = {
                        "prompt_tokens": raw_usage.prompt_tokens,
                        "completion_tokens": raw_usage.completion_tokens,
                        "total_tokens": raw_usage.total_tokens,
                    }

            return response_obj

        except Exception as e:
            error_info_str = f"Error with {model}: {type(e).__name__} - {str(e)}"
            raise
        finally:
            # Calculate duration and log with search type
            duration_ms = int((time.time() - start_time) * 1000)

            # Extract schema for logging
            try:
                schema_json = json.dumps(output_model.model_json_schema(), default=str)
            except Exception:
                schema_json = None

            self.llm_client._log_interaction(
                model=model,
                prompt=prompt,
                response=response_obj,
                token_usage=token_details,
                error_info=error_info_str,
                duration_ms=duration_ms,
                search_type=search_type,
                request_schema=schema_json,
            )

    def search_and_generate(
        self, prompt: str, output_model: Type[T], model: str, temperature: float = 0.0, max_retries: int = 1
    ) -> T:
        """
        Main method: Execute 3-step DuckDuckGo search and generation

        Args:
            prompt: The input prompt
            output_model: Pydantic model class for structured output
            model: Model to use for generation
            temperature: Sampling temperature
            max_retries: Maximum number of retries

        Returns:
            Structured output of type output_model
        """
        start_time = time.time()

        try:
            self.logger.info(f"Starting DuckDuckGo 3-step search for model: {model}")

            # Step 1: Optimize search query
            self.logger.info("Step 1: Optimizing search query...")
            optimized = self._optimize_search_query(prompt, model)

            # Step 2: Perform search
            self.logger.info("Step 2: Executing DuckDuckGo search...")
            search_results = self._retry_search_with_strategies(optimized.search_query)

            # Step 3: Generate structured response with search context
            self.logger.info("Step 3: Generating structured response with search context...")
            search_context = self._format_search_context(search_results, prompt)

            # Use the LLM client to generate final response with search context logging
            response = self._generate_with_search_logging(
                search_context, output_model, model, temperature, max_retries, "duckduckgo_search"
            )

            elapsed_time = time.time() - start_time
            self.logger.info(f"DuckDuckGo 3-step search completed in {elapsed_time:.2f} seconds")

            return response

        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"DuckDuckGo search pipeline failed after {elapsed_time:.2f}s: {type(e).__name__} - {str(e)}"
            self.logger.error(error_msg)

            # Fallback: try to generate without search
            self.logger.warning("Falling back to generation without search...")
            try:
                # Extract schema for logging
                try:
                    schema_json = json.dumps(output_model.model_json_schema(), default=str)
                except Exception:
                    schema_json = None

                return self.llm_client._generate_standard(
                    prompt, output_model, model, temperature, max_retries, schema=schema_json
                )
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Both search and fallback generation failed. Search error: {error_msg}. "
                    f"Fallback error: {fallback_error}"
                ) from e
