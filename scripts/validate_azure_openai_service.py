#!/usr/bin/env python3
"""
Validate Azure OpenAI service directly (no API).

Run from project root:
  python scripts/validate_azure_openai_service.py

Or with venv:
  source venv/bin/activate && python scripts/validate_azure_openai_service.py

Uses .env (or env vars): AZURE_OPENAI_ENDPOINT, deployment names;
  optionally AZURE_OPENAI_API_KEY. If no key, uses Azure AD (az login / Managed Identity).
"""
import os
import sys
from pathlib import Path

# Project root and .env
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Load .env before importing settings
env_file = project_root / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

from shared.config.settings import settings
from AI.src.services.azure_openai_service import AzureOpenAIService
from langchain_core.messages import HumanMessage


def main():
    print("=" * 60)
    print("Validate Azure OpenAI Service (end-to-end)")
    print("=" * 60)

    # Config summary (no secrets)
    has_endpoint = bool(settings.azure_openai_endpoint and settings.azure_openai_endpoint.strip())
    has_key = bool(settings.azure_openai_api_key and settings.azure_openai_api_key.strip())
    print(f"\nConfig: endpoint={'set' if has_endpoint else 'NOT SET'}, api_key={'set' if has_key else 'NOT SET (Azure AD)'}")

    if not has_endpoint:
        print("Set AZURE_OPENAI_ENDPOINT in .env (and deployment names). Exiting.")
        sys.exit(1)

    print("\n1. Initializing AzureOpenAIService...")
    service = AzureOpenAIService()
    llm = service.get_llm()
    embeddings = service.get_embeddings()

    # --- LLM ---
    print("\n2. LLM invoke (single turn)...")
    try:
        msg = [HumanMessage(content="Reply in one short sentence: what is 2+2?")]
        out = llm.invoke(msg)
        content = out.content if hasattr(out, "content") else str(out)
        print(f"   Response: {content[:500]}")
        print("   LLM: OK")
    except Exception as e:
        print(f"   LLM: FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # --- Embeddings ---
    print("\n3. Embeddings (embed_query)...")
    try:
        vec = embeddings.embed_query("Databricks cluster configuration")
        print(f"   Dimension: {len(vec)}, sample[:5] = {vec[:5]}")
        print("   Embeddings: OK")
    except Exception as e:
        print(f"   Embeddings: FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("All checks passed. Azure OpenAI service is working.")
    print("=" * 60)


if __name__ == "__main__":
    main()
