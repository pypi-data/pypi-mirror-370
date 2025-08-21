#!/usr/bin/env python3
"""
0. ROS2 Exec MCP Server / ROS2 実行 MCP サーバー

This MCP server exposes a single tool to execute ROS 2 (ros2) CLI commands.

Environment Variables:
- ROS2_EXEC_TIMEOUT: Default timeout seconds for command execution (default: "30")
- ALLOW_NON_ROS2   : If set to "true", allows executing non-ros2 commands (default: "false")
- DEFAULT_CWD      : Optional default working directory for command execution
- MCP_TRANSPORT    : Transport for MCP server: "stdio" (default) or "streamable-http".

Example:
uvx takanarishimbo-ros2-exec-mcp
ROS2_EXEC_TIMEOUT=60 uvx takanarishimbo-ros2-exec-mcp

このMCPサーバーは、1つのツールで ROS 2 (ros2) CLI コマンドを実行します。

環境変数:
- ROS2_EXEC_TIMEOUT: コマンド実行のデフォルトタイムアウト秒（デフォルト: "30"）
- ALLOW_NON_ROS2   : "true" の場合、ros2 以外のコマンドも許可（デフォルト: "false"）
- DEFAULT_CWD      : コマンド実行時のデフォルト作業ディレクトリ（任意）
- MCP_TRANSPORT    : MCP サーバーのトランスポート。"stdio"（デフォルト）または "streamable-http"。

例:
uvx takanarishimbo-ros2-exec-mcp
ROS2_EXEC_TIMEOUT=60 uvx takanarishimbo-ros2-exec-mcp
"""

from __future__ import annotations

import os
import shlex
import subprocess
from typing import Annotated, Optional

from pydantic import Field
from mcp.server.fastmcp import FastMCP


"""
1. Environment Configuration / 環境設定
"""


ROS2_EXEC_TIMEOUT = int(os.environ.get("ROS2_EXEC_TIMEOUT", "30"))
ALLOW_NON_ROS2 = os.environ.get("ALLOW_NON_ROS2", "false").lower() == "true"
DEFAULT_CWD = os.environ.get("DEFAULT_CWD")
_RAW_TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio").strip().lower()


def _resolve_transport(value: str) -> str:
    # Map human-friendly values to FastMCP transport values
    # - "stdio" -> "stdio"
    # - "html"  -> "streamable-http" (serves minimal HTML UI)
    # - expose "streamable-http" for advanced users as-is
    v = value.strip().lower()
    if v in (
        "stdio",
        "streamable-http",
    ):
        return v
    # Fallback to stdio on unknown value
    return "stdio"


MCP_TRANSPORT = _resolve_transport(_RAW_TRANSPORT)

"""
2. Server Initialization / サーバー初期化
"""


mcp = FastMCP("ros2-exec-mcp")


"""
3. Tool Definition / ツール定義

Tool: ros2_exec
- Executes a ROS 2 CLI command. Only commands beginning with "ros2" are allowed by default.
- Returns combined stdout/stderr and exit code.

Inputs:
- command (required): Full command string, e.g., "ros2 topic list"
- timeout (optional): Timeout seconds (default: ROS2_EXEC_TIMEOUT)
- cwd (optional): Working directory (default: DEFAULT_CWD)

Notes:
- For security, commands not starting with "ros2" are rejected by default (set ALLOW_NON_ROS2=true to override).

ツール: ros2_exec
- ROS 2 CLI コマンドを実行します。既定では "ros2" で始まるコマンドのみ許可します。
- 標準出力/標準エラーと終了コードをまとめて返します。

入力:
- command（必須）: コマンド全文の文字列。例: "ros2 topic list"
- timeout（任意）: タイムアウト秒（既定: ROS2_EXEC_TIMEOUT）
- cwd（任意）: 作業ディレクトリ（既定: DEFAULT_CWD）

備考:
- セキュリティのため、既定では "ros2" で始まらないコマンドは拒否します（ALLOW_NON_ROS2=true で上書き可能）。
"""


@mcp.tool(
    name="ros2_exec",
    description="Execute a ROS 2 CLI command (ros2 ...) and return its output.",
)
def ros2_exec(
    command: Annotated[
        str,
        Field(description=("Full command string to execute (e.g., 'ros2 topic list'). " "This string is parsed with shlex and executed without a shell.")),
    ],
    timeout: Annotated[
        Optional[int],
        Field(description=f"Timeout in seconds (optional). Default: {ROS2_EXEC_TIMEOUT}", ge=1, le=300),
    ] = None,
    cwd: Annotated[
        Optional[str],
        Field(description=("Working directory to run the command in (optional). " f"Default: {DEFAULT_CWD if DEFAULT_CWD else 'current directory'}")),
    ] = None,
) -> str:
    # Build argv from command string / コマンド文字列から argv を生成
    cmd = shlex.split(command)
    if len(cmd) == 0:
        raise ValueError("'command' is empty")

    # Enforce ros2 unless overridden / ALLOW_NON_ROS2=false の場合は 'ros2' 始まりを強制
    if not ALLOW_NON_ROS2 and (len(cmd) == 0 or cmd[0] != "ros2"):
        raise ValueError("Command must start with 'ros2' (set ALLOW_NON_ROS2=true to override)")

    t = timeout or ROS2_EXEC_TIMEOUT
    workdir = cwd or DEFAULT_CWD or os.getcwd()

    try:
        proc = subprocess.run(
            cmd,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=t,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise TimeoutError(f"Command timed out after {t}s: {shlex.join(cmd)}") from e
    except FileNotFoundError as e:
        raise FileNotFoundError("Executable not found in PATH. Ensure the command exists and your environment is sourced.") from e

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    code = proc.returncode

    # Return a readable combined result / 出力を分かりやすく整形
    result_lines = [
        f"Command: {shlex.join(cmd)}",
        f"Exit code: {code}",
    ]
    if stdout:
        result_lines.append("--- STDOUT ---\n" + stdout.rstrip())
    if stderr:
        result_lines.append("--- STDERR ---\n" + stderr.rstrip())

    return "\n".join(result_lines)


"""
4. Server Startup Function / サーバー起動関数
"""


def main() -> None:
    print("ROS2 Exec MCP Server running")
    print(f"Default timeout: {ROS2_EXEC_TIMEOUT}s")
    print(f"Allow non-ros2: {ALLOW_NON_ROS2}")
    if DEFAULT_CWD:
        print(f"Default cwd: {DEFAULT_CWD}")
    print(f"Transport: {MCP_TRANSPORT} (from MCP_TRANSPORT='{_RAW_TRANSPORT}')")
    mcp.run(transport=MCP_TRANSPORT)
