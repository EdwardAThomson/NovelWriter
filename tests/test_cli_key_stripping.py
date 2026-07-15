"""Key-strip regression test: replaces the guarantee of the deleted interim
hotfix core/generation/llm_interface/_env.py.

The billing gotcha: ai_helper runs load_dotenv(), so provider API keys from
.env sit in os.environ; the agent CLIs treat an environment API key as
outranking their configured subscription login. The llm-backends CLI
interfaces therefore strip the provider keys from a COPY of the subprocess
environment by default. This test drives the ClaudeCliInterface (imported via
the old NovelWriter path) with a fake subprocess and asserts the child env.
"""

import json
import os

import pytest

from core.generation.llm_interface.claude_cli_interface import ClaudeCliInterface


class FakeCompleted:
    def __init__(self, stdout):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = 0


@pytest.fixture()
def captured_run(monkeypatch):
    """Fake subprocess.run inside the package module, capturing kwargs."""
    import llm_backends.claude_cli_interface as mod

    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["env"] = kwargs.get("env")
        return FakeCompleted(json.dumps({"result": "stripped ok"}))

    monkeypatch.setattr(mod.shutil, "which", lambda _bin: "/usr/bin/claude")
    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    return captured


def test_claude_cli_strips_both_anthropic_key_spellings(monkeypatch, captured_run):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-metered")
    monkeypatch.setenv("CLAUDE_API_KEY", "sk-ant-legacy")

    client = ClaudeCliInterface()
    out = client.generate("write a line")

    assert out == "stripped ok"
    child_env = captured_run["env"]
    assert child_env is not None, "expected an explicit (stripped) child env"
    assert "ANTHROPIC_API_KEY" not in child_env
    assert "CLAUDE_API_KEY" not in child_env
    # The parent process environment must be untouched.
    assert os.environ["ANTHROPIC_API_KEY"] == "sk-ant-metered"
    assert os.environ["CLAUDE_API_KEY"] == "sk-ant-legacy"


def test_claude_cli_opt_out_inherits_parent_env(monkeypatch, captured_run):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-metered")

    client = ClaudeCliInterface(strip_provider_keys=False)
    client.generate("write a line")

    # env=None means the child inherits the parent environment untouched.
    assert captured_run["env"] is None
