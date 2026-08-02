# ==============================================================================
# JEE MENTOR AI - RESILIENT WEB SEARCH FALLBACK (BS4 SCRAPER)
# ==============================================================================
import re
import sys
import requests
from bs4 import BeautifulSoup

class JEEWebSearch:
    @staticmethod
    def _clean_query(query: str) -> str:
        """Removes conversational filler words to construct a high-yield keyword query."""
        cleaned = query.strip()
        if "Current Chat Query:" in cleaned:
            lines = cleaned.split("\n")
            for i, line in enumerate(lines):
                if "Current Chat Query:" in line and i + 1 < len(lines):
                    cleaned = lines[i+1].strip()
                    break
        
        cleaned = cleaned.lower()
        cleaned = re.sub(r"[^\w\s\-\.\+]", "", cleaned)
        cleaned = cleaned.replace("explain clearly step-by-step", "")
        cleaned = cleaned.replace("please explain", "")
        
        fillers = ["what is the value of", "what is", "value of", "find the", "find", "calculate the", "calculate", "determine the", "determine", "solve for", "solve"]
        for filler in fillers:
            cleaned = cleaned.replace(filler, "")
            
        # Add spacing between alphabetic characters and digits (e.g. sin60 -> sin 60)
        cleaned = re.sub(r"([a-zA-Z]+)(\d+)", r"\1 \2", cleaned)
        cleaned = re.sub(r"(\d+)([a-zA-Z]+)", r"\1 \2", cleaned)
            
        cleaned = " ".join(cleaned.split()) # normalize whitespace
        return cleaned

    @staticmethod
    def search_web(query: str, max_results: int = 3) -> str:
        """Searches DuckDuckGo Lite using requests/bs4 and returns formatted text snippets."""
        cleaned_query = JEEWebSearch._clean_query(query)
        if not cleaned_query:
            cleaned_query = query
            
        print(f"[INFO] Running Resilient Web Search. Raw query: '{query}' -> Cleaned query: '{cleaned_query}'")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            r = requests.post("https://lite.duckduckgo.com/lite/", data={"q": cleaned_query}, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"[WARNING] DuckDuckGo Lite search page returned status code: {r.status_code}")
                return ""
                
            soup = BeautifulSoup(r.text, "html.parser")
            tables = soup.find_all("table")
            
            results_table = None
            for t in tables:
                if t.find(class_="result-link") or len(t.find_all("tr")) > 10:
                    results_table = t
                    break
                    
            if not results_table and len(tables) > 1:
                results_table = tables[-1]
                
            if not results_table:
                print("[WARNING] Could not parse results table in DDG Lite HTML.")
                return ""
                
            rows = results_table.find_all("tr")
            results = []
            
            for i in range(len(rows)):
                link_tag = rows[i].find("a", class_="result-link")
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    href = link_tag.get("href", "")
                    
                    snippet = ""
                    if i + 1 < len(rows):
                        snippet_td = rows[i+1].find("td", class_="result-snippet")
                        if snippet_td:
                            snippet = snippet_td.get_text(strip=True)
                        else:
                            snippet = rows[i+1].get_text(strip=True)
                            
                    results.append((title, href, snippet))
                    if len(results) >= max_results:
                        break
                        
            if not results:
                print("[WARNING] Zero search results extracted from DDG Lite.")
                return ""
                
            formatted_snippets = []
            for idx, (title, href, snippet) in enumerate(results):
                formatted_snippets.append(f"--- Web Source #{idx+1} [{title}] ({href}) ---\n{snippet}")
                
            print(f"[SUCCESS] Resilient Web search completed. Found {len(results)} sources.")
            return "\n\n".join(formatted_snippets)
            
        except Exception as e:
            print(f"[WARNING] Resilient Web Search failed: {str(e)}")
            return ""

if __name__ == "__main__":
    # Test cases
    queries = [
        "what is the value of sin60",
        "Explain clearly step-by-step: what is the value of sin 60 degrees?"
    ]
    for q in queries:
        out = JEEWebSearch.search_web(q)
        print("\n=== Result for Query ===")
        # Safe console print for Windows encoding
        print(out.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'))
        print("========================")
