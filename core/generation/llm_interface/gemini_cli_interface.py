"""Wrapper for calling Gemini CLI from Python.

Provides a subprocess-based interface to the `gemini` CLI so NovelWriter can
use Gemini models via the local tool.
"""

import shutil
import subprocess
from typing import Optional


class GeminiCliInterface:
    """Interface for calling Gemini CLI to access Gemini models."""

    def __init__(self, model: str = "gemini-2.5-pro", gemini_bin: str = "gemini"):
        """Initialize Gemini CLI interface.

        Args:
            model: Gemini model identifier (e.g. "gemini-2.5-pro").
            gemini_bin: Path to `gemini` binary (default: "gemini" in PATH).

        Raises:
            RuntimeError: If Gemini CLI is not installed or not in PATH.
        """
        self.model = model
        self.gemini_bin = gemini_bin
        self._verify_gemini_installed()

    def _verify_gemini_installed(self) -> None:
        """Check if Gemini CLI is installed and accessible.

        Raises:
            RuntimeError: If Gemini CLI cannot be found.
        """
        if not shutil.which(self.gemini_bin):
            raise RuntimeError(
                f"Gemini CLI not found at '{self.gemini_bin}'. "
                "Install it from https://github.com/google-gemini/gemini-cli and "
                "ensure 'gemini' is on your PATH."
            )

    @staticmethod
    def is_available(gemini_bin: str = "gemini") -> bool:
        """Check if Gemini CLI is available without raising an error.
        
        Args:
            gemini_bin: Path to gemini binary
            
        Returns:
            True if Gemini CLI is available, False otherwise
        """
        return shutil.which(gemini_bin) is not None

    def generate(self, prompt: str, max_tokens: int = 2000, timeout: int = 120) -> str:
        """Generate text using Gemini CLI.

        Note: `max_tokens` is currently not forwarded; Gemini CLI will use its
        own defaults based on the configured model.

        Args:
            prompt: The prompt to send to Gemini.
            max_tokens: Maximum tokens to generate (not currently forwarded).
            timeout: Timeout in seconds (default: 120).

        Returns:
            Generated text from the Gemini CLI.

        Raises:
            RuntimeError: If Gemini CLI returns an error.
        """
        try:
            # Non-interactive call: gemini -p "..." -m <model>
            result = subprocess.run(
                [
                    self.gemini_bin,
                    "-p",
                    prompt,
                    "-m",
                    self.model,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
            )
            return result.stdout.strip()

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            raise RuntimeError(f"Gemini CLI error: {error_msg}") from e

        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"Gemini CLI timed out after {timeout}s. "
                "Try increasing timeout or simplifying the prompt."
            )

    def generate_with_retry(
        self,
        prompt: str,
        max_tokens: int = 2000,
        timeout: int = 120,
        max_retries: int = 3,
    ) -> str:
        """Generate text with automatic retry on failure.

        Args:
            prompt: The prompt to send to Gemini.
            max_tokens: Maximum tokens to generate (not currently forwarded).
            timeout: Timeout in seconds.
            max_retries: Maximum number of retry attempts.

        Returns:
            Generated text from Gemini CLI.

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
            f"Gemini CLI failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )
