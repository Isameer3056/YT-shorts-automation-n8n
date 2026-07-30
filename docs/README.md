# docs/

Export your actual n8n workflow here for others to import:

1. In n8n, open your workflow.
2. Menu (top right) → **Download**.
3. Save the resulting `.json` file into this folder as `workflow-export.json`.

Before committing it, open the file and double-check it doesn't contain any
live API keys or credential IDs — n8n's export generally excludes credential
*values*, but it's worth a quick scan, especially if you used inline keys
anywhere (e.g. pasted directly into a URL) rather than n8n's credential
manager.
