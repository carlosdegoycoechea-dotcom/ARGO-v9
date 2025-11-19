# ARGO v9.0 - Web Search Setup Guide

## Overview

ARGO v9.0 includes **real-time web search** capabilities with support for multiple providers. This allows the system to access current information from the internet to complement document-based RAG.

---

## Supported Providers

### 1. DuckDuckGo (Recommended for Start)

**Cost:** FREE
**API Key:** Not required
**Setup Difficulty:** ⭐ Easy
**Results Quality:** ⭐⭐⭐⭐ Good
**Rate Limits:** Reasonable (no official limit)

**Setup:**
```bash
# Already included in requirements.txt
pip install duckduckgo-search==6.3.5
```

**Configuration in UI:**
- Settings → Web Search → Provider: `duckduckgo`
- No .env configuration needed

**Pros:**
- ✅ Zero cost
- ✅ No registration needed
- ✅ Privacy-focused
- ✅ Works immediately

**Cons:**
- ⚠️ Less comprehensive than Google
- ⚠️ May be slower than paid APIs

---

### 2. Serper API (Google Results)

**Cost:** $5 per 1,000 searches
**API Key:** Required
**Setup Difficulty:** ⭐⭐ Moderate
**Results Quality:** ⭐⭐⭐⭐⭐ Excellent (Google-powered)
**Rate Limits:** Based on plan

**Setup:**

1. **Get API Key:**
   - Go to: https://serper.dev
   - Sign up for free account
   - Get API key from dashboard
   - Free tier: 2,500 searches

2. **Add to .env:**
   ```bash
   # In ARGO_v9.0_CLEAN/.env
   SERPER_API_KEY=your_api_key_here
   ```

3. **Configuration in UI:**
   - Settings → Web Search → Provider: `serper`

**Pros:**
- ✅ Google search quality
- ✅ Very fast
- ✅ Structured data
- ✅ Good free tier

**Cons:**
- ⚠️ Requires API key
- ⚠️ Costs after free tier

---

### 3. Brave Search API

**Cost:** FREE (2,000/month) then $5/1,000
**API Key:** Required
**Setup Difficulty:** ⭐⭐ Moderate
**Results Quality:** ⭐⭐⭐⭐⭐ Excellent
**Rate Limits:** 2,000/month free, then paid

**Setup:**

1. **Get API Key:**
   - Go to: https://brave.com/search/api/
   - Sign up for account
   - Request API access
   - Get subscription token

2. **Add to .env:**
   ```bash
   # In ARGO_v9.0_CLEAN/.env
   BRAVE_API_KEY=your_subscription_token_here
   ```

3. **Configuration in UI:**
   - Settings → Web Search → Provider: `brave`

**Pros:**
- ✅ Generous free tier
- ✅ Privacy-focused
- ✅ Independent index
- ✅ Good quality results

**Cons:**
- ⚠️ Requires approval
- ⚠️ Limited to 2,000/month free

---

### 4. Tavily API (AI-Optimized)

**Cost:** FREE (1,000/month) then $0.001 per search
**API Key:** Required
**Setup Difficulty:** ⭐⭐ Moderate
**Results Quality:** ⭐⭐⭐⭐⭐ Excellent (AI-optimized)
**Rate Limits:** 1,000/month free

**Setup:**

1. **Get API Key:**
   - Go to: https://tavily.com
   - Sign up for account
   - Get API key from dashboard

2. **Add to .env:**
   ```bash
   # In ARGO_v9.0_CLEAN/.env
   TAVILY_API_KEY=your_api_key_here
   ```

3. **Configuration in UI:**
   - Settings → Web Search → Provider: `tavily`

**Pros:**
- ✅ Optimized for AI/LLM use
- ✅ Structured, clean results
- ✅ Good free tier
- ✅ Fast response

**Cons:**
- ⚠️ Smaller than Google index
- ⚠️ Costs after free tier

---

## Quick Start (Zero Config)

**Use DuckDuckGo (Free, No Setup):**

```bash
# 1. Install dependencies
cd ARGO_v9.0_CLEAN
pip install -r requirements.txt

# 2. Run ARGO
streamlit run app/ui.py

# 3. Enable in UI
# Sidebar → Settings → Web Search
# ✓ Enable Web Search
# Provider: duckduckgo
```

**Done!** Web search is now active.

---

## How It Works

### Automatic Trigger

Web search activates **automatically** when your query contains keywords like:

**English:**
- "latest", "recent", "current", "today", "news", "update"
- "what is", "who is", "when did"
- "search", "find", "google", "web", "internet", "online"

**Spanish:**
- "actualidad", "noticia", "información"
- "buscar", "busca"

### Example Queries That Trigger Web Search:

✅ "What is the latest version of Python?"
✅ "Who is the current CEO of Microsoft?"
✅ "Find recent news about AI"
✅ "What happened today in the stock market?"
✅ "Buscar información sobre ARGO"

### Queries That Don't Trigger (Uses Only RAG):

❌ "Summarize the project requirements"
❌ "What is in document.pdf?"
❌ "Calculate the budget"

---

## Usage Flow

```
User: "What is the latest Python version?"
    ↓
1. ARGO detects "latest" keyword → triggers web search
    ↓
2. Searches web (DuckDuckGo/Serper/Brave/Tavily)
    ↓
3. Gets 3 web results
    ↓
4. ALSO searches your documents (RAG)
    ↓
5. Combines web + document context
    ↓
6. LLM generates answer using BOTH sources
    ↓
7. Shows: Answer + Sources (web URLs + documents)
```

---

## Cost Comparison

**Scenario: 500 web searches/month**

| Provider | Cost | Notes |
|----------|------|-------|
| DuckDuckGo | $0 | Unlimited free |
| Serper | $2.50 | After free tier |
| Brave | $0 | Within 2,000 free |
| Tavily | $0 | Within 1,000 free |

**Recommendation:** Start with **DuckDuckGo** (free), upgrade to **Serper** if you need Google quality.

---

## Advanced Configuration

### Custom Web Search Provider

Edit `core/web_search.py` to add your own provider:

```python
def _search_custom(self, query: str, count: int) -> List[SearchResult]:
    """Custom search implementation"""
    # Your API logic here
    return results
```

### Disable Auto-Trigger

If you want manual control:

```python
# In ui.py, remove the should_use_web_search() check
# Always or never search web
```

---

## Troubleshooting

### "duckduckgo_search not installed"

```bash
pip install duckduckgo-search==6.3.5
```

### "SERPER_API_KEY not found"

1. Check `.env` file exists in `ARGO_v9.0_CLEAN/`
2. Verify key format: `SERPER_API_KEY=abc123xyz`
3. Restart Streamlit

### "Web search failed"

Check logs:
```bash
tail -f ARGO_v9.0_CLEAN/logs/argo.log | grep WebSearch
```

### Rate Limit Exceeded

Switch to different provider or upgrade plan.

---

## Privacy Considerations

### DuckDuckGo
- ✅ No user tracking
- ✅ Queries not logged
- ✅ Privacy-focused

### Serper/Brave/Tavily
- ⚠️ Queries sent to API provider
- ⚠️ Check each provider's privacy policy
- ✅ No data stored in ARGO (only results)

---

## Performance Tips

1. **Use caching:** Web results can be cached locally
2. **Limit count:** Default 3 results is optimal
3. **Smart triggering:** Only search when needed (keywords)
4. **Choose fast provider:** Serper is fastest, DuckDuckGo slowest

---

## Examples

### Example 1: Tech News
```
Query: "What are the latest updates in Claude AI?"
→ Web search: YES (keyword: "latest")
→ Results: 3 web articles + project docs
→ Answer: Combines current news + your notes
```

### Example 2: Company Info
```
Query: "Find information about Anthropic"
→ Web search: YES (keyword: "find")
→ Results: 3 web sources
→ Answer: Current company info
```

### Example 3: Document Query
```
Query: "What is the project budget?"
→ Web search: NO (no trigger keywords)
→ Results: Only project documents
→ Answer: From your PDFs/docs
```

---

## API Key Security

**Important:**
- ✅ Always use `.env` file (gitignored)
- ✅ Never commit API keys to git
- ✅ Rotate keys regularly
- ✅ Use environment variables in production

**Example .env:**
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Web Search (choose one or more)
SERPER_API_KEY=abc123...
BRAVE_API_KEY=BSA...
TAVILY_API_KEY=tvly-...
```

---

## Comparison with Competitors

| Feature | ARGO v9.0 | Perplexity Pro | ChatGPT Plus |
|---------|-----------|----------------|--------------|
| Web Search | ✅ Multiple providers | ✅ Built-in | ✅ Browsing |
| Choose Provider | ✅ 4 options | ❌ No | ❌ No |
| Free Option | ✅ DuckDuckGo | ❌ $20/month | ❌ $20/month |
| + Your Docs | ✅ RAG + Web | ⚠️ Basic | ⚠️ Limited |
| Privacy | ✅ Local RAG | ❌ Cloud | ❌ Cloud |

---

## Support

**Issues:**
- Check logs in `logs/argo.log`
- Verify API keys in `.env`
- Test provider directly (see `core/web_search.py` main block)

**Questions:**
- Review `ARCHITECTURE_FLOW.md` for system flow
- Check provider documentation
- Verify network connectivity

---

## Next Steps

1. ✅ Start with DuckDuckGo (zero config)
2. ✅ Try queries with "latest", "recent", "news"
3. ✅ Monitor results quality
4. ✅ Upgrade to Serper if needed (better quality)
5. ✅ Set monthly budget alerts

**Web search makes ARGO competitive with Perplexity Pro** while maintaining privacy and document integration! 🚀
