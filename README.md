# 🚀 ClaimTracker — AI-Powered Health Insurance Claim Evaluation System

> **An intelligent, RAG-powered insurance claim analysis platform that evaluates healthcare claims against policy documents and provides explainable claim decisions.**

ClaimTracker is an AI-powered health insurance claim evaluation system designed to streamline the traditionally manual and time-consuming process of claim assessment.

The system accepts claim information and supporting medical documents such as **hospital bills, medical reports, and discharge summaries**, extracts relevant information, retrieves applicable clauses from insurance policy documents using **Retrieval-Augmented Generation (RAG)**, and uses an LLM to analyze the claim against the retrieved policy evidence.

The system produces one of three outcomes:

* ✅ **APPROVED** — Claim eligibility is clearly supported by the available policy evidence.
* ❌ **REJECTED** — The policy clearly establishes that the claim is not eligible.
* 🔍 **MANUAL_REVIEW** — Evidence is insufficient, ambiguous, conflicting, or requires human verification.

The goal is not to replace human insurance professionals but to provide an **AI-assisted decision-support system with traceable policy evidence and explainable reasoning**.

---

## 🎯 Problem Statement

Health insurance claim processing often requires manual verification of:

* Policy coverage
* Waiting periods
* Pre-existing diseases
* Exclusions
* Hospitalization requirements
* Treatment eligibility
* Claim limits and sub-limits
* Required documentation

Manually searching through lengthy insurance policy documents can be slow and error-prone.

**ClaimTracker addresses this problem by combining document processing, semantic search, vector databases, and LLM-based reasoning into a single claim evaluation workflow.**

---

## ✨ Key Features

### 📄 Multi-Document Claim Processing

Upload multiple claim documents including:

* Hospital Bills
* Medical Reports
* Discharge Summaries
* Other supporting PDF documents

The system extracts and combines relevant document content for claim analysis.

### 🔎 RAG-Based Policy Retrieval

Insurance policy documents are:

1. Processed and chunked
2. Converted into vector embeddings
3. Stored in Qdrant
4. Retrieved using semantic similarity search

This allows the system to find relevant policy clauses instead of passing the entire policy document to the LLM.

### 🧠 LLM-Powered Claim Evaluation

The LLM analyzes:

* Claim information
* Extracted medical document content
* Retrieved policy evidence

It then determines whether the claim should be:

`APPROVED`

`REJECTED`

or

`MANUAL_REVIEW`

### ⏳ Waiting Period Awareness

The system distinguishes between:

* Waiting periods
* Permanent exclusions

It avoids automatically rejecting claims when required information, such as the policy commencement date, is missing.

### 🔍 Explainable Decisions

Every decision includes a human-readable reason referencing the relevant policy evidence.

Example:

```json
{
  "claim_id": "CLM-F3A52A42",
  "decision": "MANUAL_REVIEW",
  "confidence": 0.97,
  "reason": "The claim involves Total Knee Replacement due to severe degenerative osteoarthritis. The policy specifies a 3-year waiting period. However, the policy commencement date is not available, so it cannot be determined whether the waiting period was completed. Manual review is required."
}
```

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │       Client         │
                    │  Claim Submission    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │    Claims API        │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │ Claim Documents │        │ Claim Metadata  │
        │ PDF Uploads     │        │ Policy Number   │
        └────────┬────────┘        └────────┬────────┘
                 │                          │
                 ▼                          │
        ┌─────────────────┐                 │
        │  PDF Processor  │                 │
        │ Text Extraction │                 │
        └────────┬────────┘                 │
                 │                          │
                 └─────────────┬────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Policy Query Builder │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Embedding Service    │
                    │ SentenceTransformers │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Qdrant         │
                    │   Vector Database    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Relevant Policy      │
                    │ Evidence Retrieval   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Claim Evaluator    │
                    │    LLM + Prompt      │
                    └──────────┬───────────┘
                               │
                               ▼
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
      APPROVED             REJECTED          MANUAL_REVIEW
```

---

# 🛠️ Tech Stack

### Backend

* **Python**
* **FastAPI**
* **Pydantic**
* **Uvicorn**

### AI / Machine Learning

* **LangChain**
* **Ollama**
* **Gemma**
* **Sentence Transformers**
* **RAG (Retrieval-Augmented Generation)**

### Vector Database

* **Qdrant**

### Document Processing

* PDF text extraction
* Document chunking
* Metadata extraction

### Development

* REST APIs
* Modular service architecture
* Environment-based configuration
* Local AI inference

---

# 🔄 Claim Evaluation Workflow

### Step 1 — Submit Claim

The user submits:

* Policy number
* Patient details
* Hospital information
* Treatment
* Admission and discharge dates
* Claim amount
* Pre-existing disease information

Along with:

* Hospital bill
* Medical report
* Discharge summary

### Step 2 — Process Documents

The PDF processor extracts text and relevant information from uploaded documents.

### Step 3 — Build Semantic Query

The system combines claim information and extracted medical information to create a semantic policy search query.

### Step 4 — Generate Embeddings

The query is converted into a vector using:

```text
all-MiniLM-L6-v2
```

### Step 5 — Retrieve Policy Evidence

Qdrant performs semantic similarity search and returns the most relevant policy chunks.

### Step 6 — Evaluate Claim

The retrieved policy evidence and claim information are passed to the LLM.

The LLM evaluates:

* Coverage
* Waiting periods
* Exclusions
* Treatment eligibility
* Pre-existing conditions
* Required information

### Step 7 — Generate Decision

The system returns:

```text
APPROVED
REJECTED
MANUAL_REVIEW
```

along with:

* Claim ID
* Confidence
* Explainable reason

---

# 🧠 Intelligent Decision Logic

A major design principle of ClaimTracker is:

> **Missing evidence should not automatically result in claim rejection.**

For example, if a policy specifies a 3-year waiting period but the policy commencement date is unavailable, the system should not assume the waiting period has expired or has not expired.

Instead:

```text
Waiting Period Found
        │
        ▼
Policy Start Date Available?
        │
    ┌───┴───┐
    │       │
   NO      YES
    │       │
    ▼       ▼
MANUAL    Calculate
REVIEW    Waiting Period
            │
            ▼
       Evaluate Claim
```

This approach reduces unsupported AI decisions and improves explainability.

---

# 📡 Example API

### Create Claim

```http
POST /claims/
Content-Type: multipart/form-data
```

Example fields:

```text
policy_number
patient_name
hospital_name
treatment
admission_date
discharge_date
claim_amount
pre_existing_disease
disease_name
hospital_bill
medical_report
discharge_summary
```

### Example Response

```json
{
  "claim_id": "CLM-F3A52A42",
  "decision": "MANUAL_REVIEW",
  "confidence": 0.97,
  "reason": "The retrieved policy evidence identifies a waiting period applicable to the claimed treatment. However, the policy commencement date is unavailable, preventing verification of whether the waiting period was completed. Manual review is required."
}
```

---

# 📁 Project Structure

```text
ClaimTracker/
│
├── app/
│   │
│   ├── claims/
│   │   ├── claim_service.py
│   │   ├── claim_evaluator.py
│   │   └── schemas.py
│   │
│   ├── documents/
│   │   └── pdf_processor.py
│   │
│   ├── embeddings/
│   │   └── embedding_service.py
│   │
│   ├── vectorstore/
│   │   └── qdrant_service.py
│   │
│   └── routers/
│       └── claims.py
│
├── uploads/
│   └── claims/
│
├── requirements.txt
├── .env
├── main.py
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/rahul-official-codebase/Claim-Tracker.git
cd ClaimTracker
```

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate on Windows:

```bash
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Start Qdrant

Run Qdrant locally using Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

## 5. Start Ollama

Install Ollama and pull the required model:

```bash
ollama pull gemma3:4b
```

## 6. Run FastAPI

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

# 🧪 Testing

The project includes synthetic test cases to validate different claim outcomes.

### Test Scenario 1

```text
Waiting period not completed
        ↓
REJECTED
```

### Test Scenario 2

```text
Waiting period completed
        ↓
APPROVED
```

### Test Scenario 3

```text
Required policy information missing
        ↓
MANUAL_REVIEW
```

### Test Scenario 4

```text
Explicit policy exclusion
        ↓
REJECTED
```

These test cases help validate the system's ability to distinguish between **eligibility, exclusion, waiting periods, and insufficient evidence**.

---

# 🔐 Important Design Considerations

ClaimTracker is designed as an **AI-assisted decision-support system** and not as a replacement for insurance professionals or legally binding claim adjudication.

The system follows an evidence-first approach:

```text
Policy Evidence
      +
Claim Documents
      +
Claim Information
      ↓
AI-Assisted Evaluation
      ↓
Explainable Decision
```

The system should use `MANUAL_REVIEW` whenever available evidence is insufficient to make a reliable determination.

---

# 🚧 Future Enhancements

* [ ] Policy database with policy-number lookup
* [ ] Policy start and renewal date verification
* [ ] Deterministic waiting-period calculation engine
* [ ] OCR support for scanned PDFs
* [ ] Advanced medical entity extraction
* [ ] Hybrid keyword + vector retrieval
* [ ] Reranking of retrieved policy evidence
* [ ] Claim history tracking
* [ ] PostgreSQL integration
* [ ] Authentication and role-based access control
* [ ] Human-in-the-loop review dashboard
* [ ] Audit logs for every AI decision
* [ ] Cloud deployment
* [ ] Automated evaluation and monitoring
* [ ] Multi-policy and multi-insurer support

---

# 💡 Why This Project Stands Out

ClaimTracker demonstrates practical implementation of modern AI engineering concepts:

* **Retrieval-Augmented Generation (RAG)**
* **Vector databases**
* **Semantic search**
* **LLM structured output**
* **Document processing**
* **AI-powered decision support**
* **Explainable AI**
* **Human-in-the-loop workflows**
* **Backend API development with FastAPI**
* **Modular service-oriented architecture**

Rather than simply generating text with an LLM, ClaimTracker focuses on **grounding AI decisions in retrieved policy evidence**, reducing unsupported conclusions and making the reasoning easier for humans to review.

---

# 👨‍💻 Author

**Rahul Singh**

Software Developer | Full-Stack Developer | AI & ML Developer

Interested in building scalable backend systems, intelligent applications, and production-ready software using modern technologies.

---

⭐ If you found this project interesting, consider giving the repository a star!

💬 Feedback, suggestions, and contributions are welcome.
