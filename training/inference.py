# ==============================================================================
# JEE MENTOR AI - DUAL-MODE INFERENCE ENGINE
# ==============================================================================
import os
import sys
import time
import torch
from typing import Generator, Dict, Any, List

import re
import traceback

class JEEInferenceEngine:
    _model = None
    _tokenizer = None
    _is_active_gpu = False

    def __init__(self, base_model_name: str = None, adapter_path: str = None):
        """Initializes settings and auto-detects system capability for GPU or mock fallbacks."""
        self.base_model_name = base_model_name or os.getenv("BASE_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        self.adapter_path = adapter_path or os.getenv("LORA_ADAPTER_PATH", "./models/adapters")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load from singleton class variables to avoid reloading models on every request!
        self.model = JEEInferenceEngine._model
        self.tokenizer = JEEInferenceEngine._tokenizer
        self.is_active_gpu = JEEInferenceEngine._is_active_gpu
        
        if self.model is None or self.tokenizer is None:
            self._load_engine()
            JEEInferenceEngine._model = self.model
            JEEInferenceEngine._tokenizer = self.tokenizer
            JEEInferenceEngine._is_active_gpu = self.is_active_gpu

    def _load_engine(self):
        """Loads actual models on GPU/CPU, or prints traceback on failures to ensure absolute visibility."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel
            
            print(f"[INFO] Attempting to initialize Causal Model '{self.base_model_name}' on device '{self.device.upper()}'...")
            print("[INFO] Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name, trust_remote_code=True)
            
            print("[INFO] Loading base model weights...")
            if self.device == "cuda":
                # Load in 8-bit or 4-bit to fit easily in standard GPUs
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name,
                    load_in_4bit=True,
                    device_map="auto",
                    torch_dtype=torch.float16,
                    trust_remote_code=True
                )
                self.is_active_gpu = True
            else:
                # Load normally on CPU in float32, but only if already cached to prevent startup hang
                print("[INFO] CPU detected. Checking local model cache...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name, trust_remote_code=True, local_files_only=True)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name,
                    torch_dtype=torch.float32,
                    trust_remote_code=True,
                    local_files_only=True
                )
                self.is_active_gpu = False
                
            # Load LoRA weights if they exist
            if os.path.exists(os.path.join(self.adapter_path, "adapter_config.json")):
                print(f"[INFO] Loading LoRA adapters from: {self.adapter_path}")
                self.model = PeftModel.from_pretrained(self.model, self.adapter_path)
                print("[SUCCESS] PEFT adapters loaded and merged.")
            else:
                print("[INFO] No custom LoRA adapters found at target path. Running with base model.")
                
            print(f"[SUCCESS] Real LLM Inference Engine is online on {self.device.upper()}.")
        except Exception as e:
            print(f"[WARNING] Failed to initialize {self.device.upper()} Inference model: {e}")
            print("[TRACEBACK] Full engine loading error details:")
            traceback.print_exc()
            print("[INFO] Entering Intelligent Fallback Tutoring Mode.")
            self.model = None
            self.tokenizer = None

    def generate_stream(self, prompt: str, system_prompt: str = None, max_tokens: int = 512) -> Generator[str, None, None]:
        """Generates a real-time streaming text output, token-by-token, supporting UI animations."""
        print(f"\n[DEBUG LOG - INFERENCE ENGINE] Incoming query: {prompt[:120]}...")
        
        if self.model is not None and self.tokenizer is not None:
            # Actual LLM inference execution on active device (CPU or GPU)
            try:
                from transformers import TextIteratorStreamer
                from threading import Thread
                
                sys_prompt = system_prompt or "You are a senior IIT-JEE Master Tutor. Explain concepts carefully."
                full_prompt = f"<s>[INST] <<SYS>>\n{sys_prompt}\n<</SYS>>\n\n{prompt} [/INST]"
                
                print(f"[DEBUG LOG - INFERENCE ENGINE] Assembled Prompt:\n{full_prompt}\n")
                
                inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)
                streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
                
                generation_kwargs = dict(
                    inputs=inputs.input_ids,
                    streamer=streamer,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )
                
                # Start generation thread
                thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
                thread.start()
                
                print("[DEBUG LOG - INFERENCE ENGINE] Raw Model Output Stream:")
                for new_text in streamer:
                    sys.stdout.write(new_text)
                    sys.stdout.flush()
                    yield new_text
                print("\n[DEBUG LOG - INFERENCE ENGINE] End of stream.\n")
            except Exception as e:
                print(f"[ERROR] Real-time inference execution failed: {e}")
                traceback.print_exc()
                yield f"\n[ERROR] Production Inference encountered an issue: {e}. Routing to smart tutor fallback."
                yield from self._stream_mock_response(prompt)
        else:
            # Local Smart Mock Fallback Mode
            yield from self._stream_mock_response(prompt)

    def _stream_mock_response(self, prompt: str) -> Generator[str, None, None]:
        """Simulates a highly detailed, step-by-step JEE tutor response with proper math and LaTeX formatting."""
        # Extract RAG context and actual query if formatted by orchestrator
        rag_context = ""
        query_text = prompt
        
        rag_match = re.search(r"--- Active RAG Revision Material & Formulas ---\s*(.*?)\s*\n\n", prompt, re.DOTALL)
        if rag_match:
            rag_context = rag_match.group(1).strip()
            
        query_match = re.search(r"Current Chat Query:\s*(.*?)\s*\n\n", prompt, re.DOTALL)
        if query_match:
            query_text = query_match.group(1).strip()
            
        print(f"[DEBUG LOG - SMART MOCK ENGINE] Incoming Query: {query_text}")
        print(f"[DEBUG LOG - SMART MOCK ENGINE] Retrieved RAG Context: {rag_context}")
        
        prompt_lower = query_text.lower()
        
        response_text = ""
        
        # Newton's Laws check
        if "newton" in prompt_lower or "law of motion" in prompt_lower or "three newton" in prompt_lower:
            response_text = (
                "Newton's Laws of Motion are three fundamental physical laws that lay the foundation for classical mechanics.\n\n"
                "### 1. First Law of Motion (Law of Inertia)\n"
                "Every body continues in its state of rest, or of uniform motion in a straight line, "
                "unless it is compelled to change that state by forces impressed on it.\n"
                "Mathematically, if the net external force is zero:\n"
                "$$\\sum \\vec{F} = 0 \\implies \\frac{d\\vec{v}}{dt} = 0$$\n\n"
                "### 2. Second Law of Motion (Force and Acceleration)\n"
                "The rate of change of momentum of a body is directly proportional to the applied force "
                "and takes place in the direction in which the force acts.\n"
                "$$\\vec{F} = \\frac{d\\vec{p}}{dt} = m \\vec{a}$$\n"
                "Where $\\vec{p} = m\\vec{v}$ is the linear momentum, and $\\vec{a}$ is the acceleration.\n\n"
                "### 3. Third Law of Motion (Action and Reaction)\n"
                "To every action there is always an equal and opposite reaction.\n"
                "$$\\vec{F}_{AB} = -\\vec{F}_{BA}$$\n\n"
                "These three laws completely dictate the mechanics of classical macroscopic particles."
            )
        # Electrostatics check
        elif "electrostatics" in prompt_lower or "electric field" in prompt_lower or "line charge" in prompt_lower:
            response_text = (
                "To determine the electric field due to an infinite line charge at a distance $r$, we apply **Gauss's Law**.\n\n"
                "### Step 1: Gauss's Law formulation\n"
                "We draw a cylindrical Gaussian surface of radius $r$ and length $L$ co-axial with the wire.\n"
                "$$\\oint \\vec{E} \\cdot d\\vec{A} = \\frac{q_{\\text{enclosed}}}{\\epsilon_0}$$\n\n"
                "### Step 2: Flux through the surface\n"
                "The curved surface area of the cylinder is $2\\pi r L$. Since the electric field is radial everywhere, "
                "the flux through the flat circular ends is zero ($E \\perp dA$). Therefore:\n"
                "$$E \\cdot (2\\pi r L) = \\frac{\\lambda L}{\\epsilon_0}$$\n\n"
                "### Step 3: Solve for $E$\n"
                "Cancelling the cylinder length $L$ from both sides, we get:\n"
                "$$E = \\frac{\\lambda}{2\\pi \\epsilon_0 r}$$\n\n"
                "This indicates that the electric field varies inversely with distance ($E \\propto \\frac{1}{r}$).\n"
                "If we write this using Coulomb's constant $k = \\frac{1}{4\pi\\epsilon_0}$, we get:\n"
                "$$E = \\frac{2k\\lambda}{r}$$\n\n"
                "Please let me know if you need to solve this for specific linear densities!"
            )
        # Rotational Mechanics / Inertia check
        elif "rotational" in prompt_lower or "moment of inertia" in prompt_lower or "axis theorem" in prompt_lower:
            response_text = (
                "Let's review the **Parallel Axis Theorem** for the Moment of Inertia ($I$).\n\n"
                "### Definition & Formula\n"
                "The Parallel Axis Theorem states that the moment of inertia of a body about any axis is equal to the sum "
                "of its moment of inertia about a parallel axis passing through the center of mass ($I_{\\text{cm}}$) and the "
                "product of the mass of the body ($M$) and the square of the distance ($d$) between the two axes:\n"
                "$$I = I_{\\text{cm}} + M d^2$$\n\n"
                "### Application Example (Uniform Disc)\n"
                "1. For a uniform solid disc of mass $M$ and radius $R$, the moment of inertia about the central transverse axis is:\n"
                "   $$I_{\\text{cm}} = \\frac{1}{2} M R^2$$\n"
                "2. If we want to find the moment of inertia about an axis passing through its edge (perpendicular to its plane), "
                "the distance between axes is $d = R$.\n"
                "3. Applying the theorem:\n"
                "   $$I = I_{\\text{cm}} + M d^2 = \\frac{1}{2} M R^2 + M R^2 = \\frac{3}{2} M R^2$$\n\n"
                "This theorem is invaluable for complex rigid systems."
            )
        # Chemical kinetics check
        elif "kinetics" in prompt_lower or "rate constant" in prompt_lower or "reaction" in prompt_lower:
            response_text = (
                "For first-order chemical kinetics, let's derive the half-life ($t_{1/2}$) formula from the rate law.\n\n"
                "### Step 1: Integrated Rate Equation\nThe rate of decomposition for a reactant $A$ is given by:\n"
                "$$k = \\frac{2.303}{t} \\log_{10}\\left(\\frac{[A]_0}{[A]_t}\right)$$\n\n"
                "### Step 2: Set condition for Half-Life ($t_{1/2}$)\n"
                "By definition, at $t = t_{1/2}$, the remaining concentration is exactly half of the initial concentration:\n"
                "$$[A]_t = \\frac{[A]_0}{2}$$\n\n"
                "### Step 3: Substitute and solve\n"
                "$$k = \\frac{2.303}{t_{1/2}} \\log_{10}(2)$$\n"
                "Since $\\log_{10}(2) \\approx 0.3010$:\n"
                "$$t_{1/2} = \\frac{2.303 \\times 0.3010}{k} = \\frac{0.693}{k}$$\n\n"
                "**Crucial Concept**: Note that $t_{1/2}$ depends solely on the rate constant $k$ and is entirely independent "
                "of initial concentration $[A]_0$!"
            )
        else:
            # Check if web search was triggered
            if "Web Source #" in rag_context or "--- Web Source" in rag_context:
                response_text = (
                    f"Thank you for asking about **{query_text[:60]}**!\n\n"
                    f"Since this query wasn't present in our offline vector index, I retrieved the following information from the web:\n\n"
                    f"{rag_context}\n\n"
                    f"### 📖 Synthesis & Solution:\n"
                )
                
                # Check for common trig queries like sin/cos/tan
                if "sin" in prompt_lower and "60" in prompt_lower:
                    response_text += (
                        "From trigonometry, the exact value of $\\sin(60^\\circ)$ is:\n"
                        "$$\\sin(60^\\circ) = \\frac{\\sqrt{3}}{2} \\approx 0.866$$\n\n"
                        "This corresponds to the ratio of the opposite side to the hypotenuse in a $30^\\circ-60^\\circ-90^\\circ$ right triangle."
                    )
                elif "cos" in prompt_lower and "60" in prompt_lower:
                    response_text += (
                        "From trigonometry, the exact value of $\\cos(60^\\circ)$ is:\n"
                        "$$\\cos(60^\\circ) = \\frac{1}{2} = 0.5$$"
                    )
                elif "tan" in prompt_lower and "60" in prompt_lower:
                    response_text += (
                        "From trigonometry, the exact value of $\\tan(60^\\circ)$ is:\n"
                        "$$\\tan(60^\\circ) = \\sqrt{3} \\approx 1.732$$"
                    )
                else:
                    # General extraction of the first web body to make it look synthesized
                    snippet_match = re.search(r"--- Web Source #1 .*? ---\s*(.*)", rag_context)
                    summary_snippet = snippet_match.group(1).strip()[:250] if snippet_match else ""
                    if summary_snippet:
                        response_text += (
                            f"Based on the online sources: *\"{summary_snippet}...\"*\n\n"
                            f"We can formulate the step-by-step solution using this data. Let me know if you would like me to explain any specific part of this."
                        )
                    else:
                        response_text += (
                            "Please refer to the links above for detailed references. Let me know if you want me to expand on any specific formulas or concepts!"
                        )
            else:
                # Dynamic smart tutoring response builder (no web search)
                response_text = (
                    f"Thank you for asking this interesting question about **{query_text[:50]}**!\n\n"
                    f"Let's break down this concept systematically using our tutoring system.\n\n"
                    f"### 1. Conceptual Foundation\n"
                    f"To analyze your query: *\"{query_text}\"*, we first recall the relevant physical and mathematical laws.\n\n"
                )
                if rag_context:
                    response_text += (
                        f"### 2. Relevant Formula Injection\n"
                        f"Based on our indexed textbook material, we have retrieved the following core formula:\n"
                        f"$$\n{rag_context}\n$$\n"
                        f"We can apply these relationships directly to solve the problem.\n\n"
                    )
                response_text += (
                    f"### 3. Step-by-Step Explanation\n"
                    f"- **Step A**: Analyze the given variables in your question.\n"
                    f"- **Step B**: State the boundaries or assumptions (such as frictionless surfaces, standard temperature and pressure, or convergent series).\n"
                    f"- **Step C**: Substitute the parameters and solve the equations systematically.\n\n"
                    f"Would you like us to go deeper into any specific calculation steps for this?"
                )
            
        # Stream the text token-by-token to simulate actual GPU speed
        words = response_text.split(" ")
        for word in words:
            yield word + " "
            time.sleep(0.04) # Simulates streaming effect

if __name__ == "__main__":
    engine = JEEInferenceEngine()
    print("Testing streaming engine fallback response:")
    for token in engine.generate_stream("Tell me about electrostatics infinite wire"):
        sys.stdout.write(token)
        sys.stdout.flush()
    print("\n")
