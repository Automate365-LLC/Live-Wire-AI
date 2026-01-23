# WS4 Architecture Draft
**Date:** Jan 13, 2026 | **Sprint:** 1

---

## 1. Response Logic & Policy

**Objective:** To deterministically route user queries to the correct information source based on risk and relevance. This logic governs the AI's response generation layer.

### 1.1 Priority Hierarchy
The system evaluates potential responses in this strict order (P0 -> P3). The first valid match executes.

| Priority | Logic Tier         | Trigger Condition                                         | Action                                                                 |
|----------|------------------|-----------------------------------------------------------|------------------------------------------------------------------------|
| P0       | Compliance Layer  | If the query touches on Legal/Compliance/Pricing.       | Strict Verbatim: Block generation. Output pre-approved static text only. ("I cannot provide legal advice...") |
| P1       | Contextual RAG    | Input detected: High semantic similarity (>75%) to content in the Ingested Playbook. | Paraphrase: Generate response using only the retrieved context from the Playbook. |
| P2       | Objection Handling| Input detected: Recognized sales objection pattern (e.g., "It's too expensive") with no P1 match. | Generalize: Retrieve standard objection script from the System Prompt. |
| P3       | Fallback (Safety) | Input detected: No match in P0, P1, or P2 (Confidence < 50%). | Silent/Safe: "I don't have that info right now." (Do not hallucinate). |

### 1.2 Response Formatting Rules [WS4-02]

**Objective:** Responses must be optimized for real-time voice conversion (speakable, concise).

- **Length Constraint:** Maximum 1–3 sentences.  
- **Style:** Conversational, "speakable" plain text. No markdown lists, no complex punctuation.  
- **Discovery Logic:** If the intent is "Discovery," end with a question rather than a statement.  

**Bad:** "We offer three plans. The Pro plan is best."  
**Good:** "The Pro plan would likely fit best here. Shall I walk you through the pricing?"

---

## 2. Data Model & Entities [WS4-04]

**Overview:** The schema supports RAG retrieval with versioning.

### 2.1 Entity Scheme
- **Workspace:** Parent container. (1 : 1 relationship with Active Playbook).  
- **Playbook:** The uploaded file.  
  - `id`: UUID  
  - `version`: String (e.g., "v1.0") - Supports [WS4-05] retention/versioning  
  - `file_path`: String (Location in storage)  
- **Document:** The processed text extracted from the Playbook  
- **Chunk:** Small text segment used for search  
  - `chunk_id`: UUID  
  - `text_content`: String (~512 tokens)  
  - `embedding`: Vector Array (The math representation for search)  

### 2.2 Storage Plan [WS4-05]
- **v0 (MVP):** Local file storage for documents; In-memory vector store.  
- **v1 (Production):** Cloud Object Storage (S3/GCS) for files; Vector Database (Pinecone/Chroma) for embeddings.

---

## 3. Ingestion v0 [S1-WS4-02]

**Overview:** Defines the constraints and mechanisms for uploading Playbooks into the Workspace 4 environment.

### 3.1 Constraints
- **Supported Formats:** .txt, .docx, .pdf  
- **Maximum File Size:** 10MB  
- **Required Metadata Fields (per Chunk):**  
  - `source_file`: String - The name of the uploaded playbook  
  - `chunk_id`: UUID - Unique ID for the text segment  
  - `ingested_at`: Timestamp - When this file was processed  

### 3.2 Logic
**Validation:**  
- Reject unsupported extensions.  
- Reject files > 10MB.  

**Processing:**  
- The system must extract raw text from the uploaded file.  
- For PDF/Docx: Use standard library to strip formatting and retain only text content.  

**Chunking Logic:**  
- Delimiter: Split text by double newlines (`\n\n`) to preserve Q&A formatting.  
- Size Limit: If a chunk exceeds 1000 characters, recursively split by single newlines.

### 3.3 Workspace Constraints
- Rule: 1 Playbook per Workspace.  
- If a user attempts to upload a second playbook to an existing workspace, the system should prompt to replace the existing one or cancel the action.  
- Merging is not supported in v0.

---

## 4. Retrieval Inputs & Query Schema [S1-WS4-03]

**Overview:** Defines the JSON payload that the backend must send to the WS4 Engine to request a response.

### 4.1 Input Schema (Request)
```json
{
  "workspace_id": "string (required)",
  "transcript_window": "string (Format: 'Speaker: Text \\n Speaker: Text')",
  "idempotency_key": "string (UUIDv4) - Required to prevent duplicate processing",
  "metadata": {
    "objection_label": "string (optional, e.g., 'price_too_high')",
    "sales_stage": "string (optional, e.g., 'discovery')",
    "rep_notes": "string (optional)"
  }
}
```

### 4.2 Output Schema (Response)
```json
{
  "response_text": "string (1-2 sentences, speakable)",
  "metadata": {
    "source_type": "string (Playbook | Objection | Fallback)",
    "confidence_score": "float",
    "attribution": {
       "source_doc_title": "string (e.g., 'Sales_Script_v1.docx')",
       "chunk_ids": ["uuid_1", "uuid_2"]
    }
  }
}
```

### 4.3 Standard Error Codes

400 Bad Request: Missing workspace_id or empty transcript_window.

422 Unprocessable Entity: File upload exceeds 10MB or unsupported format.

429 Too Many Requests: Rate limit exceeded (prevent spam).

500 Internal Server Error: LLM Service is down (Client may play a "One moment please" filler audio)

## Sprint 3 Demo Acceptance Criteria [S1-WS4-05]

**Overview:** These are the conditions required to mark the Playbook feature as "shippable" for the Sprint 3 Internal Demo.

### 5.1 Success Scenario (Happy Path)
1. Setup: User uploads "gold_playbook.txt" to Workspace A.
2. Action: User simulates a call or text input asking about pricing (e.g., "How much does it cost?").
3. Verification: System retrieves the specific pricing chunk from the text file.
4. Output (Example): "We offer tiers starting at $99/month. Shall I pull up the comparison?" (Must contain correct data from file).

### 5.2 Failure Scenario (Fallback)
1. Action: User asks a question NOT in the playbook (e.g., "What is the weather in Tokyo?").
2. Verification: System detects confidence score < 50% (or no keyword match).
3. Output (Example): "I don't have that info right now." (System must NOT hallucinate an answer).

