#!/usr/bin/env python3
"""Simple CLI for atomic-mcp."""

import argparse
import json
import os
from pathlib import Path


def get_config_path():
    """Get the path to claude_desktop_config.json."""
    if os.name == 'nt':  # Windows
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    elif os.uname().sysname == 'Darwin':  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def load_config():
    """Load existing config or create empty one."""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {"mcpServers": {}}


def save_config(config):
    """Save config to file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Config saved to: {config_path}")


def add_remote_server(name, url):
    """Add a remote MCP server."""
    config = load_config()
    config["mcpServers"][name] = {
        "command": "npx",
        "args": ["mcp-remote", url]
    }
    save_config(config)
    print(f"Added remote server '{name}' with URL: {url}")


def add_stdio_server(name, command, args=None):
    """Add a stdio MCP server."""
    config = load_config()
    server_config = {"command": command}
    if args:
        server_config["args"] = args
    config["mcpServers"][name] = server_config
    save_config(config)
    print(f"Added stdio server '{name}' with command: {command}")


def show_config():
    """Show current config."""
    config = load_config()
    print(json.dumps(config, indent=2))


def main():
    """Simple CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="atomic-mcp",
        description="Simple CLI for atomic-mcp framework"
    )
    parser.add_argument("--version", action="version", version="0.1.2")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Info command
    subparsers.add_parser("info", help="Show framework info")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage claude_desktop_config.json")
    config_subparsers = config_parser.add_subparsers(dest="config_action")
    
    # Show config
    config_subparsers.add_parser("show", help="Show current config")
    
    # Add remote server
    remote_parser = config_subparsers.add_parser("add-remote", help="Add remote MCP server")
    remote_parser.add_argument("name", help="Server name")
    remote_parser.add_argument("url", help="Server URL (e.g., http://localhost:8000/mcp/)")
    
    # Add stdio server
    stdio_parser = config_subparsers.add_parser("add-stdio", help="Add stdio MCP server")
    stdio_parser.add_argument("name", help="Server name")
    stdio_parser.add_argument("command", help="Command to run")
    stdio_parser.add_argument("args", nargs="*", help="Command arguments")
    
    args = parser.parse_args()
    
    if args.command == "info":
        print("atomic-mcp v0.1.2")
        print("MCP Server Framework using Atomic Agents and FastMCP")
    elif args.command == "config":
        if args.config_action == "show":
            show_config()
        elif args.config_action == "add-remote":
            add_remote_server(args.name, args.url)
        elif args.config_action == "add-stdio":
            add_stdio_server(args.name, args.command, args.args if args.args else None)
        else:
            config_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()