"""Wrapper for calling Codex CLI from Python.

Provides subprocess-based interface to Codex CLI for zero-cost access to GPT-5.
"""
import subprocess
import shutil
from typing import Optional


class CodexInterface:
    """Interface for calling Codex CLI to access GPT-5."""
    
    def __init__(self, codex_bin: str = "codex"):
        """Initialize Codex interface.
        
        Args:
            codex_bin: Path to codex binary (default: 'codex' in PATH)
            
        Raises:
            RuntimeError: If Codex CLI is not installed or not in PATH
        """
        self.codex_bin = codex_bin
        self._verify_codex_installed()
    
    def _verify_codex_installed(self):
        """Check if Codex CLI is installed and accessible.
        
        Raises:
            RuntimeError: If Codex CLI cannot be found
        """
        if not shutil.which(self.codex_bin):
            raise RuntimeError(
                f"Codex CLI not found at '{self.codex_bin}'. "
                "Install with: npm install -g @openai/codex-cli\n"
                "Then authenticate with: codex auth"
            )
    
    @staticmethod
    def is_available(codex_bin: str = "codex") -> bool:
        """Check if Codex CLI is available without raising an error.
        
        Args:
            codex_bin: Path to codex binary
            
        Returns:
            True if Codex CLI is available, False otherwise
        """
        return shutil.which(codex_bin) is not None
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        timeout: int = 120
    ) -> str:
        """Generate text using Codex CLI.
        
        Args:
            prompt: The prompt to send to Codex
            max_tokens: Maximum tokens to generate (default: 2000)
            timeout: Timeout in seconds (default: 120)
            
        Returns:
            Generated text from GPT-5
            
        Raises:
            RuntimeError: If Codex CLI returns an error
            subprocess.TimeoutExpired: If generation times out
        """
        try:
            # Use 'codex exec' for non-interactive execution
            result = subprocess.run(
                [
                    self.codex_bin,
                    'exec',
                    '--dangerously-bypass-approvals-and-sandbox',
                    '--skip-git-repo-check',
                    prompt
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            return result.stdout.strip()
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "Unknown error"
            raise RuntimeError(f"Codex CLI error: {error_msg}")
        
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"Codex CLI timed out after {timeout}s. "
                "Try increasing timeout or simplifying the prompt."
            )
    
    def generate_with_retry(
        self,
        prompt: str,
        max_tokens: int = 2000,
        timeout: int = 120,
        max_retries: int = 3
    ) -> str:
        """Generate text with automatic retry on failure.
        
        Args:
            prompt: The prompt to send to Codex
            max_tokens: Maximum tokens to generate
            timeout: Timeout in seconds
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated text from GPT-5
            
        Raises:
            RuntimeError: If all retry attempts fail
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
            f"Codex CLI failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )
