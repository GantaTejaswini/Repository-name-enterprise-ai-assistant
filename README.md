\# Enterprise AI Assistant



A production-oriented, multi-tenant enterprise knowledge assistant built with \*\*FastAPI, React, Elasticsearch, PostgreSQL, Redis, hybrid search, local embeddings, and Retrieval-Augmented Generation (RAG)\*\*.



The system allows authenticated users to upload PDF documents and ask natural-language questions against their organization's knowledge base while enforcing tenant isolation, RBAC, audit logging, and API rate limiting.



\---



\## Architecture



```text

&#x20;                   ┌─────────────────────┐

&#x20;                   │     React Frontend  │

&#x20;                   │      Vite + UI      │

&#x20;                   └──────────┬──────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌─────────────────────┐

&#x20;                   │    FastAPI API      │

&#x20;                   │ Auth / RBAC / RAG   │

&#x20;                   └──────┬──────┬───────┘

&#x20;                          │      │

&#x20;             ┌────────────┘      └─────────────┐

&#x20;             ▼                                 ▼

&#x20;    ┌─────────────────┐              ┌─────────────────┐

&#x20;    │  PostgreSQL     │              │ Elasticsearch   │

&#x20;    │                 │              │                 │

&#x20;    │ Users           │              │ BM25            │

&#x20;    │ Tenants         │              │ kNN             │

&#x20;    │ Roles           │              │ RRF             │

&#x20;    │ Documents       │              │ Embeddings      │

&#x20;    │ Audit Logs      │              │ Chunks          │

&#x20;    └─────────────────┘              └────────┬────────┘

&#x20;                                              │

&#x20;                                              ▼

&#x20;                                   ┌─────────────────────┐

&#x20;                                   │ Local Embedding     │

&#x20;                                   │ Nemotron Embed 1B  │

&#x20;                                   └──────────┬──────────┘

&#x20;                                              │

&#x20;                                              ▼

&#x20;                                   ┌─────────────────────┐

&#x20;                                   │ Context Builder     │

&#x20;                                   └──────────┬──────────┘

&#x20;                                              │

&#x20;                                              ▼

&#x20;                                   ┌─────────────────────┐

&#x20;                                   │ LLM Answer Provider  │

&#x20;                                   │ Extractive / Local   │

&#x20;                                   └─────────────────────┘



&#x20;                   ┌─────────────────────┐

&#x20;                   │       Redis         │

&#x20;                   │  Rate Limiting     │

&#x20;                   └─────────────────────┘

```



\---



\## Key Features



\### Authentication



\* JWT-based authentication

\* Secure password hashing

\* Access-token expiration

\* Protected API endpoints

\* Authentication validation through FastAPI dependencies



\### Role-Based Access Control



The application supports role-based authorization.



Example:



```text

admin

```



Protected resources can require specific roles before allowing access.



\### Multi-Tenant Architecture



Tenant isolation is enforced at both application and data layers.



PostgreSQL records contain tenant ownership, while Elasticsearch queries apply tenant filters during retrieval.



This prevents users from retrieving documents belonging to another organization.



\### PDF Knowledge Ingestion



The document pipeline supports:



```text

PDF Upload

&#x20;   ↓

Validation

&#x20;   ↓

Text Extraction

&#x20;   ↓

Page Processing

&#x20;   ↓

Semantic Chunking

&#x20;   ↓

Embedding Generation

&#x20;   ↓

Elasticsearch Indexing

```



Uploaded files are validated for:



\* PDF extension

\* Content type

\* File size

\* PDF signature



The system currently limits uploaded files to \*\*10 MB\*\*.



\### Hybrid Retrieval



The retrieval system combines:



1\. \*\*BM25 lexical search\*\*

2\. \*\*kNN vector similarity search\*\*

3\. \*\*Reciprocal Rank Fusion (RRF)\*\*



Conceptually:



```text

&#x20;                   User Question

&#x20;                        │

&#x20;             ┌──────────┴──────────┐

&#x20;             ▼                     ▼

&#x20;         BM25 Search           kNN Search

&#x20;             │                     │

&#x20;             └──────────┬──────────┘

&#x20;                        ▼

&#x20;                 RRF Ranking

&#x20;                        │

&#x20;                        ▼

&#x20;                  Top-K Chunks

```



This allows the system to combine keyword relevance with semantic similarity.



\### Local Embeddings



The project uses:



```text

nvidia/llama-nemotron-embed-1b-v2

```



Embeddings are generated locally and indexed in Elasticsearch.



\### RAG Pipeline



The question-answering flow is:



```text

User Question

&#x20;     ↓

Query Embedding

&#x20;     ↓

BM25 + kNN Retrieval

&#x20;     ↓

RRF Ranking

&#x20;     ↓

Top-K Relevant Chunks

&#x20;     ↓

Context Builder

&#x20;     ↓

Answer Generation

&#x20;     ↓

Answer + Sources + Timing

```



The assistant is instructed to answer using only retrieved document context and avoid unsupported information.



\### Citations



Responses include source information such as:



\* Document filename

\* Page number

\* Chunk ID

\* Document ID

\* Tenant ID

\* Retrieval ranking

\* BM25 score

\* kNN score

\* RRF score



\---



\## Security



The project includes several security controls.



\### JWT Authentication



Protected routes require a valid Bearer token.



\### RBAC



Authorization checks the user's role before allowing access to protected resources.



\### Tenant Isolation



Tenant filters are applied to Elasticsearch retrieval operations.



PostgreSQL access is also tenant-aware.



\### Audit Logging



Important actions are recorded in the audit log, including authentication events and document operations.



\### Security Headers



The API provides security-related HTTP headers including:



```text

X-Content-Type-Options

X-Frame-Options

Referrer-Policy

Permissions-Policy

```



\### Rate Limiting



Redis-backed rate limiting protects the API from excessive requests.



The current configuration allows:



```text

60 requests / minute / client

```



When the limit is exceeded:



```text

HTTP 429

```



is returned.



If Redis temporarily becomes unavailable, the application fails open rather than blocking all API traffic.



\---



\## Technology Stack



\### Frontend



\* React

\* Vite

\* JavaScript

\* CSS



\### Backend



\* Python

\* FastAPI

\* Uvicorn

\* Pydantic

\* SQLAlchemy

\* Alembic



\### Databases / Infrastructure



\* PostgreSQL

\* Elasticsearch

\* Redis



\### AI / ML



\* PyTorch

\* Transformers

\* Sentence Transformers

\* NVIDIA Nemotron embedding model

\* Retrieval-Augmented Generation



\### DevOps



\* Docker

\* Docker Compose

\* Git

\* GitHub

\* GitHub Actions



\---



\## Project Structure



```text

enterprise-ai-assistant/

│

├── .github/

│   └── workflows/

│

├── backend/

│   ├── app/

│   │   ├── api/

│   │   ├── core/

│   │   ├── middleware/

│   │   ├── models/

│   │   ├── repositories/

│   │   ├── schemas/

│   │   └── services/

│   │

│   ├── evaluation/

│   ├── migrations/

│   ├── tests/

│   ├── Dockerfile

│   ├── requirements.txt

│   └── .env

│

├── elasticsearch/

├── frontend/

├── ingestion/

├── models/

├── postgres/

├── tests/

│

├── docker-compose.yml

└── README.md

```



\---



\## Running the Project



\### Prerequisites



Install:



\* Python 3.12

\* Node.js

\* npm

\* Docker Desktop

\* Git



\---



\## Start Infrastructure with Docker



From the project root:



```powershell

docker compose up -d

```



Check containers:



```powershell

docker compose ps

```



The expected services are:



```text

enterprise-backend

enterprise-frontend

enterprise-elasticsearch

enterprise-postgres

enterprise-redis

```



\---



\## Backend



The backend runs on:



```text

http://localhost:8000

```



Health endpoint:



```text

http://localhost:8000/health

```



Interactive API documentation:



```text

http://localhost:8000/docs

```



\---



\## Frontend Development Mode



For frontend development:



```powershell

cd frontend

npm install

npm run dev

```



The development frontend is available at:



```text

http://localhost:5173

```



\---



\## Production Frontend



The Docker frontend is served through Nginx on:



```text

http://localhost

```



\---



\## Authentication



Demo account:



```text

Email: demo@company.com

Password: password123

```



Do not use demo credentials in a production deployment.



\---



\## Main API Areas



The backend exposes API groups for:



```text

/api/auth

/api/documents

/api/chat

```



Additional internal services support:



\* document ingestion

\* retrieval

\* embeddings

\* RAG

\* audit logging

\* authentication

\* authorization

\* health checks



Full interactive API documentation is available through:



```text

http://localhost:8000/docs

```



\---



\## Testing



Run the complete backend test suite:



```powershell

cd backend

.\\.venv\\Scripts\\Activate.ps1

python -m pytest tests -q

```



Current result:



```text

11 passed

```



\### Tenant Isolation Tests



```powershell

python -m pytest tests\\test\_tenant\_isolation.py -q

```



Current result:



```text

2 passed

```



\### RBAC Tests



```powershell

python -m pytest tests\\test\_rbac.py -q

```



Current result:



```text

3 passed

```



\---



\## RAG Evaluation



The project includes answer-quality evaluation under:



```text

backend/evaluation/

```



Run:



```powershell

cd backend

python -m evaluation.run\_answer\_evaluation

```



The evaluation measures:



\* Token overlap

\* Expected phrase coverage

\* Grounding

\* Retrieval latency

\* Generation latency



The evaluation was used to compare retrieval/chunking improvements during development.



\---



\## Example RAG Flow



Example:



```text

User:

What are the soft skills mentioned in my resume?

```



The system:



```text

1\. Authenticates the user

2\. Identifies the tenant

3\. Generates a query embedding

4\. Executes BM25 retrieval

5\. Executes kNN retrieval

6\. Combines rankings using RRF

7\. Builds the context

8\. Generates the answer

9\. Returns the answer with document sources

```



Example answer:



```text

\- Problem Solving

\- Adaptability

\- Willingness to Learn

```



\---



\## Docker Services



| Service       | Technology    | Port |

| ------------- | ------------- | ---: |

| Frontend      | React + Nginx |   80 |

| Backend       | FastAPI       | 8000 |

| Elasticsearch | Elasticsearch | 9200 |

| PostgreSQL    | PostgreSQL    | 5432 |

| Redis         | Redis         | 6379 |



\---



\## Environment Variables



The backend uses environment variables for configuration.



Important variables include:



```text

APP\_NAME

APP\_VERSION

ELASTICSEARCH\_URL

POSTGRES\_HOST

POSTGRES\_PORT

POSTGRES\_DB

POSTGRES\_USER

POSTGRES\_PASSWORD

JWT\_SECRET\_KEY

JWT\_ALGORITHM

JWT\_ACCESS\_TOKEN\_EXPIRE\_MINUTES

LLM\_PROVIDER

REDIS\_URL

CORS\_ORIGINS

```



Secrets must be stored in `.env` or a secure secret-management system and must never be committed to Git.



\---



\## Production Considerations



Before deploying publicly:



\* Rotate development JWT secrets.

\* Use strong production database credentials.

\* Store secrets in a secret manager.

\* Restrict CORS origins.

\* Enable TLS/HTTPS.

\* Use production authentication credentials.

\* Configure Elasticsearch





