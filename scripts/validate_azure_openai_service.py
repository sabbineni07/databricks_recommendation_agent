#!/usr/bin/env python3
"""
Minimal validation for Azure OpenAI endpoint (no LangChain).

Uses only: stdlib, python-dotenv, azure-identity.
- If AZURE_OPENAI_API_KEY is set in .env: uses API key.
- If not: uses Azure AD token (az login or Managed Identity).

Run from project root:
  pip install python-dotenv azure-identity
  python scripts/validate_azure_openai_service.py
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Load .env from project root
project_root = Path(__file__).resolve().parent.parent
env_file = project_root / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
        pass  # optional

# Config from env (no pydantic)
ENDPOINT = (os.environ.get("AZURE_OPENAI_ENDPOINT") or "").strip()
API_KEY = (os.environ.get("AZURE_OPENAI_API_KEY") or "").strip()
API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION") or "2024-05-01-preview"
CHAT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME") or "gpt-4o"
EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") or "text-embedding-3-small"


def _normalize_endpoint(endpoint: str) -> str:
    if "/api/projects/" in endpoint:
        endpoint = endpoint.split("/api/projects/")[0].rstrip("/")
    return endpoint.rstrip("/")


def _get_auth_headers():
    """Return dict of auth headers: either api-key or Authorization Bearer."""
    if API_KEY:
        return {"api-key": API_KEY}
    from azure.identity import DefaultAzureCredential
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return {"Authorization": f"Bearer {token.token}"}


def _request(url: str, body: dict, headers: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def main():
    print("=" * 60)
    print("Validate Azure OpenAI endpoint (direct REST, no LangChain)")
    print("=" * 60)

    if not ENDPOINT:
        print("Set AZURE_OPENAI_ENDPOINT in .env. Exiting.")
        sys.exit(1)

    base = _normalize_endpoint(ENDPOINT)
    auth = _get_auth_headers()
    auth_type = "api_key" if API_KEY else "Azure AD (token)"
    print(f"\nEndpoint: {base}")
    print(f"Auth: {auth_type}")

    # 1) Chat completions
    chat_url = f"{base}/openai/deployments/{CHAT_DEPLOYMENT}/chat/completions?api-version={API_VERSION}"
    print("\n1. Chat completions...")
    try:
        out = _request(
            chat_url,
            {"messages": [{"role": "user", "content": "Reply in one short sentence: what is 2+2?"}], "max_tokens": 80},
            auth,
        )
        text = out["choices"][0]["message"]["content"]
        print(f"   Response: {text.strip()}")
        print("   OK")
    except urllib.error.HTTPError as e:
        print(f"   FAILED: {e.code} {e.reason}")
        if e.fp:
            try:
                body = e.fp.read().decode()
                print(f"   Body: {body[:500]}")
            except Exception:
                pass
        sys.exit(1)
    except Exception as e:
        print(f"   FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 2) Embeddings (optional quick check)
    emb_url = f"{base}/openai/deployments/{EMBEDDING_DEPLOYMENT}/embeddings?api-version={API_VERSION}"
    print("\n2. Embeddings...")
    try:
        out = _request(emb_url, {"input": "Databricks cluster"}, auth)
        dim = len(out["data"][0]["embedding"])
        print(f"   Dimension: {dim}")
        print("   OK")
    except urllib.error.HTTPError as e:
        print(f"   FAILED: {e.code} {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"   FAILED: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("All checks passed. Endpoint is reachable with current auth.")
    print("=" * 60)


if __name__ == "__main__":
    main()
