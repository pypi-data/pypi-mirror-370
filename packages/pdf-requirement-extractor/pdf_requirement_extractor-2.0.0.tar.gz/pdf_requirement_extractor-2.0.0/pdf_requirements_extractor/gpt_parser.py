"""
Optional GPT-based enhancement for structured brand requirement parsing.

This module provides GPT-powered analysis capabilities to enhance the basic
regex-based extraction with AI-driven insights. It can:

- Parse complex brand requirements using natural language understanding
- Enhance existing extraction results with structured analysis
- Provide strategic insights and priority levels for requirements
- Categorize and organize brand elements intelligently
- Generate implementation recommendations

Key Features:
- Multiple GPT model support (GPT-3.5, GPT-4, GPT-4.1-mini, etc.)
- Configurable temperature and token limits
- Factory methods for common use cases
- Comprehensive error handling
- Fallback to regex results if GPT fails

Classes:
    GPTConfig: Configuration for GPT model parameters
    GPTParser: Core GPT-based parsing engine
    GPTRequirementParser: High-level interface combining regex and GPT

Example:
    >>> config = GPTConfig(model="gpt-4.1-mini", temperature=0.3)
    >>> parser = GPTRequirementParser(gpt_config=config, api_key="sk-...")
    >>> enhanced = parser.parse_with_gpt(text, existing_requirements)
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    OpenAI = None

logger = logging.getLogger(__name__)


@dataclass
class GPTConfig:
    """
    Configuration for GPT-powered parsing operations.
    
    This class encapsulates all the parameters needed to configure GPT model
    behavior for brand requirement extraction and enhancement. It provides
    factory methods for common use cases and validation of parameters.
    
    Attributes:
        model (str): GPT model name (e.g., "gpt-4.1-mini", "gpt-4", "gpt-3.5-turbo")
        temperature (float): Creativity level from 0.0 (deterministic) to 1.0 (creative)
        max_tokens (int): Maximum tokens in the response
        timeout (int): Request timeout in seconds
        api_key (Optional[str]): OpenAI API key (can be set via environment variable)
        
    Factory Methods:
        create_default(): Default configuration with gpt-4.1-mini
        for_cost_effective(): Optimized for low cost (gpt-3.5-turbo)
        for_high_quality(): Optimized for quality (gpt-4)
        for_fast_processing(): Optimized for speed (gpt-3.5-turbo)
        for_mini_model(): Cost-effective high quality (gpt-4.1-mini)
        
    Example:
        >>> # Explicit configuration
        >>> config = GPTConfig(model="gpt-4.1-mini", temperature=0.3)
        >>> 
        >>> # Using factory method
        >>> config = GPTConfig.for_high_quality()
    """
    
    model: str  # Model name must be specified (e.g., "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo")
    temperature: float = 0.3
    max_tokens: int = 1500
    timeout: int = 30
    api_key: Optional[str] = None
    
    @classmethod
    def create_default(cls, model: str = "gpt-4.1-mini", **kwargs) -> "GPTConfig":
        """
        Create a default configuration with balanced performance and cost.
        
        Uses gpt-4.1-mini as the default model, which offers high quality output
        at a reasonable cost with good speed. Temperature is set to 0.3 for
        consistent but slightly creative responses.
        
        Args:
            model (str): GPT model name (default: "gpt-4.1-mini")
            **kwargs: Additional configuration options to override defaults
            
        Returns:
            GPTConfig: Default configuration suitable for most use cases
            
        Example:
            >>> config = GPTConfig.create_default()
            >>> parser = GPTParser(config)
            >>> 
            >>> # Custom model with default settings
            >>> config = GPTConfig.create_default(model="gpt-4", temperature=0.2)
        """
        return cls(model=model, **kwargs)
    
    @classmethod 
    def for_cost_effective(cls, **kwargs) -> "GPTConfig":
        """
        Create a cost-optimized configuration using GPT-3.5-turbo.
        
        This configuration prioritizes low cost over quality, suitable for
        large-scale processing or when budget constraints are primary concerns.
        Uses moderate temperature for reliable responses while keeping costs low.
        
        Args:
            **kwargs: Additional configuration options to override defaults
            
        Returns:
            GPTConfig: Cost-optimized configuration
            
        Example:
            >>> config = GPTConfig.for_cost_effective()
            >>> # Process large batches with lower per-request cost
            >>> parser = GPTParser(config)
        """
        return cls(model="gpt-3.5-turbo", temperature=0.3, max_tokens=1000, **kwargs)
    
    @classmethod
    def for_high_quality(cls, **kwargs) -> "GPTConfig":
        """
        Create a high-quality configuration using GPT-4.
        
        This configuration prioritizes output quality and accuracy over cost
        and speed. Uses low temperature for consistent, deterministic responses
        with extended token limits for comprehensive analysis.
        
        Args:
            **kwargs: Additional configuration options to override defaults
            
        Returns:
            GPTConfig: High-quality configuration
            
        Example:
            >>> config = GPTConfig.for_high_quality()
            >>> # For critical documents requiring maximum accuracy
            >>> parser = GPTParser(config)
        """
        return cls(model="gpt-4", temperature=0.2, max_tokens=2000, **kwargs)
    
    @classmethod
    def for_fast_processing(cls, **kwargs) -> "GPTConfig":
        """
        Create a speed-optimized configuration.
        
        This configuration prioritizes response speed using GPT-3.5-turbo
        with reduced token limits and shorter timeouts. Suitable for real-time
        applications or when quick processing is required.
        
        Args:
            **kwargs: Additional configuration options to override defaults
            
        Returns:
            GPTConfig: Speed-optimized configuration
            
        Example:
            >>> config = GPTConfig.for_fast_processing()
            >>> # For real-time or interactive applications
            >>> parser = GPTParser(config)
        """
        return cls(model="gpt-3.5-turbo", temperature=0.1, max_tokens=800, **kwargs)
    
    @classmethod
    def for_mini_model(cls, **kwargs) -> "GPTConfig":
        """
        Create a configuration using the cost-effective GPT-4o-mini model.
        
        This configuration uses GPT-4o-mini which provides high-quality output
        similar to GPT-4 but at a significantly lower cost. Ideal for production
        environments where quality and cost-effectiveness are both important.
        
        Args:
            **kwargs: Additional configuration options to override defaults
            
        Returns:
            GPTConfig: GPT-4o-mini configuration
            
        Example:
            >>> config = GPTConfig.for_mini_model()
            >>> # Best balance of quality and cost for production use
            >>> parser = GPTParser(config)
        """
        return cls(model="gpt-4o-mini", temperature=0.3, max_tokens=1200, **kwargs)


class GPTParser:
    """
    GPT-based parser for extracting and enhancing structured requirements from text.
    
    This class provides a high-level interface for using OpenAI's GPT models to analyze
    and structure brand requirement text extracted from PDFs. It handles API communication,
    error management, and response parsing to provide clean, structured output.
    
    The parser can enhance basic text extraction by:
    - Categorizing requirements by type (visual, content, technical, etc.)
    - Extracting key-value pairs and structured data
    - Identifying missing or ambiguous requirements
    - Providing summaries and recommendations
    
    Attributes:
        config (GPTConfig): Configuration settings for GPT model behavior
        client: OpenAI client instance for API communication
        
    Example:
        >>> # Basic usage
        >>> config = GPTConfig.create_default()
        >>> parser = GPTParser(config)
        >>> result = parser.parse("Brand guidelines specify...")
        >>> 
        >>> # High-quality parsing for critical documents
        >>> config = GPTConfig.for_high_quality()
        >>> parser = GPTParser(config, api_key="your-key")
        >>> enhanced_result = parser.enhance_extraction(extracted_text)
    """
    
    def __init__(self, config: Optional[GPTConfig] = None, api_key: Optional[str] = None):
        """
        Initialize GPT parser with configuration and API credentials.
        
        Sets up the parser with the specified configuration and establishes
        connection to OpenAI API. Falls back to environment variables for
        API key if not provided directly.
        
        Args:
            config (Optional[GPTConfig]): GPT configuration. If None, uses default config
            api_key (Optional[str]): OpenAI API key. If None, looks for OPENAI_API_KEY env var
            
        Raises:
            ImportError: If OpenAI package is not installed
            ValueError: If no API key is provided and OPENAI_API_KEY env var is not set
            
        Example:
            >>> # Using environment variable for API key
            >>> parser = GPTParser()
            >>> 
            >>> # Explicit configuration and API key
            >>> config = GPTConfig.for_high_quality()
            >>> parser = GPTParser(config, api_key="sk-...")
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package required for GPT parsing. Install with: pip install openai"
            )
        
        if config is None:
            raise ValueError(
                "GPTConfig must be provided with a model name. "
                "Example: GPTConfig(model='gpt-3.5-turbo')"
            )
        
        self.config = config
        
        # Set API key
        if api_key:
            self.config.api_key = api_key
        
        if not self.config.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or provide api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.config.api_key)
        
        logger.info(f"Initialized GPTParser with model: {self.config.model}")
    
    def parse_requirements(self, text: str, existing_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parse and structure requirements from text using GPT analysis.
        
        This method sends the provided text to the GPT model for intelligent analysis
        and structuring. It can work with raw text or enhance existing extraction data
        by adding context, categorization, and missing information.
        
        The method constructs an appropriate prompt based on whether existing data
        is provided, sends the request to the GPT API, and parses the structured
        response into a standardized dictionary format.
        
        Args:
            text (str): Raw text content to analyze for requirements
            existing_data (Optional[Dict[str, Any]]): Previously extracted data to enhance.
                If provided, GPT will build upon this existing structure rather than
                starting from scratch.
                
        Returns:
            Dict[str, Any]: Structured requirements dictionary containing:
                - requirements: List of categorized requirement items
                - categories: Identified requirement categories
                - summary: Overall analysis summary
                - confidence: Confidence scores for extracted items
                - suggestions: Recommendations for improvement
                
        Raises:
            Exception: If GPT API call fails or response parsing encounters errors
            
        Example:
            >>> parser = GPTParser(GPTConfig.create_default())
            >>> text = "Brand logo must be prominently displayed..."
            >>> result = parser.parse_requirements(text)
            >>> print(result['requirements'])
            >>> 
            >>> # Enhance existing extraction
            >>> enhanced = parser.parse_requirements(text, existing_data=basic_extraction)
        """
        try:
            prompt = self._build_prompt(text, existing_data)
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout
            )
            
            result_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                parsed_result = json.loads(result_text)
                logger.info("Successfully parsed requirements with GPT")
                return parsed_result
            except json.JSONDecodeError:
                logger.warning("GPT response was not valid JSON, extracting manually")
                return self._extract_json_from_text(result_text)
            
        except Exception as e:
            logger.error(f"GPT parsing failed: {str(e)}")
            return existing_data or {}
    
    def enhance_requirements(self, requirements: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """
        Enhance existing requirements dictionary using GPT analysis.
        
        This method takes an existing requirements structure and uses GPT to add
        deeper analysis, categorization, and contextual information. It's particularly
        useful for refining basic pattern-based extraction results with AI insights.
        
        The enhancement process includes:
        - Adding missing requirement categories
        - Improving categorization and tagging
        - Identifying relationships between requirements
        - Adding confidence scores and analysis notes
        - Suggesting improvements or clarifications
        
        Args:
            requirements (Dict[str, Any]): Existing requirements dictionary to enhance.
                Should contain basic requirement structure from pattern extraction.
            original_text (str): Original PDF text content for additional context.
                Used to verify and expand upon the existing requirements.
                
        Returns:
            Dict[str, Any]: Enhanced requirements dictionary with:
                - Improved categorization and structure
                - Additional analysis and context
                - Confidence scores for each requirement
                - Suggestions for missing or unclear items
                - Cross-references between related requirements
                
        Raises:
            Exception: If GPT API call fails or enhancement process encounters errors
            
        Example:
            >>> basic_reqs = extractor.extract_requirements(pdf_path)
            >>> enhanced_reqs = parser.enhance_requirements(basic_reqs, original_text)
            >>> # Enhanced version includes AI-driven insights and improvements
        """
        try:
            prompt = f"""
            Please enhance these extracted brand requirements with additional context and analysis:
            
            Existing Requirements:
            {json.dumps(requirements, indent=2)}
            
            Original Text (excerpt):
            {original_text[:2000]}...
            
            Please provide:
            1. Enhanced categorization of requirements
            2. Priority levels for each requirement
            3. Implementation suggestions
            4. Brand consistency analysis
            5. Missing elements that should be considered
            
            Return as JSON with the same structure plus your enhancements.
            """
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self._get_enhancement_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout
            )
            
            result_text = response.choices[0].message.content
            
            try:
                enhanced_result = json.loads(result_text)
                logger.info("Successfully enhanced requirements with GPT")
                return enhanced_result
            except json.JSONDecodeError:
                logger.warning("GPT enhancement response was not valid JSON")
                return requirements
            
        except Exception as e:
            logger.error(f"GPT enhancement failed: {str(e)}")
            return requirements
    
    def _build_prompt(self, text: str, existing_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Build the GPT prompt for requirement extraction based on input context.
        
        Constructs an appropriate prompt for the GPT model based on whether this is
        a fresh extraction or an enhancement of existing data. The prompt includes
        specific instructions for brand requirement analysis and output formatting.
        
        Args:
            text (str): The text content to analyze
            existing_data (Optional[Dict[str, Any]]): Previous extraction data if available
            
        Returns:
            str: Formatted prompt string ready for GPT API
            
        Note:
            Text is truncated to first 3000 characters to stay within token limits
            while preserving the most important content (usually at document start).
        """
        
        base_prompt = f"""
        Extract structured brand requirements from this PDF text. Focus on:
        
        1. Brand Guidelines & Standards
        2. Logo Usage Rules
        3. Color Specifications (hex, RGB, CMYK, Pantone)
        4. Typography & Font Requirements
        5. Tone of Voice & Messaging
        6. Visual Style Guidelines
        7. Usage Restrictions
        8. Contact Information
        9. File Formats & Technical Specs
        10. Compliance Requirements
        
        Text to analyze:
        {text[:3000]}...
        
        """
        
        if existing_data:
            base_prompt += f"""
            
            Existing extracted data to enhance:
            {json.dumps(existing_data, indent=2)}
            """
        
        base_prompt += """
        
        Return a JSON object with this structure:
        {
            "brand_name": "string",
            "document_type": "string",
            "primary_colors": ["color specifications"],
            "secondary_colors": ["color specifications"],
            "fonts": {
                "primary": "font name",
                "secondary": "font name",
                "body": "font name"
            },
            "logo_requirements": {
                "minimum_size": "specification",
                "clear_space": "specification",
                "usage_rules": ["rule1", "rule2"],
                "prohibited_uses": ["prohibition1", "prohibition2"]
            },
            "tone_of_voice": {
                "personality": ["traits"],
                "style": "description",
                "do_say": ["examples"],
                "dont_say": ["examples"]
            },
            "technical_specs": {
                "file_formats": ["formats"],
                "dimensions": ["specs"],
                "resolution": "specification"
            },
            "contact_info": {
                "emails": ["emails"],
                "websites": ["urls"],
                "phones": ["phone numbers"]
            },
            "compliance_notes": ["important notes"],
            "additional_requirements": ["other requirements"]
        }
        """
        
        return base_prompt
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt that defines GPT's role and behavior for extraction.
        
        This system prompt establishes the AI's expertise and provides specific
        instructions for analyzing brand guideline documents. It emphasizes
        accuracy, specificity, and proper JSON formatting.
        
        Returns:
            str: System prompt that configures GPT as a brand guidelines analyst
        """
        return """
        You are an expert brand guidelines analyst. Your task is to extract structured 
        brand requirements from PDF documents with high accuracy and attention to detail.
        
        Focus on:
        - Precise color specifications (exact hex codes, Pantone numbers)
        - Specific font names and usage rules
        - Detailed logo usage guidelines
        - Technical specifications for files and dimensions
        - Brand voice and messaging guidelines
        - Compliance and legal requirements
        
        Always return valid JSON. If information is unclear or missing, use null or empty arrays.
        Be specific and avoid generic terms.
        """
    
    def _get_enhancement_system_prompt(self) -> str:
        """
        Get the system prompt for requirement enhancement and strategic analysis.
        
        This prompt configures GPT to act as a brand strategy consultant, focusing
        on adding strategic insights and implementation guidance to extracted data
        rather than just extracting raw information.
        
        Returns:
            str: System prompt for enhancement-focused analysis
        """
        return """
        You are a brand strategy consultant specializing in brand guideline implementation.
        Your task is to enhance extracted brand requirements with strategic insights,
        priority levels, and implementation recommendations.
        
        For each requirement, consider:
        - Strategic importance to brand consistency
        - Implementation difficulty and cost
        - Impact on brand recognition
        - Compliance risk levels
        - Missing elements that should be addressed
        
        Provide actionable insights while maintaining the original data structure.
        """
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON data from GPT response text when direct parsing fails.
        
        This method handles cases where GPT includes additional text around the JSON
        response or when the JSON is malformed. It uses multiple strategies to find
        and extract valid JSON content from the response.
        
        Extraction strategies:
        1. Look for JSON wrapped in code blocks (```json...```)
        2. Find JSON object boundaries using braces
        3. Extract the largest valid JSON structure found
        
        Args:
            text (str): GPT response text that may contain JSON
            
        Returns:
            Dict[str, Any]: Extracted JSON data or empty dict if extraction fails
            
        Note:
            This is a fallback method used when the primary JSON parsing fails.
            Logs warnings when extraction is necessary and errors when it fails.
        """
        try:
            # Look for JSON block in markdown
            import re
            json_pattern = r'```(?:json)?\n(.*?)\n```'
            match = re.search(json_pattern, text, re.DOTALL)
            
            if match:
                json_text = match.group(1)
                return json.loads(json_text)
            
            # Try to find JSON object
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_text = text[start:end]
                return json.loads(json_text)
            
            logger.warning("Could not extract JSON from GPT response")
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting JSON from text: {str(e)}")
            return {}


class GPTRequirementParser:
    """
    High-level parser that combines regex-based extraction with GPT enhancement.
    
    This class provides a unified interface that leverages both pattern-based extraction
    for reliable basic data collection and GPT-powered analysis for intelligent enhancement
    and contextualization. It represents the recommended approach for production use.
    
    The combined approach offers:
    - Fast, reliable pattern-based extraction for structured data
    - Intelligent AI enhancement for context and analysis
    - Graceful fallback when AI services are unavailable
    - Cost optimization through selective AI usage
    
    Attributes:
        gpt_parser (Optional[GPTParser]): GPT enhancement engine (None if unavailable)
        use_gpt (bool): Whether GPT enhancement is available and configured
        
    Example:
        >>> # Full AI-enhanced parsing
        >>> parser = GPTRequirementParser(gpt_config=GPTConfig.create_default())
        >>> result = parser.parse_document(pdf_path)
        >>> 
        >>> # Pattern-only parsing (fallback mode)
        >>> parser = GPTRequirementParser()  # No GPT config
        >>> result = parser.parse_document(pdf_path)  # Uses patterns only
    """
    
    def __init__(self, gpt_config: Optional[GPTConfig] = None, api_key: Optional[str] = None):
        """
        Initialize the combined parser with optional GPT enhancement.
        
        Creates a parser that can use both pattern-based extraction and GPT enhancement.
        If GPT configuration is not provided or fails to initialize, the parser will
        fall back to pattern-based extraction only.
        
        Args:
            gpt_config (Optional[GPTConfig]): Configuration for GPT enhancement.
                If None, only pattern-based extraction will be used.
            api_key (Optional[str]): OpenAI API key for GPT services.
                If None, looks for OPENAI_API_KEY environment variable.
                
        Example:
            >>> # AI-enhanced parser
            >>> config = GPTConfig.for_high_quality()
            >>> parser = GPTRequirementParser(config, api_key="sk-...")
            >>> 
            >>> # Pattern-only parser (no AI costs)
            >>> parser = GPTRequirementParser()
        """
        self.gpt_parser = None
        
        if OPENAI_AVAILABLE and (api_key or gpt_config):
            try:
                self.gpt_parser = GPTParser(gpt_config, api_key)
                logger.info("GPT enhancement enabled")
            except Exception as e:
                logger.warning(f"Could not initialize GPT parser: {str(e)}")
        else:
            logger.info("GPT enhancement disabled (no API key or OpenAI not available)")
    
    def parse_with_gpt(self, 
                      text: str, 
                      regex_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parse requirements using GPT, optionally enhancing regex results.
        
        Args:
            text: Original text to parse
            regex_results: Results from regex-based extraction
            
        Returns:
            Dict[str, Any]: Parsed requirements
        """
        if not self.gpt_parser:
            logger.warning("GPT parser not available, returning regex results")
            return regex_results or {}
        
        try:
            # Use GPT to parse or enhance results
            if regex_results:
                return self.gpt_parser.enhance_requirements(regex_results, text)
            else:
                return self.gpt_parser.parse_requirements(text)
                
        except Exception as e:
            logger.error(f"GPT parsing failed: {str(e)}")
            return regex_results or {}
    
    def is_available(self) -> bool:
        """Check if GPT parsing is available."""
        return self.gpt_parser is not None
