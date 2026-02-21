# Azure AI Foundry Access Checklist for Databricks Recommendation Agent

This document outlines all Azure services, permissions, and access requirements needed to run the Databricks Recommendation Agent end-to-end in an enterprise environment.

**Note**: Network access will use **private endpoints** wherever possible for enhanced security.

---

## Azure Services and Resources Required

### 1. Azure OpenAI Service (Primary Requirement)

**What you need:**
- Azure OpenAI resource in your subscription
- Access to specific models:
  - `gpt-4o` (for LLM chat completion)
  - `text-embedding-3-small` (for embeddings)

**Enterprise Guardrails to Request:**
- Model access approval (gpt-4o may require approval)
- Quota/TPS limits (request appropriate throughput)
- Region selection (ensure your region supports these models)
- **Private endpoint** for network access

**What to Request:**
```
1. Azure OpenAI resource creation approval
2. Model access for:
   - gpt-4o (chat completion)
   - text-embedding-3-small (embeddings)
3. Quota: Request appropriate TPS (Tokens Per Second)
   - Development: 10-50 TPS
   - Production: 100+ TPS (based on expected load)
4. Region: Same region as other resources (for latency)
5. Network: PRIVATE ENDPOINT (required)
   - VNet integration
   - Private DNS zone configuration
```

**Information you'll need:**
- Subscription ID
- Resource Group name: `rg-databricks-ai-agent`
- Region preference
- VNet details (for private endpoint)
- Estimated usage (for quota requests)

---

### 2. Azure AI Search (Vector Database)

**What you need:**
- Azure AI Search service
- Index with vector search capability
- Semantic search enabled (optional but recommended)
- **Private endpoint** for network access

**Enterprise Guardrails to Request:**
- Service tier selection (Basic/Standard/Premium)
- **Private endpoint** configuration (required)
- Index schema approval (if there are data governance rules)

**What to Request:**
```
1. Azure AI Search service creation
2. Service tier: 
   - Development: Basic (S1) - $75/month
   - Production: Standard (S1) or higher - $250+/month
3. Vector search capability enabled
4. Index creation with schema:
   - Fields: id, content, embedding (vector), metadata fields
   - Index name: "recommendations-index"
5. Network: PRIVATE ENDPOINT (required)
   - VNet integration
   - Private DNS zone configuration
```

**Index Schema Requirements:**
- Vector field for embeddings (1536 dimensions for text-embedding-3-small)
- Filterable fields: `document_type`, `is_recommendation`, `config_quality`
- Searchable fields: `content`, `workload_type`

---

### 3. Azure Authentication and Access

**Service Principal (for development/testing):**
- Service Principal with:
  - Reader role on subscription (minimum)
  - Cognitive Services User role on Azure OpenAI resource
  - Search Service Contributor role on Azure AI Search
  - Storage Blob Data Contributor (if using Blob Storage)

**Managed Identity (for production):**
- If deploying to Azure (App Service, Container Instances, etc.)
- Request Managed Identity assignment
- Same role assignments as above

**What to Request:**
```
1. Service Principal roles:
   - "Cognitive Services User" on Azure OpenAI resource
   - "Search Service Contributor" on Azure AI Search
   - "Storage Blob Data Contributor" on Storage Account
   - "Reader" on Subscription (for resource discovery)
2. Key Vault access (if using):
   - "Key Vault Secrets User" role
3. Private endpoint access:
   - VNet access for Service Principal/Managed Identity
   - Private DNS resolution
```

---

### 4. Azure Storage (Optional but Recommended)

**What you need:**
- Storage Account (for data files, backups)
- Container: `ai-agent-data`
- **Private endpoint** for network access

**What to Request:**
```
1. Storage Account creation
2. Container: "ai-agent-data"
3. Access tier: Hot (for frequent access)
4. Network: PRIVATE ENDPOINT (required)
   - VNet integration
   - Private DNS zone configuration
5. Firewall rules: Allow access from VNet only
```

---

### 5. Azure Key Vault (Recommended for Secrets)

**What you need:**
- Key Vault for storing API keys and secrets
- Access policies for your Service Principal/Managed Identity
- **Private endpoint** for network access

**What to Request:**
```
1. Key Vault creation
2. Network: PRIVATE ENDPOINT (required)
   - VNet integration
   - Private DNS zone configuration
3. Access policy for Service Principal:
   - Get/List secrets
   - Get/List keys (if using)
4. Store secrets:
   - azure-openai-api-key
   - azure-search-api-key
   - databricks-token
   - database-credentials
```

---

### 6. Database (Choose One)

**Option A: Azure Database for PostgreSQL**
- Flexible Server or Single Server
- **Private endpoint** for network access
- Database creation permissions

**Option B: Azure SQL Database**
- SQL Server creation
- Database creation
- **Private endpoint** for network access

**What to Request:**
```
1. Database service creation (PostgreSQL or SQL)
2. Database creation: "databricks_ai_agent" (or your name)
3. Network: PRIVATE ENDPOINT (required)
   - VNet integration
   - Private DNS zone configuration
4. Firewall rules: Allow access from VNet only
5. Admin credentials (or use Managed Identity)
```

---

### 7. Databricks Access

**What you need:**
- Databricks workspace access
- SQL Warehouse/Cluster access
- Token generation permissions
- Access to system tables:
  - `system.compute.cluster_usage`
  - `system.compute.resource_usage`
  - `system.billing.usage`
- **Private endpoint** or secure workspace access

**What to Request:**
```
1. Databricks workspace access
2. SQL Warehouse access (or cluster access)
3. Token generation permission (for API access)
4. Read access to system tables:
   - system.compute.*
   - system.billing.*
5. HTTP Path for SQL Warehouse
6. Network: Secure workspace access
   - VNet peering (if required)
   - Private endpoint (if Databricks supports it)
```

---

## Enterprise Guardrails Checklist

### Security and Compliance
- [ ] **Private endpoints** for all Azure services (required)
- [ ] Network security groups (NSG) rules
- [ ] VNet configuration and peering
- [ ] Private DNS zones for service resolution
- [ ] Data residency requirements (region selection)
- [ ] Encryption at rest (default, but verify)
- [ ] Encryption in transit (TLS 1.2+)
- [ ] RBAC assignments (least privilege)
- [ ] Key Vault for secrets (no hardcoded keys)

### Network Access
- [ ] **Private endpoints** for Azure OpenAI
- [ ] **Private endpoints** for Azure AI Search
- [ ] **Private endpoints** for Storage Account
- [ ] **Private endpoints** for Key Vault
- [ ] **Private endpoints** for Database
- [ ] VNet integration for all services
- [ ] Private DNS zone configuration
- [ ] NSG rules for VNet traffic
- [ ] Databricks network access (VNet peering or secure access)

### Cost Management
- [ ] Budget alerts configured
- [ ] Resource tagging strategy
- [ ] Cost center allocation
- [ ] Usage monitoring enabled

### Governance
- [ ] Resource naming conventions
- [ ] Resource group organization
- [ ] Policy compliance (if any)
- [ ] Audit logging enabled

---

## Step-by-Step Request Process

### Phase 1: Initial Access Request

**Subject**: Azure AI Foundry Access Request - Databricks Recommendation Agent

**Request Template**:
```
Subject: Azure AI Foundry Access Request - Databricks Recommendation Agent

Request:
1. Azure OpenAI Service
   - Models: gpt-4o, text-embedding-3-small
   - Region: [your-region]
   - Quota: [X] TPS
   - Resource Group: rg-databricks-ai-agent
   - Network: PRIVATE ENDPOINT (required)
   - VNet: [your-vnet-name]

2. Azure AI Search
   - Tier: Basic (S1) for development
   - Region: [same as OpenAI]
   - Vector search enabled
   - Network: PRIVATE ENDPOINT (required)
   - VNet: [your-vnet-name]

3. Azure Key Vault
   - Network: PRIVATE ENDPOINT (required)
   - VNet: [your-vnet-name]

4. Azure Storage Account
   - Network: PRIVATE ENDPOINT (required)
   - VNet: [your-vnet-name]

5. Azure Database (PostgreSQL or SQL)
   - Network: PRIVATE ENDPOINT (required)
   - VNet: [your-vnet-name]

6. Service Principal roles:
   - Cognitive Services User (Azure OpenAI)
   - Search Service Contributor (Azure AI Search)
   - Storage Blob Data Contributor (Storage Account)
   - Key Vault Secrets User (Key Vault)
   - Reader (Subscription)

7. Private DNS Zones:
   - privatelink.openai.azure.com
   - privatelink.search.windows.net
   - privatelink.vaultcore.azure.net
   - privatelink.blob.core.windows.net
   - privatelink.postgres.database.azure.com (if PostgreSQL)
   - privatelink.database.windows.net (if SQL)

8. Network access:
   - VNet access for all services
   - Private endpoint configuration
   - DNS resolution via private DNS zones
```

### Phase 2: Resource Creation

Once approved, you'll need:
- Azure OpenAI endpoint URL (private endpoint)
- Azure OpenAI API key (store in Key Vault)
- Azure AI Search endpoint URL (private endpoint)
- Azure AI Search API key (store in Key Vault)
- Index creation (can be done via code or portal)
- Private DNS zone records

### Phase 3: Configuration

After resources are created, you'll configure:

**Environment Variables (.env file or Key Vault):**
```bash
# Azure OpenAI (via private endpoint)
AZURE_OPENAI_ENDPOINT=https://[your-resource].openai.azure.com/
AZURE_OPENAI_API_KEY=[key-from-keyvault]
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Azure AI Search (via private endpoint)
AZURE_SEARCH_ENDPOINT=https://[your-search].search.windows.net
AZURE_SEARCH_API_KEY=[key-from-keyvault]
AZURE_SEARCH_INDEX_NAME=recommendations-index

# Key Vault
AZURE_KEY_VAULT_NAME=[your-keyvault-name]

# Storage Account (if using)
AZURE_STORAGE_ACCOUNT=[your-storage-account]
AZURE_STORAGE_KEY=[key-from-keyvault]
AZURE_STORAGE_CONTAINER=ai-agent-data

# Database (if using Azure)
AZURE_SQL_SERVER=[your-sql-server].database.windows.net
# OR
POSTGRES_HOST=[your-postgres].postgres.database.azure.com

# Service Principal (for authentication)
AZURE_TENANT_ID=[your-tenant-id]
AZURE_CLIENT_ID=[your-client-id]
AZURE_CLIENT_SECRET=[your-client-secret]
AZURE_SUBSCRIPTION_ID=[your-subscription-id]
```

**Important**: All endpoints will resolve via private DNS zones when accessed from within the VNet.

---

## Common Enterprise Blockers and Solutions

### Blocker 1: Model Access Approval
- **Solution**: Request model access through Azure portal or support ticket
- **Timeline**: Can take 1-3 business days
- **Action**: Submit request with business justification

### Blocker 2: Quota Limits
- **Solution**: Request quota increase with usage justification
- **Include**: Expected TPS, use case, business justification
- **Timeline**: Usually approved within 1-2 business days

### Blocker 3: Private Endpoint Creation
- **Solution**: Request private endpoint creation (requires VNet)
- **Requirements**: 
  - VNet must exist
  - Private DNS zones must be configured
  - NSG rules may need updates
- **Timeline**: Depends on network team availability

### Blocker 4: VNet Access
- **Solution**: Request VNet access for Service Principal/Managed Identity
- **Requirements**:
  - VNet peering (if needed)
  - NSG rules for outbound traffic
  - Private DNS zone resolution
- **Timeline**: Usually 1-2 business days

### Blocker 5: No New Resource Group Creation
- **Solution**: Use existing approved resource group
- **Update**: `azure_resource_group` in settings.py
- **Action**: Request access to existing resource group

### Blocker 6: Databricks System Table Access
- **Solution**: Request workspace admin to grant access
- **Alternative**: Use service principal with appropriate permissions
- **Action**: Submit access request to Databricks workspace admin

### Blocker 7: Private DNS Zone Configuration
- **Solution**: Request private DNS zone creation and linking
- **Requirements**:
  - Private DNS zones for each service
  - Link to VNet
  - A records for private endpoints
- **Timeline**: Usually same day if VNet exists

---

## Minimum Viable Setup (MVP)

If you need to start quickly, minimum requirements:

**Must Have:**
1. Azure OpenAI Service (gpt-4o + embeddings) with **private endpoint**
2. Azure AI Search (Basic tier) with **private endpoint**
3. Service Principal with roles
4. VNet access and private DNS zones
5. Local PostgreSQL (for development) - can migrate to Azure later

**Can Add Later:**
- Key Vault (use environment variables initially)
- Storage Account (use local storage initially)
- Azure Database (use local PostgreSQL initially)

---

## Private Endpoint Configuration Details

### Required Private Endpoints

1. **Azure OpenAI Private Endpoint**
   - Subresource: `account`
   - Private DNS zone: `privatelink.openai.azure.com`
   - DNS record: `[resource-name].openai.azure.com` → private IP

2. **Azure AI Search Private Endpoint**
   - Subresource: `searchService`
   - Private DNS zone: `privatelink.search.windows.net`
   - DNS record: `[search-name].search.windows.net` → private IP

3. **Azure Key Vault Private Endpoint**
   - Subresource: `vault`
   - Private DNS zone: `privatelink.vaultcore.azure.net`
   - DNS record: `[vault-name].vault.azure.net` → private IP

4. **Azure Storage Private Endpoint**
   - Subresource: `blob`
   - Private DNS zone: `privatelink.blob.core.windows.net`
   - DNS record: `[account-name].blob.core.windows.net` → private IP

5. **Azure Database Private Endpoint**
   - PostgreSQL: `privatelink.postgres.database.azure.com`
   - SQL: `privatelink.database.windows.net`
   - DNS record: `[server-name].postgres.database.azure.com` → private IP

### Private DNS Zone Requirements

Request creation and linking of the following private DNS zones:
- `privatelink.openai.azure.com`
- `privatelink.search.windows.net`
- `privatelink.vaultcore.azure.net`
- `privatelink.blob.core.windows.net`
- `privatelink.postgres.database.azure.com` (if PostgreSQL)
- `privatelink.database.windows.net` (if SQL)

Each zone must be:
- Created in the same subscription
- Linked to your VNet
- Configured with auto-registration (if supported)

---

## Testing Access

Once resources are created with private endpoints, test from within VNet:

```python
# Test Azure OpenAI (via private endpoint)
from AI.src.services.azure_openai_service import AzureOpenAIService
service = AzureOpenAIService()
llm = service.get_llm()
# Should work without errors (resolves via private DNS)

# Test Azure AI Search (via private endpoint)
from AI.src.services.azure_search_service import AzureSearchService
search = AzureSearchService()
# Should initialize without errors (resolves via private DNS)

# Test Key Vault (via private endpoint)
from shared.config.azure_config import AzureConfig
config = AzureConfig()
secret = config.get_secret("azure-openai-api-key")
# Should retrieve secret (resolves via private DNS)
```

**Note**: Testing must be done from within the VNet or via VPN/ExpressRoute connection.

---

## Summary Checklist

### Must Have (Private Endpoints Required)
- [ ] Azure OpenAI Service with gpt-4o and text-embedding-3-small
  - [ ] Private endpoint configured
  - [ ] Private DNS zone linked
- [ ] Azure AI Search with vector search
  - [ ] Private endpoint configured
  - [ ] Private DNS zone linked
- [ ] Service Principal with appropriate roles
- [ ] VNet access and private DNS zones
- [ ] Network security groups (NSG) configured

### Nice to Have (Private Endpoints Recommended)
- [ ] Azure Key Vault (for secrets)
  - [ ] Private endpoint configured
  - [ ] Private DNS zone linked
- [ ] Azure Storage Account
  - [ ] Private endpoint configured
  - [ ] Private DNS zone linked
- [ ] Azure Database (PostgreSQL or SQL)
  - [ ] Private endpoint configured
  - [ ] Private DNS zone linked
- [ ] Application Insights (for monitoring)

### Access Needed
- [ ] Databricks workspace access
- [ ] System table read permissions
- [ ] Token generation permission
- [ ] VNet peering (if Databricks requires it)

---

## Next Steps

1. **Review this checklist** with your team
2. **Identify VNet details** (name, resource group, region)
3. **Submit access request** using the template in Phase 1
4. **Coordinate with network team** for private endpoint creation
5. **Test connectivity** from within VNet after setup
6. **Configure application** with private endpoint URLs

---

## Support Contacts

For enterprise access requests, contact:
- **Azure Resource Management**: [Your Azure Admin Team]
- **Network Team**: [Your Network Team] (for VNet/private endpoints)
- **Security Team**: [Your Security Team] (for RBAC approvals)
- **Databricks Admin**: [Your Databricks Admin] (for workspace access)

---

## Additional Resources

- [Azure Private Endpoints Documentation](https://docs.microsoft.com/azure/private-link/private-endpoint-overview)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)
- [Private DNS Zones Documentation](https://docs.microsoft.com/azure/dns/private-dns-overview)

---

**Last Updated**: [Date]
**Version**: 1.0
**Status**: Ready for Enterprise Access Request

