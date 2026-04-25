"""Inference with fine-tuned LoRA adapter."""
import json, os, torch, logging
from pathlib import Path
logger = logging.getLogger(__name__)

class FineTunedGenerator:
    def __init__(self, adapter_path, base_model=None):
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
        from peft import PeftModel
        cfg_path = Path(adapter_path) / "adapter_config.json"
        if cfg_path.exists():
            with open(cfg_path) as f:
                base_model = base_model or json.load(f).get("base_model_name_or_path", "")
        if not base_model:
            from src.config import FINETUNE_BASE_MODEL
            base_model = FINETUNE_BASE_MODEL
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16,
                                  bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True)
        self.tokenizer = AutoTokenizer.from_pretrained(base_model, token=os.getenv("HF_TOKEN"), trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(base_model, quantization_config=bnb, device_map="auto",
                                                      token=os.getenv("HF_TOKEN"), trust_remote_code=True)
        self.model = PeftModel.from_pretrained(model, adapter_path)
        self.model.eval()

    def generate(self, prompt, max_new_tokens=2048, temperature=0.8):
        formatted = f"### Instruction:\n{prompt}\n\n### Response:\n"
        inputs = self.tokenizer(formatted, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=temperature,
                                           do_sample=True, top_p=0.9, pad_token_id=self.tokenizer.pad_token_id)
        response = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        for prefix in ["```json", "```"]:
            if response.startswith(prefix):
                response = response[len(prefix):]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        start, end = response.find("{"), response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
        return json.loads(response)
