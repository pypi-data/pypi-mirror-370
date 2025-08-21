"""
LayoutLMv3 parser implementation.

This module provides a document parser using Microsoft's LayoutLMv3 model
for structured document understanding with layout awareness.
"""

try:
    from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification, LayoutLMv3ForQuestionAnswering
    from transformers import LayoutLMv3FeatureExtractor, LayoutLMv3TokenizerFast
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    LayoutLMv3Processor = None
    LayoutLMv3ForSequenceClassification = None
    LayoutLMv3ForQuestionAnswering = None
    LayoutLMv3FeatureExtractor = None
    LayoutLMv3TokenizerFast = None

from typing import Dict, Any, Union, List, Optional
from pathlib import Path
import logging
import torch
from PIL import Image
import numpy as np
import pytesseract

from .base_ai_parser import BaseAIParser
from ..postprocessing import TextPostprocessor


class LayoutLMv3Parser(BaseAIParser):
    """
    Document parser using Microsoft's LayoutLMv3 model.
    
    LayoutLMv3 is a multimodal model that combines text, layout, and image
    information for document understanding. It's particularly effective for:
    - Form understanding and field extraction
    - Table structure analysis
    - Document classification
    - Named entity recognition in documents
    
    Attributes:
        model: LayoutLMv3 model for document understanding
        processor: LayoutLMv3 processor for input preprocessing
        feature_extractor: Feature extractor for image processing
        tokenizer: Fast tokenizer for text processing
        ocr_reader: EasyOCR reader for text extraction
    """
    
    def __init__(self, 
                 model_name: str = "rubentito/layoutlmv3-base-mpdocvqa",
                 device: str = "auto",
                 task: str = "question_answering",
                 **kwargs):
        """
        Initialize the LayoutLMv3 parser.
        
        Args:
            model_name: Hugging Face model name or path. Default is a model fine-tuned for DocVQA.
            device: Device to run inference on ("auto", "cpu", "cuda", "mps")
            task: Task type ("question_answering", "classification", "ner")
            **kwargs: Additional arguments passed to BaseAIParser
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers library is not installed. Please install it with: "
                "pip install transformers torch"
            )
        
        self.task = task
        self.model_name = model_name
        
        # Initialize the base AI parser
        super().__init__(model_name=model_name, device=device, **kwargs)
        
        # Initialize OCR reader for text extraction
        try:
            self.ocr_reader = pytesseract.pytesseract
        except ImportError:
            self.logger.warning("Tesseract OCR not available. Install with: pip install pytesseract")
            self.ocr_reader = None
        
        self.logger.info(f"LayoutLMv3 parser initialized with model: {model_name}")
        self.logger.info(f"Task: {task}, Device: {self.device}")
    
    def _initialize_model(self, **kwargs):
        """Initialize LayoutLMv3 model, processor, and tokenizer."""
        try:
            # Load processor (handles both text and image preprocessing)
            self.processor = LayoutLMv3Processor.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                apply_ocr=False  # Set to False so we can provide bounding boxes manually
            )
            
            # Load model based on task
            if self.task == "question_answering":
                # For question answering, use the QA model
                self.model = LayoutLMv3ForQuestionAnswering.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir
                )
            else:
                # For specific tasks, load appropriate model
                self.model = LayoutLMv3ForSequenceClassification.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir
                )
            
            # Move model to device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Load feature extractor and tokenizer separately for flexibility
            self.feature_extractor = LayoutLMv3FeatureExtractor.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir
            )
            self.tokenizer = LayoutLMv3TokenizerFast.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir
            )
            
        except Exception as e:
            raise ImportError(f"Failed to initialize LayoutLMv3: {e}")
    
    def _get_model_version(self) -> str:
        """Get the version of the loaded LayoutLMv3 model."""
        try:
            import transformers
            return f"LayoutLMv3-{transformers.__version__}"
        except ImportError:
            return "LayoutLMv3-Unknown"
    
    def _extract_ocr_text_and_boxes(self, document: Image.Image) -> tuple:
        """
        Extract OCR text and bounding boxes from document image using Tesseract.
        
        Args:
            document: PIL Image of the document
            
        Returns:
            tuple: (words, boxes) where words is list of strings and boxes is list of [x0, y0, x1, y1]
        """
        if self.ocr_reader is None:
            # Fallback: return empty text
            return [], []
        
        try:
            # Get image dimensions for normalization
            img_width, img_height = document.size
            
            # Run Tesseract OCR to get data
            data = pytesseract.image_to_data(document, output_type=pytesseract.Output.DICT)
            
            words = []
            boxes = []
            
            # Process each detected text element
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = data['conf'][i]
                
                # Only process text with confidence > 30 and non-empty text
                if text and conf > 30:
                    # Get bounding box coordinates
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # Normalize coordinates to [0, 1000] range as expected by LayoutLMv3
                    x0_norm = int((x / img_width) * 1000)
                    y0_norm = int((y / img_height) * 1000)
                    x1_norm = int(((x + w) / img_width) * 1000)
                    y1_norm = int(((y + h) / img_height) * 1000)
                    
                    # Ensure coordinates are within bounds
                    x0_norm = max(0, min(x0_norm, 1000))
                    y0_norm = max(0, min(y0_norm, 1000))
                    x1_norm = max(0, min(x1_norm, 1000))
                    y1_norm = max(0, min(y1_norm, 1000))
                    
                    words.append(text)
                    boxes.append([x0_norm, y0_norm, x1_norm, y1_norm])
            
            return words, boxes
            
        except Exception as e:
            self.logger.error(f"Error in OCR extraction: {e}")
            return [], []
    
    def _process_with_ai(self, document: Image.Image, **kwargs) -> Dict[str, Any]:
        """
        Process the document with LayoutLMv3 model.
        
        Args:
            document: PIL Image of the document
            **kwargs: Additional processing arguments
            
        Returns:
            Dict[str, Any]: LayoutLMv3 model output
        """
        try:
            # Prepare inputs for LayoutLMv3
            inputs = self._prepare_inputs(document, **kwargs)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Process outputs based on task
            if self.task == "question_answering":
                return self._process_question_answering_output(outputs, inputs)
            elif self.task == "classification":
                return self._process_classification_output(outputs)
            elif self.task == "ner":
                return self._process_ner_output(outputs, inputs)
            else:
                return self._process_generic_output(outputs)
                
        except Exception as e:
            self.logger.error(f"Error processing document with LayoutLMv3: {e}")
            return {"error": str(e), "text": ""}
    
    def _prepare_inputs(self, document: Image.Image, **kwargs) -> Dict[str, torch.Tensor]:
        """
        Prepare inputs for LayoutLMv3 model.
        
        Args:
            document: PIL Image of the document
            **kwargs: Additional arguments including 'prompt' for question
            
        Returns:
            Dict[str, torch.Tensor]: Model inputs
        """
        # Get question from kwargs
        question = kwargs.get('prompt', "What is the main content of this document?")
        
        # Extract OCR text and bounding boxes
        words, boxes = self._extract_ocr_text_and_boxes(document)
        
        # Defensive check: log and raise if mismatch
        if len(words) != len(boxes):
            print(f"[LayoutLMv3] ERROR: Number of words ({len(words)}) does not match number of boxes ({len(boxes)})")
            print(f"First 5 words: {words[:5]}")
            print(f"First 5 boxes: {boxes[:5]}")
            raise ValueError(f"Number of words ({len(words)}) does not match number of boxes ({len(boxes)})")
        
        # If no OCR text found, use a fallback
        if not words:
            words = ["document", "text", "content"]
            boxes = [[0, 0, 1000, 1000]]  # Normalized fallback box
        
        # Ensure all box coordinates are integers
        boxes = [[int(coord) for coord in box] for box in boxes]
        
        # Use processor to prepare inputs for question answering
        encoding = self.processor(
            document,
            question,
            words,
            boxes=boxes,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        # Cast all floating-point tensors to float32 and all integer tensors to int64 (Long)
        for key, value in encoding.items():
            if isinstance(value, torch.Tensor):
                if torch.is_floating_point(value):
                    value = value.to(torch.float32)
                elif value.dtype in [torch.int32, torch.int16, torch.int8, torch.uint8]:
                    value = value.to(torch.int64)
                encoding[key] = value.to(self.device)
        
        return encoding
    

    
    def _process_classification_output(self, outputs) -> Dict[str, Any]:
        """
        Process outputs for classification tasks.
        
        Args:
            outputs: Model outputs
            
        Returns:
            Dict[str, Any]: Classification results
        """
        probs = torch.softmax(outputs.logits, dim=-1)
        predicted_class = torch.argmax(probs, dim=-1).item()
        confidence = probs.max().item()
        
        return {
            'text': f"Class {predicted_class}",
            'confidence': confidence,
            'predictions': {
                'class': predicted_class,
                'probabilities': probs.cpu().numpy().tolist()
            }
        }
    
    def _process_ner_output(self, outputs, inputs) -> Dict[str, Any]:
        """
        Process outputs for named entity recognition.
        
        Args:
            outputs: Model outputs
            inputs: Model inputs
            
        Returns:
            Dict[str, Any]: NER results
        """
        # Extract predictions
        predictions = torch.argmax(outputs.logits, dim=-1)
        
        # Convert to tokens and labels
        input_ids = inputs['input_ids'][0]
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids)
        
        entities = []
        current_entity = None
        
        for token, pred in zip(tokens, predictions[0]):
            if token in ['[CLS]', '[SEP]', '[PAD]']:
                continue
            
            label = self.model.config.id2label[pred.item()]
            
            if label.startswith('B-'):
                if current_entity:
                    entities.append(current_entity)
                current_entity = {'text': token, 'label': label[2:]}
            elif label.startswith('I-') and current_entity:
                current_entity['text'] += ' ' + token
            else:
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None
        
        if current_entity:
            entities.append(current_entity)
        
        # Extract text
        text = ' '.join([entity['text'] for entity in entities])
        
        return {
            'text': text,
            'confidence': float(torch.softmax(outputs.logits, dim=-1).max()),
            'predictions': {
                'entities': entities,
                'tokens': tokens,
                'labels': [self.model.config.id2label[p.item()] for p in predictions[0]]
            }
        }
    
    def _process_question_answering_output(self, outputs, inputs) -> Dict[str, Any]:
        """
        Process outputs for question answering.
        
        Args:
            outputs: Model outputs
            inputs: Model inputs
            
        Returns:
            Dict[str, Any]: Question answering results
        """
        # Extract the answer span
        answer_start = torch.argmax(outputs.start_logits, dim=-1).item()
        answer_end = torch.argmax(outputs.end_logits, dim=-1).item()
        
        # Get input IDs and decode the answer span properly
        input_ids = inputs['input_ids'][0]
        
        # Use processor to decode the answer span
        try:
            # Extract the answer span tokens
            answer_ids = input_ids[answer_start:answer_end + 1]
            
            # Decode using the processor's tokenizer
            answer_text = self.tokenizer.decode(answer_ids, skip_special_tokens=True)
            
            # If that doesn't work well, try manual detokenization
            if not answer_text or answer_text.strip() == "":
                tokens = self.tokenizer.convert_ids_to_tokens(answer_ids)
                # Remove special tokens and clean up
                tokens = [token for token in tokens if token not in ['[CLS]', '[SEP]', '[PAD]']]
                answer_text = ' '.join(tokens)
                # Basic cleanup
                answer_text = answer_text.replace('Ġ', ' ').replace('_', ' ')
                answer_text = ' '.join(answer_text.split())  # Normalize whitespace
                
        except Exception as e:
            self.logger.warning(f"Error decoding answer span: {e}")
            # Fallback to raw token conversion
            tokens = self.tokenizer.convert_ids_to_tokens(input_ids)
            answer_text = ' '.join(tokens[answer_start:answer_end + 1])
        
        return {
            'text': answer_text,
            'confidence': float(torch.softmax(outputs.start_logits, dim=-1).max()),
            'predictions': {
                'answer_text': answer_text,
                'answer_start': answer_start,
                'answer_end': answer_end,
                'logits': outputs.start_logits.cpu().numpy().tolist()
            }
        }
    
    def _process_generic_output(self, outputs) -> Dict[str, Any]:
        """
        Process outputs for generic tasks.
        
        Args:
            outputs: Model outputs
            
        Returns:
            Dict[str, Any]: Generic results
        """
        return {
            'text': "LayoutLMv3 processing completed",
            'confidence': 1.0,
            'predictions': {
                'logits': outputs.logits.cpu().numpy().tolist(),
                'hidden_states': outputs.hidden_states[-1].cpu().numpy().tolist() if hasattr(outputs, 'hidden_states') else None
            }
        }
    
    def extract_layout_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract layout information from a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Dict[str, Any]: Layout information including bounding boxes, text regions, etc.
        """
        try:
            # Load document
            document = self._load_document(file_path)
            
            # Extract features using feature extractor
            features = self.feature_extractor(document, return_tensors="pt")
            
            # Get bounding boxes and other layout information
            layout_info = {
                'image_size': document.size,
                'bbox': features['bbox'].tolist(),
                'attention_mask': features['attention_mask'].tolist(),
                'pixel_values': features['pixel_values'].shape
            }
            
            return layout_info
            
        except Exception as e:
            self.logger.error(f"Error extracting layout info: {e}")
            return {"error": str(e)}
    
    def set_task(self, task: str):
        """
        Change the task type for the model.
        
        Args:
            task: New task type ("question_answering", "classification", "ner")
        """
        self.task = task
        self.logger.info(f"Task changed to: {task}")
    
    def get_supported_tasks(self) -> List[str]:
        """
        Get list of supported tasks.
        
        Returns:
            List[str]: Supported task types
        """
        return ["question_answering", "classification", "ner"]
    
    def _clean_answer_text(self, text: str) -> str:
        """
        Clean answer text by removing tokenization artifacts and applying OCR-specific cleaning.
        
        Args:
            text: Raw answer text from the model
            
        Returns:
            str: Cleaned answer text
        """
        if not text:
            return ""
        
        # Remove tokenization artifacts
        cleaned_text = text.replace('Ġ', ' ')  # Remove Ġ characters
        cleaned_text = cleaned_text.replace('_', ' ')  # Replace underscores with spaces
        
        # Apply OCR-specific text cleaning
        try:
            text_postprocessor = TextPostprocessor()
            cleaned_text, _ = text_postprocessor.clean_for_ocr(
                cleaned_text,
                remove_extra_whitespace=True,
                fix_line_breaks=True,
                fix_common_ocr_errors=True,
                normalize_quotes=True
            )
        except Exception as e:
            self.logger.warning(f"Error in text postprocessing: {e}")
            # Fallback: basic cleaning
            import re
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text

    def ask_question(self, file_path: Union[str, Path], question: str, **kwargs) -> Dict[str, Any]:
        """
        Ask a specific question about a document image using LayoutLMv3.
        Args:
            file_path: Path to the document image
            question: The question to ask
            **kwargs: Additional arguments
        Returns:
            Dict[str, Any]: Answer and metadata
        """
        try:
            document = self._load_document(file_path)
            # Use the question as a prompt (if supported by the model)
            # For now, just pass as a kwarg to _process_with_ai
            result = self._process_with_ai(document, prompt=question, **kwargs)
            
            # Clean the answer text
            raw_answer = result.get('text', '')
            cleaned_answer = self._clean_answer_text(raw_answer)
            
            # Include predictions for debugging if available
            out = {
                'question': question,
                'answer': cleaned_answer,
                'raw_answer': raw_answer,  # Keep original for debugging
                'confidence': result.get('confidence', 1.0),
                'file_path': str(file_path)
            }
            if 'predictions' in result:
                out['predictions'] = result['predictions']
            return out
        except Exception as e:
            self.logger.error(f"Error asking question: {e}")
            return {"error": str(e), "answer": ""} 