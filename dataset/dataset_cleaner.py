# ==============================================================================
# JEE MENTOR AI - DATASET CLEANER & STANDARD_FORMATTER
# ==============================================================================
import os
import json
import re
import argparse
from typing import List, Dict, Any

class JEEDataCleaner:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path

    def normalize_text(self, text: str) -> str:
        """Normalizes spacing, capitalization, and minor character variations for deduplication."""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text) # Compact consecutive whitespace
        text = re.sub(r'[^\w\s\$\\\{\}\^_\+\-\*/=\(\)]', '', text) # Remove punctuation except core math
        return text

    def clean_latex(self, text: str) -> str:
        """Fixes common mathematical LaTeX typos and standardizes math wrapping."""
        if not text:
            return ""
            
        # 1. Ensure common variables and symbols are in LaTeX where appropriate
        # E.g. convert plain symbols like 'pi' to '\pi' in math contexts
        # Convert plain fractions 'a/b' to properly bounded variables if needed, 
        # but mostly clean up spacing in LaTeX:
        text = re.sub(r'\\pi\s+', r'\\pi ', text)
        
        # 2. Fix malformed double-dollar blocks
        # Replace empty math wrappers
        text = text.replace("$$$$", "")
        
        # 3. Clean up loose ends of LaTeX backslashes
        # If there's an orphaned \sin without math wrapper, we try to keep it safe.
        
        # 4. Standardize standard physical constants
        text = re.sub(r'(\d+)\s*x\s*10\^', r'\1 \\times 10^', text)
        text = re.sub(r'(\d+)\s*\*10\^', r'\1 \\times 10^', text)
        
        return text

    def clean_records(self) -> List[Dict[str, Any]]:
        """Loads dataset, removes duplicates, applies LaTeX sanitization, and returns cleaned list."""
        if not os.path.exists(self.input_path):
            print(f"[ERROR] Input file '{self.input_path}' not found.")
            return []

        with open(self.input_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        print(f"[INFO] Loaded {len(records)} raw records. Starting cleaning pipeline...")
        
        cleaned_records = []
        seen_questions = set()
        removed_dupes = 0
        removed_malformed = 0

        for r in records:
            # 1. Validation of required keys
            required_keys = ["subject", "topic", "difficulty", "input", "output"]
            if not all(r.get(k) for k in required_keys):
                removed_malformed += 1
                continue

            # 2. Extract and sanitize values
            subject = r["subject"].strip()
            topic = r["topic"].strip()
            difficulty = r["difficulty"].strip()
            instruction = r.get("instruction", "Solve this JEE question step-by-step.").strip()
            tags = [t.strip() for t in r.get("tags", []) if t.strip()]
            source = r.get("source", "cleaned_generator").strip()
            
            # 3. Deduplication Check
            norm_q = self.normalize_text(r["input"])
            if norm_q in seen_questions:
                removed_dupes += 1
                continue
                
            # 4. Math clean-ups
            cleaned_input = self.clean_latex(r["input"])
            cleaned_output = self.clean_latex(r["output"])
            
            # Check for empty string outputs after cleaning
            if not cleaned_input or not cleaned_output or len(cleaned_output) < 30:
                removed_malformed += 1
                continue

            seen_questions.add(norm_q)
            
            # 5. Save structured object
            cleaned_records.append({
                "subject": subject,
                "topic": topic,
                "difficulty": difficulty,
                "instruction": instruction,
                "input": cleaned_input,
                "output": cleaned_output,
                "tags": tags,
                "source": source
            })

        print(f"[INFO] Cleaning complete:")
        print(f"   - Removed duplicates: {removed_dupes}")
        print(f"   - Removed malformed: {removed_malformed}")
        print(f"   - Retained high-quality records: {len(cleaned_records)}")
        
        return cleaned_records

    def save_and_report(self):
        """Runs the pipeline and saves output."""
        cleaned_data = self.clean_records()
        
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            
        print(f"[SUCCESS] Cleaned dataset written successfully to: {self.output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JEE Mentor AI - Dataset Cleaner & LaTeX Standardizer")
    parser.add_argument("--input", type=str, default="dataset/raw_jee_dataset.json", help="Raw input JSON file")
    parser.add_argument("--output", type=str, default="dataset/cleaned_jee_dataset.json", help="Cleaned output JSON file")
    args = parser.parse_args()

    cleaner = JEEDataCleaner(args.input, args.output)
    cleaner.save_and_report()
