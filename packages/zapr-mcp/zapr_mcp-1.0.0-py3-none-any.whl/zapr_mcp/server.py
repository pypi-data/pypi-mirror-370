#!/usr/bin/env python3
"""
Zapr WhatsApp MCP Server
A Model Context Protocol server for WhatsApp messaging via zapr.link
"""

import asyncio
import os
import sys
import json
import aiohttp
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    Prompt,
    PromptArgument
)

# Server info
SERVER_NAME = "zapr-whatsapp-mcp"
SERVER_VERSION = "1.0.0"

class ZaprMCPServer:
    def __init__(self):
        self.api_host = os.getenv("ZAPR_API_HOST", "https://api.zapr.link")
        self.session_id = os.getenv("ZAPR_SESSION_ID")
        
        if not self.session_id:
            raise ValueError("ZAPR_SESSION_ID environment variable is required")
        
        # Create MCP server
        self.server = Server(SERVER_NAME)
        
        # Register handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="send_whatsapp",
                    description="Send a WhatsApp message to a single number",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "number": {
                                "type": "string",
                                "description": "Recipient phone number (international format)"
                            },
                            "message": {
                                "type": "string", 
                                "description": "Message content to send"
                            }
                        },
                        "required": ["number", "message"]
                    }
                ),
                Tool(
                    name="bulk_send_whatsapp",
                    description="Send WhatsApp messages to multiple numbers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "numbers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of recipient phone numbers"
                            },
                            "message": {
                                "type": "string",
                                "description": "Message content to send"
                            }
                        },
                        "required": ["numbers", "message"]
                    }
                ),
                Tool(
                    name="get_session_status",
                    description="Check the status of a WhatsApp session",
                    inputSchema={
                        "type": "object", 
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="validate_number",
                    description="Check if a number is valid on WhatsApp",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "number": {
                                "type": "string",
                                "description": "Phone number to validate"
                            }
                        },
                        "required": ["number"]
                    }
                ),
                Tool(
                    name="send_message_with_reply",
                    description="Send a WhatsApp message and wait for reply",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "number": {
                                "type": "string",
                                "description": "Recipient phone number"
                            },
                            "message": {
                                "type": "string",
                                "description": "Message to send"
                            },
                            "num_replies": {
                                "type": "integer",
                                "description": "Number of replies to wait for (1-3)",
                                "default": 1
                            },
                            "timeout_secs": {
                                "type": "integer",
                                "description": "Timeout in seconds (default 60)",
                                "default": 60
                            }
                        },
                        "required": ["number", "message"]
                    }
                ),
                Tool(
                    name="get_recent_messages",
                    description="Get recent WhatsApp messages from the session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of messages to retrieve (default 10)",
                                "default": 10
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="list_prompts",
                    description="List all available prompt templates for WhatsApp messaging",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list:
            """Handle tool calls"""
            try:
                # Always add sessionId to arguments if not present
                if "sessionId" not in arguments:
                    arguments["sessionId"] = self.session_id
                
                if name == "send_whatsapp":
                    return await self._send_whatsapp(arguments)
                elif name == "bulk_send_whatsapp":
                    return await self._bulk_send_whatsapp(arguments)
                elif name == "get_session_status":
                    return await self._get_session_status()
                elif name == "validate_number":
                    return await self._validate_number(arguments)
                elif name == "send_message_with_reply":
                    return await self._send_reply(arguments)
                elif name == "get_recent_messages":
                    return await self._get_recent_messages(arguments)
                elif name == "list_prompts":
                    return await self._list_prompts_tool()
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="zapr://session/status",
                    name="Session Status",
                    description="Current WhatsApp session status and statistics",
                    mimeType="application/json"
                ),
                Resource(
                    uri="zapr://session/info",
                    name="Session Information",
                    description="Detailed session information including limits and plan",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific resource"""
            if uri == "zapr://session/status":
                status = await self._get_session_status()
                return status[0].text
            elif uri == "zapr://session/info":
                return json.dumps({
                    "session_id": self.session_id,
                    "api_host": self.api_host,
                    "status": "connected",
                    "plan": "free",
                    "limits": {
                        "mcp_daily": 5,
                        "api_daily": 10
                    }
                })
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_prompts()
        async def list_prompts():
            """List available prompts"""
            print("DEBUG: list_prompts called!", file=sys.stderr)
            return [
                Prompt(
                    name="send_message",
                    description="Send a WhatsApp message to a contact",
                    arguments=[
                        PromptArgument(
                            name="number",
                            description="The recipient's phone number",
                            required=True
                        ),
                        PromptArgument(
                            name="message", 
                            description="The message content",
                            required=True
                        )
                    ]
                ),
                Prompt(
                    name="bulk_message",
                    description="Send the same message to multiple WhatsApp contacts",
                    arguments=[
                        PromptArgument(
                            name="numbers",
                            description="Comma-separated list of phone numbers",
                            required=True
                        ),
                        PromptArgument(
                            name="message",
                            description="The message content", 
                            required=True
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict):
            """Get a specific prompt"""
            if name == "send_message":
                number = arguments.get("number", "+1234567890")
                message = arguments.get("message", "Hello from Zapr!")
                return {
                    "description": "Send a WhatsApp message to a contact",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": f"Please send the following WhatsApp message:\n\nTo: {number}\nMessage: {message}\n\nUse the send_whatsapp tool to send this message."
                            }
                        }
                    ]
                }
            elif name == "bulk_message":
                numbers = arguments.get("numbers", "+1234567890,+0987654321")
                message = arguments.get("message", "Hello from Zapr!")
                numbers_list = [n.strip() for n in numbers.split(",")]
                return {
                    "description": "Send the same message to multiple WhatsApp contacts",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text", 
                                "text": f"Please send the following message to multiple contacts:\n\nTo: {', '.join(numbers_list)}\nMessage: {message}\n\nUse the bulk_send_whatsapp tool to send this message."
                            }
                        }
                    ]
                }
            else:
                raise ValueError(f"Unknown prompt: {name}")
    
    async def _send_whatsapp(self, args: dict) -> list:
        """Send single WhatsApp message"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "send_whatsapp",
                "arguments": {
                    "sessionId": self.session_id,
                    "number": args["number"],
                    "message": args["message"]
                }
            }
        }
        
        result = await self._call_api(payload)
        return [TextContent(type="text", text=str(result))]
    
    async def _bulk_send_whatsapp(self, args: dict) -> list:
        """Send bulk WhatsApp messages"""
        payload = {
            "jsonrpc": "2.0", 
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "bulk_send_whatsapp",
                "arguments": {
                    "sessionId": self.session_id,
                    "numbers": args["numbers"],
                    "message": args["message"]
                }
            }
        }
        
        result = await self._call_api(payload)
        return [TextContent(type="text", text=str(result))]
    
    async def _get_session_status(self) -> list:
        """Get session status"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1, 
            "method": "tools/call",
            "params": {
                "name": "get_session_status",
                "arguments": {
                    "sessionId": self.session_id
                }
            }
        }
        
        result = await self._call_api(payload)
        return [TextContent(type="text", text=str(result))]
    
    async def _validate_number(self, args: dict) -> list:
        """Validate phone number"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call", 
            "params": {
                "name": "validate_number",
                "arguments": {
                    "sessionId": self.session_id,
                    "number": args["number"]
                }
            }
        }
        
        result = await self._call_api(payload)
        return [TextContent(type="text", text=str(result))]
    
    async def _send_reply(self, args: dict) -> list:
        """Send message and wait for reply"""
        # Prepare request for message-with-reply endpoint
        number = args["number"]
        message = args["message"]
        num_replies = args.get("num_replies", 1)
        timeout_secs = args.get("timeout_secs", 60)
        
        # Call the message-with-reply endpoint directly
        session_id = self.session_id
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_host}/message-with-reply/{session_id}",
                json={
                    "number": number,
                    "message": message,
                    "num_replies": num_replies,
                    "timeout_secs": timeout_secs
                },
                headers={
                    "Content-Type": "application/json",
                    "X-MCP-Request": "true"
                },
                timeout=aiohttp.ClientTimeout(total=timeout_secs + 10)  # Add buffer to timeout
            ) as response:
                if response.status == 200:
                    try:
                        result = await response.json()
                        # Format the reply nicely
                        if isinstance(result, dict) and result.get("replies"):
                            replies_text = "\n\n📩 Replies received:\n"
                            for i, reply in enumerate(result["replies"], 1):
                                # reply is a string, not an object
                                replies_text += f"{i}. {reply}\n"
                            return [TextContent(type="text", text=f"✅ Message sent to {number}\n{replies_text}")]
                        else:
                            return [TextContent(type="text", text=f"✅ Message sent to {number}\n⏰ No replies received within {timeout_secs} seconds")]
                    except Exception as e:
                        return [TextContent(type="text", text=f"❌ Failed to parse response: {str(e)}")]
                else:
                    error_text = await response.text()
                    return [TextContent(type="text", text=f"❌ Failed to send message: {error_text}")]
    
    async def _get_recent_messages(self, args: dict) -> list:
        """Get recent messages from the session"""
        limit = args.get("limit", 10)
        session_id = self.session_id
        
        # Call the messages API to get recent messages
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_host}/{session_id}/recent-messages",
                params={"limit": limit},
                headers={
                    "X-MCP-Request": "true"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data and response_data.get("messages"):
                        messages = response_data["messages"]
                        messages_text = f"📱 Recent {len(messages)} messages:\n\n"
                        for msg in messages:
                            timestamp = msg.get("timestamp", "")
                            from_number = msg.get("number", "Unknown")  # Fixed: use "number" field
                            message_text = msg.get("message", "")
                            is_from_me = msg.get("is_from_me", False)
                            
                            sender = "You" if is_from_me else from_number
                            messages_text += f"[{timestamp}] {sender}: {message_text}\n"
                        
                        return [TextContent(type="text", text=messages_text)]
                    else:
                        return [TextContent(type="text", text="📱 No recent messages found")]
                else:
                    return [TextContent(type="text", text=f"❌ Failed to get messages: HTTP {response.status}")]
    
    async def _list_prompts_tool(self) -> list:
        """List all available prompt templates as a tool function"""
        prompts_info = """# 📋 zapr-whatsapp MCP Functions & Examples

| Function | Natural Prompt Example |
|----------|------------------------|
| `send_whatsapp` | "Send a WhatsApp message to +5521981328933 saying 'Hello from zapr!'" |
| `bulk_send_whatsapp` | "Send 'Meeting at 3pm today' to these contacts: +5521981328933, +5521988570927" |
| `send_message_with_reply` | "Ask +5521981328933 'What's your favorite color?' and wait for their response" |
| `get_recent_messages` | "Show me the last 10 WhatsApp messages from this session" |
| `get_session_status` | "Check if my WhatsApp Web connection is active" |
| `validate_number` | "Is +5521981328933 a valid WhatsApp number?" |
| `list_prompts` | "What functions are available in the WhatsApp MCP server?" |

**Prompt Templates**: `send_message`, `bulk_message` - Generate structured instructions for messaging workflows."""
        
        return [TextContent(type="text", text=prompts_info)]
    
    async def _call_api(self, payload: dict) -> dict:
        """Call Zapr API with MCP request"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_host}/mcp",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-MCP-Request": "true",
                    "X-Session-ID": self.session_id
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error {response.status}: {await response.text()}")

async def main():
    """Main entry point"""
    try:
        print("DEBUG: Starting Zapr MCP Server...", file=sys.stderr)
        server = ZaprMCPServer()
        print("DEBUG: MCP Server initialized successfully", file=sys.stderr)
        
        # Run stdio server
        async with stdio_server() as (read_stream, write_stream):
            await server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=SERVER_NAME,
                    server_version=SERVER_VERSION,
                    capabilities=server.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    asyncio.run(main())