# Softcurse Architecture Visualizer — User Guide

This guide explains how to use the visualizer to explore, analyze, and understand your codebase architecture.

## 1. Getting Started

1. Open **ArchitectureVisualizerApp.exe**.
2. You'll see the **DropZone** — the project input screen.

### Loading a Project

You have three ways to load a project:

| Method | How |
|---|---|
| **ZIP Upload** | Drag & drop a `.zip` file onto the DropZone |
| **GitHub URL** | Paste a GitHub repository URL (e.g., `https://github.com/user/repo`) |
| **GitNexus Server** | Connect to a running `gitnexus serve` instance |

## 2. Exploring the Graph

After loading, the interactive knowledge graph renders automatically.

- **Pan**: Click and drag the canvas background.
- **Zoom**: Scroll the mouse wheel.
- **Select Node**: Click any node to see its details in the right panel.
- **Community Colors**: Nodes are automatically colored by functional community (Leiden algorithm).
- **Edge Types**: Lines represent dependencies — imports, calls, extends, and implements.

### Graph Controls

- **File Tree** (left panel): Browse your codebase folder structure. Click a file to focus it in the graph.
- **Right Panel**: Shows node details, code references, and the AI chat tab.
- **Status Bar** (bottom): Shows indexing progress and graph statistics.

## 3. AI Chat

The AI chat lets you ask natural language questions about your codebase architecture.

### Setup
1. Click the **⚙️** icon in the title bar.
2. Select your AI provider (Google Gemini recommended — free tier).
3. Paste your API key and click Save.

### Example Questions
- "What depends on the UserService class?"
- "Show me the execution flow for authentication"
- "What would break if I rename this function?"
- "Find all functions related to database access"
- "Which modules have the highest coupling?"

The AI agent uses **Graph RAG** — it queries the knowledge graph directly, so it understands your entire codebase structure, not just individual files.

## 4. Impact Analysis

Click any symbol node to see its **360° context**:

- **Incoming**: What calls/imports this symbol (upstream dependencies).
- **Outgoing**: What this symbol calls/imports (downstream dependencies).
- **Processes**: Execution flows that pass through this symbol.
- **Confidence Scores**: How confident the analysis is about each relationship.

## 5. Cypher Queries

For advanced analysis, use the **Query** button to write direct Cypher queries against the graph database.

Example queries:
```cypher
-- Find all functions in a file
MATCH (f:File {name: 'main.ts'})-[:CodeRelation {type: 'DEFINES'}]->(fn:Function)
RETURN fn.name, fn.startLine

-- Find what imports a specific file
MATCH (f:File)-[:CodeRelation {type: 'IMPORTS'}]->(target:File {name: 'utils.ts'})
RETURN f.name, f.filePath

-- Find the most connected nodes
MATCH (n)-[r:CodeRelation]-()
RETURN n.name, labels(n)[0] AS type, count(r) AS connections
ORDER BY connections DESC
LIMIT 10
```

## 6. Supported Languages

The Tree-sitter WASM parsers support deep analysis for:

C, C++, C#, Go, Java, JavaScript, PHP, Python, Ruby, Rust, Swift, TypeScript, TSX

Each language gets full import resolution, call chain tracing, class inheritance detection, and constructor inference.

## 7. Settings

Click **⚙️** in the title bar to configure:

- **AI Provider**: Choose between Google Gemini, OpenAI, Anthropic, Ollama, OpenRouter, or MiniMax.
- **Model Selection**: Pick the specific model for each provider.
- **Temperature**: Control AI response creativity (lower = more precise).
- **Intelligent Clustering**: Enable LLM-powered semantic cluster naming.
