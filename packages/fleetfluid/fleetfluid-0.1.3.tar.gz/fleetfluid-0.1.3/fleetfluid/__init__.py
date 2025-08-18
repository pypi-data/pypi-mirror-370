"""
FleetFluid - AI Agent Functions for ETL Processing

A Python package providing AI-powered agent functions for data transformation,
text processing, and intelligent data manipulation in ETL pipelines.
"""

from .core import FleetFluid, SingleLabelResult, MultipleLabelResult

# Global instance
_instance = None

def init(model: str = "openai:gpt-4", **kwargs) -> None:
    """
    Initialize FleetFluid with model configuration.
    
    Args:
        model: Model identifier (e.g., "openai:gpt-4", "anthropic:claude-3-sonnet")
        **kwargs: Additional configuration passed to PydanticAI agents
    """
    global _instance
    _instance = FleetFluid(model=model, **kwargs)

def ai(prompt: str, data: str) -> str:
    """
    Apply AI transformation to data using the given prompt.
    
    Args:
        prompt: Instruction for the AI (e.g., "write it grammatically correct")
        data: Input data to transform
        
    Returns:
        Transformed data as string
        
    Raises:
        RuntimeError: If FleetFluid hasn't been initialized
    """
    if _instance is None:
        raise RuntimeError("FleetFluid not initialized. Call fleetfluid.init() first.")
    return _instance.ai(prompt, data)

def label(text: str, labels: list[str], multiple: bool = False):
    """
    Label text using AI agent with structured output.
    
    Args:
        text: Input text to label
        labels: List of possible labels to choose from
        multiple: If True, select multiple labels; if False, select single best label
        
    Returns:
        Structured result with selected label(s) and confidence scores
        
    Raises:
        RuntimeError: If FleetFluid not initialized. Call fleetfluid.init() first.
    """
    if _instance is None:
        raise RuntimeError("FleetFluid not initialized. Call fleetfluid.init() first.")
    return _instance.label(text, labels, multiple)

def anonymize(text: str) -> str:
    """
    Anonymize personal information in text using AI.
    
    Args:
        text: Input text containing personal information to anonymize
        
    Returns:
        Anonymized text with personal information replaced by placeholders
        
    Raises:
        RuntimeError: If FleetFluid hasn't been initialized
    """
    if _instance is None:
        raise RuntimeError("FleetFluid not initialized. Call fleetfluid.init() first.")
    return _instance.anonymize(text)

def describe(features: dict, style: str = "natural") -> str:
    """
    Generate a meaningful text description from a dictionary of features.
    
    Args:
        features: Dictionary of product/object features
        style: Description style ("natural", "marketing", "technical", "casual")
        
    Returns:
        Natural language description of the features
        
    Raises:
        RuntimeError: If FleetFluid hasn't been initialized
    """
    if _instance is None:
        raise RuntimeError("FleetFluid not initialized. Call fleetfluid.init() first.")
    return _instance.describe(features, style)

def extract(extraction_type: str, text: str) -> list:
    """
    Extract specific types of information from text using AI.
    
    Args:
        extraction_type: Type of information to extract (e.g., "skills", "countries", "companies", "technologies")
        text: Input text to extract information from
        
    Returns:
        List of extracted items
        
    Raises:
        RuntimeError: If FleetFluid hasn't been initialized
    """
    if _instance is None:
        raise RuntimeError("FleetFluid not initialized. Call fleetfluid.init() first.")
    return _instance.extract(extraction_type, text)

# Version info
__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "AI Agent Functions for ETL Processing"

# Export main functions and classes
__all__ = ["init", "ai", "label", "anonymize", "describe", "extract", "SingleLabelResult", "MultipleLabelResult"]