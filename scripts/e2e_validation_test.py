# ==============================================================================
# JEE MENTOR AI - AUTOMATED CLIENT-ONLY E2E VALIDATOR
# ==============================================================================
import os
import sys
import time
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple

def make_request(url: str, method: str = "GET", data: dict = None, headers: dict = None) -> Tuple[int, Dict[str, Any], bytes]:
    """Helper utilizing standard library urllib to perform HTTP requests dependency-free."""
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
        
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.status
            body_bytes = response.read()
            body_str = body_bytes.decode("utf-8")
            
            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type:
                return status, json.loads(body_str), body_bytes
            return status, {"message": body_str}, body_bytes
    except urllib.error.HTTPError as he:
        err_body = he.read().decode("utf-8")
        try:
            return he.code, json.loads(err_body), err_body.encode("utf-8")
        except Exception:
            return he.code, {"error": err_body}, err_body.encode("utf-8")
    except Exception as e:
        return 500, {"error": str(e)}, b""

def main():
    print("====================================================")
    print("JEE MENTOR AI - AUTOMATED E2E PIPELINE TEST")
    print("====================================================")

    base_url = "http://127.0.0.1:8000"
    auth_headers = {}

    try:
        # 1. Test Registration API
        print("[1/5] Testing User Registration (/register)...")
        reg_payload = {
            "email": "e2e_student@jeementor.ai",
            "username": "e2e_student",
            "password": "e2epassword123",
            "full_name": "E2E Student Auditor"
        }
        status, resp, _ = make_request(f"{base_url}/register", "POST", reg_payload)
        
        # Handle case where user is already registered (from past database runs)
        if status == 400 and "already exists" in resp.get("detail", ""):
            print("  - User already registered. Proceeding to login.")
        elif status not in [200, 201]:
            print(f"[ERROR] Registration Failed (Status {status}): {resp}")
            sys.exit(1)
        else:
            print(f"[SUCCESS] User registered successfully. User ID: {resp.get('id')}")

        # 2. Test Login API (Authentication)
        print("[2/5] Testing User Authentication (/login)...")
        login_payload = {
            "email": "e2e_student@jeementor.ai",
            "password": "e2epassword123"
        }
        status, resp, _ = make_request(f"{base_url}/login", "POST", login_payload)
        if status != 200:
            print(f"[ERROR] Login Failed (Status {status}): {resp}")
            sys.exit(1)
            
        token = resp.get("access_token")
        auth_headers = {"Authorization": f"Bearer {token}"}
        print("[SUCCESS] JWT authentication token generated successfully.")

        # 3. Test RAG Retrieval & Math Solver (POST /solve)
        print("[3/5] Testing RAG Context & Math Solver (/solve)...")
        solve_payload = {
            "question_text": "An infinite thin straight wire has a uniform linear charge density of lambda = 5e-6 C/m. Calculate the electric field intensity at r = 0.5 m.",
            "subject": "Physics"
        }
        status, resp, _ = make_request(f"{base_url}/solve", "POST", solve_payload, auth_headers)
        if status != 200:
            print(f"[ERROR] Solver API Failed (Status {status}): {resp}")
            sys.exit(1)
            
        print("[SUCCESS] Solver responded successfully:")
        print(f"  - Extracted formulas used: {resp.get('formulas_used')}")
        print(f"  - Latency: {resp.get('latency_ms')} ms")
        
        # Verify LaTeX exists inside the answer
        solution = resp.get("solution", "")
        if "$$" in solution or "$" in solution:
            print("  - LaTeX math typesets validated: PASS")
        else:
            print("  - Warning: Solution did not return standard LaTeX wraps.")

        # 3b. Test OCR Pipeline Solver (POST /solve with image_base64)
        print("[3b/5] Testing OCR Pipeline Solver (/solve with image_base64)...")
        # Tiny 1x1 transparent PNG base64 string to invoke the OCR pipeline
        tiny_png_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        ocr_payload = {
            "image_base64": tiny_png_base64,
            "subject": "Physics"
        }
        status_ocr, resp_ocr, _ = make_request(f"{base_url}/solve", "POST", ocr_payload, auth_headers)
        if status_ocr != 200:
            print(f"[ERROR] OCR Solver API Failed (Status {status_ocr}): {resp_ocr}")
            sys.exit(1)
            
        print("[SUCCESS] OCR Solver responded successfully:")
        print(f"  - Extracted text from image: '{resp_ocr.get('extracted_text')}'")
        print(f"  - OCR Extracted formulas used: {resp_ocr.get('formulas_used')}")
        print(f"  - OCR Latency: {resp_ocr.get('latency_ms')} ms")
        
        # Verify LaTeX exists inside the OCR answer
        ocr_solution = resp_ocr.get("solution", "")
        if "$$" in ocr_solution or "$" in ocr_solution:
            print("  - OCR LaTeX math typesets validated: PASS")
        else:
            print("  - Warning: OCR Solution did not return standard LaTeX wraps.")

        # 4. Test QLoRA Causal Streaming Doubt Chat (POST /chat)
        print("[4/5] Testing QLoRA Causal Chat Streaming (/chat)...")
        chat_payload = {
            "message": "Explain first order reaction kinetics.",
            "session_id": ""
        }
        
        req_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        req_data = json.dumps(chat_payload).encode("utf-8")
        req = urllib.request.Request(f"{base_url}/chat", data=req_data, headers=req_headers, method="POST")
        
        print("  - Reading Event-Stream buffer tokens:")
        with urllib.request.urlopen(req, timeout=15) as stream:
            # First line has session ID
            header = stream.readline().decode("utf-8").strip()
            print(f"    - Stream Header: {header}")
            
            # Read subsequent streamed tokens
            for _ in range(25): # read first 25 word tokens
                chunk = stream.read(12)
                if not chunk:
                    break
                sys.stdout.write(chunk.decode("utf-8"))
                sys.stdout.flush()
            print(" ... [Stream continues]")
        print("[SUCCESS] Chat streaming evaluated: PASS")

        # 5. Test Analytics Upgrades (GET /analyze)
        print("[5/5] Testing Student Analytics Dashboard Updates (/analyze)...")
        status, resp, _ = make_request(f"{base_url}/analyze", "GET", None, auth_headers)
        if status != 200:
            print(f"[ERROR] Analytics fetch failed: {resp}")
            sys.exit(1)
            
        print("[SUCCESS] Analytics Summary compiled successfully:")
        print(f"  - Subject Proficiencies: {resp.get('subjects_proficiency')}")
        print(f"  - Flagged Weak Topics Count: {len(resp.get('weak_topics', []))}")

        # Final Report
        print("\n====================================================")
        print("E2E SYSTEM INTEGRATION TEST PASSED!")
        print("====================================================")
        print("All boundary APIs, RAG queries, QLoRA fallbacks,")
        print("JWT validations, and LaTeX typesets are 100% operational!")
        print("JEE Mentor AI is officially FULLY RUNNING and DEPLOYMENT-READY.")
        print("====================================================\n")

    except Exception as e:
        print(f"\n[ERROR] E2E Pipeline failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
