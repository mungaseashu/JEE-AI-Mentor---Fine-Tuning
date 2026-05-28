# ==============================================================================
# JEE MENTOR AI - SYNTHETIC DATASET GENERATOR
# ==============================================================================
import os
import json
import random
import time
import argparse
from typing import List, Dict, Any
import requests

# Constants for Generation
SUBJECTS = ["Physics", "Chemistry", "Mathematics"]

TOPICS = {
    "Physics": [
        "Electrostatics", "Current Electricity", "Rotational Mechanics", 
        "Thermodynamics", "Geometrical Optics", "Modern Physics", "Kinematics"
    ],
    "Chemistry": [
        "Chemical Bonding", "Chemical Kinetics", "Thermodynamics and Energetics",
        "Organic Reactions & Mechanisms", "Coordination Compounds", "Electrochemistry", "Mole Concept"
    ],
    "Mathematics": [
        "Definite Integration", "Matrices and Determinants", "Probability",
        "Complex Numbers", "Limits, Continuity & Differentiability", "Coordinate Geometry", "Vectors & 3D"
    ]
}

DIFFICULTIES = ["Easy", "Medium", "Hard"]

# Programmatic question templates to guarantee 1000+ highly structured samples out-of-the-box
PROGRAMMATIC_TEMPLATES = {
    "Physics": [
        {
            "topic": "Electrostatics",
            "concept": "Electric field of line charge",
            "input_template": "An infinite thin straight wire has a uniform linear charge density of $\\lambda = {val} \\times 10^{{-6}}$ C/m. Calculate the electric field intensity at a perpendicular distance of $r = {dist}$ m from the wire. (Take $\\epsilon_0 = 8.85 \\times 10^{{-12}}$ C$^2$/N.m$^2$)",
            "output_template": "To find the electric field intensity due to an infinite linear charge, we use Gauss's Law.\n\n### Step 1: Identify the standard formula\nThe electric field $E$ at a perpendicular distance $r$ from a line charge with linear charge density $\\lambda$ is given by:\n$$E = \\frac{{\\lambda}}{{2\\pi\\epsilon_0 r}}$$\n\n### Step 2: Rewrite in terms of known constant $k = \\frac{{1}}{{4\\pi\\epsilon_0}} = 9 \\times 10^9$ N.m$^2$/C$^2$\n$$E = \\frac{{2k\\lambda}}{{r}}$$\n\n### Step 3: Substitute the given values\nGiven:\n- $\\lambda = {val} \\times 10^{{-6}}$ C/m\n- $r = {dist}$ m\n- $k = 9 \\times 10^9$ N.m$^2$/C$^2$\n\n$$E = \\frac{{2 \\times (9 \\times 10^9) \\times ({val} \\times 10^{{-6}})}}{{{dist}}}$$\n$$E = \\frac{{{num} \\times 10^3}}{{{dist}}}$$\n$$E = {final:.2f} \\times 10^3$ N/C\n\n### Conclusion\nThe electric field intensity at a distance of ${dist}$ m is **${final:.2f} \\times 10^3$ N/C**.",
            "tags": ["Gauss's Law", "Electric Field", "Infinite Line Charge"],
            "difficulty": "Medium"
        },
        {
            "topic": "Rotational Mechanics",
            "concept": "Moment of inertia of compound system",
            "input_template": "A uniform disc of mass $M = {mass}$ kg and radius $R = {rad}$ m has a small circular hole of radius $r = {hole}$ m cut out from it. The center of the hole is at a distance of $d = {dist}$ m from the center of the disc. Find the moment of inertia of the remaining portion of the disc about an axis passing through the center of the original disc and perpendicular to its plane.",
            "output_template": "We solve this using the Principle of Superposition and the Parallel Axis Theorem.\n\n### Step 1: Calculate the area and mass densities\nLet $\\sigma$ be the mass per unit area of the original uniform disc.\n- Total Area of original disc: $A = \\pi R^2 = \\pi ({rad})^2 = {area_orig:.3f}\\pi$ m$^2$\n- Mass density $\\sigma = \\frac{{M}}{{\\pi R^2}} = \\frac{{{mass}}}{{\\pi ({rad})^2}} = {density:.3f}/\\pi$ kg/m$^2$\n\n### Step 2: Mass of the removed circular portion ($m$)\n- Area of cut-out portion: $a = \\pi r^2 = \\pi ({hole})^2 = {area_hole:.3f}\\pi$ m$^2$\n- Mass of removed portion: $m = \\sigma \\times a = \\left(\\frac{{{mass}}}{{\\pi ({rad})^2}}\\right) \\times \\pi ({hole})^2 = {mass_removed:.3f}$ kg\n\n### Step 3: Moments of inertia about the center axis\n- Moment of inertia of original whole disc $I_{{whole}}$:\n  $$I_{{whole}} = \\frac{{1}}{{2}} M R^2 = \\frac{{1}}{{2}} \\times {mass} \\times ({rad})^2 = {i_whole:.4f}\\text{{ kg.m}}^2$$\n- Moment of inertia of cut-out portion about its own center axis $I_{{cut\\_cm}}$:\n  $$I_{{cut\\_cm}} = \\frac{{1}}{{2}} m r^2 = \\frac{{1}}{{2}} \\times {mass_removed:.4f} \\times ({hole})^2 = {i_cut_cm:.6f}\\text{{ kg.m}}^2$$\n- By Parallel Axis Theorem, moment of inertia of cut-out portion about the main disc center $I_{{cut}}$ is:\n  $$I_{{cut}} = I_{{cut\\_cm}} + m d^2 = {i_cut_cm:.6f} + ({mass_removed:.4f} \\times {dist}^2) = {i_cut:.4f}\\text{{ kg.m}}^2$$\n\n### Step 4: Subtract moments of inertia\n$$I_{{remaining}} = I_{{whole}} - I_{{cut}} = {i_whole:.4f} - {i_cut:.4f} = {final:.4f}\\text{{ kg.m}}^2$$\n\n### Conclusion\nThe moment of inertia of the remaining portion of the disc is **{final:.4f} kg.m$^2$**.",
            "tags": ["Moment of Inertia", "Parallel Axis Theorem", "System of Particles"],
            "difficulty": "Hard"
        }
    ],
    "Chemistry": [
        {
            "topic": "Chemical Kinetics",
            "concept": "First order reaction half life",
            "input_template": "A first-order reaction has a rate constant of $k = {rate} \\times 10^{{-3}}$ s$^{{-1}}$. Calculate the time required for ${fraction}\\%$ of the reactant to decompose.",
            "output_template": "For a first-order chemical reaction, we use the integrated rate equation.\n\n### Step 1: Write down the integrated rate expression\n$$k = \\frac{{2.303}}{{t}} \\log\\left(\\frac{{[A]_0}}{{[A]_t}}\\right)$$\n\n### Step 2: Define concentrations\nLet the initial concentration $[A]_0 = 100$.\nSince ${fraction}\\%$ of the reactant has decomposed, the remaining concentration $[A]_t$ is:\n$$[A]_t = 100 - {fraction} = {rem}$$\n\n### Step 3: Rearrange and substitute given parameters\nGiven:\n- $k = {rate} \\times 10^{{-3}}$ s$^{{-1}}$\n- $[A]_0 = 100$\n- $[A]_t = {rem}$\n\n$$t = \\frac{{2.303}}{{k}} \\log\\left(\\frac{{100}}{{{rem}}}\\right)$$\n$$t = \\frac{{2.303}}{{{rate} \\times 10^{{-3}}}} \\log({ratio:.3f})$$\n$$t = {pre_log:.2f} \\times {log_val:.4f}$$\n$$t = {final:.2f}\\text{{ seconds}}$$\n\n### Conclusion\nThe time required for reactant to decompose to ${fraction}\\%$ is **{final:.2f} seconds**.",
            "tags": ["Chemical Kinetics", "First Order Reaction", "Rate Constant"],
            "difficulty": "Medium"
        }
    ],
    "Mathematics": [
        {
            "topic": "Definite Integration",
            "concept": "Integral of symmetric trigonometric limits",
            "input_template": "Evaluate the definite integral: $\\int_0^{{\\pi/2}} \\frac{{\\sin^{{{power}}} x}}{{\\sin^{{{power}}} x + \\cos^{{{power}}} x}} \\, dx$.",
            "output_template": "We solve this definite integral using properties of definite integrals (specifically the King's Rule).\n\n### Step 1: Let the integral be $I$\n$$I = \\int_0^{{\\pi/2}} \\frac{{\\sin^{{{power}}} x}}{{\\sin^{{{power}}} x + \\cos^{{{power}}} x}} \\, dx \\quad \\text{{--- (Equation 1)}}$$\n\n### Step 2: Apply the property $\\int_a^b f(x) \\, dx = \\int_a^b f(a+b-x) \\, dx$\nHere, $a = 0$ and $b = \\pi/2$. So we replace $x$ with $(\\pi/2 - x)$:\n$$I = \\int_0^{{\\pi/2}} \\frac{{\\sin^{{{power}}} (\\pi/2 - x)}}{{\\sin^{{{power}}} (\\pi/2 - x) + \\cos^{{{power}}} (\\pi/2 - x)}} \\, dx$$\n\nSince $\\sin(\\pi/2 - x) = \\cos x$ and $\\cos(\\pi/2 - x) = \\sin x$, we get:\n$$I = \\int_0^{{\\pi/2}} \\frac{{\\cos^{{{power}}} x}}{{\\cos^{{{power}}} x + \\sin^{{{power}}} x}} \\, dx \\quad \\text{{--- (Equation 2)}}$$\n\n### Step 3: Add Equation 1 and Equation 2\n$$2I = \\int_0^{{\\pi/2}} \\frac{{\\sin^{{{power}}} x + \\cos^{{{power}}} x}}{{\\sin^{{{power}}} x + \\cos^{{{power}}} x}} \\, dx$$\n$$2I = \\int_0^{{\\pi/2}} 1 \\, dx$$\n$$2I = [x]_0^{{\\pi/2}}$$\n$$2I = \\frac{{\\pi}}{{2}} - 0$$\n$$I = \\frac{{\\pi}}{{4}}$$\n\n### Conclusion\nThe value of the definite integral is **$\\frac{{\\pi}}{{4}}$**.",
            "tags": ["Definite Integration", "Properties of Integrals", "King's Rule"],
            "difficulty": "Easy"
        },
        {
            "topic": "Complex Numbers",
            "concept": "Roots of unity geometry",
            "input_template": "If $z = x + iy$ is a complex number satisfying $|z - {h}| = {r}$, find the minimum value of $|z - {px} - {py}i|$.",
            "output_template": "This problem is best solved geometrically using the representation of complex numbers in the Argand plane.\n\n### Step 1: Geometric interpretation of the given equation\nThe equation $|z - {h}| = {r}$ represents a circle $C$ in the complex plane with:\n- Center $C_0 = ({h}, 0)$\n- Radius $R = {r}$\n\n### Step 2: Geometric interpretation of the target expression\nThe expression $|z - ({px} + {py}i)|$ represents the distance from a point $z$ on the circle $C$ to a fixed point $P = ({px}, {py})$.\n\n### Step 3: Calculate the distance from center $C_0$ to point $P$\n$$d_{{center}} = \\sqrt{{( {px} - {h} )^2 + ( {py} - 0 )^2}}$$\n$$d_{{center}} = \\sqrt{{( {dx} )^2 + {py}^2}} = \\sqrt{{{dx2} + {py2}}} = \\sqrt{{{d2sum}}} = {d_center:.2f}$$\n\n### Step 4: Find the minimum distance\nThe minimum distance from a point on the circle to the point $P$ lies along the line connecting the center $C_0$ to $P$.\n- Minimum Distance $d_{{min}} = |d_{{center}} - R|$\n- Substituting values: $d_{{min}} = |{d_center:.2f} - {r}| = {final:.2f}$\n\n### Conclusion\nThe minimum value of $|z - {px} - {py}i|$ is **{final:.2f}**.",
            "tags": ["Complex Numbers", "Circle Geometry", "Argand Plane"],
            "difficulty": "Hard"
        }
    ]
}

class JEEQuestionGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def generate_programmatic_sample(self) -> Dict[str, Any]:
        """Generates a mathematically perfect, randomized sample based on templates."""
        subject = random.choice(SUBJECTS)
        templates = PROGRAMMATIC_TEMPLATES.get(subject)
        
        # Fallback if no template defined for custom selection
        if not templates:
            subject = "Physics"
            templates = PROGRAMMATIC_TEMPLATES["Physics"]
            
        template = random.choice(templates)
        
        # Instantiate values randomly
        topic = template["topic"]
        difficulty = template["difficulty"]
        tags = list(template["tags"])
        
        variables = {}
        if topic == "Electrostatics":
            val = random.randint(2, 500)
            dist = round(random.uniform(0.05, 5.0), 3)
            variables = {
                "val": val, "dist": dist, "num": 18 * val,
                "final": (18.0 * val) / dist
            }
        elif topic == "Rotational Mechanics":
            mass = round(random.uniform(2.0, 50.0), 2)
            rad = round(random.uniform(1.5, 10.0), 2)
            hole = round(rad / random.uniform(2.1, 3.9), 2)
            dist = round(rad / random.uniform(2.0, 2.5), 2)
            area_orig = round(rad ** 2, 3)
            area_hole = round(hole ** 2, 3)
            density = round(mass / area_orig, 3)
            mass_removed = round(density * area_hole, 3)
            i_whole = round(0.5 * mass * (rad ** 2), 4)
            i_cut_cm = round(0.5 * mass_removed * (hole ** 2), 6)
            i_cut = round(i_cut_cm + mass_removed * (dist ** 2), 4)
            variables = {
                "mass": mass, "rad": rad, "hole": hole, "dist": dist,
                "area_orig": area_orig, "density": density, "area_hole": area_hole,
                "mass_removed": mass_removed, "i_whole": i_whole, "i_cut_cm": i_cut_cm,
                "i_cut": i_cut, "final": i_whole - i_cut
            }
        elif topic == "Chemical Kinetics":
            rate = round(random.uniform(0.5, 9.9), 2)
            fraction = random.choice([25, 40, 50, 60, 75, 80, 90, 95, 99])
            rem = 100 - fraction
            ratio = 100.0 / rem
            import math
            log_val = math.log10(ratio)
            pre_log = 2.303 / (rate * 1e-3)
            variables = {
                "rate": rate, "fraction": fraction, "rem": rem, "ratio": ratio,
                "log_val": log_val, "pre_log": pre_log, "final": pre_log * log_val
            }
        elif topic == "Definite Integration":
            power = random.choice(["2", "3", "4", "5", "6", "7", "n", "3/2", "5/2"])
            variables = {"power": power}
        elif topic == "Complex Numbers":
            h = random.randint(1, 1000)
            r = random.randint(1, 200)
            px = h + random.randint(201, 500)
            py = random.randint(50, 400)
            dx = px - h
            d_center = (dx**2 + py**2)**0.5
            variables = {
                "h": h, "r": r, "px": px, "py": py, "dx": dx,
                "dx2": dx**2, "py2": py**2, "d2sum": dx**2 + py**2,
                "d_center": d_center, "final": abs(d_center - r)
            }
            
        inp = template["input_template"].format(**variables)
        out = template["output_template"].format(**variables)
        
        # Add slight variations to prevent absolute identity
        variation_prefixes = [
            "Solve the following question from JEE Syllabus.",
            "Analyze the given problem and determine the answer.",
            "Detailed mathematical solution is required for the following:",
            "Find the correct solution for this JEE question.",
            "Determine the correct numerical response for this JEE Main style problem.",
            "Work out the solution to the given question carefully.",
            "Answer this physical chemistry problem by following first principles.",
            "Evaluate this high-yield JEE mathematics question."
        ]
        
        return {
            "subject": subject,
            "topic": topic,
            "difficulty": difficulty,
            "instruction": random.choice(variation_prefixes),
            "input": inp,
            "output": out,
            "tags": tags,
            "source": "synthetic_programmatic_v1"
        }

    def generate_llm_sample(self, subject: str, topic: str, difficulty: str) -> Dict[str, Any]:
        """Queries the Hugging Face API to generate a high quality JEE question-answer pair."""
        if not self.api_key:
            raise ValueError("Hugging Face API key not found. Programmatic fallback required.")
            
        prompt = f"""[INST] You are an expert JEE IIT-JEE Master Tutor.
Generate one HIGH-QUALITY, challenging and mathematically correct {subject} question from the topic '{topic}' at '{difficulty}' difficulty.
The output MUST be a valid JSON object matching this schema EXACTLY:
{{
  "subject": "{subject}",
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "instruction": "Solve this challenging JEE question step-by-step.",
  "input": "Write the JEE question here. Use LaTeX for math wrapped inside $ for inline and $$ for block equations.",
  "output": "Provide an extremely comprehensive step-by-step solution here. Explain key formulas, constants, list logical step 1, 2, and 3, and state the final answer clearly. Wrap math in LaTeX standard ($ and $$).",
  "tags": ["tag1", "tag2"],
  "source": "huggingface_api"
}}
Ensure the JSON is perfectly formatted, with no extra text before or after, and all quotes escaped correctly. [/INST]"""

        try:
            response = requests.post(
                self.api_url,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 1024, "temperature": 0.7}},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result[0]["generated_text"] if isinstance(result, list) else result.get("generated_text", "")
                
                # Extract JSON string out of prompt response
                json_start = text.find("{")
                json_end = text.rfind("}")
                if json_start != -1 and json_end != -1:
                    json_str = text[json_start:json_end+1]
                    sample = json.loads(json_str)
                    # Quick schema validation
                    required_keys = ["subject", "topic", "difficulty", "instruction", "input", "output", "tags"]
                    if all(k in sample for k in required_keys):
                        return sample
            
            raise Exception(f"API returned status {response.status_code} or malformed content.")
        except Exception as e:
            # Fallback will be handled in master loop
            raise e

    def generate_bulk_dataset(self, size: int = 1000, use_api: bool = False) -> List[Dict[str, Any]]:
        """Generates a complete bulk dataset of the requested size."""
        dataset = []
        api_failed_count = 0
        
        print(f"[INFO] Generating {size} synthetic JEE records...")
        
        for i in range(size):
            if use_api and self.api_key:
                try:
                    # Select criteria
                    subj = random.choice(SUBJECTS)
                    top = random.choice(TOPICS[subj])
                    diff = random.choice(DIFFICULTIES)
                    
                    sample = self.generate_llm_sample(subj, top, diff)
                    dataset.append(sample)
                    print(f"  [API] Successfully generated sample {i+1}/{size} [{subj} - {top}]")
                    time.sleep(1) # Rate limit friendliness
                    continue
                except Exception:
                    api_failed_count += 1
            
            # Programmatic Generator (Highly reliable, zero cost, mathematically valid)
            sample = self.generate_programmatic_sample()
            dataset.append(sample)
            if (i+1) % 100 == 0 or (i+1) == size:
                print(f"  [PROG] Successfully generated sample {i+1}/{size} [{sample['subject']} - {sample['topic']}]")
                
        if api_failed_count > 0:
            print(f"[WARNING] {api_failed_count} API generations failed and gracefully fell back to programmatic templates.")
            
        return dataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JEE Mentor AI - Custom Synthetic Dataset Generator")
    parser.add_argument("--size", type=int, default=1050, help="Number of records to generate (default 1050)")
    parser.add_argument("--use-api", action="store_true", help="Try using Hugging Face API (requires HUGGINGFACE_API_KEY environment variable)")
    parser.add_argument("--output", type=str, default="dataset/raw_jee_dataset.json", help="Output file path")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    generator = JEEQuestionGenerator()
    data = generator.generate_bulk_dataset(size=args.size, use_api=args.use_api)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"[SUCCESS] Dataset generation finished! Saved {len(data)} records to {args.output}")
