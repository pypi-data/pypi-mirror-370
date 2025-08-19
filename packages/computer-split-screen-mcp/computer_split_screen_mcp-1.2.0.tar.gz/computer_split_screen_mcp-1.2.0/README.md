# Computer Split Screen MCP

Cross-platform MCP server that exposes split-screen tools (halves, quadrants, thirds) plus maximize/minimize for both Windows and macOS.  
Works with MCP clients via `uvx`.

## Features

- **Cross-platform support**: Windows and macOS
- **Split-screen layouts**: Halves, quadrants, thirds, and two-thirds variations
- **Window controls**: Maximize and minimize
- **MCP integration**: Full Model Context Protocol server support

## Install / Run via MCP client

Configure your MCP client:

```json
{
  "mcpServers": {
    "computer-split-screen": {
      "command": "uvx",
      "args": ["computer-split-screen-mcp"],
      "env": {}
    }
  }
}
```

## Available Tools

- `left-half` - Snap current window to left half
- `right-half` - Snap current window to right half
- `top-half` - Snap current window to top half
- `bottom-half` - Snap current window to bottom half
- `top-left` - Top-left quadrant
- `top-right` - Top-right quadrant
- `bottom-left` - Bottom-left quadrant
- `bottom-right` - Bottom-right quadrant
- `left-third` - Left third (1/3)
- `middle-third` - Middle third (1/3)
- `right-third` - Right third (1/3)
- `left-two-thirds` - Left two-thirds (2/3)
- `right-two-thirds` - Right two-thirds (2/3)
- `maximize` - OS maximize (bordered)
- `fullscreen` - Fullscreen (no borders via macOS)(bordered via Windows)
- `minimize` - Minimize window

## Platform Dependencies

- **Windows**: Requires `pywin32>=306`
- **macOS**: No additional dependencies required (uses built-in AppleScript)
