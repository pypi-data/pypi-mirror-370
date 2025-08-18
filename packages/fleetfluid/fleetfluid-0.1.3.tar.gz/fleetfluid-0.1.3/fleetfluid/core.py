"""
Core FleetFluid implementation with PydanticAI agents.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName


class SingleLabelResult(BaseModel):
    """Result for single label classification."""
    label: str = Field(description="The selected label from the provided options")
    confidence: float = Field(description="Confidence score between 0 and 1", ge=0, le=1)
    reasoning: str = Field(description="Brief explanation of why this label was chosen")


class MultipleLabelResult(BaseModel):
    """Result for multiple label classification."""
    labels: List[str] = Field(description="List of selected labels from the provided options")
    confidence_scores: Dict[str, float] = Field(description="Confidence score for each selected label")
    reasoning: str = Field(description="Brief explanation of why these labels were chosen")


class FleetFluid:
    """Main FleetFluid class containing AI agent functions."""
    
    def __init__(self, model: str = "openai:gpt-4", **kwargs):
        """
        Initialize FleetFluid with model configuration.
        
        Args:
            model: Model identifier for PydanticAI
            **kwargs: Additional configuration for PydanticAI agents
        """
        self.model = model
        self.agent_config = kwargs
        self._ai_agent: Optional[Agent] = None
        self._label_agent: Optional[Agent] = None
    
    def _get_ai_agent(self) -> Agent:
        """Lazy initialization of the AI transformation agent."""
        if self._ai_agent is None:
            # Extract model settings from agent_config
            model_settings = {}
            agent_kwargs = {}
            
            for key, value in self.agent_config.items():
                if key in ['temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty']:
                    model_settings[key] = value
                else:
                    agent_kwargs[key] = value
            
            # Create ModelSettings if we have model-specific parameters
            if model_settings:
                from pydantic_ai.models import ModelSettings
                agent_kwargs['model_settings'] = ModelSettings(model_settings)
            
            self._ai_agent = Agent(
                model=self.model,
                system_prompt=(
                    "You are a helpful AI assistant specialized in text transformation and processing. "
                    "You will receive a transformation prompt and input data. "
                    "Apply the requested transformation accurately and return only the transformed result. "
                    "Do not include explanations, markdown formatting, or additional text unless specifically requested."
                ),
                **agent_kwargs
            )
        return self._ai_agent
    
    def _get_label_agent(self) -> Agent:
        """Lazy initialization of the labeling agent."""
        if self._label_agent is None:
            # Extract model settings from agent_config
            model_settings = {}
            agent_kwargs = {}
            
            for key, value in self.agent_config.items():
                if key in ['temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty']:
                    model_settings[key] = value
                else:
                    agent_kwargs[key] = value
            
            # Create ModelSettings if we have model-specific parameters
            if model_settings:
                from pydantic_ai.models import ModelSettings
                agent_kwargs['model_settings'] = ModelSettings(model_settings)
            
            self._label_agent = Agent(
                model=self.model,
                system_prompt=(
                    "You are a specialized AI assistant for text classification and labeling. "
                    "You will receive text content and a list of possible labels. "
                    "Your task is to select the most appropriate label(s) based on the content. "
                    "Be precise and thoughtful in your selection, considering the context and meaning of the text."
                ),
                **agent_kwargs
            )
        return self._label_agent
    
    def ai(self, prompt: str, data: str) -> str:
        """
        Apply AI transformation to data using the given prompt.
        
        This is a synchronous wrapper around the async PydanticAI agent.
        
        Args:
            prompt: Instruction for the AI (e.g., "write it grammatically correct", "translate to Spanish")
            data: Input data to transform
            
        Returns:
            Transformed data as string
        """
        return asyncio.run(self._ai_async(prompt, data))
    
    def label(self, text: str, labels: List[str], multiple: bool = False) -> Union[SingleLabelResult, MultipleLabelResult]:
        """
        Label text using AI agent with structured output.
        
        Args:
            text: Input text to label
            labels: List of possible labels to choose from
            multiple: If True, select multiple labels; if False, select single best label
            
        Returns:
            Structured result with selected label(s) and confidence scores
        """
        return asyncio.run(self._label_async(text, labels, multiple))
    
    async def _ai_async(self, prompt: str, data: str) -> str:
        """Async implementation of AI transformation."""
        agent = self._get_ai_agent()
        
        # Combine the transformation prompt with the data
        full_prompt = f"{prompt}\n\nInput data: {data}"
        
        try:
            result = await agent.run(full_prompt)
            return str(result.output)
        except Exception as e:
            raise RuntimeError(f"AI transformation failed: {str(e)}") from e
    
    async def _label_async(self, text: str, labels: List[str], multiple: bool = False) -> Union[SingleLabelResult, MultipleLabelResult]:
        """Async implementation of labeling."""
        agent = self._get_label_agent()
        
        # Create the prompt for labeling
        labels_str = ", ".join(labels)
        if multiple:
            prompt = f"""
            Analyze the following text and select the most appropriate labels from the provided options.
            
            Text: {text}
            Available labels: {labels_str}
            
            Select multiple labels that best describe the text content. You can choose one or more labels as appropriate.
            """
            result_class = MultipleLabelResult
        else:
            prompt = f"""
            Analyze the following text and select the single most appropriate label from the provided options.
            
            Text: {text}
            Available labels: {labels_str}
            
            Select the single best label that most accurately describes the text content.
            """
            result_class = SingleLabelResult
        
        try:
            # Use the correct PydanticAI structured output approach
            result = await agent.run(prompt, output_type=result_class)
            return result.output
        except Exception as e:
            raise RuntimeError(f"Labeling failed: {str(e)}") from e
    
    async def ai_async(self, prompt: str, data: str) -> str:
        """
        Async version of ai() method for use in async contexts.
        
        Args:
            prompt: Instruction for the AI
            data: Input data to transform
            
        Returns:
            Transformed data as string
        """
        return await self._ai_async(prompt, data)
    
    async def label_async(self, text: str, labels: List[str], multiple: bool = False) -> Union[SingleLabelResult, MultipleLabelResult]:
        """
        Async version of label() method for use in async contexts.
        
        Args:
            text: Input text to label
            labels: List of possible labels to choose from
            multiple: If True, select multiple labels; if False, select single best label
            
        Returns:
            Structured result with selected label(s) and confidence scores
        """
        return await self._label_async(text, labels, multiple)
    
    def anonymize(self, text: str) -> str:
        """
        Anonymize personal information in text using AI.
        
        This is a synchronous wrapper around the async PydanticAI agent.
        
        Args:
            text: Input text containing personal information to anonymize
            
        Returns:
            Anonymized text with personal information replaced by placeholders
        """
        return asyncio.run(self._anonymize_async(text))
    
    async def _anonymize_async(self, text: str) -> str:
        """Async implementation of text anonymization."""
        agent = self._get_ai_agent()
        
        # Create the anonymization prompt
        prompt = f"""
        Anonymize the following text by replacing personal information with appropriate placeholders.
        
        Replace:
        - Names with [NAME]
        - Email addresses with [EMAIL]
        - Phone numbers with [PHONE]
        - Addresses with [ADDRESS]
        - Social security numbers with [SSN]
        - Credit card numbers with [CARD_NUMBER]
        - Any other personally identifiable information with appropriate placeholders
        
        Input text: {text}
        
        Return only the anonymized text without explanations or additional formatting.
        """
        
        try:
            result = await agent.run(prompt)
            return str(result.output)
        except Exception as e:
            raise RuntimeError(f"Anonymization failed: {str(e)}") from e
    
    async def anonymize_async(self, text: str) -> str:
        """
        Async version of anonymize() method for use in async contexts.
        
        Args:
            text: Input text containing personal information to anonymize
            
        Returns:
            Anonymized text with personal information replaced by placeholders
        """
        return await self._anonymize_async(text)
    
    def describe(self, features: Dict[str, Any], style: str = "natural") -> str:
        """
        Generate a meaningful text description from a dictionary of features.
        
        This is a synchronous wrapper around the async PydanticAI agent.
        
        Args:
            features: Dictionary of product/object features
            style: Description style ("natural", "marketing", "technical", "casual")
            
        Returns:
            Natural language description of the features
        """
        return asyncio.run(self._describe_async(features, style))
    
    async def _describe_async(self, features: Dict[str, Any], style: str = "natural") -> str:
        """Async implementation of feature description generation."""
        agent = self._get_ai_agent()
        
        # Convert features dict to a readable format
        features_str = ", ".join([f"{key}: {value}" for key, value in features.items()])
        
        prompt = f"""
        Create a meaningful text description based on the following features.
        
        Features: {features_str}
        Style: Write that text in {style} style.
        
        Combine the features into a coherent, natural sentence that flows well.
        Do not list the features separately - integrate them naturally.
        Return only the description without explanations or additional formatting.
        """
        
        try:
            result = await agent.run(prompt)
            return str(result.output)
        except Exception as e:
            raise RuntimeError(f"Description generation failed: {str(e)}") from e
    
    async def describe_async(self, features: Dict[str, Any], style: str = "natural") -> str:
        """
        Async version of describe() method for use in async contexts.
        
        Args:
            features: Dictionary of product/object features
            style: Description style ("natural", "marketing", "technical", "casual")
            
        Returns:
            Natural language description of the features
        """
        return await self._describe_async(features, style)
    
    def extract(self, extraction_type: str, text: str) -> List[str]:
        """
        Extract specific types of information from text using AI.
        
        This is a synchronous wrapper around the async PydanticAI agent.
        
        Args:
            extraction_type: Type of information to extract (e.g., "skills", "countries", "companies", "technologies")
            text: Input text to extract information from
            
        Returns:
            List of extracted items
        """
        return asyncio.run(self._extract_async(extraction_type, text))
    
    async def _extract_async(self, extraction_type: str, text: str) -> List[str]:
        """Async implementation of information extraction."""
        agent = self._get_ai_agent()
        
        prompt = f"""
        Extract {extraction_type} from the following text.
        
        Text: {text}
        
        Return only a list of {extraction_type}, one per line, without explanations or additional formatting.
        If no {extraction_type} are found, return an empty list.
        Be thorough and extract both explicit and implicit {extraction_type} mentioned in the text.
        """
        
        try:
            result = await agent.run(prompt)
            # Parse the result to extract individual items
            extracted_text = str(result.output).strip()
            
            if not extracted_text:
                return []
            
            # Split by newlines and clean up each item
            items = [item.strip() for item in extracted_text.split('\n') if item.strip()]
            
            # Remove any bullet points or numbering if present
            cleaned_items = []
            for item in items:
                # Remove common list markers
                cleaned = item.lstrip('•-*0123456789. ')
                if cleaned:
                    cleaned_items.append(cleaned)
            
            return cleaned_items
            
        except Exception as e:
            raise RuntimeError(f"Information extraction failed: {str(e)}") from e
    
    async def extract_async(self, extraction_type: str, text: str) -> List[str]:
        """
        Async version of extract() method for use in async contexts.
        
        Args:
            extraction_type: Type of information to extract (e.g., "skills", "countries", "companies", "technologies")
            text: Input text to extract information from
            
        Returns:
            List of extracted items
        """
        return await self._extract_async(extraction_type, text)
    