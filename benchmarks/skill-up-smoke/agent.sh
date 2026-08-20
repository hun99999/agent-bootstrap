#!/usr/bin/env bash
set -euo pipefail

input_path="${1:-}"
if [[ -z "$input_path" || ! -f "$input_path" ]]; then
  echo "missing SessionInput: $input_path" >&2
  exit 1
fi

printf '%s\n' '{"exit_code":0,"final_message":"skill-up-smoke-ok","turns":1,"input_tokens":0,"output_tokens":0,"transcript":[{"role":"assistant","content":"skill-up-smoke-ok"}]}'
