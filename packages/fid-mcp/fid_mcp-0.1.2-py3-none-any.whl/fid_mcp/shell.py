#!/usr/bin/env python3
"""
Interactive Shell Function

Provides a generalized interactive shell interface using pexpect for
managing long-running shell sessions and executing commands with
real-time output handling.
"""

import logging
import os
import re
import time
from typing import Dict, Any, Optional, List, Union
import pexpect

logger = logging.getLogger(__name__)


class InteractiveShell:
    """Manages an interactive shell session using pexpect"""

    def __init__(
        self,
        shell_cmd: str = "bash",
        shell_args: List[str] = None,
        cwd: str = None,
        timeout: int = 300,
        prompt_pattern: str = None,
        custom_prompt: str = None,
        encoding: str = "utf-8",
    ):
        """
        Initialize an interactive shell session

        Args:
            shell_cmd: Command to start the shell (default: "bash")
            shell_args: Arguments for the shell command
            cwd: Working directory for the shell
            timeout: Default timeout for operations in seconds
            prompt_pattern: Regex pattern to match shell prompts
            custom_prompt: Custom prompt to set (helps avoid ANSI sequences)
            encoding: Text encoding for the shell
        """
        self.shell_cmd = shell_cmd
        self.shell_args = shell_args or ["--norc", "--noprofile"]
        self.cwd = cwd or os.getcwd()
        self.timeout = timeout
        self.prompt_pattern = prompt_pattern or [r"\$", r"#", r">", r"nsh>", r"px4>"]
        self.custom_prompt = custom_prompt
        self.encoding = encoding

        self.process = None
        self.is_active = False
        self.created_at = time.time()
        self.command_history = []

    def start(self) -> Dict[str, Any]:
        """Start the interactive shell session"""
        try:
            # Start the shell process
            self.process = pexpect.spawn(
                self.shell_cmd,
                self.shell_args,
                cwd=self.cwd,
                timeout=self.timeout,
                encoding=self.encoding,
            )

            # Wait for initial shell prompt
            initial_timeout = 10
            try:
                self.process.expect(self.prompt_pattern, timeout=initial_timeout)
            except pexpect.TIMEOUT:
                output = self.process.before or ""
                return {
                    "success": False,
                    "error": f"Timeout waiting for shell prompt after {initial_timeout}s",
                    "output": output,
                }

            # Set custom prompt if specified
            if self.custom_prompt:
                self._set_custom_prompt()

            # Clear any remaining output
            self._clear_buffer()

            self.is_active = True
            logger.info(f"Started interactive shell: {self.shell_cmd} in {self.cwd}")

            return {
                "success": True,
                "shell_cmd": self.shell_cmd,
                "cwd": self.cwd,
                "message": "Interactive shell started successfully",
            }

        except Exception as e:
            logger.error(f"Failed to start shell: {e}")
            self.is_active = False
            return {
                "success": False,
                "error": f"Shell startup failed: {str(e)}",
                "shell_cmd": self.shell_cmd,
                "shell_args": self.shell_args,
                "cwd": self.cwd,
            }

    def execute_command(
        self,
        command: str,
        wait: int = 0,
        expect_patterns: List[str] = None,
        capture_output: bool = True,
        continue_on_error: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute a command in the interactive shell

        Args:
            command: Command to execute
            wait: Wait time in seconds. If 0, complete as soon as prompt appears.
                  If > 0, always wait this long and return output (ignore prompts)
            expect_patterns: Additional patterns to expect (beyond prompt)
            capture_output: Whether to capture and return output
            continue_on_error: Whether to continue if command fails

        Returns:
            Dictionary with execution results
        """
        if not self.is_active or not self.process:
            return {
                "success": False,
                "error": "Shell session is not active",
                "command": command,
            }

        command_start_time = time.time()

        try:
            # Clear buffer before sending command
            self._clear_buffer()

            # Send the command
            logger.info(f"Executing command: {command}")
            self.process.sendline(command)

            # If wait > 0, use simple time-based approach
            if wait > 0:
                return self._execute_with_fixed_wait(
                    command, wait, capture_output, command_start_time
                )

            # Determine what patterns to expect
            expect_patterns = expect_patterns or []
            all_patterns = (
                self.prompt_pattern + expect_patterns + [pexpect.TIMEOUT, pexpect.EOF]
            )

            # For wait=0, wait for prompt to appear
            return self._execute_with_prompt_wait(
                command, expect_patterns, capture_output, command_start_time
            )

        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            duration = time.time() - command_start_time
            return {
                "success": False,
                "error": f"Command execution failed: {str(e)}",
                "command": command,
                "duration": duration,
                "session_active": self.is_active,
                "process_alive": self.process.isalive() if self.process else False,
            }

    def _execute_with_fixed_wait(
        self, command: str, wait: int, capture_output: bool, command_start_time: float
    ) -> Dict[str, Any]:
        """Execute command and wait for fixed time, ignoring prompts"""
        logger.info(f"Waiting {wait} seconds for command to complete")

        all_output = ""

        # Collect output for the specified wait time
        end_time = command_start_time + wait
        while time.time() < end_time:
            try:
                remaining = end_time - time.time()
                chunk = self.process.read_nonblocking(
                    size=1000, timeout=min(remaining, 1)
                )
                if capture_output and chunk:
                    all_output += chunk
            except pexpect.TIMEOUT:
                continue  # Keep waiting
            except pexpect.EOF:
                break

        # Clean up output
        clean_output = self._clean_output(all_output, command) if capture_output else ""
        duration = time.time() - command_start_time

        # Always consider fixed-wait commands successful
        result = {
            "success": True,
            "command": command,
            "output": clean_output,
            "duration": duration,
            "cwd": self.cwd,
        }

        self.command_history.append(result)
        return result

    def _execute_with_prompt_wait(
        self,
        command: str,
        expect_patterns: List[str],
        capture_output: bool,
        command_start_time: float,
    ) -> Dict[str, Any]:
        """Execute command and wait for prompt to appear"""
        all_patterns = (
            self.prompt_pattern
            + (expect_patterns or [])
            + [pexpect.TIMEOUT, pexpect.EOF]
        )
        all_output = ""
        command_completed = False

        # Use a reasonable default timeout for prompt detection
        max_wait = 60  # 60 seconds max

        while not command_completed:
            try:
                elapsed = time.time() - command_start_time
                if elapsed > max_wait:
                    logger.warning(f"Command '{command}' exceeded maximum wait time")
                    break

                # Wait for patterns
                index = self.process.expect(all_patterns, timeout=5)

                # Collect output
                if capture_output and self.process.before:
                    all_output += self.process.before

                # Check what we matched
                if index < len(self.prompt_pattern):
                    # Found a prompt - command is done
                    if self._is_real_prompt_match(
                        all_output, self.prompt_pattern[index]
                    ):
                        command_completed = True
                        logger.info(f"Command completed after {elapsed:.2f}s")

                elif index < len(self.prompt_pattern) + len(expect_patterns or []):
                    # Matched a custom pattern - continue reading
                    continue

                elif index >= len(all_patterns) - 2:  # TIMEOUT or EOF
                    # Continue unless we've exceeded max wait
                    continue

            except pexpect.TIMEOUT:
                continue
            except pexpect.EOF:
                if self.process.before and capture_output:
                    all_output += self.process.before
                break

        # Clean up output and determine success
        clean_output = self._clean_output(all_output, command) if capture_output else ""
        success = self._check_command_success(clean_output, command, False)
        duration = time.time() - command_start_time

        # Store result
        result = {
            "success": success,
            "command": command,
            "output": clean_output,
            "duration": duration,
            "cwd": self.cwd,
        }

        # Add error details if command failed
        if not success:
            error_info = self._extract_error_details(clean_output, command)
            result["error"] = error_info

        self.command_history.append(result)
        return result

    def send_input(self, text: str) -> Dict[str, Any]:
        """Send input to the interactive shell without expecting a prompt"""
        if not self.is_active or not self.process:
            return {"success": False, "error": "Shell session is not active"}

        try:
            self.process.send(text)
            return {"success": True, "message": f"Sent input: {repr(text)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_output(self, timeout: int = 5) -> Dict[str, Any]:
        """Read available output from the shell"""
        if not self.is_active or not self.process:
            return {"success": False, "error": "Shell session is not active"}

        try:
            output = ""
            try:
                while True:
                    chunk = self.process.read_nonblocking(size=1000, timeout=timeout)
                    if not chunk:
                        break
                    output += chunk
                    timeout = 0.1  # Reduce timeout for subsequent reads
            except pexpect.TIMEOUT:
                pass  # Normal - no more data available

            return {"success": True, "output": output}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def close(self) -> Dict[str, Any]:
        """Close the interactive shell session and kill any child processes"""
        try:
            if self.process and self.is_active:
                # Send exit command to shell first
                try:
                    self.process.sendline("exit")
                    self.process.expect(pexpect.EOF, timeout=5)
                except (pexpect.TIMEOUT, pexpect.EOF):
                    pass  # Shell may have already exited

                # Terminate the process and its children
                if self.process.isalive():
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except pexpect.TIMEOUT:
                        # Force kill if it doesn't terminate gracefully
                        self.process.kill()

                # Kill any remaining child processes (like gazebo)
                self._kill_child_processes()

                self.process.close()
                self.is_active = False
                logger.info(
                    "Closed interactive shell session and cleaned up child processes"
                )
                return {
                    "success": True,
                    "message": "Shell session closed and child processes terminated",
                }
            return {"success": True, "message": "Shell session was already closed"}
        except Exception as e:
            logger.error(f"Error closing shell session: {e}")
            return {"success": False, "error": str(e)}

    def _kill_child_processes(self):
        """Kill child processes spawned by the shell"""
        try:
            import psutil
            import signal

            if not self.process or not hasattr(self.process, "pid"):
                return

            try:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)

                # First try to terminate children gracefully
                for child in children:
                    try:
                        child.terminate()
                        logger.info(
                            f"Terminated child process: {child.pid} ({child.name()})"
                        )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                # Wait a bit for graceful termination
                import time

                time.sleep(2)

                # Force kill any remaining children
                for child in children:
                    try:
                        if child.is_running():
                            child.kill()
                            logger.info(
                                f"Force killed child process: {child.pid} ({child.name()})"
                            )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        except ImportError:
            # psutil not available, try basic approach
            logger.warning("psutil not available, using basic process cleanup")
            try:
                import os
                import signal

                if self.process and hasattr(self.process, "pid"):
                    # Try to kill the process group
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                    time.sleep(2)
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except Exception as e:
                logger.debug(f"Basic process cleanup failed: {e}")
        except Exception as e:
            logger.debug(f"Child process cleanup failed: {e}")

    def _extract_error_details(self, output: str, command: str) -> str:
        """Extract detailed error information from command output, focusing on the tail"""
        if not output:
            return f"Command '{command}' failed with no output"

        lines = output.split("\n")
        non_empty_lines = [line.strip() for line in lines if line.strip()]

        if not non_empty_lines:
            return f"Command '{command}' failed with no readable output"

        # Always return the last 10 lines of output for context
        # This is most useful for build errors, compilation failures, etc.
        tail_lines = non_empty_lines[-10:]

        # Also look for critical error patterns in the tail
        error_patterns = [
            "error:",
            "failed",
            "cannot",
            "permission denied",
            "no such file or directory",
            "command not found",
            "syntax error",
            "make: ***",
            "fatal:",
            "abort:",
            "exception:",
            "compilation terminated",
            "build failed",
        ]

        # Find error lines in the tail
        error_lines = []
        for line in tail_lines:
            line_lower = line.lower()
            if any(pattern in line_lower for pattern in error_patterns):
                error_lines.append(line)

        # If we found specific errors in tail, prioritize those
        if error_lines:
            return f"Errors found: {' | '.join(error_lines[:5])}"

        # Otherwise return the complete tail for context
        return f"Command failed - Last 10 lines: {' | '.join(tail_lines)}"

    def _cleanup_on_error(self):
        """Clean up processes when command fails or times out"""
        logger.info("Cleaning up processes due to error/timeout")
        try:
            # Kill child processes but keep the shell session alive if possible
            self._kill_child_processes()
        except Exception as e:
            logger.debug(f"Error during cleanup: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the shell session"""
        return {
            "is_active": self.is_active,
            "shell_cmd": self.shell_cmd,
            "cwd": self.cwd,
            "created_at": self.created_at,
            "commands_executed": len(self.command_history),
            "process_alive": self.process.isalive() if self.process else False,
        }

    def _set_custom_prompt(self):
        """Set a custom prompt to avoid ANSI escape sequences"""
        try:
            if self.custom_prompt:
                self.process.sendline(f'export PS1="{self.custom_prompt}"')
                # Update prompt pattern to match custom prompt
                self.prompt_pattern = [re.escape(self.custom_prompt)]
                # Wait for new prompt
                self.process.expect(self.prompt_pattern, timeout=10)
                # Clear any remaining output
                self.process.sendline("")
                self.process.expect(self.prompt_pattern, timeout=5)
                logger.info(f"Set custom prompt: {self.custom_prompt}")
        except Exception as e:
            logger.warning(f"Failed to set custom prompt: {e}")

    def _clear_buffer(self):
        """Clear any accumulated output in the process buffer"""
        if not self.process or not self.is_active:
            return

        try:
            while True:
                try:
                    discarded = self.process.read_nonblocking(size=1000, timeout=0.1)
                    if not discarded:
                        break
                    logger.debug(
                        f"Discarded buffer content: {repr(discarded[:100])}..."
                    )
                except pexpect.TIMEOUT:
                    break
                except pexpect.EOF:
                    break
        except Exception as e:
            logger.debug(f"Error clearing buffer: {e}")

    def _clean_output(self, raw_output: str, command: str) -> str:
        """Clean up raw pexpect output"""
        if not raw_output:
            return ""

        # Remove ANSI escape sequences
        cleaned = re.sub(r"\x1b\[[?]?[0-9;]*[a-zA-Z]", "", raw_output)

        # Remove carriage returns
        cleaned = cleaned.replace("\r", "")

        # For commands that produce important status output, preserve more content
        # This can be configured by caller through command patterns or other means

        # For other commands, use the original cleaning logic
        lines = cleaned.split("\n")
        clean_lines = []

        skip_command_echo = False

        for line in lines:
            # Skip the echoed command line
            if command in line and not skip_command_echo:
                skip_command_echo = True
                continue
            elif skip_command_echo:
                clean_lines.append(line)

        # If we didn't find the command echo, return all lines
        if not skip_command_echo:
            clean_lines = lines

        # Remove empty lines at start and end
        while clean_lines and not clean_lines[0].strip():
            clean_lines.pop(0)
        while clean_lines and not clean_lines[-1].strip():
            clean_lines.pop()

        return "\n".join(clean_lines)

    def _is_real_prompt_match(self, output: str, prompt_pattern: str) -> bool:
        """Check if a prompt match is real or just appears in log output"""
        if not output:
            return False

        # Get the last few lines of output
        lines = output.split("\n")
        last_lines = lines[-3:]  # Check last 3 lines

        # Look for the prompt pattern at the start or end of recent lines
        import re

        for line in last_lines:
            line = line.strip()
            # Check if prompt appears at the end of line (most common)
            if line.endswith(prompt_pattern.replace("\\", "")):
                return True
            # Check if prompt is the only thing on the line
            if line == prompt_pattern.replace("\\", "") or re.match(
                prompt_pattern, line
            ):
                return True

        return False

    def _check_command_success(
        self, output: str, command: str, continue_on_error: bool = False
    ) -> bool:
        """Check if command was successful based on output"""
        if continue_on_error:
            return True

        if not output:
            return True  # No output might be success for some commands

        output_lower = output.lower()

        # Common error indicators
        error_indicators = [
            "error:",
            "failed",
            "cannot",
            "permission denied",
            "no such file or directory",
            "command not found",
            "syntax error",
            "make: *** [",
            "compilation terminated",
            "build failed",
            "fatal error",
            "abort",
            "segmentation fault",
        ]

        for indicator in error_indicators:
            if indicator in output_lower:
                return False

        return True


class ShellSessionManager:
    """Manages multiple interactive shell sessions"""

    def __init__(self):
        self.sessions: Dict[str, InteractiveShell] = {}

    def create_session(
        self, session_id: str, shell_cmd: str = "bash", **kwargs
    ) -> Dict[str, Any]:
        """Create a new shell session"""
        if session_id in self.sessions:
            return {"success": False, "error": f"Session '{session_id}' already exists"}

        try:
            session = InteractiveShell(shell_cmd=shell_cmd, **kwargs)
            result = session.start()

            if result["success"]:
                self.sessions[session_id] = session
                result["session_id"] = session_id
            else:
                result["error"] = (
                    f"Failed to create session '{session_id}': {result.get('error', 'Unknown error')}"
                )

            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception creating session '{session_id}': {str(e)}",
                "shell_cmd": shell_cmd,
                "kwargs": kwargs,
            }

    def get_session(self, session_id: str) -> Optional[InteractiveShell]:
        """Get an existing shell session"""
        return self.sessions.get(session_id)

    def execute_in_session(
        self, session_id: str, command: str, **kwargs
    ) -> Dict[str, Any]:
        """Execute command in a specific session"""
        session = self.get_session(session_id)
        if not session:
            return {
                "success": False,
                "error": f"Session '{session_id}' not found in active sessions: {list(self.sessions.keys())}",
            }

        try:
            result = session.execute_command(command, **kwargs)
            result["session_id"] = session_id
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception executing command in session '{session_id}': {str(e)}",
                "command": command,
                "session_id": session_id,
            }

    def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close and remove a session"""
        session = self.sessions.pop(session_id, None)
        if not session:
            return {"success": False, "error": f"Session '{session_id}' not found"}

        result = session.close()
        result["session_id"] = session_id
        return result

    def list_sessions(self) -> Dict[str, Any]:
        """List all active sessions"""
        sessions_info = {}
        for session_id, session in self.sessions.items():
            sessions_info[session_id] = session.get_status()

        return {"success": True, "sessions": sessions_info}

    def cleanup_inactive_sessions(self) -> Dict[str, Any]:
        """Remove inactive sessions"""
        inactive_sessions = []
        for session_id, session in list(self.sessions.items()):
            if not session.is_active or (
                session.process and not session.process.isalive()
            ):
                inactive_sessions.append(session_id)
                session.close()
                del self.sessions[session_id]

        return {
            "success": True,
            "cleaned_sessions": inactive_sessions,
            "message": f"Cleaned up {len(inactive_sessions)} inactive sessions",
        }

    def cleanup_all_sessions(self) -> Dict[str, Any]:
        """Force close all sessions and clean up their processes"""
        closed_sessions = []
        for session_id, session in list(self.sessions.items()):
            try:
                session.close()
                closed_sessions.append(session_id)
            except Exception as e:
                logger.error(f"Error closing session {session_id}: {e}")

        self.sessions.clear()

        return {
            "success": True,
            "closed_sessions": closed_sessions,
            "message": f"Force closed {len(closed_sessions)} sessions",
        }


# Global session manager
session_manager = ShellSessionManager()
