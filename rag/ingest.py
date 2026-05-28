# ==============================================================================
# JEE MENTOR AI - RAG INGESTION PIPELINE & CORPUS SEEDER
# ==============================================================================
import os
import uuid
from typing import List, Dict, Any
from rag.vector_store import JEEVectorStore

# A premium, pre-seeded knowledge base of core JEE Formulas and Concepts
# to ensure the retriever has rich content right out-of-the-box.
JEE_PRESEEDED_KNOWLEDGE = [
    # --- PHYSICS: ELECTROSTATICS ---
    {
        "text": "Coulomb's Law: The electrostatic force of attraction or repulsion between two point charges q1 and q2 separated by a distance r in vacuum is given by F = (1 / (4 * pi * epsilon_0)) * (q1 * q2 / r^2). The vector form is F_12 = k * (q1 * q2 / r^2) * r_hat_12. Constant k = 1 / (4 * pi * epsilon_0) ≈ 9 * 10^9 N.m^2/C^2. Epsilon_0 (permittivity of free space) = 8.854 * 10^-12 C^2/N.m^2.",
        "metadata": {"subject": "Physics", "topic": "Electrostatics", "type": "Formula"}
    },
    {
        "text": "Electric Field of an Infinite Line Charge: By applying Gauss's Law to a cylindrical Gaussian surface of radius r and length L surrounding a straight infinite wire of uniform linear charge density lambda, we find that the net flux is E * 2 * pi * r * L = lambda * L / epsilon_0. Solving for E gives E = lambda / (2 * pi * epsilon_0 * r). This field is directed radially outwards if lambda is positive, and inwards if lambda is negative.",
        "metadata": {"subject": "Physics", "topic": "Electrostatics", "type": "Derivation"}
    },
    {
        "text": "Electric Potential due to a Point Charge: The electric potential V at a distance r from a point charge q is defined as the work done in bringing a unit positive charge from infinity to that point. Mathematically, V = q / (4 * pi * epsilon_0 * r). Potential is a scalar quantity and is measured in Volts (V). The potential due to a system of charges is the algebraic sum of individual potentials.",
        "metadata": {"subject": "Physics", "topic": "Electrostatics", "type": "Theory"}
    },
    
    # --- PHYSICS: ROTATIONAL MECHANICS ---
    {
        "text": "Moment of Inertia (MOI) Formulas: For a uniform ring of mass M and radius R, I = M*R^2 about the central axis perpendicular to the plane. For a uniform solid disc of mass M and radius R, I = 0.5 * M * R^2. For a uniform solid sphere of mass M and radius R, I = (2/5) * M * R^2. For a hollow thin-walled sphere, I = (2/3) * M * R^2.",
        "metadata": {"subject": "Physics", "topic": "Rotational Mechanics", "type": "Formula"}
    },
    {
        "text": "Parallel Axis Theorem: The moment of inertia I of any body about an axis passing through some point is given by I = I_cm + M * d^2, where I_cm is the moment of inertia of the body about a parallel axis passing through its center of mass, M is the total mass of the body, and d is the perpendicular distance between the two axes.",
        "metadata": {"subject": "Physics", "topic": "Rotational Mechanics", "type": "Theory"}
    },
    {
        "text": "Perpendicular Axis Theorem: For a planar laminar body, the moment of inertia about an axis perpendicular to the plane (z-axis) is equal to the sum of the moments of inertia about two mutually perpendicular axes lying in the plane of the body (x and y axes) intersecting the z-axis: I_z = I_x + I_y. Note: This applies strictly to 2D flat objects.",
        "metadata": {"subject": "Physics", "topic": "Rotational Mechanics", "type": "Theory"}
    },

    # --- CHEMISTRY: CHEMICAL KINETICS ---
    {
        "text": "First Order Reaction Rate Equations: For a first-order reaction A -> Products, the differential rate law is -d[A]/dt = k[A]. The integrated rate law is ln([A]_0 / [A]_t) = k * t, which is often written as k = (2.303 / t) * log10([A]_0 / [A]_t). The half-life equation for a first-order reaction is t_1/2 = ln(2) / k ≈ 0.693 / k. Notice that the half-life is completely independent of the initial concentration of reactant.",
        "metadata": {"subject": "Chemistry", "topic": "Chemical Kinetics", "type": "Formula"}
    },
    {
        "text": "Arrhenius Equation: The temperature dependence of reaction rates is expressed by the Arrhenius equation: k = A * e^(-E_a / (R * T)), where k is the rate constant, A is the frequency/pre-exponential factor, E_a is the activation energy in Joules, R is the universal gas constant (8.314 J/mol.K), and T is the absolute temperature in Kelvin. In linear logarithmic form: ln(k2 / k1) = (E_a / R) * (1/T1 - 1/T2).",
        "metadata": {"subject": "Chemistry", "topic": "Chemical Kinetics", "type": "Formula"}
    },

    # --- MATHEMATICS: DEFINITE INTEGRATION ---
    {
        "text": "King's Rule / Definite Integration Property: A crucial integration property is Integral from a to b of f(x) dx = Integral from a to b of f(a + b - x) dx. For limits 0 to pi/2, this translates into substituting x with (pi/2 - x), which converts sin(x) to cos(x) and vice-versa, allowing symmetric denominators to be added and integrated cleanly.",
        "metadata": {"subject": "Mathematics", "topic": "Definite Integration", "type": "Theory"}
    },
    {
        "text": "Leibniz Rule for Differentiation under Integral Sign: If f(x, t) and its partial derivative are continuous, then d/dx [ Integral from g(x) to h(x) of f(t) dt ] = f(h(x)) * h'(x) - f(g(x)) * g'(x). This rule is frequently used in JEE Advanced to solve limits containing definite integrals.",
        "metadata": {"subject": "Mathematics", "topic": "Definite Integration", "type": "Formula"}
    },

    # --- MATHEMATICS: COMPLEX NUMBERS ---
    {
        "text": "Complex Numbers - Locus and Geometry: The equation |z - z_0| = R represents a circle in the Argand plane with center z_0 and radius R. The inequality |z - z_0| <= R represents the interior of the circle. The equation |z - z1| = |z - z2| represents the perpendicular bisector of the line segment joining the points z1 and z2.",
        "metadata": {"subject": "Mathematics", "topic": "Complex Numbers", "type": "Theory"}
    },
    {
        "text": "Euler's Formula and De Moivre's Theorem: Euler's formula states that e^(i * theta) = cos(theta) + i * sin(theta). De Moivre's Theorem states that for any integer n, (cos(theta) + i * sin(theta))^n = cos(n * theta) + i * sin(n * theta). This is instrumental in solving complex exponential systems and finding roots of unity.",
        "metadata": {"subject": "Mathematics", "topic": "Complex Numbers", "type": "Formula"}
    }
]

class JEEDataIngester:
    def __init__(self, db_path: str = "./data/chroma"):
        self.db = JEEVectorStore(persist_directory=db_path)

    def split_text_recursive(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """A simple, robust text-splitter mimicking langchain's RecursiveCharacterTextSplitter."""
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_words))
            if len(chunk_words) < chunk_size:
                break
            i += (chunk_size - overlap)
            
        return chunks

    def ingest_preseeded_corpus(self):
        """Seeds the ChromaDB vector database with the pre-assembled list of JEE knowledge."""
        print("[INFO] Starting database seeding with core JEE formulas...")
        
        texts = []
        metadatas = []
        ids = []
        
        for item in JEE_PRESEEDED_KNOWLEDGE:
            # Although they are short, we still run the splitter to conform to production pipeline
            chunks = self.split_text_recursive(item["text"], chunk_size=200, overlap=30)
            
            for index, chunk in enumerate(chunks):
                texts.append(chunk)
                
                # Append source tracking to metadata
                meta = item["metadata"].copy()
                meta["chunk_index"] = index
                meta["source"] = "jee_preseeded_corpus"
                metadatas.append(meta)
                
                # Generate unique ID
                ids.append(str(uuid.uuid4()))

        self.db.add_documents(texts, metadatas, ids)
        print(f"[SUCCESS] Ingested {len(texts)} semantic chunks into the RAG system!")

    def ingest_local_file(self, filepath: str, subject: str, topic: str):
        """Allows loading external files (e.g. NCERT chapters or custom notes) into the index."""
        if not os.path.exists(filepath):
            print(f"[ERROR] Ingestion source file '{filepath}' does not exist.")
            return

        print(f"[INFO] Ingesting file: {filepath} for {subject} - {topic}...")
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = self.split_text_recursive(content, chunk_size=300, overlap=40)
        
        texts = []
        metadatas = []
        ids = []
        
        for idx, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({
                "subject": subject,
                "topic": topic,
                "type": "Notes",
                "chunk_index": idx,
                "source": os.path.basename(filepath)
            })
            ids.append(str(uuid.uuid4()))

        self.db.add_documents(texts, metadatas, ids)
        print(f"[SUCCESS] Ingested {len(texts)} chunks from '{os.path.basename(filepath)}'.")

if __name__ == "__main__":
    ingester = JEEDataIngester()
    ingester.ingest_preseeded_corpus()
