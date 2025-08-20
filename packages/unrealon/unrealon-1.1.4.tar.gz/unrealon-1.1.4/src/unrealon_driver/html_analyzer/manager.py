"""
HTML Analyzer Manager - Main interface for HTML analysis operations.
"""

from typing import Optional, Tuple
from unrealon_driver.smart_logging import create_smart_logger

from .config import HTMLAnalyzerConfig, HTMLCleaningConfig
from .cleaner import HTMLCleaner, HTMLCleaningStats
from .websocket_analyzer import WebSocketHTMLAnalyzer
from .models import HTMLAnalysisResult, HTMLParseResult, HTMLAnalyzerStats, HTMLAnalysisRequest, HTMLParseRequest, HTMLAnalyzerError, HTMLCleaningError, HTMLAnalysisError


class HTMLAnalyzer:
    """
    🧠 HTML Analyzer - Complete HTML processing and analysis system

    Features:
    - Smart HTML cleaning with noise removal
    - JavaScript data extraction
    - WebSocket-based LLM analysis
    - Token-optimized output
    - Configurable cleaning strategies
    """

    def __init__(self, config: HTMLAnalyzerConfig):
        self.config = config
        self.logger = create_smart_logger(parser_id=config.parser_id)

        # Initialize components
        self.cleaner = HTMLCleaner(parser_id=config.parser_id, config=config.cleaning_config)

        # Initialize WebSocket analyzer if enabled
        if config.enable_websocket_analysis and config.websocket_url:
            self.websocket_analyzer = WebSocketHTMLAnalyzer(config)
        else:
            self.websocket_analyzer = None

    async def analyze_html(self, html: str, instructions: Optional[str] = None, session_id: Optional[str] = None, clean_first: bool = True, preserve_js_data: bool = True, aggressive_cleaning: bool = False, **kwargs) -> HTMLAnalysisResult:
        """
        Complete HTML analysis workflow

        Args:
            html: Raw HTML content
            instructions: Analysis instructions for LLM
            session_id: Session identifier
            clean_first: Whether to clean HTML before analysis
            preserve_js_data: Whether to extract JavaScript data
            aggressive_cleaning: Whether to apply aggressive cleaning
            **kwargs: Additional parameters

        Returns:
            Analysis result with cleaned HTML and extracted data
        """
        try:
            self.logger.info("🧠 Starting HTML analysis workflow")

            # Initialize result with proper typing
            result_data = {"success": True, "original_html_size": len(html), "cleaned_html": html, "extracted_data": {}, "analysis_result": {}, "cleaning_stats": {}, "error_message": ""}

            # Step 1: Clean HTML if requested
            if clean_first:
                cleaned_html, extracted_data = await self.cleaner.clean_html(html, preserve_js_data=preserve_js_data, aggressive_cleaning=aggressive_cleaning)

                result_data["cleaned_html"] = cleaned_html
                result_data["extracted_data"] = extracted_data
                result_data["cleaned_html_size"] = len(cleaned_html)

                # Get cleaning statistics
                stats = self.cleaner.get_cleaning_stats(html, cleaned_html)
                result_data["cleaning_stats"] = stats.model_dump()

                self.logger.info(f"✅ HTML cleaned: {len(html)} → {len(cleaned_html)} chars")
            else:
                result_data["cleaned_html_size"] = len(html)

            # Step 2: Perform LLM analysis via WebSocket if available
            if self.websocket_analyzer and instructions:
                analysis_result = await self.websocket_analyzer.analyze_html(result_data["cleaned_html"], instructions=instructions, session_id=session_id, **kwargs)
                result_data["analysis_result"] = analysis_result

                if analysis_result.get("success") == "true":
                    self.logger.info("✅ LLM analysis completed successfully")
                else:
                    self.logger.warning(f"⚠️ LLM analysis failed: {analysis_result.get('error_message')}")
            else:
                if not self.websocket_analyzer:
                    self.logger.info("ℹ️ WebSocket analyzer not configured - skipping LLM analysis")
                else:
                    self.logger.info("ℹ️ No instructions provided - skipping LLM analysis")

            return HTMLAnalysisResult.model_validate(result_data)

        except Exception as e:
            self.logger.error(f"❌ HTML analysis failed: {str(e)}")
            error_result = {"success": False, "original_html_size": len(html), "cleaned_html": "", "cleaned_html_size": 0, "extracted_data": {}, "analysis_result": {}, "cleaning_stats": {}, "error_message": str(e)}
            return HTMLAnalysisResult.model_validate(error_result)

    async def clean_html_only(self, html: str, preserve_js_data: bool = True, aggressive_cleaning: bool = False) -> Tuple[str, dict[str, str]]:
        """
        Clean HTML without LLM analysis

        Args:
            html: Raw HTML content
            preserve_js_data: Whether to extract JavaScript data
            aggressive_cleaning: Whether to apply aggressive cleaning

        Returns:
            Tuple of (cleaned_html, extracted_data)
        """
        return await self.cleaner.clean_html(html, preserve_js_data=preserve_js_data, aggressive_cleaning=aggressive_cleaning)

    async def analyze_with_llm_only(self, html: str, instructions: str, session_id: Optional[str] = None, **kwargs) -> dict[str, str]:
        """
        Perform LLM analysis without cleaning

        Args:
            html: HTML content (should be pre-cleaned)
            instructions: Analysis instructions
            session_id: Session identifier
            **kwargs: Additional parameters

        Returns:
            LLM analysis result
        """
        if not self.websocket_analyzer:
            return {"success": "false", "parsed_data": "", "markdown": "", "error_message": "WebSocket analyzer not configured"}

        return await self.websocket_analyzer.analyze_html(html, instructions=instructions, session_id=session_id, **kwargs)

    async def parse_html(self, html: str, url: Optional[str] = None, instructions: Optional[str] = None, session_id: Optional[str] = None, **kwargs) -> HTMLParseResult:
        """
        Complete HTML parsing workflow: clean → analyze.

        This is the main method that should be used by ParserManager.
        Returns standardized string-based result format.

        Args:
            html: Raw HTML content
            url: Source URL (for logging)
            instructions: Optional analysis instructions
            session_id: Optional session ID
            **kwargs: Additional parameters

        Returns:
            Standardized parsing result dictionary with string values
        """
        try:
            if url:
                self.logger.info(f"🔄 Processing HTML from {url}: {len(html)} characters")
            else:
                self.logger.info(f"🔄 Processing HTML: {len(html)} characters")

            # Use existing analyze_html method
            result = await self.analyze_html(html=html, instructions=instructions, session_id=session_id, **kwargs)

            # Convert to standardized string format for ParserManager
            if result.success:
                analysis_result = result.analysis_result
                return HTMLParseResult(success="true", parsed_data=str(analysis_result.get("parsed_data", "")), markdown=str(analysis_result.get("markdown", "")), error_message="")
            else:
                return HTMLParseResult(success="false", parsed_data="", markdown="", error_message=result.error_message or "Analysis failed")

        except Exception as e:
            self.logger.error(f"❌ HTML parsing failed: {str(e)}")
            return HTMLParseResult(success="false", parsed_data="", markdown="", error_message=str(e))

    def get_cleaning_stats(self, original_html: str, cleaned_html: str) -> HTMLCleaningStats:
        """Get cleaning statistics"""
        return self.cleaner.get_cleaning_stats(original_html, cleaned_html)

    def get_stats(self) -> HTMLAnalyzerStats:
        """Get HTML analyzer statistics"""
        return HTMLAnalyzerStats(cleaned_count=getattr(self.cleaner, "_cleaned_count", 0), total_reduction=getattr(self.cleaner, "_total_reduction", 0.0), websocket_enabled=self.websocket_analyzer is not None)

    async def close(self):
        """Close all resources"""
        if self.websocket_analyzer:
            await self.websocket_analyzer.close()
        self.logger.info("🔌 HTML Analyzer closed")


def create_html_analyzer(parser_id: str, websocket_url: Optional[str] = None, api_key: Optional[str] = None, cleaning_config: Optional[HTMLCleaningConfig] = None, **kwargs) -> HTMLAnalyzer:
    """
    Create HTML analyzer with configuration

    Args:
        parser_id: Parser identifier
        websocket_url: WebSocket URL for LLM analysis (optional, auto-detected if not provided)
        api_key: API key for authentication
        cleaning_config: HTML cleaning configuration
        **kwargs: Additional configuration options

    Returns:
        Configured HTMLAnalyzer instance
    """
    # Only pass websocket_url if explicitly provided, otherwise use auto-detection
    config_kwargs = {"parser_id": parser_id, "api_key": api_key, "cleaning_config": cleaning_config or HTMLCleaningConfig(), **kwargs}
    if websocket_url is not None:
        config_kwargs["websocket_url"] = websocket_url
    
    config = HTMLAnalyzerConfig(**config_kwargs)

    return HTMLAnalyzer(config)


# Convenience functions
async def quick_analyze_html(html: str, parser_id: str, instructions: Optional[str] = None, websocket_url: Optional[str] = None, **kwargs) -> HTMLAnalysisResult:
    """
    Quick HTML analysis convenience function

    Args:
        html: Raw HTML content
        instructions: Analysis instructions
        parser_id: Parser identifier
        websocket_url: WebSocket URL for analysis (optional, auto-detected if not provided)
        **kwargs: Additional options

    Returns:
        Analysis result
    """
    analyzer = create_html_analyzer(parser_id=parser_id, websocket_url=websocket_url, **kwargs)

    try:
        return await analyzer.analyze_html(html, instructions=instructions, **kwargs)
    finally:
        await analyzer.close()


async def quick_clean_html(html: str, parser_id: str, **kwargs) -> Tuple[str, dict[str, str]]:
    """
    Quick HTML cleaning convenience function

    Args:
        html: Raw HTML content
        parser_id: Parser identifier
        **kwargs: Cleaning options

    Returns:
        Tuple of (cleaned_html, extracted_data)
    """
    analyzer = create_html_analyzer(parser_id=parser_id)

    try:
        return await analyzer.clean_html_only(html, **kwargs)
    finally:
        await analyzer.close()
