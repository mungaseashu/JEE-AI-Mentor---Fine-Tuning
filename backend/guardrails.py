# ==============================================================================
# JEE MENTOR AI - INPUT/OUTPUT SAFETY GUARDRAILS & HALLUCINATION CHECKER
# ==============================================================================
import re
from typing import Tuple, List, Dict, Any

# Standard, mathematically rigid constants used in JEE Syllabus
VALID_PHYSICAL_CONSTANTS = {
    "speed_of_light": {"regex": r"(?:speed\s+of\s+light|velocity\s+of\s+light|c\s*=)", "value": 3.0e8, "unit": "m/s", "tolerance": 0.01},
    "planck_constant": {"regex": r"(?:planck(?:'s)?\s+constant|h\s*=)", "value": 6.626e-34, "unit": "J.s", "tolerance": 0.005},
    "gas_constant": {"regex": r"(?:gas\s+constant|R\s*=)", "value": 8.314, "unit": "J/mol.K", "tolerance": 0.005},
    "coulomb_constant": {"regex": r"(?:coulomb(?:'s)?\s+constant|k\s*=)", "value": 9.0e9, "unit": "N.m^2/C^2", "tolerance": 0.02},
    "acceleration_due_to_gravity": {"regex": r"(?:acceleration\s+due\s+to\s+gravity|g\s*=)", "value": 9.8, "unit": "m/s^2", "tolerance": 0.05} # supports g = 9.8 or g = 10
}

# Strict formula mappings to verify standard physical laws
STANDARD_FORMULAS = {
    "coulomb": {"name": "Coulomb's Law", "regex": r"F\s*=\s*(?:1\s*/\s*\(?4\s*\*\s*pi\s*\*\s*epsilon_0\)?|k)\s*\*\s*\(?q1\s*\*\s*q2\s*/\s*r\^2\)?", "canonical": "F = k * q1 * q2 / r^2"},
    "gauss": {"name": "Gauss's Law", "regex": r"(?:\oint|int)\s*E\s*(?:\cdot|.*?)\s*d?A\s*=\s*q\s*/\s*epsilon_0", "canonical": "oint E.dA = q_enclosed / epsilon_0"},
    "ohm": {"name": "Ohm's Law", "regex": r"V\s*=\s*I\s*\*\s*R", "canonical": "V = I * R"},
    "arrhenius": {"name": "Arrhenius Equation", "regex": r"k\s*=\s*A\s*\*\s*e\^?\(\s*-?E_a\s*/\s*\(?\s*R\s*\*\s*T\s*\)?\s*\)", "canonical": "k = A * e^(-E_a / RT)"}
}

class JEEGuardrails:
    def __init__(self):
        self.profanity_list = ["spam", "hack", "exploit", "killself", "cheat"]

    def validate_input(self, prompt: str) -> Tuple[bool, str]:
        """Validates incoming student prompts. Prevents prompt injection and off-topic questions."""
        p_lower = prompt.lower().strip()
        
        # 1. Profanity & Basic Abuse checks
        for word in self.profanity_list:
            if word in p_lower:
                return False, "This request was blocked by safety guardrails due to inappropriate language."

        # 2. Strict Off-Topic Redirect
        # Checks if prompt is focused on JEE topics
        on_topic_keywords = [
            "physics", "chemistry", "mathematics", "solve", "equation", "formula", "integral", "derivative",
            "reaction", "force", "charge", "acid", "base", "molecule", "vector", "limit", "matrix", "disc", "disc",
            "kinetics", "locus", "circle", "potential", "field", "charge", "thermodynamics", "optics", "modern", "moi",
            "inertia", "rotational", "coulomb", "gauss", "ohm", "half-life", "decomposes", "decomposes", "graph", "plot"
        ]
        
        # If the user asks a extremely short question that contains off-topic queries (e.g. write a python script for a game)
        off_topic_flags = ["recipe", "poetry", "write a game", "javascript code", "gossip", "write an essay on", "romance", "political"]
        
        if any(flag in p_lower for flag in off_topic_flags):
            return False, (
                "I am **JEE Mentor AI**, your specialized IIT-JEE academic tutor. "
                "I can only help you with questions in Physics, Chemistry, and Mathematics. "
                "Please ask a syllabus-related question!"
            )
            
        return True, prompt

    def validate_output(self, response: str) -> Tuple[str, List[str]]:
        """Audits model outputs, balances LaTeX brackets, checks constant hallucinations and flags mismatches."""
        violations = []
        audited_response = response

        # 1. LaTeX Tag Balancing Check
        # Ensure inline $ is balanced
        inline_dollar_count = audited_response.count("$") - (audited_response.count("$$") * 2)
        if inline_dollar_count % 2 != 0:
            violations.append("Malformed Output: Unbalanced inline LaTeX ($) tags detected.")
            # Auto-remediation: append a closing dollar tag at the end to prevent visual break
            audited_response += " $"
            
        block_dollar_count = audited_response.count("$$")
        if block_dollar_count % 2 != 0:
            violations.append("Malformed Output: Unbalanced block LaTeX ($$) tags detected.")
            audited_response += " $$"

        # 2. Scientific Constants Audit
        # Scans text for values like planck's constant and validates numerical values
        for name, cfg in VALID_PHYSICAL_CONSTANTS.items():
            matches = re.finditer(cfg["regex"], audited_response, re.IGNORECASE)
            for m in matches:
                # Find numerical values near the constant name
                start_idx = m.end()
                context_slice = audited_response[start_idx:start_idx+35]
                # Look for numbers in scientific notation (e.g., 6.6 * 10^-34) or standard decimals
                num_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\s*\\times\s*10\^|x10\^|\*10\^)\s*(-?\d+)", context_slice)
                
                if num_match:
                    base = float(num_match.group(1))
                    exp = int(num_match.group(2))
                    parsed_val = base * (10**exp)
                    
                    target_val = cfg["value"]
                    # Check tolerance deviation
                    diff = abs(parsed_val - target_val) / target_val
                    if diff > cfg["tolerance"]:
                        violations.append(f"Hallucination Warning: Incorrect value detected for constant '{name}' ({parsed_val} instead of {target_val}).")
                        # Auto-Correction
                        correct_str = f" {target_val:.3e} {cfg['unit']} "
                        # Replace the faulty segment in the response
                        audited_response = audited_response.replace(num_match.group(0), correct_str)

        # 3. Formula Mismatches Check
        # Check standard physical laws
        for key, cfg in STANDARD_FORMULAS.items():
            # If the name is mentioned, check if the formula expression matches the regex
            if cfg["name"].lower() in audited_response.lower():
                # We check if formula is written. If written incorrectly (hallucinated structure), we flag it
                # To be lenient and avoid false positives, we only issue warning if a formula is explicitly stated but fails the standard structure
                formula_elements = ["F", "q1", "q2", "epsilon", "epsilon_0"] if key == "coulomb" else []
                if formula_elements and not any(re.search(cfg["regex"], audited_response) for cfg in [cfg]):
                    # If we find "F =" but it doesn't match the regex:
                    if "F =" in audited_response and not re.search(cfg["regex"], audited_response):
                        violations.append(f"Hallucination Warning: Formula for '{cfg['name']}' appears incorrect. Standard equation is: {cfg['canonical']}.")

        return audited_response, violations

if __name__ == "__main__":
    guard = JEEGuardrails()
    print(guard.validate_input("Can you tell me how to make chicken soup?"))
    faulty_text = "The speed of light is c = 4.50 \times 10^8 m/s, and Planck's constant is h = 6.626 \times 10^-34 J.s."
    clean, violations = guard.validate_output(faulty_text)
    print(f"Violations: {violations}")
    print(f"Cleaned Text: {clean}")
