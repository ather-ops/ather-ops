<!-- Ather Assadullah Peer (@ather-ops) — monochrome animated profile -->
<!-- All motion lives inside self-hosted SVGs in this repo, so nothing 404s. -->

# Ather Assadullah Peer

<div align="center">

### ML / AI Engineer · RAG Systems · Agentic AI · LLM Applications

**B.C.A. (Online) at LPU · 917 GitHub contributions in the last year · 100+ LeetCode problems**

</div>

---

<div align="center">

[![Portfolio](https://img.shields.io/badge/Portfolio-1f2937?style=for-the-badge&logo=vercel&logoColor=white)](https://portfolio-two-pink-24.vercel.app/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-334155?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/ather-assadullah-164492301)
[![X](https://img.shields.io/badge/X-0f172a?style=for-the-badge&logo=x&logoColor=white)](https://x.com/PeerAther47970)
[![Email](https://img.shields.io/badge/Email-475569?style=for-the-badge&logo=gmail&logoColor=white)](mailto:peerather07@gmail.com)
[![LeetCode](https://img.shields.io/badge/LeetCode-64748b?style=for-the-badge&logo=leetcode&logoColor=white)](https://leetcode.com/)

</div>

---

<table>
 <tr>
 <td align="center" valign="top">
 <img src="photo-reveal.svg" width="370" alt="Portrait of Ather Assadullah Peer" />
 </td>
 <td align="center" valign="top">
 <img src="info-card.svg" width="490" alt="Ather's info card" />
 </td>
 </tr>
</table>

---

## Contribution

<p align="center">
 <img src="contrib-heatmap.svg" alt="Ather's contribution graph" />
</p>

<p align="center">
 <img src="streak-graph.svg" alt="Ather's day streak graph" />
</p>

---

## About Me

Self-taught AI/ML engineer building **production RAG systems**, **multi-tool agentic assistants**, and **ML algorithms from mathematical first principles** — no shortcuts, no abstractions I haven't understood at the layer beneath.

- **Shipped two live AI apps**: [Xpect AI](https://x-ai-test.streamlit.app) (RAG, 0 → live in 15 days; 183 commits) and [Amazn AI](https://amazn-agentic-ai.streamlit.app) (multi-tool agent).
- **917 GitHub contributions in the last year** across 14 public repositories.
- **100+ LeetCode problems solved** across Easy, Medium and Hard; earned the **50 Days Badge 2026**.
- **Qualified in the top 23% of 1,34,421 applicants** for **Amazon ML Summer School 2026** (cleared CV + SOP screening; invited to the selection test).
- Implement ML algorithms (gradient descent, backpropagation, ensemble methods) **from scratch in NumPy**, validated line-by-line against library implementations.
- **Accepted to Since AI Hackathon 2026** — 72-hour in-person AI hackathon in Turku, Finland (6–8 Nov 2026).
- Based in **Bangalore, India** — open to remote roles worldwide.

---

## Education

| Year | Degree / Certificate | Institute | Score |
|---|---|---|---|
| 2026 – Present | **B.C.A. (Online)** — AI & ML specialization | Lovely Professional University | In progress |
| 2025 | Class XII (Science: PCM + Biology) | — | **80%** |
| 2023 | Class X | — | **80%** |

Self-study parallel track on agentic AI, RAG systems, and mathematical ML foundations.

---

## What I Build

| Area | Details |
|---|---|
| **RAG Systems** | End-to-end pipelines with FAISS, SentenceTransformers, Groq, Gemini, LangChain, ChromaDB — sub-second retrieval at scale |
| **Agentic AI** | smolagents CodeAgent, multi-tool orchestration, tool calling, ReAct agents; LangGraph (learning) |
| **Classical ML** | Linear/Logistic Regression, Random Forest, XGBoost, Gradient Descent, Backpropagation — built in NumPy from scratch |
| **Async API Systems** | Concurrent data collection from multiple real-world APIs, aggregation pipelines, real-time intelligence engines |
| **SQL & Databases** | Normalized schema design, JOINs, window functions, aggregations, grouping, CSV reporting (SQLite, PostgreSQL) |
| **Full-Stack Deployment** | FastAPI, Streamlit Cloud, HuggingFace Spaces, Vercel, Google Sheets API, PyMuPDF |

---

## Featured Projects

### [Xpect AI](https://x-ai-test.streamlit.app) — Semantic Movie Search with RAG · `Live`
End-to-end RAG over **8,800+ Netflix titles**: 384-dimensional embeddings via SentenceTransformers (all-MiniLM-L6-v2), FAISS similarity search, a persistent vector store, and answers grounded in retrieved context. **Rebuilt the retrieval layer from scratch**, replacing ChromaDB + NLTK with FAISS and lightweight pure-Python preprocessing. **Moved the LLM layer** from Gemini 2.5 Flash to **Groq (openai/gpt-oss-20b)** for noticeably faster inference. Modular codebase (EDA notebooks, `rag_engine`, `llm` and `pipeline` modules); deployed on Streamlit Cloud. 183 commits.
[Repo](https://github.com/ather-ops/Xpect-AI) · `Python` `FAISS` `SentenceTransformers` `Groq` `Streamlit`

### [Amazn AI](https://amazn-agentic-ai.streamlit.app) — Multi-Tool Agentic Assistant · `Live`
Built a **multi-tool agent** with smolagents: a `CodeAgent` routes each question to Product RAG, Support RAG or live order lookup, and chains tools into one answer (e.g., order status plus return policy). **Two independent RAG pipelines** with separate FAISS indexes — product search over the Amazon dataset, and support Q&A over a 134-page Amazon-style knowledge base (PyMuPDF extraction, cleaning, overlapping chunks). Live order lookup through a read-only Google Sheets tool, credentials in env secrets; deployed on Streamlit Cloud.
[Repo](https://github.com/ather-ops/Amazn-AI) · `Python` `smolagents` `FAISS` `SentenceTransformers` `Groq (LiteLLM)` `Google Sheets API` `PyMuPDF` `Streamlit`

### [PulseMesh](https://pulsh-mesh.streamlit.app) — Async API Intelligence Engine · `Live`
Concurrent data-aggregation engine that fans out across multiple real-world APIs in parallel, normalizes the responses, and surfaces structured intelligence in a single Streamlit dashboard. Built around `asyncio`, `aiohttp`, and a clean ETL core.
[Repo](https://github.com/ather-ops/pulsemesh) · `Python` `asyncio` `aiohttp` `Streamlit` `Pandas`

### [Atlas Agent](https://github.com/ather-ops/atlas-agent) — Autonomous AI Assistant · `in development`
Agent built on smolagents that **reasons, plans and selects tools**. Working tools today are date/time, system info and live weather. RAG memory and multi-agent orchestration are planned next.
`Python` `smolagents` `HuggingFace Inference API` `Gradio` `OpenWeather API`

### [Hospital Management SQL](https://github.com/ather-ops/Hospital-Management-SQL) — Database Engineering · `Live`
Designed a **relational database** (patients, doctors, appointments, treatments, billing) and wrote multi-table analytical SQL (joins, aggregations, grouping) for questions such as top-spending patients, doctor performance and treatment revenue, with CSV reports.
`SQL` `SQLite` `CSV reporting`

### Rain Predictor — Rainfall Classification · `Live`
Classification model that predicts rainfall. Live demo.
[Repo](https://github.com/ather-ops) · `Python` `scikit-learn`

### Customer Churn Predictor — Customer Retention · `Live`
Classification model for customer retention. Live demo.
[Repo](https://github.com/ather-ops) · `Python` `scikit-learn`

### [ML Algorithms from Mathematical Foundations](https://github.com/ather-ops) · `Code`
Implemented **Linear and Logistic Regression** and a **fraud-detection classifier** from scratch, validated against library outputs. Building **Random Forest** and **XGBoost** the same way — bootstrap sampling, entropy-based splits, gradient boosting, L1/L2 regularization.
`Python` `NumPy` `Pandas` `Matplotlib` `Scikit-learn`

---

## Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-0f172a?style=flat-square&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1e293b?style=flat-square&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-1f2937?style=flat-square&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-334155?style=flat-square&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-1e293b?style=flat-square)
![SQL](https://img.shields.io/badge/SQL-334155?style=flat-square&logo=mysql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-1f2937?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-334155?style=flat-square&logo=streamlit&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-0f172a?style=flat-square&logo=huggingface&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1f2937?style=flat-square&logo=langchain&logoColor=white)
![Git](https://img.shields.io/badge/Git-334155?style=flat-square&logo=git&logoColor=white)

**Languages:** Python (Advanced), C, C++, SQL
**RAG & LLMs:** RAG pipelines, FAISS, SentenceTransformers, Groq API (LiteLLM), Gemini API, LangChain, ChromaDB, Prompt Engineering, Semantic Search
**Agentic AI:** smolagents (CodeAgent), multi-tool orchestration, tool calling, ReAct agents; LangGraph (learning)
**ML / AI:** Scikit-learn, XGBoost, Random Forest, Linear and Logistic Regression, Gradient Descent, Backpropagation, Neural Networks (NumPy, from scratch)
**Deep Learning:** PyTorch (learning)
**Tools & Cloud:** Streamlit Cloud, HuggingFace Spaces, Vercel, Git/GitHub, Google Sheets API (gspread), PyMuPDF, Pandas, NumPy; FastAPI and AWS (learning)

</div>

---

## Key Achievements

- **Amazon ML Summer School 2026** — Top 23% of 1,34,421 applicants nationwide (cleared CV + SOP screening; invited to the selection test — quiz and coding round).
- **Since AI Hackathon 2026** — Accepted to a 72-hour in-person AI hackathon in Turku, Finland (6–8 Nov 2026) with 15 company challenges.
- **GenAI Powered Data Analytics Job Simulation — Tata Group (via Forage)** — EDA and risk profiling, delinquency prediction with AI, business storytelling, and an AI-driven collections strategy.
- **100+ LeetCode problems solved** across Easy, Medium and Hard; earned the **50 Days Badge 2026**.
- **Two production AI apps live** — Xpect AI (RAG, 0 → live in 15 days; 183 commits) and Amazn AI (multi-tool agent).
- **917 GitHub contributions in the last year** across 14 public repositories.
- Self-taught trajectory from zero ML knowledge to production RAG + multi-tool agentic systems within months, no formal CS background.

---

## Relevant Courses & Learning

- **Google ML Crash Course** — neural networks, embeddings, LLMs, RAG (ongoing)
- **Hugging Face Agents Course** — smolagents, ReAct (Units 1–2 completed)
- **Learn PyTorch for Deep Learning (Zero to Mastery)** — in progress
- **Advanced Python** — decorators, generators, async, OOP, type hints (in progress)
- **AWS Cloud Fundamentals** — EC2, S3, Lambda (in progress)
- **DSA in Python (GeeksforGeeks)** — arrays through dynamic programming
- **Next:** Transformers, LLM fine-tuning (LoRA), AWS deployment

---

## What I Bring to a Team

**Production Velocity** · Shipped Xpect AI (RAG) and Amazn AI (multi-tool agent), zero to live
**Mathematical Depth** · ML algorithms and gradient math implemented in NumPy, validated line-by-line
**Agentic AI Focus** · smolagents CodeAgent, multi-tool orchestration, RAG memory in progress
**Remote Discipline** · Daily commits, written-first communication, no-supervision-required execution

<br/>

<div align="center">

 **+91 91031-07882** (WhatsApp preferred) · **peerather07@gmail.com** · Bangalore, India · Open to Remote

</div>