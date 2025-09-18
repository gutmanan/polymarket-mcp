# Polymarket MCP Server

A [Model Context Protocol][mcp] (MCP) server for Polymarket's CLOB (Central Limit Order Book) API.

This provides access to Polymarket's prediction markets, order books, trading functionality, and market data through standardized MCP interfaces, allowing AI assistants to query market data, analyze prediction markets, and execute trades.

[mcp]: https://modelcontextprotocol.io

## ⚠️ Security Notice

This server requires a **private key** to interact with the Polymarket CLOB API for trading functionality. Please ensure:

- Never commit your private key to version control
- Use a dedicated wallet with limited funds for testing
- Store your private key securely (consider using environment variables or secure key management)
- Be aware that this gives the MCP server the ability to execute trades on your behalf

## Features

- [x] Market data access via CLOB API
  - [x] List all available markets with filtering options
  - [x] Search markets by question text
  - [x] Get real-time order book data
  - [x] Get mid prices and current prices
  - [x] Filter markets by active/live status

- [x] Trading functionality
  - [x] Place limit orders
  - [x] Place market orders
  - [x] Check USDC wallet balance

- [x] Docker containerization support

- [x] Provide interactive tools for AI assistants

The list of tools is configurable, so you can choose which tools you want to make available to the MCP client.
This is useful if you don't use certain functionality or if you don't want to take up too much of the context window.

## Connecting to Claude Desktop on Mac

### Prerequisites

Before setting up the Polymarket MCP server with Claude Desktop, ensure you have:

1. **Claude Desktop App**: Download and install from [Claude.ai](https://claude.ai/download)
2. **Python 3.10+**: Check with `python3 --version`
3. **UV Package Manager**: Install with:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
4. **Polymarket Wallet**: A wallet with some USDC for trading (optional, required only for trading features)

### Step 1: Clone and Setup the Project

```bash
# Clone the repository
git clone <repository-url>
cd polymarket-mcp

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Step 2: Configure Environment Variables

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Edit the `.env` file with your configuration:
   ```bash
   nano .env
   ```

3. Add your configuration (replace with your actual values):
   ```env
   # Polymarket CLOB API Configuration
   CLOB_HOST=https://clob.polymarket.com
   RPC_URL=https://polygon-rpc.com
   
   # Required for wallet operations and order signing
   # Replace with your actual private key (without 0x prefix)
   PRIVATE_KEY=your_private_key_here
   
   # Optional CLOB API credentials (will be auto-generated if not provided)
   # CLOB_API_KEY=
   # CLOB_SECRET=
   # CLOB_PASS_PHRASE=
   ```

### Step 3: Test the Server

Before configuring Claude Desktop, test that the server works:

```bash
# Activate virtual environment if not already active
source .venv/bin/activate

# Run the server directly to test
python -m polymarket_mcp_server.server
```

The server should start without errors. Press `Ctrl+C` to stop it.

### Step 4: Configure Claude Desktop

1. **Locate Claude Desktop Configuration**:
   On Mac, the configuration file is located at:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. **Create or Edit Configuration File**:
   If the file doesn't exist, create it:
   ```bash
   mkdir -p ~/Library/Application\ Support/Claude
   touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

3. **Add Server Configuration**:
   Open the configuration file in your preferred editor:
   ```bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

   Add the following configuration (replace `<FULL_PATH_TO_PROJECT>` with the actual path):
   ```json
   {
     "mcpServers": {
       "polymarket": {
         "command": "uv",
         "args": [
           "run",
           "python",
           "-m",
           "polymarket_mcp_server.server"
         ],
         "cwd": "<FULL_PATH_TO_PROJECT>",
         "env": {
           "CLOB_HOST": "https://clob.polymarket.com",
           "RPC_URL": "https://polygon-rpc.com",
           "PRIVATE_KEY": "your_private_key_here"
         }
       }
     }
   }
   ```

   **Important Notes**:
   - Replace `<FULL_PATH_TO_PROJECT>` with the absolute path to your polymarket-mcp directory
   - Replace `your_private_key_here` with your actual private key
   - You can find the full path with: `pwd` (when in the project directory)

4. **Alternative Configuration (Using .env file)**:
   If you prefer to keep sensitive data in the `.env` file:
   ```json
   {
     "mcpServers": {
       "polymarket": {
         "command": "uv",
         "args": [
           "run",
           "python",
           "-m",
           "polymarket_mcp_server.server"
         ],
         "cwd": "<FULL_PATH_TO_PROJECT>"
       }
     }
   }
   ```

### Step 5: Restart Claude Desktop

1. **Quit Claude Desktop** completely (Cmd+Q or Claude Desktop → Quit)
2. **Reopen Claude Desktop**
3. **Verify Connection**: Look for the Polymarket server in the MCP section or try asking Claude about Polymarket markets

### Step 6: Test the Integration

Once Claude Desktop is running with the MCP server configured, you can test it by asking Claude:

- "What are the current active markets on Polymarket?"
- "Search for markets about the 2024 election"
- "What's the current price for [specific market]?"
- "Show me my USDC balance" (if you have trading configured)

### Troubleshooting

#### Common Issues:

1. **"spawn uv ENOENT" Error**:
   - Ensure `uv` is installed and in your PATH
   - Try using the full path to `uv`: `/usr/local/bin/uv` or find it with `which uv`

2. **Server Not Starting**:
   - Check that all dependencies are installed: `uv pip install -e .`
   - Verify your `.env` file has correct values
   - Test the server manually first

3. **Private Key Issues**:
   - Ensure private key is without `0x` prefix
   - Make sure the wallet has some MATIC for gas fees on Polygon
   - Verify the private key corresponds to a valid Ethereum address

4. **Configuration File Issues**:
   - Ensure JSON syntax is valid (use a JSON validator)
   - Check that file paths are absolute and correct
   - Verify file permissions allow Claude Desktop to read the config

#### Debug Steps:

1. **Check Claude Desktop Logs**:
   - On Mac: `~/Library/Logs/Claude/`
   - Look for error messages related to MCP servers

2. **Test Server Manually**:
   ```bash
   cd /path/to/polymarket-mcp
   source .venv/bin/activate
   python -m polymarket_mcp_server.server
   ```

3. **Verify Environment**:
   ```bash
   # Check if uv is accessible
   which uv
   
   # Check Python version
   python3 --version
   
   # Verify project structure
   ls -la src/polymarket_mcp_server/
   ```

### Docker Alternative

If you prefer using Docker:

1. **Build the Docker Image**:
   ```bash
   docker build -t polymarket-mcp-server .
   ```

2. **Configure Claude Desktop for Docker**:
   ```json
   {
     "mcpServers": {
       "polymarket": {
         "command": "docker",
         "args": [
           "run",
           "--rm",
           "-i",
           "-e", "CLOB_HOST=https://clob.polymarket.com",
           "-e", "RPC_URL=https://polygon-rpc.com",
           "-e", "PRIVATE_KEY=your_private_key_here",
           "polymarket-mcp-server"
         ]
       }
     }
   }
   ```

## Available Tools

| Tool | Category | Description |
| --- | --- | --- |
| `get_markets` | Market Data | Get a list of all available markets from CLOB API with filtering options |
| `get_order_book` | Market Data | Get the current order book for a specific token |
| `get_mid_price` | Market Data | Get the mid price for a specific token based on order book |
| `get_price` | Market Data | Get the current price for a specific token and side (BUY/SELL) |
| `search_markets` | Market Data | Search for markets by question text |
| `place_limit_order` | Trading | Place a limit order on Polymarket |
| `place_market_order` | Trading | Place a market order on Polymarket |
| `get_usdc_balance` | Wallet | Get USDC balance for the configured wallet |

## Development

Contributions are welcome! Please open an issue or submit a pull request if you have any suggestions or improvements.

This project uses [`uv`](https://github.com/astral-sh/uv) to manage dependencies. Install `uv` following the instructions for your platform:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You can then create a virtual environment and install the dependencies with:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
uv pip install -e .
```

### Environment Variables Support

The server loads environment variables from a `.env` file in the project root directory if present. Copy `.env.template` to `.env` and adjust the values as needed.

### Testing

The project includes a comprehensive test suite that ensures functionality and helps prevent regressions.

Run the tests with pytest:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run the tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

Tests are organized into:
- Server functionality tests
- Main application tests
- Error handling tests

When adding new features, please also add corresponding tests.

## Project Structure

The project has been organized with a `src` directory structure:

```
polymarket-mcp/
├── src/
│   └── polymarket_mcp_server/
│       ├── __init__.py      # Package initialization
│       └── server.py        # MCP server implementation
├── Dockerfile               # Docker configuration
├── .env.template            # Template for environment variables
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## License

MIT

---

**Need Help?** 
- Check the [troubleshooting section](#troubleshooting) above
- Review Claude Desktop logs for specific error messages
- Ensure all prerequisites are properly installed
- Test the server manually before configuring Claude Desktop