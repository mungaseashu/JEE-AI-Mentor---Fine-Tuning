# ==============================================================================
# JEE MENTOR AI - QLORA FINE-TUNING PIPELINE
# ==============================================================================
import os
import sys
import json
import torch
from typing import Dict, Any, List
from datasets import Dataset

# Import configuration params
from training.config import (
    BASE_MODEL_NAME,
    OUTPUT_DIR,
    QUANT_CONFIG,
    LORA_CONFIG,
    TRAINING_HYPERPARAMS
)

def format_instruction_prompt(sample: Dict[str, Any]) -> str:
    """Standardizes prompt formatting for causal instruction tuning."""
    return (
        f"<s>[INST] <<SYS>>\nYou are a senior IIT-JEE Master Tutor. Explain concepts in Physics, Chemistry, "
        f"and Mathematics with rigorous step-by-step logic, clear formulas, and LaTeX notations.\n<</SYS>>\n\n"
        f"{sample['instruction']}\n\nQuestion:\n{sample['input']} [/INST]\n"
        f"Solution:\n{sample['output']} </s>"
    )

def format_dataset(dataset_path: str) -> Dataset:
    """Loads cleaned JSON data and returns structured Hugging Face Dataset."""
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Format texts for instruction tuning
    formatted_data = []
    for item in data:
        formatted_text = format_instruction_prompt(item)
        formatted_data.append({
            "text": formatted_text,
            "subject": item["subject"],
            "topic": item["topic"]
        })

    return Dataset.from_list(formatted_data)

def run_fine_tuning():
    """Configures quantization, loads models, prepares adapters, and executes fine-tuning."""
    print("🚀 Starting Fine-Tuning Pipeline...")
    
    # 1. Hardware Verification
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Using hardware device: {device}")
    
    if device != "cuda":
        print("[WARNING] QLoRA training strictly requires a CUDA-enabled GPU with bitsandbytes support.")
        print("[WARNING] Skipping actual SFT training loop to prevent CPU memory thrashing. Fine-tuning setup completed successfully!")
        return

    # 2. Import ML libraries dynamically to prevent crashes on non-GPU standard CPU systems
    try:
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            TrainingArguments,
            set_seed
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer
    except ImportError as ie:
        print(f"[ERROR] Failed to import key training packages: {ie}. Make sure requirements are fully installed.")
        sys.exit(1)

    set_seed(42)

    # 3. Load Tokenizer
    print(f"[INFO] Loading Tokenizer: {BASE_MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right" # Crucial for causal LM evaluations

    # 4. Configure BitsAndBytes 4-bit Quantization
    print("[INFO] Setting up 4-bit Quantization Configuration...")
    compute_dtype = getattr(torch, QUANT_CONFIG["bnb_4bit_compute_dtype"])
    
    bnb_config = BitsAndBytesConfig(
        load_in_4_bit=QUANT_CONFIG["load_in_4bit"],
        bnb_4bit_quant_type=QUANT_CONFIG["bnb_4bit_quant_type"],
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=QUANT_CONFIG["bnb_4bit_use_double_quant"]
    )

    # 5. Load Base Causal LM
    print(f"[INFO] Loading Base Model in 4-bit: {BASE_MODEL_NAME} (This may take a moment)...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Optimize VRAM footprint
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    # 6. Apply LoRA Config
    print("[INFO] Applying Low-Rank Adapters (PEFT)...")
    lora_config = LoraConfig(
        r=LORA_CONFIG["r"],
        lora_alpha=LORA_CONFIG["lora_alpha"],
        lora_dropout=LORA_CONFIG["lora_dropout"],
        target_modules=LORA_CONFIG["target_modules"],
        bias=LORA_CONFIG["bias"],
        task_type=LORA_CONFIG["task_type"]
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 7. Dataset split and preparation
    print("[INFO] Formatting and splitting local dataset...")
    hf_dataset = format_dataset(TRAINING_HYPERPARAMS["dataset_path"])
    split_dataset = hf_dataset.train_test_split(test_size=1.0 - TRAINING_HYPERPARAMS["train_split_ratio"])
    train_data = split_dataset["train"]
    eval_data = split_dataset["test"]
    print(f"  - Training samples: {len(train_data)}")
    print(f"  - Validation samples: {len(eval_data)}")

    # 8. Define SFT Training Arguments
    print("[INFO] Configuring SFT Training Arguments...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        learning_rate=TRAINING_HYPERPARAMS["learning_rate"],
        weight_decay=TRAINING_HYPERPARAMS["weight_decay"],
        adam_beta1=TRAINING_HYPERPARAMS["adam_beta1"],
        adam_beta2=TRAINING_HYPERPARAMS["adam_beta2"],
        lr_scheduler_type=TRAINING_HYPERPARAMS["lr_scheduler_type"],
        warmup_ratio=TRAINING_HYPERPARAMS["warmup_ratio"],
        num_train_epochs=TRAINING_HYPERPARAMS["num_train_epochs"],
        per_device_train_batch_size=TRAINING_HYPERPARAMS["per_device_train_batch_size"],
        per_device_eval_batch_size=TRAINING_HYPERPARAMS["per_device_eval_batch_size"],
        gradient_accumulation_steps=TRAINING_HYPERPARAMS["gradient_accumulation_steps"],
        logging_steps=TRAINING_HYPERPARAMS["logging_steps"],
        evaluation_strategy=TRAINING_HYPERPARAMS["evaluation_strategy"],
        eval_steps=TRAINING_HYPERPARAMS["eval_steps"],
        save_strategy=TRAINING_HYPERPARAMS["save_strategy"],
        save_steps=TRAINING_HYPERPARAMS["save_steps"],
        save_total_limit=TRAINING_HYPERPARAMS["save_total_limit"],
        fp16=TRAINING_HYPERPARAMS["fp16"],
        bf16=TRAINING_HYPERPARAMS["bf16"],
        gradient_checkpointing=TRAINING_HYPERPARAMS["gradient_checkpointing"],
        group_by_length=True,  # Speeds up training by grouping similar length texts together
        report_to="none"       # Prevents locking due to wandb configuration prompt in console
    )

    # 9. Instantiate SFT Trainer
    print("[INFO] Initializing SFT Trainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_data,
        eval_dataset=eval_data,
        dataset_text_field="text",
        max_seq_length=TRAINING_HYPERPARAMS["max_seq_length"],
        tokenizer=tokenizer,
        args=training_args,
        packing=TRAINING_HYPERPARAMS["packing"]
    )

    # 10. Execute Training Epochs
    print("🔥 Starting actual SFT QLoRA Training Loop (This will consume GPU resources)...")
    trainer.train()

    # 11. Save trained adapter weights
    print(f"[SUCCESS] Training complete! Saving final LoRA adapters to: {OUTPUT_DIR}")
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("🎉 QLoRA Adapters successfully written to persistent storage.")

if __name__ == "__main__":
    run_fine_tuning()
