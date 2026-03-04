#!/usr/bin/env bash
#
# Minimal validation for Azure OpenAI using curl (no Python).
# Runs chat completion and embeddings calls in sequence.
#
# Usage (from project root):
#   chmod +x scripts/validate_azure_openai_curl.sh
#   ./scripts/validate_azure_openai_curl.sh
#
# Required env:
#   AZURE_OPENAI_ENDPOINT           e.g. https://YOUR-RESOURCE.openai.azure.com
#   AZURE_OPENAI_DEPLOYMENT_NAME   e.g. gpt-4o
#   AZURE_OPENAI_EMBEDDING_DEPLOYMENT  e.g. text-embedding-3-small
#
# Optional:
#   AZURE_OPENAI_API_VERSION       default: 2024-05-01-preview
#   AZURE_OPENAI_API_KEY           if set, uses key auth
#   If no key: uses `az account get-access-token` for Azure AD token.

set -euo pipefail

ENDPOINT="${AZURE_OPENAI_ENDPOINT:-}"
CHAT_DEPLOYMENT="${AZURE_OPENAI_DEPLOYMENT_NAME:-gpt-4o}"
EMBED_DEPLOYMENT="${AZURE_OPENAI_EMBEDDING_DEPLOYMENT:-text-embedding-3-small}"
API_VERSION="${AZURE_OPENAI_API_VERSION:-2024-05-01-preview}"
API_KEY="${AZURE_OPENAI_API_KEY:-}"

if [[ -z "$ENDPOINT" ]]; then
  echo "ERROR: AZURE_OPENAI_ENDPOINT is not set."
  exit 1
fi

echo "============================================================"
echo "Validate Azure OpenAI via curl"
echo "============================================================"
echo "Endpoint: $ENDPOINT"
echo "Chat deployment: $CHAT_DEPLOYMENT"
echo "Embedding deployment: $EMBED_DEPLOYMENT"
echo "API version: $API_VERSION"

AUTH_HEADER=""
if [[ -n "$API_KEY" ]]; then
  echo "Auth: api-key"
  AUTH_HEADER="api-key: $API_KEY"
else
  echo "Auth: Azure AD token via az CLI"
  ACCESS_TOKEN="$(az account get-access-token \
    --resource https://cognitiveservices.azure.com \
    --query accessToken -o tsv)"
  AUTH_HEADER="Authorization: Bearer $ACCESS_TOKEN"
fi

echo
echo "1. Chat completions..."
CHAT_URL="$ENDPOINT/openai/deployments/$CHAT_DEPLOYMENT/chat/completions?api-version=$API_VERSION"
curl -sS -X POST \
  "$CHAT_URL" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "messages": [
      { "role": "user", "content": "Reply in one short sentence: what is 2+2?" }
    ],
    "max_tokens": 80
  }' | jq -r '.choices[0].message.content // "NO_CONTENT"' || {
    echo "Chat request failed."
    exit 1
  }

echo
echo "2. Embeddings..."
EMB_URL="$ENDPOINT/openai/deployments/$EMBED_DEPLOYMENT/embeddings?api-version=$API_VERSION"
curl -sS -X POST \
  "$EMB_URL" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "input": "Databricks cluster"
  }' | jq -r '"Dimension: \(.data[0].embedding | length)\nVector (first 10): \((.data[0].embedding[0:10]) // [])"' || {
    echo "Embeddings request failed."
    exit 1
  }

echo
echo "============================================================"
echo "curl validation completed."
echo "============================================================"

