<!-- Ather Assadullah Peer (@ather-ops) — monochrome animated profile -->
<!-- All motion lives inside self-hosted SVGs in this repo, so nothing 404s. -->

# Ather Assadullah Peer

<div align="center">

### ML / AI Engineer · RAG Systems · Agentic AI · LLM Applications

**CSE in AI/ML at LPU present · 917 GitHub contributions in the last year · 100+ LeetCode problems**

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

- **Shipped two live AI apps**: [Xpect AI](https://x-ai-test.streamlit.app) (RAG, zero to deployment in 15 days; 183 commits) and [Amazn AI](https://amazn-agentic-ai.streamlit.app) (multi-tool agent).
- **917 GitHub contributions in the last year** across 14 public repositories.
- **100+ LeetCode problems solved** — Array 85, Math 30, Hash Table 24, Binary Search 24; earned the **50 Days and 100 Days Badges 2026**.
- **Qualified in the top 23% of 1,34,421 applicants** for **Amazon ML Summer School 2026** (cleared CV + SOP screening; invited to the selection test).
- Implement ML algorithms **from scratch in NumPy** — Ridge matches Scikit-learn exactly (MSE 0.4598, R² 0.9767); Titanic random forest hits **80.9% test accuracy**.
- **Accepted to Since AI Hackathon 2026** — 72-hour in-person AI hackathon in Turku, Finland (6–8 Nov 2026).
- Based in **Bangalore, India** — open to remote roles worldwide.

**Project evolution:** Classical ML → SQL analytics → RAG → multi-tool agents — every stage deployed live.

---

## Education

**CSE in AI/ML at LPU present**

Self-study parallel track on agentic AI, RAG systems, and mathematical ML foundations.

---

## What I Build

| Area | Details |
|---|---|
| **RAG Systems** | End-to-end pipelines with FAISS, SentenceTransformers, Groq, Gemini, ChromaDB, Prompt Engineering, Semantic Search — sub-second retrieval at scale |
| **Agentic AI** | smolagents CodeAgent, multi-tool orchestration, tool calling, ReAct agents; LangGraph (learning) |
| **ML from Scratch** | Linear/Logistic Regression, KNN, Naive Bayes, SVM, Ridge, Lasso, Decision Tree, Random Forest, Gradient Descent — built in NumPy |
| **Data Analysis** | Pandas, NumPy, Matplotlib, Seaborn — EDA, data cleaning, feature engineering, outlier treatment |
| **SQL & Databases** | Normalized schema design, JOINs, window functions, aggregations, grouping, CSV reporting (SQLite) |
| **Full-Stack Deployment** | FastAPI, Streamlit Cloud, HuggingFace Spaces, Vercel, Google Sheets API, PyMuPDF |

---

## Featured Projects

### [Xpect AI](https://x-ai-test.streamlit.app) — Semantic Movie Search with RAG · `Live`
End-to-end RAG over **8,807 Netflix titles**: 384-dimensional `all-MiniLM-L6-v2` embeddings, FAISS similarity search with **exact search (top-5 retrieval)**, a persistent vector store, and answers grounded in retrieved context. **Rebuilt the retrieval layer from scratch**, replacing ChromaDB + NLTK with FAISS and lightweight pure-Python preprocessing. **Moved the LLM layer** from Gemini 2.5 Flash to **Groq (openai/gpt-oss-20b)** for noticeably faster inference. Modular codebase (EDA notebooks, `rag_engine`, `llm` and `pipeline` modules); deployed on Streamlit Cloud. 183 commits.
[Repo](https://github.com/ather-ops/Xpect-AI) · `Python` `FAISS` `SentenceTransformers` `Groq` `Streamlit`

### [Amazn AI](https://amazn-agentic-ai.streamlit.app) — Multi-Tool Agentic Assistant · `Live`
Built a **multi-tool agent** with smolagents: a `CodeAgent` routes each question to Product RAG, Support RAG or live order lookup, and chains tools into one answer (e.g., order status plus return policy). **Two independent RAG pipelines** with separate FAISS indexes — product search over the Amazon dataset, and support Q&A over a 134-page Amazon-style knowledge base (PyMuPDF extraction, cleaning, overlapping chunks). Live order lookup through a read-only Google Sheets tool, credentials kept in environment secrets; deployed on Streamlit Cloud.
[Repo](https://github.com/ather-ops/Amazn-AI) · `Python` `smolagents` `FAISS` `SentenceTransformers` `Groq (LiteLLM)` `Google Sheets API` `PyMuPDF` `Streamlit`

### [PulseMesh](https://pulsh-mesh.streamlit.app) — Async API Intelligence Engine · `Live`
Concurrent data-aggregation engine that fans out across multiple real-world APIs in parallel, normalizes the responses, and surfaces structured intelligence in a single Streamlit dashboard. Built around `asyncio`, `aiohttp`, and a clean ETL core.
[Repo](https://github.com/ather-ops/pulsemesh) · `Python` `asyncio` `aiohttp` `Streamlit` `Pandas`

### [Atlas Agent](https://github.com/ather-ops/atlas-agent) — Autonomous AI Assistant · `in development`
Agent built on smolagents that **reasons, plans and selects tools**. Working tools today are date/time, system info and live weather. RAG memory and multi-agent orchestration are planned next.
`Python` `smolagents` `HF Inference API` `Gradio` `OpenWeather API`

### [Hospital Management SQL](https://github.com/ather-ops/Hospital-Management-SQL) — Database Engineering · `Live`
Designed a **relational database** (patients, doctors, appointments, treatments, billing) and wrote multi-table analytical SQL (joins, aggregations, grouping) for questions such as top-spending patients, doctor performance and treatment revenue, with CSV reports.
`SQL` `SQLite` `CSV reporting`

### [Rain Predictor App](https://github.com/ather-ops/Rain-Predictor-App) — Rainfall Classification · `Code`
ML web app that predicts whether it will rain tomorrow from today's weather conditions — feature pipeline, trained classifier (with saved scaler, label encoder and model), and a Streamlit interface for predictions.
[Repo](https://github.com/ather-ops/Rain-Predictor-App) · `Python` `scikit-learn` `Streamlit`

### [Customer Churn Predictor](https://github.com/ather-ops/Customer-churn-predictor) — Customer Retention · `Code`
Classification model that predicts which customers are likely to churn, so retention action can be targeted at the right accounts — trained pipeline with saved scaler and model, served through a Streamlit interface.
[Repo](https://github.com/ather-ops/Customer-churn-predictor) · `Python` `scikit-learn`

### [ML Algorithms from Scratch](https://github.com/ather-ops/Supervised-ML-from-scratch) · `Code`
Implemented **linear and logistic regression, KNN, Naive Bayes, SVM, Ridge, Lasso, decision tree and random forest** from scratch in NumPy, Pandas and Matplotlib. **Ridge matches Scikit-learn exactly (MSE 0.4598, R² 0.9767)**; **Titanic random forest: 80.9% test accuracy**.
[From scratch](https://github.com/ather-ops/Supervised-ML-from-scratch) · [Trees & ensembles](https://github.com/ather-ops/decision-trees-forest) · [Scikit-learn workflows](https://github.com/ather-ops/Supervised-ML-with-Scikit-Learn)
`Python` `NumPy` `Pandas` `Matplotlib` `Scikit-learn`

### [Cafe Sales Analysis](https://github.com/ather-ops/Supervised-ML-from-scratch) — Data Cleaning and EDA · `Code`
Cleaned a dirty 10,000-transaction dataset (missing values, error placeholders, type fixes), engineered day, item, price and size categories, and treated outliers with **IQR removal and capping**. EDA across items, locations, payments and time: **Salad led revenue despite Juice selling more**, weekdays out-earned weekends (**Rs 64,897 vs 24,346**), and **~40% of sales had no location recorded**.
`Python` `Pandas` `NumPy` `Matplotlib` `Seaborn`

---

## Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-0f172a?style=flat-square&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1e293b?style=flat-square&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-1f2937?style=flat-square&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3F4F75?style=flat-square&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=flat-square&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-334155?style=flat-square&logo=scikit-learn&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-334155?style=flat-square&logo=mysql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-1f2937?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-334155?style=flat-square&logo=streamlit&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-0f172a?style=flat-square&logo=huggingface&logoColor=white)
![Git](https://img.shields.io/badge/Git-334155?style=flat-square&logo=git&logoColor=white)

**Languages:** Python (Advanced), C, C++, SQL
**Data Analysis:** Pandas, NumPy, Matplotlib, Seaborn, EDA, data cleaning, feature engineering
**ML / AI:** Scikit-learn, linear and logistic regression, KNN, Naive Bayes, SVM, Ridge and Lasso, decision trees, random forest, gradient descent, gradient boosting; PyTorch (learning)
**RAG & LLMs:** RAG pipelines, FAISS, SentenceTransformers, Groq API (LiteLLM), Gemini API, ChromaDB, Prompt Engineering, Semantic Search
**Agentic AI:** smolagents (CodeAgent), multi-tool orchestration, tool calling, ReAct agents; LangGraph (learning)
**Tools & Cloud:** Streamlit Cloud, HuggingFace Spaces, Vercel, Git/GitHub, Google Sheets API (gspread), PyMuPDF; FastAPI and AWS (learning)

</div>

---

## Key Achievements

- **Amazon ML Summer School 2026** — Top 23% of 1,34,421 applicants nationwide (cleared CV + SOP screening; invited to the selection test — quiz and coding round).
- **Since AI Hackathon 2026** — Accepted to a 72-hour in-person AI hackathon in Turku, Finland (6–8 Nov 2026) with 15 company challenges.
- **GenAI Powered Data Analytics Job Simulation — Tata Group (via Forage)** — EDA and risk profiling, delinquency prediction with AI, business storytelling, and an AI-driven collections strategy.
- **100+ LeetCode problems solved** — Array 85, Math 30, Hash Table 24, Binary Search 24; earned the **50 Days and 100 Days Badges 2026**.
- **Two production AI apps live** — Xpect AI (RAG, zero to deployment in 15 days; 183 commits) and Amazn AI (multi-tool agent).
- **917 GitHub contributions in the last year** across 14 public repositories.
- **Nine ML algorithms from scratch** — Ridge matching Scikit-learn exactly (MSE 0.4598, R² 0.9767) and a Titanic random forest at 80.9% test accuracy.
- Self-taught trajectory from zero ML knowledge to production RAG + multi-tool agentic systems within months, built alongside the CSE program.

---

## Relevant Courses & Learning

- **Google ML Crash Course** — neural networks, embeddings, LLMs, RAG (ongoing)
- **Hugging Face Agents Course** — smolagents, ReAct (Units 1–2 completed)
- **Learn PyTorch for Deep Learning (Zero to Mastery)** — in progress
- **Advanced Python** — decorators, generators, async, OOP, type hints (in progress)
- **AWS Cloud Fundamentals** — EC2, S3, Lambda (in progress)
- **Next:** Transformers, LLM fine-tuning (LoRA), AWS deployment

---

## What I Bring to a Team

**Production Velocity** · Shipped Xpect AI (RAG) and Amazn AI (multi-tool agent), zero to live
**Mathematical Depth** · Nine ML algorithms implemented in NumPy, validated line-by-line against Scikit-learn
**Agentic AI Focus** · smolagents CodeAgent, multi-tool orchestration, RAG memory in progress
**Remote Discipline** · Daily commits, written-first communication, no-supervision-required execution

<br/>

<div align="center">

 **peerather07@gmail.com** · Bangalore, India · Open to Remote

</div>