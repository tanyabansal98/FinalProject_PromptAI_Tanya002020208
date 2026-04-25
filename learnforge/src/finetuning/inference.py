"""Inference with fine-tuned LoRA adapter. Supports CUDA, Apple MPS, and CPU."""
import json, os, torch, logging
from pathlib import Path
logger = logging.getLogger(__name__)


def _get_device():
    """Detect best available device."""
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class FineTunedGenerator:
    def __init__(self, adapter_path, base_model=None):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import PeftModel

        cfg_path = Path(adapter_path) / "adapter_config.json"
        if cfg_path.exists():
            with open(cfg_path) as f:
                adapter_cfg = json.load(f)
            base_model = base_model or adapter_cfg.get("base_model_name_or_path", "")

        if not base_model:
            from src.config import FINETUNE_BASE_MODEL
            base_model = FINETUNE_BASE_MODEL

        device = _get_device()
        logger.info(f"Loading base model: {base_model} on {device}")

        # Load tokenizer from adapter path (has all tokenizer files)
        self.tokenizer = AutoTokenizer.from_pretrained(
            adapter_path, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load WITHOUT quantization — works on CUDA, MPS, and CPU
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
            trust_remote_code=True,
        )

        # For MPS/CPU, move manually
        if device != "cuda":
            model = model.to(device)

        self.model = PeftModel.from_pretrained(model, adapter_path)
        self.model.eval()
        self.device = device
        logger.info(f"Fine-tuned model loaded on {device}")

    def generate(self, prompt, max_new_tokens=1024, temperature=0.8):
        formatted = f"### Instruction:\n{prompt}\n\n### Response:\n"
        inputs = self.tokenizer(formatted, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:],
            skip_special_tokens=True).strip()

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
