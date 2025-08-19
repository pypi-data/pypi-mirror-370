"""LLM post-processing module for HIL responses using DSPy."""

import logging
from typing import Optional

# Basic LiteLLM logging control (fastapi dependency now satisfied)
import os
os.environ["LITELLM_SUPPRESS_DEBUG_INFO"] = "true"

try:
    import dspy
except ImportError:
    dspy = None

from ..config import LLMConfig

logger = logging.getLogger(__name__)


class TextEnhancementSignature(dspy.Signature):
    """Enhance user text input while preserving meaning and context."""
    
    original_text: str = dspy.InputField(
        desc="Original user input text"
    )
    user_instruction: str = dspy.InputField(
        desc="Additional context or instructions from user"
    )
    input_type: str = dspy.InputField(
        desc="Type of input: 'text' or 'voice_transcription'"
    )
    
    enhanced_text: str = dspy.OutputField(
        desc="Enhanced, structured, and improved text while preserving original meaning"
    )


class TranscriptionEnhancementSignature(dspy.Signature):
    """Improve voice transcription with careful attention to preserving context."""
    
    transcription: str = dspy.InputField(
        desc="Raw voice transcription that may contain errors"
    )
    user_instruction: str = dspy.InputField(
        desc="User's additional context or clarification"
    )
    question_context: str = dspy.InputField(
        desc="Original question or context that prompted this response"
    )
    
    improved_text: str = dspy.OutputField(
        desc="Carefully improved transcription with preserved meaning and context. CRITICAL: Do not change the fundamental meaning or add information not implied in the original transcription. Focus on fixing obvious transcription errors, improving clarity, and structuring the text while maintaining the user's original intent and voice."
    )


class HILPostProcessorError(Exception):
    """HIL post-processor error."""
    pass


class HILPostProcessor:
    """DSPy-based post-processor for HIL responses."""
    
    def __init__(self, llm_config: LLMConfig):
        self.config = llm_config
        self.lm = None
        self.text_enhancer = None
        self.transcription_enhancer = None
        
        if dspy is None:
            logger.warning("DSPy not available. LLM post-processing will be disabled.")
            self.config.enabled = False
            return
        
        if llm_config.enabled:
            self._initialize_dspy()
    
    def _initialize_dspy(self):
        """Initialize DSPy with configured LM."""
        try:
            # Further suppress LiteLLM debug output during initialization
            import litellm
            litellm.suppress_debug_info = True
            litellm.set_verbose = False
            
            # Configure LM - all endpoints are OpenAI-compatible
            if self.config.base_url:
                # Custom OpenAI-compatible endpoint
                self.lm = dspy.LM(
                    model=self.config.model,
                    api_key=self.config.api_key,
                    api_base=self.config.base_url,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                provider_info = f"custom endpoint ({self.config.base_url})"
            else:
                # Standard OpenAI API
                self.lm = dspy.LM(
                    model=f"openai/{self.config.model}",
                    api_key=self.config.api_key,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                provider_info = "OpenAI API"
            
            # Configure DSPy
            dspy.configure(lm=self.lm)
            
            # Initialize predictors
            self.text_enhancer = dspy.Predict(TextEnhancementSignature)
            self.transcription_enhancer = dspy.Predict(TranscriptionEnhancementSignature)
            
            logger.info(f"DSPy initialized with {provider_info}, model: {self.config.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize DSPy: {e}")
            raise HILPostProcessorError(f"Failed to initialize DSPy: {e}")
    
    def enhance_text_response(
        self, 
        text: str, 
        user_instruction: str = "",
        is_transcription: bool = False,
        question_context: str = ""
    ) -> str:
        """Enhance text response using LLM."""
        
        if not self.config.enabled or not text.strip():
            return text
        
        if dspy is None:
            logger.warning("DSPy not available, returning original text")
            return text
        
        try:
            if is_transcription and self.transcription_enhancer:
                result = self.transcription_enhancer(
                    transcription=text,
                    user_instruction=user_instruction or "Please improve this transcription",
                    question_context=question_context
                )
                logger.debug(f"Enhanced transcription: {text[:50]}... -> {result.improved_text[:50]}...")
                return result.improved_text
            elif self.text_enhancer:
                result = self.text_enhancer(
                    original_text=text,
                    user_instruction=user_instruction or "Please structure and enhance this text",
                    input_type="voice_transcription" if is_transcription else "text"
                )
                logger.debug(f"Enhanced text: {text[:50]}... -> {result.enhanced_text[:50]}...")
                return result.enhanced_text
            else:
                logger.warning("No DSPy predictors available, returning original text")
                return text
                
        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
            # Fallback to original text if enhancement fails
            return text
    
    def is_enabled(self) -> bool:
        """Check if post-processing is enabled and available."""
        return self.config.enabled and dspy is not None and self.lm is not None