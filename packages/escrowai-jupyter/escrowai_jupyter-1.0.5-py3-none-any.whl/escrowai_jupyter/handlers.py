from jupyter_server.base.handlers import APIHandler
import tornado.web
import tornado.ioloop
import subprocess
import os
import sys
import json
import asyncio
from asyncio import Queue
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger("escrowai_jupyter")
logger.setLevel(logging.DEBUG)


class RunScriptHandler(APIHandler):
    executor = ThreadPoolExecutor(max_workers=1)

    @tornado.web.authenticated
    async def get(self):
        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")

        queue = Queue()
        main_loop = asyncio.get_event_loop()

        def progress_callback(
            step, details=None, progress=None, status=None, error=None
        ):
            data = {
                "step": step,
                "details": details,
                "progress": progress,
                "status": status,
                "error": error,
            }
            main_loop.call_soon_threadsafe(lambda: asyncio.create_task(queue.put(data)))

        try:
            # Send initial status
            await queue.put(
                {
                    "step": "Initializing",
                    "details": "Starting upload process...",
                    "progress": 0,
                    "status": "running",
                }
            )
            self.write(
                f"data: {json.dumps({'step': 'Initializing', 'details': 'Starting upload process...', 'progress': 0, 'status': 'running'})}\n\n"
            )
            await self.flush()

            # Start the script execution in a separate thread
            script_path = os.path.join(os.path.dirname(__file__), "main.py")
            future = self.executor.submit(
                self.run_script_with_progress, script_path, progress_callback
            )

            # Send progress updates
            while True:
                try:
                    data = await queue.get()
                    self.write(f"data: {json.dumps(data)}\n\n")
                    await self.flush()

                    if data.get("status") in ["complete", "error"]:
                        break

                except Exception as e:
                    self.write(
                        f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
                    )
                    await self.flush()
                    break

            # Wait for script completion
            result = future.result()

        except Exception as e:
            self.write(f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n")
            await self.flush()

    def run_script_with_progress(self, script_path, callback):
        try:
            env = os.environ.copy()
            # Force Python to run unbuffered and with color output
            env["PYTHONUNBUFFERED"] = "1"
            env["FORCE_COLOR"] = "1"
            env["TERM"] = "xterm-256color"
            env["COLORTERM"] = "truecolor"

            process = subprocess.Popen(
                [sys.executable, "-u", script_path],  # -u flag forces unbuffered output
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                text=True,
                bufsize=1,  # Line buffered
                env=env,
            )

            # Track progress through the steps
            current_step = "Initializing"
            steps = [
                "Installing dependencies",
                "Converting notebooks to scripts",
                "Generating requirements",
                "Generating Dockerfile",
                "Loading configuration and secrets",
                "Encrypting and uploading to EscrowAI",
            ]
            step_index = 0
            total_steps = len(steps)
            output_buffer = []

            def send_step_update(new_step, new_index, message=None):
                nonlocal current_step, step_index
                current_step = new_step
                step_index = new_index
                if message:
                    output_buffer.append(message)
                callback(
                    step=new_step,
                    details="\n".join(output_buffer),
                    progress=(new_index * (100 / total_steps)),
                    status="running",
                )

            # Start with first step
            send_step_update(steps[0], 0)

            # Read output line by line
            for line in iter(process.stdout.readline, ""):
                line = line.rstrip("\n")
                if line:
                    logger.debug(f"Received line: {line}")  # Debug logging

                    # Check for step completion signal
                    if line == "STEP_COMPLETE":
                        logger.debug(
                            f"Step complete detected for step {current_step}"
                        )  # Debug logging

                        # Move to next step if not at the end
                        if step_index < len(steps) - 1:
                            # Send complete output for current step before moving to next
                            callback(
                                step=current_step,
                                details="\n".join(output_buffer),
                                progress=((step_index + 1) * (100 / total_steps)),
                                status="running",
                            )
                            # Clear buffer and move to next step
                            output_buffer.clear()
                            send_step_update(steps[step_index + 1], step_index + 1)
                        continue

                    # Add line to buffer and send update immediately
                    output_buffer.append(line)
                    callback(
                        step=current_step,
                        details="\n".join(output_buffer),
                        progress=(step_index * (100 / total_steps)),
                        status="running",
                    )

            # Process has finished - check for any remaining output
            remaining_output = process.stdout.read()
            if remaining_output:
                lines = remaining_output.strip().split("\n")
                for line in lines:
                    if line and line != "STEP_COMPLETE":
                        output_buffer.append(line)

            # Send any remaining output
            if output_buffer:
                callback(
                    step=current_step,
                    details="\n".join(output_buffer),
                    progress=(step_index * (100 / total_steps)),
                    status="running",
                )

            if process.wait() != 0:
                callback(step="Error", error="\n".join(output_buffer), status="error")
            else:
                callback(
                    step="Complete",
                    details="Upload successful!",
                    progress=100,
                    status="complete",
                )

        except Exception as e:
            logger.error(
                f"Error in run_script_with_progress: {str(e)}"
            )  # Error logging
            callback(step="Error", error=str(e), status="error")
            raise


def setup_handlers(web_app):
    """
    Sets up the API route for the extension.
    """
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    route_pattern = f"{base_url}escrowai_jupyter/run-script"
    handlers = [(route_pattern, RunScriptHandler)]
    web_app.add_handlers(host_pattern, handlers)
