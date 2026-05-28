# ==============================================================================
# JEE MENTOR AI - ADVANCED MATH, PLOTTING, & UNIT CONVERSION TOOLS
# ==============================================================================
import os
import re
import math
import base64
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple

class JEEMathTools:
    def __init__(self):
        # Configure dark-theme aesthetics for matplotlib plotting
        self.plot_dir = "./backend/plots"
        os.makedirs(self.plot_dir, exist_ok=True)

    # --- Tool 1: Safe Arithmetic Calculator ---
    def calculate(self, expression: str) -> str:
        """Safely parses and evaluates mathematical arithmetic expressions."""
        # Sanitize expression: only allow numbers, math ops, and select whitelisted words
        clean_expr = expression.replace("^", "**") # standard python exponent
        clean_expr = re.sub(r'[a-zA-Z_]+', lambda m: m.group(0) if m.group(0) in ['sin', 'cos', 'tan', 'log', 'log10', 'sqrt', 'pi', 'e', 'exp'] else '', clean_expr)
        
        # Strip all unsafe chars
        clean_expr = re.sub(r'[^0-9\+\-\*/\(\)\.\s\*,]', '', clean_expr) if not any(w in clean_expr for w in ['sin', 'cos', 'tan', 'log', 'sqrt', 'pi', 'e']) else clean_expr
        
        if not clean_expr.strip():
            return "Error: Expression contains forbidden characters or is empty."

        safe_dict = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "sqrt": math.sqrt,
            "exp": math.exp, "pi": math.pi, "e": math.e
        }
        
        try:
            # Evaluate under strict namespace
            result = eval(clean_expr, {"__builtins__": None}, safe_dict)
            return f"Result: {result}"
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"

    # --- Tool 2: SymPy Symbolic Solver ---
    def solve_symbolic(self, equation: str, variable: str = "x", mode: str = "solve") -> str:
        """Uses SymPy to solve algebraic equations, evaluate derivatives, or integrate functions."""
        try:
            import sympy as sp
            
            x = sp.Symbol(variable)
            # Standardize notation
            eq_cleaned = equation.replace("^", "**")
            
            if mode == "solve":
                # Solve sp.Eq(expr, 0)
                # Parse equality sign if present
                if "=" in eq_cleaned:
                    left, right = eq_cleaned.split("=")
                    expr = sp.sympify(left) - sp.sympify(right)
                else:
                    expr = sp.sympify(eq_cleaned)
                    
                roots = sp.solve(expr, x)
                return f"Solutions for {variable}: {roots}"
                
            elif mode == "diff":
                expr = sp.sympify(eq_cleaned)
                derivative = sp.diff(expr, x)
                return f"Derivative of {expr} w.r.t {variable}: {derivative}"
                
            elif mode == "integrate":
                expr = sp.sympify(eq_cleaned)
                integral = sp.integrate(expr, x)
                return f"Indefinite Integral of {expr} w.r.t {variable}: {sp.pretty(integral)}"
                
            else:
                return "Error: Unknown symbolic mode. Choose: 'solve', 'diff', or 'integrate'."
        except ImportError:
            return "Error: SymPy is not installed on the system."
        except Exception as e:
            return f"Symbolic Solver Error: {str(e)}"

    # --- Tool 3: Sleek Matplotlib neon graph plotter ---
    def plot_graph(self, equation_y: str, x_min: float = -10, x_max: float = 10) -> Dict[str, Any]:
        """Plots a function y = f(x) using high-yield dark aesthetics and returns a base64 image."""
        try:
            import matplotlib
            matplotlib.use('Agg') # Non-interactive backend
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Clean equation: y = x^2 - 4x + 3 -> x**2 - 4*x + 3
            expr = equation_y
            if "y=" in equation_y.replace(" ", ""):
                expr = equation_y.split("=")[1]
            
            expr_cleaned = expr.replace("^", "**")
            # Safe multiplication additions: e.g. 4x -> 4*x
            expr_cleaned = re.sub(r'(\d+)x', r'\1*x', expr_cleaned)
            
            # Formulate math parser
            x_vals = np.linspace(x_min, x_max, 400)
            
            # Safe local environment for numpy operations
            safe_dict = {
                "x": x_vals, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "sqrt": np.sqrt, "log": np.log, "exp": np.exp, "pi": np.pi
            }
            
            y_vals = eval(expr_cleaned, {"__builtins__": None}, safe_dict)
            
            # Create Plot with Neon Glassmorphic Theme
            fig, ax = plt.subplots(figsize=(7, 4.5), facecolor='#0D0E12')
            ax.set_facecolor('#0D0E12')
            
            # Plot the line with neon glow effect
            ax.plot(x_vals, y_vals, color='#8B5CF6', linewidth=2.5, label=f"y = {expr.strip()}", zorder=3)
            ax.plot(x_vals, y_vals, color='#8B5CF6', linewidth=6.0, alpha=0.3, zorder=2) # glow layer
            
            # Stylize grid and axis labels
            ax.grid(True, color='#1F2937', linestyle='--', alpha=0.6, zorder=1)
            ax.spines['bottom'].set_color('#374151')
            ax.spines['top'].set_color('#374151')
            ax.spines['left'].set_color('#374151')
            ax.spines['right'].set_color('#374151')
            ax.tick_params(colors='#9CA3AF', which='both')
            ax.xaxis.label.set_color('#D1D5DB')
            ax.yaxis.label.set_color('#D1D5DB')
            
            ax.set_xlabel('x-axis')
            ax.set_ylabel('y-axis')
            ax.set_title(f"Graph of {equation_y}", color='#F3F4F6', fontsize=12, pad=15)
            ax.legend(facecolor='#1F2937', edgecolor='#374151', labelcolor='#F3F4F6')
            
            plt.tight_layout()
            
            # Save to BytesIO for base64 return
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=120)
            buffer.seek(0)
            img_str = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return {
                "success": True,
                "base64": f"data:image/png;base64,{img_str}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Graph Plotting Failed: {str(e)}"
            }

    # --- Tool 4: Physical Unit Converter ---
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> str:
        """Performs high-precision physical and chemical unit conversions."""
        f_u = from_unit.lower().strip()
        t_u = to_unit.lower().strip()
        
        # eV <-> Joules (Modern Physics)
        if f_u == "ev" and t_u == "j":
            return f"{value} eV = {value * 1.60218e-19:.6e} Joules"
        elif f_u == "j" and t_u == "ev":
            return f"{value} Joules = {value / 1.60218e-19:.6e} eV"
            
        # Angstrom <-> Meters (Atomic Structure)
        elif f_u in ["angstrom", "a", "å"] and t_u == "m":
            return f"{value} Å = {value * 1e-10:.2e} meters"
        elif f_u == "m" and t_u in ["angstrom", "a", "å"]:
            return f"{value} meters = {value / 1e-10:.2e} Å"
            
        # atm <-> Pascal (Thermodynamics / States of Matter)
        elif f_u == "atm" and t_u == "pa":
            return f"{value} atm = {value * 101325:.2f} Pascals"
        elif f_u == "pa" and t_u == "atm":
            return f"{value} Pascals = {value / 101325:.6f} atm"
            
        # Calorie <-> Joule (Thermodynamics)
        elif f_u == "cal" and t_u == "j":
            return f"{value} calories = {value * 4.184:.3f} Joules"
        elif f_u == "j" and t_u == "cal":
            return f"{value} Joules = {value / 4.184:.3f} calories"
            
        else:
            return f"Error: Conversion from '{from_unit}' to '{to_unit}' is currently not supported."

if __name__ == "__main__":
    tools = JEEMathTools()
    print(tools.calculate("2 * sin(pi / 6) + sqrt(16)"))
    print(tools.convert_units(10.0, "eV", "J"))
    print(tools.plot_graph("y = x^2 - 3x + 2")["success"])
