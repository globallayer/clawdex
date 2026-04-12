# Clawdex VS Code Extension

**Collective AI Coding Agent Brain** - Brings community knowledge directly into your editor.

Every verified fix makes ALL AI agents smarter. Automatic sharing, fully anonymized.

## Features

### Log Errors & Solutions
When you fix a bug, log it to Clawdex so you (and the community) can find it later.

- Right-click on selected text > "Clawdex: Log Error & Solution"
- Or use Command Palette: `Clawdex: Log Error & Solution`

### Find Solutions
When you encounter an error, search the knowledge base for solutions.

- Select error text > Right-click > "Clawdex: Find Solution for Selected Text"
- Or use Command Palette: `Clawdex: Find Solution for Error`

### Auto-Query on Error (Optional)
When enabled, Clawdex automatically searches for solutions when errors appear in the Problems panel.

### Verify Solutions
After applying a solution, verify it worked. Verified solutions are **automatically contributed** to the community brain.

- Command Palette: `Clawdex: Verify Solution Worked`

### Log Decisions & Patterns
Track architectural decisions and reusable patterns:

- `Clawdex: Log Architectural Decision`
- `Clawdex: Log Reusable Pattern`

### Status Bar
Shows current knowledge base stats. Click to view detailed statistics.

## Requirements

1. **Python 3.10+** installed
2. **Clawdex** Python package installed:
   ```bash
   pip install clawdex
   # or
   uv pip install clawdex
   ```

## Installation

### From VSIX (Local)
1. Download the `.vsix` file
2. In VS Code: Extensions > ... > Install from VSIX

### From Source
```bash
cd clawdex/vscode-extension
npm install
npm run compile
```

Then press F5 to launch Extension Development Host.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `clawdex.pythonPath` | `python` | Path to Python executable |
| `clawdex.enableStatusBar` | `true` | Show stats in status bar |
| `clawdex.autoQueryOnError` | `true` | Auto-search when errors detected |
| `clawdex.defaultLanguage` | `""` | Default language context (auto-detected) |
| `clawdex.defaultFramework` | `""` | Default framework context |
| `clawdex.communityEnabled` | `false` | Enable community brain search |

## Commands

| Command | Description |
|---------|-------------|
| `Clawdex: Log Error & Solution` | Log an error and its fix |
| `Clawdex: Find Solution for Error` | Search for solutions |
| `Clawdex: Find Solution for Selected Text` | Search using selected text |
| `Clawdex: Verify Solution Worked` | Mark solution as working |
| `Clawdex: Log Architectural Decision` | Record a decision |
| `Clawdex: Log Reusable Pattern` | Record a pattern |
| `Clawdex: Show Knowledge Base Stats` | View statistics |
| `Clawdex: Refresh Stats` | Refresh status bar |

## How It Works

```
1. You fix an error
   |
   v
2. Log it to Clawdex (secrets auto-redacted)
   |
   v
3. Verify it worked
   |
   v
4. Automatically contributed to community brain (anonymized)
   |
   v
5. Other developers & AI agents can find your solution
```

## Privacy & Security

- **Secret Redaction**: API keys, passwords, tokens are stripped BEFORE storage
- **Anonymization**: Project paths, IPs, emails removed BEFORE sharing
- **Local Encryption**: AES-256 for your private copy
- **Verification Gate**: Only WORKING solutions get shared

## Troubleshooting

### "Command not found" errors
Make sure `clawdex` is installed and accessible from your Python path:
```bash
python -m clawdex stats
```

### No solutions found
The knowledge base grows over time. Start by logging your own fixes!

### Status bar shows "?"
Check that Python and Clawdex are properly installed. View the Output panel (View > Output > Clawdex) for debug info.

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode
npm run watch

# Package extension
npm run package
```

## License

FSL-1.1-Apache-2.0 (Functional Source License)

- Free for personal use
- Free for company internal use
- Free to modify and self-host
- Cannot offer as a competing hosted service
- Becomes Apache 2.0 after 4 years
