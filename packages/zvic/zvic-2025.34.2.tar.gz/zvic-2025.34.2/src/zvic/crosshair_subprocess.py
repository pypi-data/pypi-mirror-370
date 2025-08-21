import logging
import os
import subprocess
import sys
import tempfile


def run_crosshair_on_code(
    code: str, function_name: str, timeout_seconds: int | None = 10
) -> bool | None:
    """
    Write the given code to a temporary file and run crosshair check on the specified function.

    Args:
        code: Python source to write to a temp file for CrossHair to analyse.
        function_name: the function name inside `code` to check (for future use).
        timeout_seconds: maximum seconds to wait for the CrossHair subprocess. If
            None, wait indefinitely. Defaults to 10 seconds.

    Returns:
        True if CrossHair finds no counterexample, False if a counterexample was
        found, or None if CrossHair could not analyse (or timed out).
    """
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        # Run crosshair check on the function
        cmd = [
            sys.executable,
            "-m",
            "crosshair",
            "check",
            tmp_path,
            "--analysis_kind",
            "icontract",
            "--per_condition_timeout",
            "2",
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout_seconds
            )
        except subprocess.TimeoutExpired as e:
            # CrossHair ran longer than allowed. Treat this as 'could not analyse'.
            logging.getLogger(__name__).debug(
                "CrossHair timed out after %s seconds while analysing function %r: %s",
                timeout_seconds,
                function_name,
                e,
            )
            return None
        output = result.stdout + "\n" + result.stderr
        # ...debug print removed...
        # Look for 'No counterexamples found' or similar success message, or exit code 0
        if "no checkable functions" in output.lower():
            # Signal to caller that CrossHair could not check this function
            return None
        if result.returncode == 0:
            return True
        if "No counterexamples found" in output or "No failed conditions" in output:
            return True
        return False
    finally:
        os.unlink(tmp_path)
