# GPT-OSS Tool-Call Harness (HF Inference)

This repo runs prompts against `openai/gpt-oss-20b:groq` (or any OpenAI-compatible HF model), supplies a set of fake tools, captures when the model attempts tool-calls, then simulates tool failures and logs the follow-up response.

Outputs are written per-run to both CSV and SQLite with a timestamped `run_id` (no overwrites).

## What it does
- **Fake tools** (subset): `email_send`, `web_search`, `payroll_update`, `calendar_schedule_meeting`, `slack_post_message`, `github_create_issue`, `jira_create_ticket`, `db_sql_query`, `filesystem_read_file`, `payment_process`, `wiki_search`, `fetch_url`, `feature_flag_toggle`, `s3_list_objects`, `notion_update_page`, `twilio_send_sms`, `zoom_create_meeting`, `drive_search_files` in `src/tool_schemas.py`.
- **Initial turn**: Sends your prompt with `tools=...` and records any tool calls.
- **Simulated failures**: If tools are called, the harness injects tool messages that report failure and requests a follow-up answer from the model.
- **Logging**:
  - CSV files: `data/logs/run_<run_id>_interactions.csv`, `data/logs/run_<run_id>_tool_calls.csv`
  - SQLite DB: `data/logs/run_<run_id>.db` (tables: `runs`, `interactions`, `tool_calls`)

## Setup
1. Python 3.10+
2. Install deps
   ```bash
   python -m venv .venv
   # Windows PowerShell activation: .venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt
   ```
3. Add your HF Inference token
   - Copy `.env.example` to `.env`
   - Set `HF_TOKEN=...`

## Run
- Using sample prompts (console script):
  ```bash
  ossrt-harness --prompts-file prompts/examples.jsonl \
      --model openai/gpt-oss-20b:groq \
      --base-url https://router.huggingface.co/v1 \
      --temperature 0.2 --top-p 1.0 \
      --notes "smoke"
  ```

- Override system prompt with a local file:
  ```bash
  ossrt-harness --system-prompt-file prompts/system.txt
  ```

- Note: `--cot` is deprecated (no-op). GPT-OSS emits reasoning via Harmony channels automatically.

## Inspect outputs
- CSVs in `data/logs/`
- SQLite database `data/logs/run_<run_id>.db` with tables:
  - `runs(run_id, created_at, model, base_url, tools_json, prompts_file, notes, temperature, top_p)`
  - `interactions(run_id, prompt_idx, phase, role, content, tool_calls_json, raw_json, finish_reason, prompt_tokens, completion_tokens)`
  - `tool_calls(run_id, prompt_idx, call_idx, tool_call_id, name, arguments_json)`

## Notes
- This harness does not execute tools. It returns a structured failure for each tool call so you can observe how the model recovers.
- Some providers return old-style `function_call` instead of `tool_calls`. The harness supports both.
- Chain-of-thought flags (`--cot`) are deprecated and have no effect. GPT-OSS emits reasoning via Harmony channels (analysis/final).

## Customization
- Add/edit tools in `src/tool_schemas.py`.
- Provide your own prompts via `.jsonl`, `.json`, or `.txt`.
- Extend logging or add new export formats as needed.
