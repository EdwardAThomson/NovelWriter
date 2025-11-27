"""Wrapper for calling Claude Code (claude) CLI from Python.

Provides a subprocess-based interface to the `claude` CLI so NovelWriter can
use Claude models via the local tool in headless (non-interactive) mode.
"""

import json
import shutil
import subprocess
from typing import Optional


class ClaudeCliInterface:
    """Interface for calling Claude Code CLI in headless mode."""

    def __init__(self, claude_bin: str = "claude"):
        """Initialize Claude CLI interface.

        Args:
            claude_bin: Path to `claude` binary (default: "claude" in PATH).

        Raises:
            RuntimeError: If Claude Code CLI is not installed or not in PATH.
        """
        self.claude_bin = claude_bin
        self._verify_claude_installed()

    def _verify_claude_installed(self) -> None:
        """Check if Claude Code CLI is installed and accessible.

        Raises:
            RuntimeError: If Claude Code CLI cannot be found.
        """
        if not shutil.which(self.claude_bin):
            raise RuntimeError(
                f"Claude Code CLI not found at '{self.claude_bin}'. "
                "Install it from https://github.com/anthropics/claude-code and "
                "ensure 'claude' is on your PATH."
            )

    @staticmethod
    def is_available(claude_bin: str = "claude") -> bool:
        """Check if Claude CLI is available without raising an error.
        
        Args:
            claude_bin: Path to claude binary
            
        Returns:
            True if Claude CLI is available, False otherwise
        """
        return shutil.which(claude_bin) is not None

    def _run_headless(self, prompt: str, timeout: int = 120) -> str:
        """Run Claude Code in headless mode and return raw stdout.

        Uses `claude -p "<prompt>" --output-format json` to get a structured
        response and extract the `result` field as the generated text.
        """
        try:
            result = subprocess.run(
                [
                    self.claude_bin,
                    "-p",
                    prompt,
                    "--output-format",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            raise RuntimeError(f"Claude Code CLI error: {error_msg}") from e
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"Claude Code CLI timed out after {timeout}s. "
                "Try increasing timeout or simplifying the prompt."
            )

        stdout = result.stdout.strip()
        if not stdout:
            raise RuntimeError("Claude Code CLI returned empty output")
        return stdout

    def _parse_json_result(self, stdout: str) -> str:
        """Parse JSON output from Claude Code and extract the `result` text."""
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse Claude Code JSON output: {e}") from e

        if isinstance(data, dict) and "result" in data:
            return str(data["result"])

        raise RuntimeError(
            "Claude Code JSON output did not contain a 'result' field. "
            "Raw output: " + stdout
        )

    def generate(self, prompt: str, max_tokens: int = 2000, timeout: int = 120) -> str:
        """Generate text using Claude Code CLI in headless mode.

        Note: `max_tokens` is currently not forwarded; Claude Code will use its
        own defaults and configuration.

        Args:
            prompt: The prompt to send to Claude.
            max_tokens: Maximum tokens to generate (not currently forwarded).
            timeout: Timeout in seconds (default: 120).

        Returns:
            Generated text from Claude Code.

        Raises:
            RuntimeError: If Claude Code CLI returns an error or invalid JSON.
        """
        stdout = self._run_headless(prompt, timeout=timeout)
        return self._parse_json_result(stdout)

    def generate_with_retry(
        self,
        prompt: str,
        max_tokens: int = 2000,
        timeout: int = 120,
        max_retries: int = 3,
    ) -> str:
        """Generate text with automatic retry on failure.

        Args:
            prompt: The prompt to send to Claude.
            max_tokens: Maximum tokens to generate (not currently forwarded).
            timeout: Timeout in seconds.
            max_retries: Maximum number of retry attempts.

        Returns:
            Generated text from Claude Code.

        Raises:
            RuntimeError: If all retry attempts fail.
        """
        last_error: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                return self.generate(prompt, max_tokens, timeout)
            except RuntimeError as e:
                last_error = e
                if attempt < max_retries - 1:
                    continue

        raise RuntimeError(
            f"Claude Code CLI failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )
