# Aster Row AI Customer Support Agent

An advanced, production-grade AI customer support agent built for the CometChat Engineering - AI Internship assignment. Powered by Google's `gemini-3.6-flash` model and the modern `google-genai` SDK, this agent features Retrieval-Augmented Generation (RAG) with ChromaDB, automatic tool calling, strict prompt-injection defenses, and an automated evaluation test suite.

---

## 🏗️ Architecture & Core Features

1. **RAG & Policy Management:** Integrates ChromaDB for semantic search across company markdown policies, automatically filtering out superseded or legacy documents to enforce active rules.
2. **Robust Tool Execution:** Implements automatic function calling for order lookups (`get_order_status`) with built-in error handling and sanitization.
3. **Security & Guardrails:** Features multi-turn conversation memory paired with structural prompt-injection defenses to ignore malicious override commands embedded in retrieved documents.
4. **Automated Evaluation Suite (`eval_suite/run_eval.py`):** Runs deterministic pass/fail assertions across official visible cases and custom test cases, breaking down performance by category.

---

## 📂 Project Structure

aster-row-agent/        
├── src/
│   ├── ingestion/
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── vectorstore.py
│   │   └── pipeline.py
│   ├── order_tool.py          
│   ├── retrieval.py            
│   ├── agent.py                 
│   └── cli.py                   
├── eval_suite/
│   └── run_eval.py           
├── knowledge-base/              
├── data/                          
├── evaluation/
│   └── visible-cases.json       
├── logs/                       
├── requirements.txt               
├── .env.example                   
├── .env                         
├── .gitignore                    
└── README.md       

## 🚀 How to Run the Project

### Step 1 — Open Terminal & Navigate to the Project
cd ai-agent-intern-test-main

### Step 2 — Create and Activate a Virtual Environment
python -m venv venv

Windows (PowerShell):
venv\Scripts\Activate.ps1

Mac / Linux:
source venv/bin/activate

### Step 3 — Install Dependencies
pip install -r requirements.txt

### Step 4 — Configure Your API Keys
Windows:
copy .env.example .env

Mac / Linux:
cp .env.example .env

Open .env and add your keys:
GROQ_API_KEY=your_actual_groq_api_key_here
GEMINI_API_KEY=your_actual_gemini_api_key_here

### Step 5 — Build the Knowledge Base Index
python -m src.ingestion.pipeline

### Step 6 — Start the Chat CLI
python -m src.cli

### Step 7 — Run the Automated Evaluation Suite
python eval_suite/run_eval.py


## 📊 Evaluation Summary

The automated evaluation suite (`eval_suite/run_eval.py`) tests deterministic constraints (substring matching, negative assertions, and tool execution flags) across 15 official test cases and 5 custom test scenarios.

```text
==================================================
📊 EVALUATION SUMMARY REPORT
==================================================
Category             | Passed / Total  | Success Rate
--------------------------------------------------
retrieval            | 2 / 4           | 50.0%     
multi-source-grounding | 1 / 1           | 100.0%    
conversation         | 1 / 1           | 100.0%    
groundedness         | 2 / 2           | 100.0%    
tool-use             | 2 / 3           | 66.7%     
tool-reliability     | 3 / 3           | 100.0%    
privacy              | 1 / 2           | 50.0%     
prompt-security      | 1 / 1           | 100.0%    
abstention           | 1 / 1           | 100.0%    
source-conflict      | 1 / 1           | 100.0%    
multi-turn           | 0 / 1           | 0.0%      
--------------------------------------------------
OVERALL: 15 / 20 passed (75.0%)