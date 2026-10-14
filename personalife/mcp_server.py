"""Model Context Protocol (MCP) server for PersonaLife.
Allows Claude Desktop, OpenCode, Antigravity, and MCP-compatible chat apps to interact with simulated personas.
Supports standard JSON-RPC 2.0 over Stdio.
"""
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from .service import PersonaLife
from .prompt import render_roleplay_prompt
from .clock import instant

logger = logging.getLogger("personalife.mcp")

def get_tools_definition():
    return [
        {
            "name": "get_roleplay_prompt",
            "description": "Returns an immersive, fully formatted system prompt for roleplaying with a living persona. Automatically brings simulated time to the present and includes current location, activity, mood, and memories.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "persona_id": {
                        "type": "string",
                        "description": "Identifier of the persona (e.g., 'jenna')."
                    },
                    "auto_advance": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to automatically fast-forward the persona's life to current real-world time."
                    }
                },
                "required": ["persona_id"]
            }
        },
        {
            "name": "get_persona_state",
            "description": "Retrieves the current detailed state, location, and ongoing activity of the persona.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "persona_id": {
                        "type": "string",
                        "description": "Identifier of the persona."
                    },
                    "auto_advance": {
                        "type": "boolean",
                        "default": True,
                        "description": "Fast-forward simulation to current real-time."
                    }
                },
                "required": ["persona_id"]
            }
        },
        {
            "name": "record_chat_interaction",
            "description": "Records a conversation session with the persona into its persistent ledger and memory.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "persona_id": {
                        "type": "string",
                        "description": "Identifier of the persona."
                    },
                    "summary": {
                        "type": "string",
                        "description": "Concise summary of what was discussed and experienced in the chat."
                    },
                    "duration_minutes": {
                        "type": "number",
                        "default": 10,
                        "description": "Approximate duration of the conversation in minutes."
                    }
                },
                "required": ["persona_id", "summary"]
            }
        },
        {
            "name": "search_memories",
            "description": "Searches both episodic and long-term memories of the persona.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "persona_id": {
                        "type": "string",
                        "description": "Identifier of the persona."
                    },
                    "query": {
                        "type": "string",
                        "default": "",
                        "description": "Keyword to filter memories."
                    }
                },
                "required": ["persona_id"]
            }
        },
        {
            "name": "advance_time",
            "description": "Explicitly advances canonical simulation time for the persona to a target timestamp.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "persona_id": {
                        "type": "string",
                        "description": "Identifier of the persona."
                    },
                    "to_time": {
                        "type": "string",
                        "description": "ISO timestamp to advance to. Defaults to now."
                    }
                },
                "required": ["persona_id"]
            }
        }
    ]

class MCPServer:
    def __init__(self, database="personalife.sqlite3", memory=None):
        self.database = database
        self.memory = memory

    def handle_tool_call(self, name, arguments):
        pid = arguments.get("persona_id")
        if not pid:
            raise ValueError("persona_id is required")

        with PersonaLife(self.database, memory=self.memory) as app:
            if name == "get_roleplay_prompt":
                auto_advance = arguments.get("auto_advance", True)
                now_dt = datetime.now(timezone.utc) if auto_advance else None
                ctx = app.get_persona_context(pid, now=now_dt)
                state = app._s(pid)
                prompt_text = render_roleplay_prompt(ctx, state.get("persona"))
                return prompt_text

            elif name == "get_persona_state":
                auto_advance = arguments.get("auto_advance", True)
                if auto_advance:
                    app.advance_to(pid, datetime.now(timezone.utc))
                return app.get_current_state(pid)

            elif name == "record_chat_interaction":
                summary = arguments.get("summary", "")
                mins = max(1.0, float(arguments.get("duration_minutes", 10)))
                from datetime import timedelta
                cur = instant(app._s(pid)["cursor"])
                now_utc = datetime.now(timezone.utc)
                start = max(cur, now_utc)
                end = start + timedelta(minutes=mins)
                result = app.apply_chat_event(pid, start, end, summary)
                return result

            elif name == "search_memories":
                q = arguments.get("query", "")
                return app.get_memories(pid, query=q)

            elif name == "advance_time":
                to_time = arguments.get("to_time") or datetime.now(timezone.utc)
                return app.advance_to(pid, to_time)

            else:
                raise ValueError(f"Unknown tool: {name}")

    def process_message(self, msg):
        method = msg.get("method")
        msg_id = msg.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "personalife-mcp",
                        "version": "1.2.0"
                    }
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": get_tools_definition()
                }
            }

        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                result_data = self.handle_tool_call(tool_name, tool_args)
                if isinstance(result_data, str):
                    text_content = result_data
                else:
                    text_content = json.dumps(result_data, ensure_ascii=False, indent=2)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": text_content}
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": f"Error: {str(e)}"}
                        ],
                        "isError": True
                    }
                }

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        else:
            if msg_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            return None

    def run_stdio(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                response = self.process_message(msg)
                if response is not None:
                    sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="PersonaLife MCP Server")
    parser.add_argument("--db", default="personalife.sqlite3", help="SQLite database path")
    args = parser.parse_args()
    server = MCPServer(database=args.db)
    server.run_stdio()

if __name__ == "__main__":
    main()
