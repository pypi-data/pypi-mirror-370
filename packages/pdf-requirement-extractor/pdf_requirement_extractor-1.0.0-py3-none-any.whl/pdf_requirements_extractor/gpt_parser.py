"""
Optional GPT-based summarization for structured brand requirement parsing.
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
    """Configuration for GPT parsing."""
    
    model: str  # Model name must be specified (e.g., "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo")
    temperature: float = 0.3
    max_tokens: int = 1500
    timeout: int = 30
    api_key: Optional[str] = None
    
    @classmethod
    def create_default(cls, model: str = "gpt-4o-mini", **kwargs) -> "GPTConfig":
        """
        Create a GPTConfig with default settings.
        
        Args:
            model: GPT model name (default: "gpt-4o-mini")
            **kwargs: Additional configuration options
            
        Returns:
            GPTConfig: Configured instance
        """
        return cls(model=model, **kwargs)
    
    @classmethod 
    def for_cost_effective(cls, **kwargs) -> "GPTConfig":
        """Create configuration optimized for cost-effectiveness."""
        return cls(model="gpt-3.5-turbo", temperature=0.3, max_tokens=1000, **kwargs)
    
    @classmethod
    def for_high_quality(cls, **kwargs) -> "GPTConfig":
        """Create configuration optimized for highest quality results."""
        return cls(model="gpt-4", temperature=0.2, max_tokens=2000, **kwargs)
    
    @classmethod
    def for_fast_processing(cls, **kwargs) -> "GPTConfig":
        """Create configuration optimized for fast processing."""
        return cls(model="gpt-3.5-turbo", temperature=0.1, max_tokens=800, **kwargs)
    
    @classmethod
    def for_mini_model(cls, **kwargs) -> "GPTConfig":
        """Create configuration using GPT-4o-mini for cost-effective high quality."""
        return cls(model="gpt-4o-mini", temperature=0.3, max_tokens=1200, **kwargs)


class GPTParser:
    """
    GPT-based parser for extracting structured requirements from text.
    """
    
    def __init__(self, config: Optional[GPTConfig] = None, api_key: Optional[str] = None):
        """
        Initialize GPT parser.
        
        Args:
            config: GPT configuration
            api_key: OpenAI API key
            
        Raises:
            ImportError: If OpenAI package not available
            ValueError: If no API key provided
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
        Parse requirements from text using GPT.
        
        Args:
            text: Text to parse
            existing_data: Existing extraction data to enhance
            
        Returns:
            Dict[str, Any]: Enhanced requirements dictionary
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
        Enhance existing requirements using GPT analysis.
        
        Args:
            requirements: Existing requirements dictionary
            original_text: Original PDF text
            
        Returns:
            Dict[str, Any]: Enhanced requirements
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
        """Build the GPT prompt for requirement extraction."""
        
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
        """Get the system prompt for GPT."""
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
        """Get the system prompt for requirement enhancement."""
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
        """Extract JSON from GPT response text if direct parsing fails."""
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
    High-level parser that combines regex extraction with GPT enhancement.
    """
    
    def __init__(self, gpt_config: Optional[GPTConfig] = None, api_key: Optional[str] = None):
        """
        Initialize the combined parser.
        
        Args:
            gpt_config: Configuration for GPT
            api_key: OpenAI API key
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
