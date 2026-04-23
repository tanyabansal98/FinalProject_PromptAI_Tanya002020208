# 🩺 Symptom Journey Mapper

AI-powered multi-agent system for longitudinal symptom tracking, severity triage, and intelligent care routing.

---

## 🚀 Overview

Symptom Journey Mapper transforms fragmented patient symptom inputs into a **structured, time-aware, clinically grounded narrative**.

Instead of isolated snapshots, the system tracks symptoms across time, detects patterns, evaluates severity, and generates a **doctor-ready summary**.

---

## ❗ Problem

- Patients get ~5 minutes to explain symptoms
- Symptoms evolve over months/years but are discussed in isolation
- Diagnostic errors affect millions annually
- Standard LLMs:
  - No memory across sessions
  - No temporal reasoning
  - No clinical grounding
  - No safety guarantees

---

## 💡 Solution

A **multi-agent pipeline** that:
- Tracks symptom progression over time
- Detects escalation and patterns
- Applies clinical triage logic
- Grounds outputs using verified medical sources
- Generates structured summaries for clinical use

---

## 🧠 Architecture

### Agent Pipeline

1. **Symptom Extractor**
   - Converts raw text → structured data
   - Extracts symptoms, severity, duration, frequency
   - Maps to ICD-10 codes

2. **Temporal Pattern Analyzer**
   - Tracks symptoms across entries
   - Detects escalation, co-occurrence, cycles

3. **Condition Cluster Engine (RAG)**
   - Retrieves medical literature
   - Maps symptom clusters to possible conditions
   - Outputs are citation-backed

4. **Severity & Urgency Classifier**
   - Scores severity (functional impact)
   - Detects urgency using clinical red-flag rules

5. **Care Pathway Router**
   - Recommends care level (Routine → ER)
   - Suggests relevant specialists

6. **Narrative Summary Generator**
   - Produces a doctor-ready report
   - Includes timeline, patterns, severity trends, and citations

---

## 📊 Urgency Scoring
- U(t) = α·R(t) + β·S(t) + γ·(Δseverity/Δtime)

- 
- R(t): Red-flag detection (rule-based override)
- S(t): Symptom severity
- Δseverity/Δtime: Rate of change
- α >> β, γ → Emergency signals dominate

---

## 🛡️ Safety Features

- RAG grounding (no hallucinated claims)
- Rule-based red-flag overrides
- Confidence tagging for temporal claims
- Explicit uncertainty handling ("I don’t know")

---

## 📚 Data Sources

- ICD-10-CM (CDC/WHO)
- NIH MedlinePlus
- PubMed Open Access
- CDC Clinical Guidelines
- Emergency Severity Index (ESI)
- OpenFDA API

---

## 🧪 Evaluation

- Extraction: Precision / Recall
- Temporal reasoning accuracy
- RAG faithfulness (claim ↔ source)
- Triage agreement (Cohen’s Kappa)
- Routing accuracy (guideline-based)

---

## ⚙️ Tech Stack

**Backend**
- Python
- FastAPI
- LLM APIs (OpenAI / Claude)

**AI**
- NER / Information Extraction
- RAG pipeline
- Multi-agent orchestration

**Frontend**
- React.js

**Storage**
- ChromaDB (vector database)

---

## 🧱 MVP Scope

### Phase 1 (Core)
- Symptom extraction
- Temporal tracking
- Severity scoring
- Summary generation

### Phase 2
- RAG-based condition clustering
- Care routing

---

## 💰 Cost

- LLM APIs: $5–15
- Embeddings: $1–3
- Vector DB: Free
- Datasets: Free

**Total: < $20**

---

## 🎯 Output

- Symptom timeline
- Pattern detection
- Severity progression
- Condition associations (with citations)
- Care recommendations
- Doctor-ready summary

---

## ⚠️ Disclaimer

- Not a diagnostic tool
- Does not replace medical professionals
- Designed to assist clinical conversations

---

## 👩‍💻 Author

Tanya Bansal  
MS Information Systems — Northeastern University  
4+ years Software Engineering @ Jio Platforms

---

## ⭐ Key Insight

This system shifts healthcare from:
**fragmented symptom recall → structured longitudinal understanding**
