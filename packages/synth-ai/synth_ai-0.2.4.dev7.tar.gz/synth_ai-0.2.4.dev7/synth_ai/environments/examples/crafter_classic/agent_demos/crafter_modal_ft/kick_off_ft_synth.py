#!/usr/bin/env python3
"""Kick off Synth fine-tuning runs using the same production backend
configuration that our integration tests rely on.

This script doesn't launch the actual fine-tuning process (that lives on the
backend service) – it simply ensures that the current environment is
correctly configured to talk to the production API so that any subsequent CLI
commands or library calls inherit the right base URL and API key.

It re-uses the `setup_synth_environment` helper from
`test_crafter_react_agent_lm_synth.py` to resolve the correct endpoint and
authentication details.
"""

# Re-use the helper we already maintain in the neighbouring test module.
from test_crafter_react_agent_lm_synth import setup_synth_environment  # type: ignore


def main() -> None:
    base_url, api_key = setup_synth_environment()

    # Print info so that callers know what endpoint they are using.
    print("✅ Synth/Modal backend configured")
    print(f"   BASE_URL: {base_url}")
    print("   API_KEY:  [hidden]")

    # Optionally, you could kick off a fine-tune job here. For now we simply
    # confirm that the environment variables are set so that users can run
    # whatever downstream command they need (e.g. `uv run python some_ft.py`).


if __name__ == "__main__":
    main()

