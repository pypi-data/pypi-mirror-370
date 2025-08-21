
import asyncio
import datetime
import os
import signal
import psutil
import tempfile
import time
from typing import Any, Optional, Callable, Dict, List, Union
from pathlib import Path


class ShellOutputEvent:
    """Represents different types of shell output events."""
    def __init__(self, event_type: str, **kwargs):
        self.type = event_type
        self.__dict__.update(kwargs)


def format_memory_usage(bytes_count: int) -> str:
    """Format bytes into human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} TB"


def is_binary_data(data: bytes) -> bool:
    """Check if data contains binary content."""
    if not data:
        return False
    # Check for null bytes or high ratio of non-printable characters
    null_count = data.count(b'\x00')
    if null_count > 0:
        return True

    # Check for non-printable characters (excluding common whitespace)
    printable_chars = sum(1 for b in data if 32 <= b <= 126 or b in [9, 10, 13])
    return (printable_chars / len(data)) < 0.7


async def execute_command(
    command: str,
    cwd: Optional[str] = None,
    timeout: int = 30,
    output_callback: Optional[Callable[[str], None]] = None,
    update_interval: float = 1.0,
    max_output_size: int = 10 * 1024 * 1024,  # 10MB limit
    track_background_processes: bool = True
) -> Dict[str, Any]:
    """
    Execute a bash command with advanced features including:
    - Real-time output streaming
    - Binary data detection
    - Background process tracking
    - Process group management
    - Memory usage monitoring
    - Cancellation support

    Args:
        command: Shell command to execute
        cwd: Working directory (optional)
        timeout: Command timeout in seconds
        output_callback: Callback for real-time output updates
        update_interval: Interval for output updates in seconds
        max_output_size: Maximum output size before truncation
        track_background_processes: Whether to track background processes

    Returns:
        Dict containing execution results and metadata
    """
    start_time = time.time()
    cumulative_stdout = ""
    cumulative_stderr = ""
    last_update_time = time.time()
    is_binary_stream = False
    bytes_received = 0
    background_pids: List[int] = []
    process_group_id = None
    was_cancelled = False

    # Prepare enhanced command for background process tracking
    enhanced_command = command
    temp_file_path = None

    if track_background_processes and os.name != 'nt':  # Unix-like systems
        # Create temporary file for process tracking
        temp_fd, temp_file_path = tempfile.mkstemp(prefix='shell_pgrep_', suffix='.tmp')
        os.close(temp_fd)

        # Wrap command to capture background process IDs
        if not command.strip().endswith('&'):
            enhanced_command = f"{{ {command.strip()}; }}; __code=$?; pgrep -g 0 >{temp_file_path} 2>&1; exit $__code;"
        else:
            enhanced_command = f"{{ {command.strip()} }}; __code=$?; pgrep -g 0 >{temp_file_path} 2>&1; exit $__code;"

    process = None

    try:
        # Create subprocess with process group
        if os.name == 'nt':  # Windows
            process = await asyncio.create_subprocess_shell(
                enhanced_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                shell=True,
            )
        else:  # Unix-like systems
            process = await asyncio.create_subprocess_shell(
                enhanced_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                shell=True,
                preexec_fn=os.setsid,  # Create new process group
            )

        process_group_id = process.pid

        async def read_stream_with_updates():
            """Read both stdout and stderr with real-time updates."""
            nonlocal cumulative_stdout, cumulative_stderr, last_update_time
            nonlocal is_binary_stream, bytes_received, was_cancelled

            tasks = []
            if process.stdout:
                tasks.append(asyncio.create_task(read_stream(process.stdout, 'stdout')))
            if process.stderr:
                tasks.append(asyncio.create_task(read_stream(process.stderr, 'stderr')))

            if tasks:
                try:
                    await asyncio.gather(*tasks)
                except asyncio.CancelledError:
                    was_cancelled = True
                    raise

        async def read_stream(stream, stream_name):
            """Read a single stream with binary detection and updates."""
            nonlocal cumulative_stdout, cumulative_stderr, last_update_time
            nonlocal is_binary_stream, bytes_received

            buffer = b""

            while True:
                try:
                    chunk = await stream.read(8192)  # Read in chunks
                    if not chunk:
                        break

                    buffer += chunk
                    bytes_received += len(chunk)

                    # Check for binary data
                    if not is_binary_stream and is_binary_data(buffer[-min(1024, len(buffer)):]):
                        is_binary_stream = True
                        if output_callback:
                            output_callback('[Binary output detected. Halting stream...]')
                        return

                    # Handle binary stream progress
                    if is_binary_stream:
                        current_time = time.time()
                        if current_time - last_update_time > update_interval:
                            if output_callback:
                                output_callback(f'[Receiving binary output... {format_memory_usage(bytes_received)} received]')
                            last_update_time = current_time
                        continue

                    # Process text data
                    try:
                        text_chunk = chunk.decode('utf-8', errors='replace')
                        if stream_name == 'stdout':
                            cumulative_stdout += text_chunk
                        else:
                            cumulative_stderr += text_chunk

                        # Check output size limit
                        total_size = len(cumulative_stdout.encode('utf-8')) + len(cumulative_stderr.encode('utf-8'))
                        if total_size > max_output_size:
                            truncation_msg = f"\n[Output truncated at {format_memory_usage(max_output_size)}]"
                            if stream_name == 'stdout':
                                cumulative_stdout += truncation_msg
                            else:
                                cumulative_stderr += truncation_msg
                            break

                        # Update output if callback provided and enough time has passed
                        current_time = time.time()
                        if output_callback and current_time - last_update_time > update_interval:
                            current_output = cumulative_stdout + (f"\n{cumulative_stderr}" if cumulative_stderr else "")
                            output_callback(current_output)
                            last_update_time = current_time

                    except UnicodeDecodeError:
                        # Handle potential encoding issues
                        continue

                except asyncio.CancelledError:
                    was_cancelled = True
                    break
                except Exception as e:
                    # Log error but continue
                    error_msg = f"\nError reading {stream_name}: {str(e)}"
                    if stream_name == 'stdout':
                        cumulative_stdout += error_msg
                    else:
                        cumulative_stderr += error_msg
                    break

        # Execute with timeout
        try:
            # Start reading streams
            read_task = asyncio.create_task(read_stream_with_updates())

            # Wait for process completion
            try:
                await asyncio.wait_for(process.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                # Kill process group
                if process_group_id:
                    try:
                        if os.name != 'nt':
                            os.killpg(process_group_id, signal.SIGTERM)
                            await asyncio.sleep(1)  # Grace period
                            try:
                                os.killpg(process_group_id, signal.SIGKILL)
                            except ProcessLookupError:
                                pass  # Already terminated
                        else:
                            process.kill()
                    except (ProcessLookupError, PermissionError):
                        pass  # Process already terminated or no permission

                # Cancel reading task
                read_task.cancel()
                try:
                    await read_task
                except asyncio.CancelledError:
                    pass

                return {
                    "success": False,
                    "error": f"Command timed out after {timeout} seconds",
                    "stdout": cumulative_stdout,
                    "stderr": cumulative_stderr,
                    "code": -1,
                    "signal": signal.SIGTERM.value if os.name != 'nt' else None,
                    "command": command,
                    "directory": cwd or "(root)",
                    "executedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "duration": time.time() - start_time,
                    "backgroundPids": [],
                    "processGroupId": process_group_id,
                    "wasCancelled": True,
                    "isBinaryOutput": is_binary_stream,
                    "bytesReceived": bytes_received
                }

            # Wait for stream reading to complete
            try:
                await read_task
            except asyncio.CancelledError:
                pass

        except asyncio.CancelledError:
            was_cancelled = True
            # Kill process group if cancelled
            if process and process_group_id:
                try:
                    if os.name != 'nt':
                        os.killpg(process_group_id, signal.SIGKILL)
                    else:
                        process.kill()
                except (ProcessLookupError, PermissionError):
                    pass
            raise

        # Extract background process IDs (Unix-like systems only)
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                with open(temp_file_path, 'r') as f:
                    pgrep_output = f.read().strip()
                    if pgrep_output:
                        for line in pgrep_output.split('\n'):
                            line = line.strip()
                            if line.isdigit():
                                pid = int(line)
                                if pid != process.pid:
                                    background_pids.append(pid)
            except Exception:
                pass  # Ignore pgrep errors

        # Determine exit status
        exit_code = process.returncode
        exit_signal = None

        # On Unix, negative return codes indicate termination by signal
        if os.name != 'nt' and exit_code is not None and exit_code < 0:
            exit_signal = -exit_code
            exit_code = None

        # Final result
        total_output = cumulative_stdout + (f"\n{cumulative_stderr}" if cumulative_stderr else "")

        result = {
            "success": exit_code == 0 and not was_cancelled,
            "stdout": cumulative_stdout,
            "stderr": cumulative_stderr,
            "output": total_output,
            "code": exit_code,
            "signal": exit_signal,
            "command": command,
            "directory": cwd or "(root)",
            "executedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "duration": time.time() - start_time,
            "backgroundPids": background_pids,
            "processGroupId": process_group_id,
            "wasCancelled": was_cancelled,
            "isBinaryOutput": is_binary_stream,
            "bytesReceived": bytes_received
        }

        # Add error message if command failed
        if not result["success"] and not was_cancelled:
            if exit_signal:
                result["error"] = f"Command terminated by signal {exit_signal}"
            elif exit_code and exit_code != 0:
                result["error"] = f"Command failed with exit code {exit_code}"
            elif cumulative_stderr:
                result["error"] = f"Command failed: {cumulative_stderr.strip()}"
            else:
                result["error"] = "Command failed for unknown reason"
        elif was_cancelled:
            result["error"] = "Command was cancelled"

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": cumulative_stdout,
            "stderr": cumulative_stderr,
            "output": cumulative_stdout + (f"\n{cumulative_stderr}" if cumulative_stderr else ""),
            "code": -1,
            "signal": None,
            "command": command,
            "directory": cwd or "(root)",
            "executedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "duration": time.time() - start_time,
            "backgroundPids": background_pids,
            "processGroupId": process_group_id,
            "wasCancelled": was_cancelled,
            "isBinaryOutput": is_binary_stream,
            "bytesReceived": bytes_received
        }

    finally:
        # Cleanup temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass  # Ignore cleanup errors


# Convenience function with simpler interface
async def simple_execute_command(command: str, cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
    """Simplified version of execute_command for basic use cases."""
    result = await execute_command(command, cwd, timeout)
    return {
        "success": result["success"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "code": result["code"],
        "command": result["command"],
        "executedAt": result["executedAt"]
    }


# Example usage function
async def demo_execute_command():
    """Demonstrate enhanced command execution features."""

    def output_handler(output: str):
        print(f"Real-time output: {output[-100:]}")  # Show last 100 chars

    # Example 1: Basic command
    result = await execute_command("echo 'Hello World'")
    print("Basic command result:", result["success"])

    # Example 2: Command with real-time output
    result = await execute_command(
        "for i in {1..5}; do echo 'Step $i'; sleep 1; done",
        output_callback=output_handler,
        update_interval=0.5
    )
    print("Command with real-time output:", result["success"])

    # Example 3: Background process tracking
    result = await execute_command(
        "sleep 10 & echo 'Background process started'",
        track_background_processes=True,
    )
    print("Background PIDs:", result["backgroundPids"])

    # Example 4: Binary output detection
    result = await execute_command("cat /bin/ls | head -100")
    print("Is binary output:", result["isBinaryOutput"])


if __name__ == "__main__":
    asyncio.run(demo_execute_command())

