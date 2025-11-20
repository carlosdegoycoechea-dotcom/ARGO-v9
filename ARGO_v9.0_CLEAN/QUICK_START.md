# ARGO v9.0 Clean - Quick Start

## Installation (2 minutes)

```bash
# 1. Extract package
cd ARGO_v9.0_CLEAN

# 2. Run install script
./install.sh

# 3. Edit .env file
nano .env
# Add: OPENAI_API_KEY=sk-your-key-here

# Done!
```

## First Run (1 minute)

```bash
# Test initialization
python -c "from core.bootstrap import initialize_argo; print('OK')"

# Run audit (optional but recommended)
python scripts/audit_architecture.py

# Start UI
streamlit run app/ui.py
```

## Migration from v9.0 F1

```bash
python scripts/migrate_to_clean.py ../ARGO_v9.0 ./
```

## Key Differences from v9.0 F1

| Aspect | Old | New |
|--------|-----|-----|
| Bootstrap | 2 files | 1 file |
| Init function | `initialize_argo_f1()` | `initialize_argo()` |
| RAG engines | 2 | 1 (consolidated) |
| Databases | 2 | 1 |
| Config | Scattered | `config/settings.yaml` |
| LLM calls | Direct + Router | Router only |
| Chunking | Multiple places | `tools/extractors.py` only |

## Architecture Rules

1. **Single init:** Only `initialize_argo()` exists
2. **Router only:** All LLM calls via `model_router.run()`
3. **Central chunking:** Only `extractors.extract_and_chunk()`
4. **Config from YAML:** No hardcoded values

## Need Help?

- See: `README.md` for full guide
- See: `DELIVERY_COMPLETE.md` for technical details
- Run: `python scripts/audit_architecture.py` to check compliance
