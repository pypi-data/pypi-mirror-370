"""
DeepSeek-VL parser implementation.

This module provides a document parser using DeepSeek's DeepSeek-VL model
for multimodal document understanding with vision and language capabilities.
"""

import warnings
import os

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*image_processor_class.*")
warnings.filterwarnings("ignore", message=".*use_fast.*")
warnings.filterwarnings("ignore", message=".*legacy.*")
warnings.filterwarnings("ignore", message=".*device.*")

# Set environment variables to suppress tokenizer warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

try:
    from transformers import AutoModelForCausalLM
    from deepseek_vl.models import VLChatProcessor, MultiModalityCausalLM
    from deepseek_vl.utils.io import load_pil_images
    DEEPSEEK_VL_AVAILABLE = True
except ImportError:
    DEEPSEEK_VL_AVAILABLE = False
    AutoModelForCausalLM = None
    VLChatProcessor = None
    MultiModalityCausalLM = None
    load_pil_images = None

from typing import Dict, Any, Union, List, Optional
from pathlib import Path
import logging
import torch
from PIL import Image
import numpy as np

from .base_ai_parser import BaseAIParser


class DeepSeekVLParser(BaseAIParser):
    """
    Document parser using DeepSeek's DeepSeek-VL model.
    
    DeepSeek-VL is a multimodal model that combines vision and language
    understanding for document analysis. It's particularly effective for:
    - Document understanding and analysis
    - Visual question answering
    - Image captioning and description
    - Multimodal reasoning
    - Document OCR (e.g., Tesseract [key: 'tesseract']) and text extraction
    
    Attributes:
        model: DeepSeek-VL model for multimodal understanding
        processor: VLChatProcessor for input preprocessing
        tokenizer: Tokenizer for text processing
    """
    
    def __init__(self, 
                 model_name: str = "deepseek-ai/deepseek-vl-7b-chat",
                 device: str = "auto",
                 max_length: int = 2048,
                 temperature: float = 0.1,
                 device_mode: str = "auto",
                 **kwargs):
        """
        Initialize the DeepSeek-VL parser.
        
        Args:
            model_name: Hugging Face model name or path
            device: Device to run inference on (kept for compatibility, not used)
            max_length: Maximum sequence length for generation
            temperature: Temperature for text generation
            device_mode: 'auto', 'cuda', or 'cpu'.
                - 'auto': Use CUDA+bfloat16 if available, else CPU+float32 (default)
                - 'cuda': Force CUDA+bfloat16 (for GPU machines)
                - 'cpu': Force CPU+float32 (for Apple Silicon/CPU compatibility)
            **kwargs: Additional arguments passed to BaseAIParser
        """
        if not DEEPSEEK_VL_AVAILABLE:
            raise ImportError(
                "DeepSeek-VL library is not installed. "
                "To use the DeepSeek-VL parser, you must install it from source: "
                "\n\n"
                "    pip install git+https://github.com/deepseek-ai/DeepSeek-VL.git\n\n"
                "See the DocCraft README for more details."
            )
        
        self.max_length = max_length
        self.temperature = temperature
        self.device_mode = device_mode
        
        # Initialize the base AI parser
        super().__init__(model_name=model_name, device=device, **kwargs)
        
        self.logger.info(f"DeepSeek-VL parser initialized with model: {model_name}")
        self.logger.info(f"Max length: {max_length}, Temperature: {temperature}, Device mode: {self.device_mode}")
    
    def _initialize_model(self, **kwargs):
        """Initialize DeepSeek-VL model, processor, and tokenizer."""
        try:
            import torch
            import sys
            import io
            from deepseek_vl.utils.io import load_pil_images
            
            # Temporarily redirect stdout to suppress transformers warnings
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                # Load processor and tokenizer
                self.processor = VLChatProcessor.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir
                )
                self.tokenizer = self.processor.tokenizer
                
                # Load model with trust_remote_code
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir,
                    trust_remote_code=True
                )
            finally:
                # Restore stdout
                sys.stdout = old_stdout
            
            # Device logic
            mode = self.device_mode.lower() if hasattr(self, 'device_mode') else 'auto'
            if mode == 'cuda':
                self.model = self.model.to(torch.bfloat16).cuda().eval()
            elif mode == 'cpu':
                self.model = self.model.to(torch.float32).cpu().eval()
            else:  # auto
                if torch.cuda.is_available():
                    self.model = self.model.to(torch.bfloat16).cuda().eval()
                else:
                    self.model = self.model.to(torch.float32).cpu().eval()
            
        except Exception as e:
            raise ImportError(f"Failed to initialize DeepSeek-VL: {e}")
    
    def _get_model_version(self) -> str:
        """Get the version of the loaded DeepSeek-VL model."""
        try:
            import deepseek_vl
            # Check if __version__ exists, otherwise use a default
            if hasattr(deepseek_vl, '__version__'):
                return f"DeepSeek-VL-{deepseek_vl.__version__}"
            else:
                return "DeepSeek-VL-1.0.0"
        except ImportError:
            return "DeepSeek-VL-Unknown"
    
    def _process_with_ai(self, document: Image.Image, **kwargs) -> Dict[str, Any]:
        """
        Process the document with DeepSeek-VL model (official HuggingFace example style).
        """
        try:
            import torch
            from deepseek_vl.utils.io import load_pil_images
            # Get prompt from kwargs or use default
            prompt = kwargs.get('prompt', "Please extract and describe all the text content from this document image.")
            # Get the file path from kwargs (required for DeepSeek-VL)
            file_path = kwargs.get('file_path', None)
            if file_path is None:
                raise ValueError("file_path must be provided in kwargs for DeepSeek-VL parser.")
            # Prepare conversation as in the official example, using file path
            conversation = [
                {
                    "role": "User",
                    "content": f"<image_placeholder>Answer with ONLY the requested information. No explanations. No extra words. Just the answer. Question: {prompt}",
                    "images": [file_path]
                },
                {
                    "role": "Assistant",
                    "content": ""
                }
            ]
            # Use load_pil_images to ensure correct format
            pil_images = load_pil_images(conversation)
            prepare_inputs = self.processor(
                conversations=conversation,
                images=pil_images,
                force_batchify=True
            ).to(self.model.device)
            # Force float32 on CPU for all floating point tensors in prepare_inputs
            if self.model.device.type == 'cpu':
                import torch
                if hasattr(prepare_inputs, '__dict__'):
                    prepare_inputs_dict = dict(prepare_inputs.__dict__)
                else:
                    prepare_inputs_dict = dict(prepare_inputs)
                for k, v in prepare_inputs_dict.items():
                    if isinstance(v, torch.Tensor) and v.is_floating_point() and v.dtype != torch.float32:
                        prepare_inputs_dict[k] = v.float()
                prepare_inputs = type(prepare_inputs)(**prepare_inputs_dict)
            # Run image encoder to get the image embeddings
            inputs_embeds = self.model.prepare_inputs_embeds(**prepare_inputs)
            if self.model.device.type == 'cpu' and inputs_embeds.dtype != torch.float32:
                inputs_embeds = inputs_embeds.float()
            # Run the model to get the response
            outputs = self.model.language_model.generate(
                inputs_embeds=inputs_embeds,
                attention_mask=prepare_inputs.attention_mask,
                pad_token_id=self.tokenizer.eos_token_id,
                bos_token_id=self.tokenizer.bos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                max_new_tokens=kwargs.get('max_new_tokens', 512),
                do_sample=kwargs.get('do_sample', False),
                use_cache=True
            )
            answer = self.tokenizer.decode(outputs[0].cpu().tolist(), skip_special_tokens=True)
            # Optionally remove the prompt from the answer
            try:
                sft_format = prepare_inputs['sft_format'][0] if 'sft_format' in prepare_inputs else ''
            except (KeyError, IndexError, TypeError):
                sft_format = ''
            if answer.startswith(sft_format):
                answer = answer[len(sft_format):].strip()
            return {
                'text': answer,
                'confidence': 1.0,
                'predictions': {
                    'prompt': prompt,
                    'response': answer,
                    'model_name': self.model_name
                }
            }
        except Exception as e:
            import traceback
            self.logger.error(f"Error processing document with DeepSeek-VL: {e}")
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return {"error": str(e), "text": "", "confidence": 0.0}
    
    def ask_question(self, file_path: Union[str, Path], question: str, **kwargs) -> Dict[str, Any]:
        """
        Ask a specific question about a document.
        
        Args:
            file_path: Path to the document
            question: Question to ask about the document
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Answer and metadata
        """
        try:
            # Process with question, passing file_path for DeepSeek-VL
            result = self._process_with_ai(None, prompt=question, file_path=str(file_path), **kwargs)
            
            return {
                'question': question,
                'answer': result['text'],
                'confidence': result['confidence'],
                'file_path': str(file_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error asking question: {e}")
            return {"error": str(e), "answer": "", "confidence": 0.0}
    
    def extract_structured_info(self, file_path: Union[str, Path], 
                              fields: List[str], **kwargs) -> Dict[str, Any]:
        """
        Extract structured information from a document.
        
        Args:
            file_path: Path to the document
            fields: List of fields to extract (e.g., ["date", "amount", "sender"])
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Structured information
        """
        try:
            # Create a structured extraction prompt
            fields_str = ", ".join(fields)
            prompt = f"Please extract the following information from this document: {fields_str}. Return the results in a clear, structured format."
            
            # Load document
            document = self._load_document(file_path)
            
            # Process with structured extraction prompt
            result = self._process_with_ai(document, prompt=prompt, **kwargs)
            
            # For DeepSeek-VL, we'll return the raw response as structured data
            # since it doesn't have built-in JSON output capabilities
            structured_data = {"extracted_text": result['text'], "fields": fields}
            
            return {
                'fields': fields,
                'data': structured_data,
                'confidence': result['confidence'],
                'file_path': str(file_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting structured info: {e}")
            return {"error": str(e), "data": {}}
    
    def summarize_document(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Generate a summary of the document.
        
        Args:
            file_path: Path to the document
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, Any]: Document summary
        """
        prompt = "Please provide a comprehensive summary of this document, including key information, main points, and any important details."
        return self.ask_question(file_path, prompt, **kwargs)
    
    def set_generation_params(self, max_length: int = None, temperature: float = None):
        """
        Set generation parameters.
        
        Args:
            max_length: Maximum sequence length
            temperature: Temperature for generation
        """
        if max_length is not None:
            self.max_length = max_length
        if temperature is not None:
            self.temperature = temperature
        
        self.logger.info(f"Generation params updated: max_length={self.max_length}, temperature={self.temperature}")
    
    def get_model_capabilities(self) -> List[str]:
        """
        Get list of model capabilities.
        
        Returns:
            List[str]: Supported capabilities
        """
        return [
            "document_question_answering",
            "text_extraction",
            "document_summarization",
            "visual_reasoning",
            "image_captioning",
            "multimodal_understanding"
        ] 

    def _extract_text_impl(self, file_path: Union[str, Path], **kwargs) -> tuple[str, dict]:
        """
        Extract text from a document using DeepSeek-VL, consistent with other parsers.
        Args:
            file_path: Path to the document to parse
            **kwargs: Additional arguments for AI processing
        Returns:
            tuple[str, dict]: Tuple of (extracted_text, metadata)
        """
        # Load and preprocess the document (image or PDF as image)
        document = self._load_document(file_path)
        # Call the AI processor, always passing file_path as a keyword
        ai_result = self._process_with_ai(document, file_path=str(file_path), **kwargs)
        # Post-process the AI output
        extracted_text = self._post_process_ai_output(ai_result)
        # Prepare metadata
        metadata = self._prepare_metadata(file_path, ai_result, 0.0)  # extraction_time will be set by BaseParser
        return extracted_text, metadata 