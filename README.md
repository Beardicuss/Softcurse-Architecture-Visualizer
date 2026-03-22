# Softcurse Architecture Visualizer

A professional-grade code intelligence platform powered by [GitNexus](https://github.com/abhigyanpatwari/GitNexus). Analyzes and visualizes codebase architectures across **13+ programming languages** with GPU-accelerated WebGL graph rendering, AI-powered chat, impact analysis, and deep dependency tracking.

Built as a WPF desktop app embedding a React + TypeScript web application via WebView2.

## Features

- **13+ Language Support**: C, C++, C#, Go, Java, JavaScript, PHP, Python, Ruby, Rust, Swift, TypeScript, TSX — all parsed via Tree-sitter WASM.
- **Sigma.js WebGL Graph**: GPU-accelerated rendering for 10,000+ node graphs with ForceAtlas2 layout and Leiden community clustering.
- **AI Chat Agent**: Ask questions about your codebase architecture using Google Gemini, OpenAI, Anthropic, or local Ollama models.
- **Impact Analysis**: Click any symbol to see what depends on it — upstream/downstream with confidence scores.
- **Process Flow Tracing**: Trace execution paths from entry points through entire call chains.
- **Community Detection**: Leiden algorithm auto-groups related symbols into functional clusters.
- **Cypher Queries**: Advanced users can query the LadybugDB graph database directly.
- **File Tree Browser**: Navigate your codebase with an interactive file tree and source code viewer.
- **Hybrid Search**: Combine BM25 text search with vector similarity for semantic code search.
- **Wiki Generation**: Auto-generate documentation from your codebase structure.
- **Mermaid Diagrams**: Render architecture diagrams directly in the app.
- **Cyberpunk Theme**: Deep black (#020202), cyan (#0ff), neon blue (#08f) Softcurse aesthetic.

## Quick Start

1. **Launch** `ArchitectureVisualizerApp.exe`.
2. **Load a Project**: Drag & drop a ZIP file, enter a GitHub repo URL, or connect to a GitNexus server.
3. **Explore**: The interactive graph renders automatically with community clustering and dependency edges.
4. **AI Chat**: Click the chat panel, configure your API key in ⚙️ Settings, and ask questions about your code.

## AI Configuration

The app supports multiple LLM providers for the AI chat feature:

| Provider | Setup |
|---|---|
| **Google Gemini** (recommended) | Free tier at [aistudio.google.com](https://aistudio.google.com/) |
| **Ollama** (local) | Install from [ollama.com](https://ollama.com/), no API key needed |
| **OpenAI** | Requires API key from [platform.openai.com](https://platform.openai.com/) |
| **Anthropic** | Requires API key from [console.anthropic.com](https://console.anthropic.com/) |
| **OpenRouter** | Multi-model access at [openrouter.ai](https://openrouter.ai/) |

Configure via ⚙️ Settings in the title bar. API keys are stored locally and never sent anywhere except the LLM provider.

## Development

### Prerequisites
- .NET 8.0 SDK
- Node.js 18+

### Build the Web App
```powershell
cd ArchitectureVisualizerApp/Assets/WebApp
npm install
npm run build
```

### Build the Desktop App
```powershell
cd ArchitectureVisualizerApp
dotnet build
dotnet run
```

### Publish Installer
```powershell
dotnet publish -c Release -r win-x64 --self-contained true /p:PublishSingleFile=true -o publish
# Then compile analyzer.iss with Inno Setup
```

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop Shell | WPF + WebView2 (.NET 8) |
| Web App | Vite + React + TypeScript |
| Graph Rendering | Sigma.js + graphology + ForceAtlas2 |
| Code Parsing | Tree-sitter WASM (13 languages) |
| Graph Database | LadybugDB WASM |
| AI Agent | LangChain (multi-provider) |
| Community Detection | Leiden Algorithm |
| Search | MiniSearch (BM25) + HuggingFace Embeddings |
| Installer | Inno Setup |

## License

Softcurse Proprietary — All Rights Reserved.
