# zapr-mcp

Zapr WhatsApp MCP Server - Send WhatsApp messages from Claude Desktop and other MCP-compatible LLMs.

## Installation

```bash
pip install zapr-mcp
```

Or with uv (recommended):
```bash
uv run --with zapr-mcp zapr-mcp
```

## Configuration

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "zapr-whatsapp": {
      "command": "uv",
      "args": ["run", "--with", "zapr-mcp", "zapr-mcp"],
      "env": {
        "ZAPR_SESSION_ID": "your-session-id-here",
        "ZAPR_API_HOST": "https://api.zapr.link"
      }
    }
  }
}
```

## Features

- ✅ Send WhatsApp messages to single or multiple recipients
- ✅ Validate phone numbers
- ✅ Check session status
- ✅ Automatic session authentication
- ✅ Rate limiting support
- ✅ Full MCP protocol compliance

## Tools Available

- `send_whatsapp` - Send a message to a single number
- `bulk_send_whatsapp` - Send messages to multiple numbers
- `get_session_status` - Check WhatsApp session status
- `validate_number` - Validate if a number is on WhatsApp

## Requirements

- Python 3.10+
- Active zapr.link session
- Claude Desktop or any MCP-compatible client

## Support

For support, visit [zapr.link](https://zapr.link) or contact support@zapr.link

## License

MIT