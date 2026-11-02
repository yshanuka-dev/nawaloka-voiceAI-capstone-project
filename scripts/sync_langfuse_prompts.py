#!/usr/bin/env python3
"""
Sync all default system and user prompts to Langfuse Prompt Management.
"""

from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv(".env")

from langfuse import Langfuse
from memory.prompts import (
    _DISTILL_SYSTEM_FALLBACK,
    _DISTILL_USER_FALLBACK,
    _RECALL_SYSTEM_FALLBACK,
    _RECALL_USER_FALLBACK,
)
from agents.prompts.agent_prompts import (
    _AGENT_SYSTEM_FALLBACK,
    _ROUTER_SYSTEM_FALLBACK,
    _ROUTER_USER_FALLBACK,
    _SYNTHESISER_SYSTEM_FALLBACK,
    _SYNTHESISER_USER_FALLBACK,
    _ADMIN_AGENT_FALLBACK,
    _CLINICAL_AGENT_FALLBACK,
    _DIRECT_AGENT_FALLBACK,
    _MERGE_SYNTHESISER_FALLBACK,
)


def to_mustache(prompt_str: str) -> str:
    """Convert Python format {var} to Mustache {{var}} for Langfuse."""
    import re
    # Replace single {var} with {{var}} if not already {{var}}
    return re.sub(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})", r"{{\1}}", prompt_str)


PROMPTS_TO_SYNC = {
    # Memory prompts
    "nawaloka-distill-system": (_DISTILL_SYSTEM_FALLBACK, "Distillation system persona for extracting memory facts"),
    "nawaloka-distill-user": (to_mustache(_DISTILL_USER_FALLBACK), "Distillation user turn template"),
    "nawaloka-recall-system": (_RECALL_SYSTEM_FALLBACK, "Recall system assistant prompt"),
    "nawaloka-recall-user": (to_mustache(_RECALL_USER_FALLBACK), "Recall user turn template"),

    # Agent prompts
    "nawaloka-agent-system": (_AGENT_SYSTEM_FALLBACK, "Base Nawaloka Health Assistant persona"),
    "nawaloka-router-system": (_ROUTER_SYSTEM_FALLBACK, "Intent classification router system prompt"),
    "nawaloka-router-user": (to_mustache(_ROUTER_USER_FALLBACK), "Intent classification router user turn template"),
    "nawaloka-synthesiser-system": (_SYNTHESISER_SYSTEM_FALLBACK, "Response synthesiser system prompt"),
    "nawaloka-synthesiser-user": (to_mustache(_SYNTHESISER_USER_FALLBACK), "Response synthesiser user turn template"),

    # Sub-agent personas
    "nawaloka-admin-agent": (_ADMIN_AGENT_FALLBACK, "Admin Agent persona (CRM/scheduling)"),
    "nawaloka-clinical-agent": (_CLINICAL_AGENT_FALLBACK, "Clinical Agent persona (RAG/medical KB)"),
    "nawaloka-direct-agent": (_DIRECT_AGENT_FALLBACK, "Direct Agent persona (Concierge)"),
    "nawaloka-merge-synthesiser": (_MERGE_SYNTHESISER_FALLBACK, "Multi-agent output merger prompt"),
}


def main():
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL", "https://us.cloud.langfuse.com")

    if not public_key or not secret_key:
        print("[ERROR] Langfuse keys are not configured in .env")
        return 1

    client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )

    print(f"Syncing {len(PROMPTS_TO_SYNC)} prompts to Langfuse ({host})...\n")

    for name, (content, desc) in PROMPTS_TO_SYNC.items():
        try:
            client.create_prompt(
                name=name,
                prompt=content,
                labels=["production"],
                type="text",
                commit_message=f"Auto-synced: {desc}",
            )
            print(f"  [OK] Synced '{name}' (labeled: production)")
        except Exception as e:
            print(f"  [FAILED] '{name}': {e}")

    print("\nPrompt sync complete! They are now active in your Langfuse dashboard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
