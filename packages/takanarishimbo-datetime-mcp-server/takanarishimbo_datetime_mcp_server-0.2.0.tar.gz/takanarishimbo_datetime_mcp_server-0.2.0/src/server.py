#!/usr/bin/env python3
"""
0. DateTime MCP Server

This server provides tools to get the current date and time in various formats.

Environment Variables:
- DATETIME_FORMAT: Controls the output format of the datetime (default: "iso")
  Supported formats:
  - "iso": ISO 8601 format (2024-01-15T10:30:00.000000+00:00)
  - "unix": Unix timestamp in seconds
  - "unix_ms": Unix timestamp in milliseconds
  - "human": Human-readable format (Mon, Jan 15, 2024 10:30:00 AM UTC)
  - "date": Date only (2024-01-15)
  - "time": Time only (10:30:00)
  - "custom": Custom format using DATE_FORMAT_STRING environment variable
- DATE_FORMAT_STRING: Custom date format string (only used when DATETIME_FORMAT="custom")
  Uses Python strftime format codes
- TIMEZONE: Timezone to use (default: "UTC")
  Examples: "UTC", "America/New_York", "Asia/Tokyo"

Example:
  DATETIME_FORMAT=iso uvx uvx-datetime-mcp-server
  DATETIME_FORMAT=human TIMEZONE=America/New_York uvx uvx-datetime-mcp-server
  DATETIME_FORMAT=custom DATE_FORMAT_STRING="%Y-%m-%d %H:%M:%S" uvx uvx-datetime-mcp-server

0. 日時MCPサーバー

このサーバーは、現在の日付と時刻を様々な形式で取得するツールを提供します。

環境変数:
- DATETIME_FORMAT: 日時の出力形式を制御します(デフォルト: "iso")
  サポートされる形式:
  - "iso": ISO 8601形式 (2024-01-15T10:30:00.000000+00:00)
  - "unix": 秒単位のUnixタイムスタンプ
  - "unix_ms": ミリ秒単位のUnixタイムスタンプ
  - "human": 人間が読める形式 (Mon, Jan 15, 2024 10:30:00 AM UTC)
  - "date": 日付のみ (2024-01-15)
  - "time": 時刻のみ (10:30:00)
  - "custom": DATE_FORMAT_STRING環境変数を使用したカスタム形式
- DATE_FORMAT_STRING: カスタム日付形式文字列(DATETIME_FORMAT="custom"の場合のみ使用)
  Python strftimeフォーマットコードを使用
- TIMEZONE: 使用するタイムゾーン(デフォルト: "UTC")
  例: "UTC", "America/New_York", "Asia/Tokyo"

例:
  DATETIME_FORMAT=iso uvx uvx-datetime-mcp-server
  DATETIME_FORMAT=human TIMEZONE=America/New_York uvx uvx-datetime-mcp-server
  DATETIME_FORMAT=custom DATE_FORMAT_STRING="%Y-%m-%d %H:%M:%S" uvx uvx-datetime-mcp-server
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, Literal, Annotated

import pytz
from pydantic import Field
from mcp.server.fastmcp import FastMCP

"""
1. Environment Configuration

Get configuration from environment variables

Examples:
  DATETIME_FORMAT="iso" → ISO 8601 format output
  DATETIME_FORMAT="unix" → Unix timestamp in seconds
  DATETIME_FORMAT="custom" DATE_FORMAT_STRING="%Y-%m-%d" → Custom date format
  TIMEZONE="America/New_York" → Use New York timezone
  No environment variables → Defaults to ISO format with UTC timezone

1. 環境設定

環境変数から設定を取得

例:
  DATETIME_FORMAT="iso" → ISO 8601形式の出力
  DATETIME_FORMAT="unix" → 秒単位のUnixタイムスタンプ
  DATETIME_FORMAT="custom" DATE_FORMAT_STRING="%Y-%m-%d" → カスタム日付形式
  TIMEZONE="America/New_York" → ニューヨークのタイムゾーンを使用
  環境変数なし → UTCタイムゾーンでISO形式をデフォルト使用
"""
DATETIME_FORMAT = os.environ.get("DATETIME_FORMAT", "iso")
DATE_FORMAT_STRING = os.environ.get("DATE_FORMAT_STRING", "%Y-%m-%d %H:%M:%S")
TIMEZONE = os.environ.get("TIMEZONE", "UTC")

"""
2. Server Initialization

Create MCP server instance with metadata

Examples:
  Server name: "uvx-datetime-mcp-server"
  Version: "0.1.0"
  Protocol: Model Context Protocol (MCP)

2. サーバー初期化

メタデータを持つMCPサーバーインスタンスを作成

例:
  サーバー名: "uvx-datetime-mcp-server"
  バージョン: "0.1.0"
  プロトコル: Model Context Protocol (MCP)
"""
mcp = FastMCP("uvx-datetime-mcp-server")


"""
3. Date Formatting Function

Helper function to format date based on format type

Examples:
  format_datetime(now, "iso", "UTC") → "2024-01-15T10:30:00.000000+00:00"
  format_datetime(now, "unix", "UTC") → "1705318200"
  format_datetime(now, "human", "America/New_York") → "Mon, Jan 15, 2024 05:30:00 AM EST"
  format_datetime(now, "date", "Asia/Tokyo") → "2024-01-15"
  format_datetime(now, "time", "Europe/London") → "10:30:00"
  format_datetime(now, "custom", "UTC") → Uses DATE_FORMAT_STRING environment variable

3. 日付フォーマット関数

形式タイプに基づいて日付をフォーマットするヘルパー関数

例:
  format_datetime(now, "iso", "UTC") → "2024-01-15T10:30:00.000000+00:00"
  format_datetime(now, "unix", "UTC") → "1705318200"
  format_datetime(now, "human", "America/New_York") → "Mon, Jan 15, 2024 05:30:00 AM EST"
  format_datetime(now, "date", "Asia/Tokyo") → "2024-01-15"
  format_datetime(now, "time", "Europe/London") → "10:30:00"
  format_datetime(now, "custom", "UTC") → DATE_FORMAT_STRING環境変数を使用
"""


def format_datetime(now: datetime, format_type: str) -> str:
    """
    Format datetime based on requested format type.

    Args:
        now: datetime object to format
        format_type: Output format type

    Returns:
        Formatted datetime string
    """
    if format_type == "iso":
        return now.isoformat()
    elif format_type == "unix":
        return str(int(now.timestamp()))
    elif format_type == "unix_ms":
        return str(int(now.timestamp() * 1000))
    elif format_type == "human":
        return now.strftime("%a, %b %d, %Y %I:%M:%S %p %Z")
    elif format_type == "date":
        return now.strftime("%Y-%m-%d")
    elif format_type == "time":
        return now.strftime("%H:%M:%S")
    elif format_type == "custom":
        return format_custom_date(now, DATE_FORMAT_STRING)
    else:
        return now.isoformat()


"""
4. Custom Date Formatter

Simple custom date formatter with token replacement for Python strftime codes

Examples:
  format_custom_date(now, "%Y-%m-%d", "UTC") → "2024-01-15"
  format_custom_date(now, "%d/%m/%Y %H:%M", "UTC") → "15/01/2024 10:30"
  format_custom_date(now, "%y-%m-%d %H:%M:%S", "UTC") → "24-01-15 10:30:45"
  Supported tokens: %Y (4-digit year), %y (2-digit year), %m (month), %d (day)
                    %H (24-hour), %M (minutes), %S (seconds)

4. カスタム日付フォーマッター

Python strftimeコードによるトークン置換を使用したシンプルなカスタム日付フォーマッター

例:
  format_custom_date(now, "%Y-%m-%d", "UTC") → "2024-01-15"
  format_custom_date(now, "%d/%m/%Y %H:%M", "UTC") → "15/01/2024 10:30"
  format_custom_date(now, "%y-%m-%d %H:%M:%S", "UTC") → "24-01-15 10:30:45"
  サポートされるトークン: %Y (4桁の年), %y (2桁の年), %m (月), %d (日)
                        %H (24時間), %M (分), %S (秒)
"""


def format_custom_date(now: datetime, format_string: str) -> str:
    """
    Simple custom date formatter using Python strftime.

    Args:
        now: datetime object to format
        format_string: Python strftime format string

    Returns:
        Formatted datetime string using the custom format

    Examples:
        format_custom_date(now, "%Y-%m-%d") → "2024-01-15"
        format_custom_date(now, "%d/%m/%Y %H:%M") → "15/01/2024 10:30"
    """
    return now.strftime(format_string)


"""
5. Tool Definition

Define the "get_current_time" tool. Schema is auto-generated by FastMCP from the
function signature (Annotated + Field)

Inputs:
  - format?   : "iso" | "unix" | "unix_ms" | "human" | "date" | "time" | "custom"
                (default = DATETIME_FORMAT)
  - timezone? : IANA TZ string (default = TIMEZONE)

Notes:
  - format="custom" uses DATE_FORMAT_STRING
  - Unknown timezone → ValueError('Error: Unknown timezone "<tzname>"')

Examples: { "format": "iso" } / { "format": "unix", "timezone": "UTC" } / {}
    
5. ツール定義

"get_current_time" を定義。スキーマは関数シグネチャ（Annotated + Field）から
FastMCP が自動生成します

入力:
  - format（任意）  : "iso" | "unix" | "unix_ms" | "human" | "date" | "time" | "custom"
                      （既定 = DATETIME_FORMAT）
  - timezone（任意）: IANA タイムゾーン文字列（既定 = TIMEZONE）

補足:
  - format="custom" の場合は DATE_FORMAT_STRING を使用
  - 不明なタイムゾーン → ValueError('Error: Unknown timezone "<tzname>"')

例: { "format": "iso" } / { "format": "unix", "timezone": "UTC" } / {}
"""


@mcp.tool(
    name="get_current_time",
    description="Get the current date and time in various formats",
)
def get_current_time(
    format: Annotated[
        Optional[Literal["iso", "unix", "unix_ms", "human", "date", "time", "custom"]],
        Field(
            description=(
                f"Output format for the datetime (optional). "
                f'Defaults to DATETIME_FORMAT env (current default: "{DATETIME_FORMAT}"). '
                "Valid: iso, unix, unix_ms, human, date, time, custom."
            )
        ),
    ] = None,
    timezone: Annotated[
        Optional[str],
        Field(
            description=(
                f'Timezone to use (optional). Defaults to TIMEZONE env (current default: "{TIMEZONE}"). '
                'Valid timezones: any IANA TZ (e.g., "UTC", "America/New_York", "Asia/Tokyo").'
            )
        ),
    ] = None,
) -> str:
    fmt = format or DATETIME_FORMAT
    tzname = timezone or TIMEZONE

    try:
        tz = pytz.timezone(tzname)
    except pytz.exceptions.UnknownTimeZoneError as e:
        raise ValueError(f"Error: Unknown timezone '{tzname}'") from e

    now = datetime.now(tz)
    return format_datetime(now, fmt)


"""
6. Server Startup Function

Initialize and run the MCP server with stdio transport

Examples:
  Normal startup → "DateTime MCP Server running on stdio"
  With ISO format → "Default format: iso"
  With custom format → "Default format: custom" + "Custom format string: %Y-%m-%d"
  With timezone → "Default timezone: America/New_York"
  Transport: stdio (communicates via stdin/stdout)
  Connection error → Process exits with appropriate error

6. サーバー起動関数

stdioトランスポートでMCPサーバーを初期化して実行

例:
  通常の起動 → "DateTime MCP Server running on stdio"
  ISO形式で → "Default format: iso"
  カスタム形式で → "Default format: custom" + "Custom format string: %Y-%m-%d"
  タイムゾーン付き → "Default timezone: America/New_York"
  トランスポート: stdio (stdin/stdout経由で通信)
  接続エラー → プロセスは適切なエラーで終了
"""


def main() -> None:
    print("DateTime MCP Server running on stdio")
    print(f"Default format: {DATETIME_FORMAT}")
    print(f"Default timezone: {TIMEZONE}")
    if DATETIME_FORMAT == "custom":
        print(f"Custom format string: {DATE_FORMAT_STRING}")
    mcp.run(transport="stdio")
