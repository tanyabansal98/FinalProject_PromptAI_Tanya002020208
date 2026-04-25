"""QLoRA fine-tuning for educational content generation. Run on Google Colab with GPU."""
import json, os, random, yaml, torch, numpy as np
from pathlib import Path

random.seed(42); np.random.seed(42); torch.manual_seed(42)

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset


def format_instruction(example):
    return f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['response']}"


def train(config_path="src/finetuning/configs/qlora_3b.yaml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    model_name = cfg["base_model"]
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=os.getenv("HF_TOKEN"), trust_remote_code=True)
    except Exception:
        model_name = cfg.get("fallback_model", "Qwen/Qwen2.5-3B-Instruct")
        print(f"Falling back to {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=os.getenv("HF_TOKEN"), trust_remote_code=True)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    qcfg = cfg["quantization"]
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=qcfg["load_in_4bit"],
        bnb_4bit_compute_dtype=getattr(torch, qcfg["bnb_4bit_compute_dtype"]),
        bnb_4bit_quant_type=qcfg["bnb_4bit_quant_type"],
        bnb_4bit_use_double_quant=qcfg["bnb_4bit_use_double_quant"])

    model = AutoModelForCausalLM.from_pretrained(
        model_name, quantization_config=bnb_config, device_map="auto",
        token=os.getenv("HF_TOKEN"), trust_remote_code=True)
    model = prepare_model_for_kbit_training(model)

    lcfg = cfg["lora"]
    lora_config = LoraConfig(r=lcfg["r"], lora_alpha=lcfg["alpha"], lora_dropout=lcfg["dropout"],
                              target_modules=lcfg["target_modules"], bias=lcfg["bias"], task_type=lcfg["task_type"])
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    tcfg = cfg["training"]
    dcfg = cfg["data"]
    train_dataset = load_dataset("json", data_files=dcfg["train_path"], split="train")
    val_dataset = load_dataset("json", data_files=dcfg["val_path"], split="train")

    training_args = SFTConfig(
        output_dir=tcfg["output_dir"], num_train_epochs=tcfg["num_train_epochs"],
        per_device_train_batch_size=tcfg["per_device_train_batch_size"],
        gradient_accumulation_steps=tcfg["gradient_accumulation_steps"],
        learning_rate=tcfg["learning_rate"], lr_scheduler_type=tcfg["lr_scheduler_type"],
        warmup_ratio=tcfg["warmup_ratio"], logging_steps=tcfg["logging_steps"],
        save_strategy=tcfg["save_strategy"], eval_strategy=tcfg["evaluation_strategy"],
        bf16=tcfg["bf16"], max_seq_length=tcfg["max_seq_length"],
        gradient_checkpointing=tcfg["gradient_checkpointing"], optim=tcfg["optim"],
        report_to="none")

    trainer = SFTTrainer(model=model, args=training_args, train_dataset=train_dataset,
                         eval_dataset=val_dataset, processing_class=tokenizer,
                         formatting_func=format_instruction)

    print("Starting training...")
    trainer.train()
    model.save_pretrained(tcfg["output_dir"])
    tokenizer.save_pretrained(tcfg["output_dir"])
    print(f"✅ LoRA adapter saved to {tcfg['output_dir']}")

if __name__ == "__main__":
    train()
