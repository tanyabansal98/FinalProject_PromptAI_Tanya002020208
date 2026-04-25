# Fine-Tuning Report

## Task

Fine-tune a small LLM to generate structured educational content (lessons, quizzes, flashcards) given a topic, level, and module objectives.

## Data

- **Source:** 180 instruction-tuned examples across 20 topics × 3 levels × 3 content types
- **Pre-built:** No API cost to generate — included in `data/processed/`
- **Splits:** 144 train / 18 val / 18 test
- **Format:** `{"instruction": "Generate a...", "response": "{JSON content}"}`

## Model Configuration

| Parameter | Value |
|-----------|-------|
| Base model | Llama-3.2-3B-Instruct (or Qwen2.5-3B fallback) |
| Method | QLoRA |
| LoRA rank (r) | 16 |
| LoRA alpha | 32 |
| Target modules | q_proj, k_proj, v_proj, o_proj |
| Quantization | 4-bit NF4, double quantization |
| Epochs | 3 |
| Batch size | 4 (effective 16 with gradient accumulation) |
| Learning rate | 2e-4, cosine scheduler |
| GPU | Google Colab T4 (free tier) |

## Training Instructions

1. Upload `train.jsonl`, `val.jsonl`, `train_lora.py`, `qlora_3b.yaml` to Colab
2. Install: `!pip install -q transformers peft trl bitsandbytes accelerate datasets pyyaml`
3. Set token: `os.environ["HF_TOKEN"] = "hf_..."`
4. Run: `!python train_lora.py`
5. Download `models/lora_adapter/` back to project
6. Set `USE_FINETUNED=true` in `.env`

## What the Fine-Tuned Model Does

Agent 2 (Content Generator) tries the fine-tuned model first for lesson/quiz/flashcard generation. If it fails, it falls back to GPT-4o-mini. This means:
- **With fine-tuning:** Faster generation, no API cost per request, consistent JSON formatting
- **Without fine-tuning:** App works perfectly via API fallback — fine-tuning is an optimization, not a requirement

## Evaluation

*(Fill in after training)*
- Training duration: ___ minutes on T4
- Final train loss: ___
- Final val loss: ___
- Trainable parameters: ___ / ___ total
