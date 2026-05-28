# ==============================================================================
# JEE MENTOR AI - DATASET VALIDATOR & STATS AUDITOR
# ==============================================================================
import os
import json
import argparse
from collections import Counter
from typing import List, Dict, Any

# Valid configuration bounds
ALLOWED_SUBJECTS = {"Physics", "Chemistry", "Mathematics"}
ALLOWED_DIFFICULTIES = {"Easy", "Medium", "Hard"}

class JEEDataValidator:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def validate_schema(self) -> bool:
        """Enforces schema constraints and logs issues or validation success."""
        if not os.path.exists(self.file_path):
            print(f"[ERROR] Target validation file '{self.file_path}' does not exist.")
            return False

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as jde:
            print(f"[ERROR] File is not a valid JSON structure. Decode Error: {jde}")
            return False

        if not isinstance(data, list):
            print("[ERROR] Top-level JSON entity must be a List (Array).")
            return False

        errors = []
        warnings = []
        
        # Statistics aggregations
        subject_counts = Counter()
        difficulty_counts = Counter()
        topic_counts = Counter()
        tags_counter = Counter()
        
        q_lengths = []
        ans_lengths = []
        latex_blocks = 0
        latex_inlines = 0

        for idx, r in enumerate(data):
            # Check existence of keys
            for key in ["subject", "topic", "difficulty", "instruction", "input", "output", "tags", "source"]:
                if key not in r:
                    errors.append(f"Record {idx}: Missing critical key '{key}'")
                    continue
            
            if len(errors) > 50:
                print("[ERROR] Too many validation errors. Aborting early.")
                return False

            # Type validations
            if not isinstance(r.get("subject"), str):
                errors.append(f"Record {idx}: 'subject' field must be a string")
            elif r["subject"] not in ALLOWED_SUBJECTS:
                errors.append(f"Record {idx}: Unknown subject '{r['subject']}' (Must be: {ALLOWED_SUBJECTS})")

            if not isinstance(r.get("difficulty"), str):
                errors.append(f"Record {idx}: 'difficulty' field must be a string")
            elif r["difficulty"] not in ALLOWED_DIFFICULTIES:
                errors.append(f"Record {idx}: Unknown difficulty '{r['difficulty']}'")

            if not isinstance(r.get("topic"), str) or not r["topic"].strip():
                errors.append(f"Record {idx}: 'topic' field must be a non-empty string")
            
            if not isinstance(r.get("input"), str) or len(r["input"].strip()) < 10:
                errors.append(f"Record {idx}: 'input' is missing or too short")

            if not isinstance(r.get("output"), str) or len(r["output"].strip()) < 20:
                errors.append(f"Record {idx}: 'output' solution is missing or too short")

            if not isinstance(r.get("tags"), list):
                errors.append(f"Record {idx}: 'tags' must be a List of strings")
            else:
                for tag in r["tags"]:
                    if not isinstance(tag, str):
                        errors.append(f"Record {idx}: Tag '{tag}' is not a string")

            # Collect metrics if no critical errors found so far for this row
            if not errors:
                subject_counts[r["subject"]] += 1
                difficulty_counts[r["difficulty"]] += 1
                topic_counts[r["topic"]] += 1
                
                for t in r["tags"]:
                    tags_counter[t] += 1
                    
                q_len = len(r["input"])
                ans_len = len(r["output"])
                q_lengths.append(q_len)
                ans_lengths.append(ans_len)
                
                # Check LaTeX wrapping consistency
                latex_inlines += len(r["input"].split('$')) // 2
                latex_blocks += len(r["output"].split('$$')) // 2

        # Final Report printing
        if errors:
            print(f"\n[ERROR] Validation Failed with {len(errors)} errors!")
            for err in errors[:20]:
                print(f"   - {err}")
            if len(errors) > 20:
                print(f"   ... and {len(errors) - 20} more errors.")
            return False

        print("\n====================================================")
        print("DATASET VALIDATION PASSED SUCCESSFULLY!")
        print("====================================================")
        print(f"[INFO] General Statistics:")
        print(f"   - Total valid records: {len(data)}")
        print(f"   - Average Question Length: {sum(q_lengths)/len(q_lengths):.1f} chars")
        print(f"   - Average Solution Length: {sum(ans_lengths)/len(ans_lengths):.1f} chars")
        print(f"   - Approx Inline LaTeX Equations ($...$): {latex_inlines}")
        print(f"   - Approx Block LaTeX Derivations ($$...$$): {latex_blocks}")
        
        print(f"\n[INFO] Subject Distribution:")
        for subj, count in subject_counts.items():
            print(f"   - {subj}: {count} ({count/len(data)*100:.1f}%)")

        print(f"\n[INFO] Difficulty Distribution:")
        for diff, count in difficulty_counts.items():
            print(f"   - {diff}: {count} ({count/len(data)*100:.1f}%)")

        print(f"\n[INFO] Top 10 Core Topics:")
        for topic, count in topic_counts.most_common(10):
            print(f"   - {topic}: {count}")

        print(f"\n[INFO] Top 10 Popular Tags:")
        for tag, count in tags_counter.most_common(10):
            print(f"   - {tag}: {count}")
        print("====================================================\n")
        
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JEE Mentor AI - Dataset Schema & Metrics Auditor")
    parser.add_argument("--file", type=str, default="dataset/cleaned_jee_dataset.json", help="Path to JSON dataset file to validate")
    args = parser.parse_args()

    validator = JEEDataValidator(args.file)
    success = validator.validate_schema()
    
    import sys
    sys.exit(0 if success else 1)
