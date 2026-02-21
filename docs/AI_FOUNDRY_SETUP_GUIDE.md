# AI Foundry Setup Guide – End-to-End Testing

This guide walks you through setting up an Azure AI Foundry project and connecting it to the Databricks Recommendation Agent for real end-to-end tests.

---

## Quick Start Summary

| Step | Action |
|------|--------|
| 1 | Sign in to [ai.azure.com](https://ai.azure.com) |
| 2 | Create project and deploy **gpt-4o** and **text-embedding-3-small** |
| 3 | Copy endpoint and API key from Keys and Endpoint |
| 4 | (Optional) Create Azure AI Search and run `python scripts/create_search_index.py` |
| 5 | Copy `.env.example` to `.env` and fill in credentials |
| 6 | Run `python scripts/test_local_agent.py` or `make up` then call the API |

---

## Overview

You need:

1. **Azure OpenAI** – For `gpt-4o` (chat) and `text-embedding-3-small` (embeddings)
2. **Azure AI Search** (optional for full RAG) – For vector search over recommendations
3. **Local or Docker** – To run the agent

The agent can run with only Azure OpenAI; Azure AI Search adds RAG (historical recommendations).

---

## Part 1: Create Azure OpenAI Resource (AI Foundry / Portal)

### Step 1: Sign in to AI Foundry

1. Open [https://ai.azure.com](https://ai.azure.com)
2. Sign in with your Azure (personal or work) account
3. Ensure you have an active subscription

### Step 2: Create a Project and Deploy gpt-4o

**Option A: Via AI Foundry (Quick)**

1. On the landing page, select **Model catalog** (or **Explore models**)
2. Search for **gpt-4o** and open it
3. Click **Use this model**
4. If prompted:
   - Choose **Create new project**
   - Enter a project name (e.g. `databricks-recommendation-agent`)
   - Pick a **Resource group** (or create one)
   - Pick a **Region** (e.g. East US)
5. On the deployment screen:
   - **Deployment name**: `gpt-4o` (matches project config)
   - Review and click **Deploy**
6. Wait until the deployment shows **Succeeded**

**Option B: Via Azure Portal (Standard Azure OpenAI)**

1. Go to [Azure Portal](https://portal.azure.com) → **Create a resource**
2. Search for **Azure OpenAI** → **Create**
3. Basics:
   - **Subscription**: Your subscription
   - **Resource group**: Create or select
   - **Region**: e.g. East US
   - **Name**: e.g. `my-openai-databricks-agent`
   - **Pricing tier**: Standard S0
4. **Network**: Start with **All networks** for testing
5. Click **Review + create** → **Create**

### Step 3: Deploy text-embedding-3-small

1. In AI Foundry:
   - Open your project
   - Go to **Models + endpoints** (or **Deployments**)
   - Click **+ Deploy model** / **Deploy base model**
2. Or in Azure Portal:
   - Open your Azure OpenAI resource
   - Go to **Model deployments** → **Deploy model**
3. Deploy:
   - **Model**: `text-embedding-3-small`
   - **Deployment name**: `text-embedding-3-small`
   - Click **Deploy**

### Step 4: Get Endpoint and API Key

**From AI Foundry**

1. Open your project
2. Go to **Project settings** or **Overview**
3. Copy:
   - **Endpoint** (e.g. `https://<resource>.openai.azure.com`)
   - **Keys** → **Key 1**

**From Azure Portal**

1. Open your Azure OpenAI resource
2. Go to **Keys and Endpoint**
3. Copy:
   - **Endpoint** (e.g. `https://<resource>.openai.azure.com`)
   - **KEY 1**

**Note for Foundry:** If your endpoint looks like `https://xxx.services.ai.azure.com/api/projects/your-project`, you can use it as-is – the project normalizes it automatically. Set `AZURE_OPENAI_API_VERSION=2024-05-01-preview` in `.env` for Foundry compatibility.

---

## Part 2: Create Azure AI Search (Optional, for RAG)

### Step 1: Create Search Service

1. In [Azure Portal](https://portal.azure.com) → **Create a resource**
2. Search for **Azure AI Search** → **Create**
3. Configure:
   - **Subscription**: Same as above
   - **Resource group**: Same as above
   - **URL**: e.g. `databricks-agent-search` (globally unique)
   - **Pricing tier**: Free (F) for testing
4. Click **Review + create** → **Create**

### Step 2: Get Search Credentials

1. Open the AI Search resource
2. Go to **Keys**
3. Copy:
   - **URL** (e.g. `https://<name>.search.windows.net`)
   - **Primary admin key**

### Step 3: Create the Index

Use the provided script:

```bash
# From project root, with .env configured
python scripts/create_search_index.py
```

Or create manually in the portal:

1. Open the Search service → **Indexes** → **+ Add index**
2. **Index name**: `recommendations-index`
3. Add fields:

| Name            | Type       | Key | Searchable | Filterable | Sortable | Retrievable |
|-----------------|------------|-----|------------|------------|----------|-------------|
| id              | Edm.String | Yes | No         | No         | No       | Yes         |
| job_id          | Edm.String | No  | Yes        | Yes        | No       | Yes         |
| job_run_id      | Edm.String | No  | No         | Yes        | No       | Yes         |
| workspace_id    | Edm.String | No  | No         | Yes        | No       | Yes         |
| workload_type   | Edm.String | No  | Yes        | Yes        | No       | Yes         |
| content         | Edm.String | No  | Yes        | No         | No       | Yes         |
| embedding       | Collection(Edm.Single) | No | No | No | No | Yes |
| document_type   | Edm.String | No  | No         | Yes        | No       | Yes         |
| is_recommendation | Edm.Boolean | No | No       | Yes        | No       | Yes         |
| config_quality  | Edm.String | No  | No         | Yes        | No       | Yes         |
| recommendation  | Edm.String | No  | No         | No         | No       | Yes         |
| metrics         | Edm.String | No  | No         | No         | No       | Yes         |
| current_config  | Edm.String | No  | No         | No         | No       | Yes         |

4. Add **Vector search** profile and algorithm (e.g. HNSW) for `embedding` (dimension 1536)
5. Save the index

---

## Part 3: Configure the Project

### Step 1: Create `.env`

Copy from example:

```bash
cp .env.example .env
```

### Step 2: Edit `.env`

```bash
# === Azure OpenAI (required) ===
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# === Azure AI Search (optional - omit for non-RAG mode) ===
AZURE_SEARCH_ENDPOINT=https://YOUR-SEARCH.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key-here
AZURE_SEARCH_INDEX_NAME=recommendations-index

# === Local Testing Mode ===
USE_LOCAL_DATA=true

# === Database (optional for cost analytics) ===
USE_POSTGRES=true
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DATABASE=databricks_agent
```

Replace:

- `YOUR-RESOURCE` with your Azure OpenAI resource name
- `your-api-key-here` with Key 1
- `YOUR-SEARCH` and `your-search-api-key-here` if using Azure AI Search

### Step 3: Remove Hardcoded Secrets (Important)

`shared/config/settings.py` contains default tenant/client IDs. Remove or override them:

- Either delete the default values and set them only via `.env`
- Or ensure `.env` defines `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` if you use them

---

## Part 4: Run End-to-End Tests

### Option A: Local Python

```bash
# Activate virtual environment
source .venv/bin/activate   # or: .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run local agent test (uses sample CSV data)
python scripts/test_local_agent.py
```

### Option B: Docker

```bash
# Start services
make up

# Wait for DB to be ready
sleep 5

# Run API
# API runs on http://localhost:8000
```

### Option C: API Request

```bash
# With API running
curl -X POST http://localhost:8000/api/recommendations/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job-001",
    "start_date": "2024-01-15",
    "end_date": "2024-01-20"
  }'
```

### Expected Response

You should get JSON with:

- `recommendation` (node family, vcpus, workers, etc.)
- `explanation`
- `pattern_analysis`
- `risk_assessment`
- `token_usage_analysis`
- `request_id`

---

## Part 5: Alternative – Foundry Endpoint Format

If your endpoint is `https://<resource>.services.ai.azure.com` (AI Foundry Model Inference), the current LangChain integration may not work directly. Options:

**Option 1: Use an Azure OpenAI Resource**

Create a separate Azure OpenAI resource in the portal with endpoint `https://<name>.openai.azure.com`.

**Option 2: Use langchain-azure-ai**

1. Install:

   ```bash
   pip install langchain-azure-ai
   ```

2. Update `AI/src/services/azure_openai_service.py` to use `AzureAIChatCompletionsModel` from `langchain_azure_ai` with:
   - `endpoint`: `https://<resource>.services.ai.azure.com/models`
   - `credential`: API key or `DefaultAzureCredential`
   - `model`: deployment name (e.g. `gpt-4o`)

---

## Troubleshooting

### "Missing credentials" or Mock LLM Used

- Ensure `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` are set in `.env`
- No spaces around `=` in `.env`
- Restart the process after editing `.env`

### 401 Unauthorized

- Check the API key
- Ensure the key is for the correct resource/region

### "API version not supported"

- **Foundry** (`*.services.ai.azure.com`): Set `AZURE_OPENAI_API_VERSION=2024-05-01-preview`
- **Standard Azure OpenAI** (`*.openai.azure.com`): Use `2024-02-15-preview` or `2024-05-01-preview`

### 404 for Deployment

- Deployment names must match: `gpt-4o`, `text-embedding-3-small`
- Wait a few minutes after creating deployments

### Model Access / Quota

- Some models require approval
- Submit a request in the [Azure OpenAI access form](https://aka.ms/oai/access)

### Azure AI Search Index Errors

- Run `python scripts/create_search_index.py` to create the index
- Ensure the index has a vector field `embedding` with 1536 dimensions

---

## Checklist

- [ ] Azure OpenAI resource created
- [ ] gpt-4o deployed
- [ ] text-embedding-3-small deployed
- [ ] Endpoint and API key copied
- [ ] (Optional) Azure AI Search created and index `recommendations-index` created
- [ ] `.env` configured
- [ ] `python scripts/test_local_agent.py` succeeds
- [ ] API returns a recommendation when called
