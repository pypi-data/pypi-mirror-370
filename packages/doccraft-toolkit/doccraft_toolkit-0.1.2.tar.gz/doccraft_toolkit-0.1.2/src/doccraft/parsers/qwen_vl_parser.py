from .base_ai_parser import BaseAIParser
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
from PIL import Image
import torch
import os
import re

class QwenVLParser(BaseAIParser):
    def __init__(self, model_name: str = "Qwen/Qwen-VL-Chat", device: str = "auto", device_mode: str = "auto", **kwargs):
        self.device_mode = device_mode
        super().__init__(model_name=model_name, device=device, **kwargs)

    def _initialize_model(self, **kwargs):
        # Force CPU usage to avoid device placement issues
        device_map = "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map=device_map,
            trust_remote_code=True,
            torch_dtype=torch.float32  # Use float32 for CPU
        ).eval()
        # Optionally set generation config
        try:
            self.model.generation_config = GenerationConfig.from_pretrained(self.model_name, trust_remote_code=True)
        except Exception:
            pass  # Not all models have this

    def _get_model_version(self) -> str:
        return getattr(self.model.config, 'version', 'unknown')

    def _process_with_ai(self, document, question: str = None, image_path: str = None, **kwargs):
        # document is a PIL Image, image_path is the file path
        if question is None:
            question = "What does this image show?"
        if image_path is None:
            raise ValueError("image_path must be provided for Qwen-VL parser.")
        
        # Use model.chat() method for cleaner responses
        query = f'<img>{image_path}</img>{question}'
        
        try:
            response, history = self.model.chat(self.tokenizer, query=query, history=None)
            print(f"Qwen-VL | Question: {question}\nQwen-VL | Answer: {response}\n")
            return {'answer': response, 'confidence': 1.0, 'raw_answer': response}
        except Exception as e:
            # Fallback to original method if chat fails
            full_question = f"Answer this question about the image: {question}"
            query = self.tokenizer.from_list_format([
                {'image': image_path},
                {'text': full_question}
            ])
            # Ensure pad token is set and distinct from eos token
            if self.tokenizer.pad_token is None or self.tokenizer.pad_token == self.tokenizer.eos_token:
                self.tokenizer.add_special_tokens({'pad_token': '<|pad|>'})
                self.model.resize_token_embeddings(len(self.tokenizer))
            inputs = self.tokenizer(query, return_tensors='pt', padding=True, return_attention_mask=True)
            inputs = inputs.to(self.model.device)
            
            with torch.no_grad():
                pred = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    max_new_tokens=50,
                    do_sample=False
                )
            
            response = self.tokenizer.decode(pred.cpu()[0], skip_special_tokens=True)
            
            # Post-process: extract answer after the last question
            answer = response
            idx = response.rfind('?')
            if idx != -1:
                after_q = response[idx+1:]
                lines = [line.strip() for line in after_q.splitlines() if line.strip()]
                if lines:
                    answer = lines[0]
            print(f"Qwen-VL | Question: {question}\nQwen-VL | Answer: {answer}\n")
            return {'answer': answer, 'confidence': 1.0, 'raw_answer': response}

    def ask_question(self, image_path: str, question: str) -> dict:
        result = self._process_with_ai(document=None, question=question, image_path=image_path)
        # Use 'answer' key instead of 'text'
        return {
            'answer': result['answer'],
            'confidence': result.get('confidence', 1.0),
            'raw_answer': result['raw_answer']
        } 

    def _extract_text_impl(self, file_path, **kwargs):
        question = kwargs.pop('prompt', None)
        return self._process_with_ai(None, image_path=str(file_path), question=question, **kwargs), {} 