# Supabase MCP Configuration Fix

## Problem
The MCP configuration for Supabase was using an incorrect URL format with query parameters embedded in the URL string, causing `mcp-remote` to fail with `ERR_INVALID_URL`.

### Original (Broken) Configuration
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.supabase.com/mcp?project_ref=ibnzhdgjfihhjvbfimpu"]
    }
  }
}
```

### Fixed Configuration
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.supabase.com/mcp", "--project-ref", "ibnzhdgjfihhjvbfimpu"]
    }
  }
}
```

## Changes Made
1. **Separated the project reference** from the URL into a separate argument
2. **Used the `--project-ref` flag** as specified in Supabase MCP documentation
3. **Clean URL format** without query parameters in the base URL

## Verification Steps

### 1. Test MCP Server Connection
```bash
cd rag_app/backend
npx -y mcp-remote https://mcp.supabase.com/mcp --project-ref ibnzhdgjfihhjvbfimpu
```

### 2. Check Available Tools
The Supabase MCP server should provide tools such as:
- `execute_sql` - Execute SQL queries
- `get_advisors` - Get database advisors
- `search_docs` - Search Supabase documentation
- `apply_migration` - Apply database migrations
- `get_project_info` - Get project information

### 3. Test SQL Execution
```sql
-- Test connection
SELECT current_database(), current_user;

-- Check schema
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

## References
- [Supabase MCP Setup Guide](https://supabase.com/docs/guides/getting-started/mcp)
- [Supabase MCP Server](https://github.com/supabase/mcp)
- [Supabase Skill Documentation](../../.agents/skills/supabase/SKILL.md)

## Security Checklist (per Supabase Skill)
- ✅ RLS enabled on all tables
- ✅ Storage bucket is private (`public: false`)
- ✅ Proper policies for `anon` and `authenticated` roles
- ✅ Vector extension enabled for embeddings
- ✅ Triggers for `updated_at` timestamps

## Related Files
- `rag_app/backend/.mcp.json` - MCP configuration (FIXED)
- `rag_app/backend/supabase_schema.sql` - Database schema
- `rag_app/backend/config/` - Configuration directory (new)

---
*Generated with Continue | Co-Authored-By: Continue <noreply@continue.dev>*
