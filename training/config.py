# ==============================================================================
# JEE MENTOR AI - QLORA FINE-TUNING CONFIGURATION
# ==============================================================================
import os

# --- Model Selection Config ---
# Local debugging defaults to TinyLlama. Production scales to Llama 3 or Mistral.
BASE_MODEL_NAME = os.getenv("BASE_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
OUTPUT_DIR = os.getenv("LORA_ADAPTER_PATH", "./models/adapters")

# --- QLoRA Quantization Settings (bitsandbytes) ---
QUANT_CONFIG = {
    "load_in_4bit": True,
    "bnb_4bit_quant_type": "nf4",             # Normalized Float 4 (superior to linear fp4)
    "bnb_4bit_compute_dtype": "float16",       # Computation precision (bfloat16 if GPU supports)
    "bnb_4bit_use_double_quant": True,        # Nested quantization to save extra ~0.4 bits/param
}

# --- PEFT / LoRA Adapter Settings ---
LORA_CONFIG = {
    "r": 16,                                  # Rank of decomposition
    "lora_alpha": 32,                         # Scaling factor (usually 2x Rank)
    "lora_dropout": 0.05,                     # Prevents overfitting
    "target_modules": [                       # Attention projections to adapt
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    "bias": "none",
    "task_type": "CAUSAL_LM"
}

# --- Training Hyperparameters (TRL SFTTrainer) ---
TRAINING_HYPERPARAMS = {
    "dataset_path": "dataset/cleaned_jee_dataset.json",
    "train_split_ratio": 0.9,                 # 90% train, 10% validation
    
    # Optimizer & LR Scheduler
    "learning_rate": 2e-4,
    "weight_decay": 0.01,
    "adam_beta1": 0.9,
    "adam_beta2": 0.999,
    "lr_scheduler_type": "cosine",            # Cosine decay schedule
    "warmup_ratio": 0.03,
    
    # Steps and Batching
    "num_train_epochs": 3,
    "per_device_train_batch_size": 2,         # Low batch size to run on standard GPUs
    "per_device_eval_batch_size": 2,
    "gradient_accumulation_steps": 4,         # Effective batch size = batch_size * grad_accum * GPUs
    
    # Logging and Checkpointing
    "logging_steps": 10,
    "evaluation_strategy": "steps",
    "eval_steps": 50,
    "save_strategy": "steps",
    "save_steps": 50,
    "save_total_limit": 2,                    # Retain only the best 2 checkpoints to conserve disk space
    
    # Hardware Optimizations
    "fp16": True,                             # Mixed precision training
    "bf16": False,                            # Set True if using Ampere GPUs (e.g. A100, RTX 3090+)
    "gradient_checkpointing": True,           # Saves massive VRAM by recomputing activations during backward pass
    "max_seq_length": 1024,                   # JEE context limits
    "packing": False,                         # Set True to pack small samples into single sequence (high efficiency)
}
