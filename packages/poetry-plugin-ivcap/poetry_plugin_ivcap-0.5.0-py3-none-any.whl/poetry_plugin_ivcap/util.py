#
# Copyright (c) 2025 Commonwealth Scientific and Industrial Research Organisation (CSIRO). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file. See the AUTHORS file for names of contributors.
#
import subprocess
import platform
from datetime import datetime, timezone

def get_name(data) -> str:
    project_data = data.get("project", {})
    name = project_data.get("name").replace("-", "_").replace(".", "_")
    return name


def command_exists(cmd: str) -> bool:
    system = platform.system()

    check_cmd = {
        "Windows": ["where", cmd],
        "Linux": ["which", cmd],
        "Darwin": ["which", cmd],
    }.get(system)

    if not check_cmd:
        raise RuntimeError(f"Unsupported OS: {system}")

    try:
        subprocess.run(check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def string_to_number(s):
  """Converts a string to a number (int)."""
  s = s.replace("'", "")  # Remove all single quotes
  try:
    return int(s.strip())
  except ValueError as e:
    print(e)
    return None  # Or raise an exception, depending on your needs

import io
import sys

def execute_subprocess_and_capture_output(command):
    """
    Executes a subprocess, prints all outputs to the console in real-time, and returns a full copy of the output.

    Args:
        command (list): A list of strings representing the command to execute.

    Returns:
        str: A string containing the full output of the subprocess.
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    full_output = ""

    # Read stdout and stderr in real-time
    while True:
        stdout_line = process.stdout.readline()
        stderr_line = process.stderr.readline()

        if stdout_line:
            print("Stdout:", stdout_line, end="")  # Print to console immediately
            sys.stdout.flush()
            full_output += stdout_line
        if stderr_line:
            print("Stderr:", stderr_line, end="")  # Print to console immediately
            sys.stderr.flush()
            full_output += stderr_line

        # Check if the process has finished
        if process.poll() is not None:
            break

    # Read any remaining output
    for line in process.stdout:
        print("Stdout:", line, end="")
        sys.stdout.flush()
        full_output += line
    for line in process.stderr:
        print("Stderr:", line, end="")
        sys.stderr.flush()
        full_output += line

    return full_output

def get_version(data, tag, line):
    if not tag:
        try:
            tag = subprocess.check_output(['git', 'rev-parse', "--short", 'HEAD']).decode().strip()
        except Exception as e:
            line(f"<warning>WARN: retrieving commit hash: {e}</warning>")
            tag = "latest"

    project_data = data.get("project", {})
    v = project_data.get("version", None)
    if not v:
        try:
            v = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0']).decode().strip()
        except Exception as e:
            line(f"<error>Error retrieving latest tag: {e}</error>")
            v = "???"
    now = datetime.now(timezone.utc).astimezone()
    version = f"{v}|{tag}|{now.replace(microsecond=0).isoformat()}"
    return version