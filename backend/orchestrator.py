# ==============================================================================
# JEE MENTOR AI - COGNITIVE REQUEST ORCHESTRATOR
# ==============================================================================
import time
import re
from typing import Generator, Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session

# Import backend modules
from backend.tools import JEEMathTools
from backend.ocr import JEEOcrPipeline
from backend.guardrails import JEEGuardrails
from backend.cache import jee_cache
from backend.memory import JEEConversationMemoryManager
from rag.retriever import JEERetriever
from training.inference import JEEInferenceEngine
from backend.web_search import JEEWebSearch

class JEEOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.tools = JEEMathTools()
        self.ocr = JEEOcrPipeline()
        self.guardrails = JEEGuardrails()
        self.retriever = JEERetriever()
        self.llm = JEEInferenceEngine()
        self.memory_manager = JEEConversationMemoryManager(db)

    def detect_intent(self, prompt: str) -> str:
        """Parses prompt text to categorize student intent for routing."""
        p_lower = prompt.lower().strip()
        
        # 1. Plot Graph Intent
        if any(w in p_lower for w in ["plot", "draw", "graph", "sketch"]):
            # Look for equations or functions
            if any(sym in p_lower for sym in ["x^2", "x**2", "sin", "cos", "y =", "x =", "f(x)"]):
                return "PLOT"
                
        # 2. Symbolic Equations solving
        if any(w in p_lower for w in ["integrate", "differentiation", "derivative", "solve the equation", "roots of"]):
            if any(sym in p_lower for sym in ["x^2", "x**2", "sin", "cos", "tan", "="]):
                return "SYMBOLIC"
                
        # 3. Quick Calculator math
        if any(char in p_lower for char in ["+", "-", "*", "/"]):
            # If it's a brief math line with digits
            if re.search(r"\d+\s*[\+\-\*/]\s*\d+", p_lower):
                return "CALCULATE"
                
        return "CHAT"

    def orchestrate_question_solve(self, question_text: Optional[str] = None, image_base64: Optional[str] = None, subject: Optional[str] = None) -> Dict[str, Any]:
        """OCR Solver entry point: Extracts text, fetches RAG notes, solves via LLM, and formats response."""
        start_time = time.time()
        extracted = None
        
        # 1. OCR Extraction if image provided
        if image_base64:
            print("[INFO] OCR image upload detected. Invoking tiered OCR pipeline...")
            extracted = self.ocr.extract_text_from_base64(image_base64)
            print(f"[SUCCESS] Extracted text: '{extracted[:60]}...'")
            active_prompt = extracted
        elif question_text:
            active_prompt = question_text
        else:
            return {"error": "Provide either question_text or image_base64."}

        # 2. RAG Retrieval
        print("[INFO] Fetching RAG references for formula lookup...")
        rag_context = self.retriever.retrieve_context(active_prompt, k=2, subject=subject)
        
        # Web Search Fallback if RAG is empty
        is_rag_empty = not rag_context or "No matching reference material" in rag_context or "No highly relevant formulas" in rag_context
        if is_rag_empty:
            print("[INFO] Offline RAG context is empty. Triggering Web Search fallback...")
            web_context = JEEWebSearch.search_web(active_prompt)
            if web_context:
                rag_context = web_context
        
        # 3. Intent Detection to see if plotting needed
        intent = self.detect_intent(active_prompt)
        graph_base64 = None
        tool_output = ""
        
        if intent == "PLOT":
            print("[INFO] Graph Plotting triggered during Solver routing.")
            # Attempt to extract equation like y = x^2 - 4x
            eq_match = re.search(r"(?:y\s*=.*?|x\^2.*|sin\(x\).*)", active_prompt, re.IGNORECASE)
            eq_str = eq_match.group(0) if eq_match else "y = x^2"
            plot_res = self.tools.plot_graph(eq_str)
            if plot_res.get("success"):
                graph_base64 = plot_res["base64"]
                tool_output = f"\n[MATPLOTLIB GRAPH PLOTTED SUCCESSFUL FOR: {eq_str}]\n"

        # 4. Prompt construction
        system_prompt = (
            "You are a senior IIT-JEE Master Tutor. Solve this question with strict step-by-step mathematical reasoning. "
            "Show every intermediate step, state which physics/chemistry constants are used, and wrap all variables "
            "and expressions in clean LaTeX syntax. Conclude with a highlighted bold final answer."
        )
        
        final_prompt = (
            f"Here is a challenging JEE problem.\n\n"
            f"Question:\n{active_prompt}\n\n"
            f"--- RAG Text Book Notes & Formulas ---\n{rag_context}\n\n"
            f"{tool_output}"
            f"Please solve this question and render a premium explanation."
        )

        # 5. Model Inference (Non-streaming solve return for clean schema packaging)
        print("[INFO] Invoking LLM solver...")
        llm_response = ""
        for token in self.llm.generate_stream(final_prompt, system_prompt=system_prompt, max_tokens=1024):
            llm_response += token
            
        # 6. Apply Guardrails to final output
        print("[INFO] Auditing solver solution against safety guardrails...")
        audited_response, violations = self.guardrails.validate_output(llm_response)
        
        if violations:
            print(f"[WARNING] Guardrails flagged issues during solver: {violations}")

        latency = (time.time() - start_time) * 1000
        
        return {
            "extracted_text": extracted,
            "solution": audited_response,
            "formulas_used": self.retriever.retrieve_formulas_only(active_prompt, k=2),
            "graph_base64": graph_base64,
            "latency_ms": round(latency, 2)
        }

    def orchestrate_chat_stream(self, session_id: str, prompt: str) -> Generator[str, None, None]:
        """Orchestrates streaming chat turns, managing memory summaries, intent routing, and guardrails."""
        
        # 1. Input Guardrails validation
        is_safe, error_msg = self.guardrails.validate_input(prompt)
        if not is_safe:
            yield f"[GUARDRAIL REDIRECT] {error_msg}"
            return

        # 2. Caching layer lookup
        # Attempt to load a fast response from cache for repeated queries
        cache_key = f"chat_cache:{session_id}:{hash(prompt)}"
        cached_resp = jee_cache.get(cache_key)
        if cached_resp:
            print("[INFO] Cache HIT! Serving cached answer.")
            for token in cached_resp.split(" "):
                yield token + " "
            return

        # 3. Session memory loading and auto-summarization
        summary_context, active_history = self.memory_manager.load_session_context(session_id)
        
        # 4. Fetch RAG reference contexts
        rag_context = self.retriever.retrieve_context(prompt, k=2)
        
        # Web Search Fallback if RAG is empty
        is_rag_empty = not rag_context or "No matching reference material" in rag_context or "No highly relevant formulas" in rag_context
        if is_rag_empty:
            print("[INFO] Offline RAG context is empty. Triggering Web Search fallback...")
            web_context = JEEWebSearch.search_web(prompt)
            if web_context:
                rag_context = web_context

        # 5. Intent detection & tool execution
        intent = self.detect_intent(prompt)
        tool_injections = ""
        
        if intent == "PLOT":
            # Extract equation
            eq_match = re.search(r"y\s*=\s*[a-zA-Z0-9\^_\+\-\*/\(\)\.\s]+", prompt)
            eq_str = eq_match.group(0) if eq_match else "y = x^2"
            plot_res = self.tools.plot_graph(eq_str)
            if plot_res.get("success"):
                # Inject graph notice into prompt
                tool_injections = f"\n[TOOL NOTIFICATION: Matplotlib generated a chart for '{eq_str}'. The graph has been loaded successfully on user UI card.]\n"
                
        elif intent == "SYMBOLIC":
            # Detect solve mode
            mode = "solve"
            if "integrate" in prompt.lower():
                mode = Sp_mode = "integrate"
            elif "derivative" in prompt.lower() or "differentiation" in prompt.lower():
                mode = Sp_mode = "diff"
                
            # Basic equation capture
            sp_match = re.search(r"(?:integrate|solve|derivative)\s+([a-zA-Z0-9\^_\+\-\*/\(\)\.\s=]+)", prompt, re.IGNORECASE)
            eq_str = sp_match.group(1) if sp_match else "x^2 - 4*x + 3"
            
            sp_result = self.tools.solve_symbolic(eq_str, mode=mode)
            tool_injections = f"\n[VERIFIED SYMPY MATH TOOL OUTPUT for '{eq_str}': {sp_result}]\n"
            
        elif intent == "CALCULATE":
            # Extract basic math
            math_match = re.search(r"([0-9\+\-\*/\(\)\.\s\*,]+)", prompt)
            math_str = math_match.group(0) if math_match else "2 * 3"
            calc_res = self.tools.calculate(math_str)
            tool_injections = f"\n[VERIFIED CALCULATOR TOOL ARITHMETIC RESULT for '{math_str}': {calc_res}]\n"

        # 6. Prompt Assembly
        sys_prompt = (
            "You are a brilliant senior IIT-JEE Master Tutor. Explain concepts strictly related to Physics, "
            "Chemistry, and Mathematics. Adopt a premium, helpful, academic tone. Explain key formulas "
            "using LaTeX wrapped in $ for inline and $$ for block equations. Be encouraging."
        )
        if summary_context:
            sys_prompt += f"\n[HISTORICAL SUMMARY SUMMARY]: {summary_context}"

        assembled_prompt = (
            f"--- Active RAG Revision Material & Formulas ---\n{rag_context}\n\n"
            f"{tool_injections}"
            f"Current Chat Query:\n{prompt}\n\n"
            f"Explain clearly step-by-step:"
        )

        # Print debug logs to terminal
        try:
            print(f"\n[ORCHESTRATOR DEBUG LOG]")
            print(f"  - Incoming Query: '{prompt}'")
            print(f"  - Retrieved RAG Context: '{rag_context}'")
            print(f"  - Assembled Prompt:\n{assembled_prompt}\n")
        except UnicodeEncodeError:
            print(f"\n[ORCHESTRATOR DEBUG LOG (SAFE PRINT)]")
            print(f"  - Incoming Query: '{prompt.encode('ascii', errors='replace').decode('ascii')}'")
            print(f"  - Retrieved RAG Context: '{rag_context.encode('ascii', errors='replace').decode('ascii')}'")
            print(f"  - Assembled Prompt:\n{assembled_prompt.encode('ascii', errors='replace').decode('ascii')}\n")

        # 7. Streaming response capture
        full_response = ""
        for token in self.llm.generate_stream(assembled_prompt, system_prompt=sys_prompt):
            full_response += token
            yield token

        try:
            print(f"  - Raw Model Output: '{full_response}'")
        except UnicodeEncodeError:
            print(f"  - Raw Model Output: '{full_response.encode('ascii', errors='replace').decode('ascii')}'")

        # 8. Apply Output Guardrails
        audited_res, violations = self.guardrails.validate_output(full_response)
        
        # Save to DB history
        self.memory_manager.add_message(session_id, "user", prompt)
        self.memory_manager.add_message(session_id, "assistant", audited_res, metadata={"violations": violations, "intent": intent})

        # Cache response for future lookups (expire in 2 hours)
        jee_cache.set(cache_key, audited_res, expire_seconds=7200)
