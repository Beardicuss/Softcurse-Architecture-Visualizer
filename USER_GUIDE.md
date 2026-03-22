<p align="center">
  <img src="ArchitectureVisualizerApp/Assets/ui/arch.png" alt="Softcurse Architecture Visualizer" width="120" />
</p>

<h1 align="center">User Guide</h1>

<p align="center">
  <em>Complete guide to exploring, analyzing, and understanding your codebase architecture</em>
</p>

---

## Table of Contents

1. [Installation](#1-installation)
2. [Loading a Project](#2-loading-a-project)
3. [Navigating the Graph](#3-navigating-the-graph)
4. [File Tree Browser](#4-file-tree-browser)
5. [Node Inspector & Impact Analysis](#5-node-inspector--impact-analysis)
6. [AI Chat](#6-ai-chat)
7. [Cypher Query Console](#7-cypher-query-console)
8. [Process Flow Tracing](#8-process-flow-tracing)
9. [Search](#9-search)
10. [Settings & Configuration](#10-settings--configuration)
11. [Supported Languages](#11-supported-languages)
12. [Keyboard Shortcuts](#12-keyboard-shortcuts)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Installation

### From Installer
1. Download and run `SoftcurseArchitectureVisualizerSetup_v2.0.0.exe`.
2. Follow the setup wizard — choose install directory and desktop shortcut preference.
3. Launch from the Start Menu or Desktop.

### From Source
See the [README.md](README.md) for build-from-source instructions.

### System Requirements
| Component | Minimum |
|---|---|
| OS | Windows 10 (version 1809+) |
| RAM | 4 GB |
| GPU | Any GPU with WebGL 2.0 support |
| Disk | 500 MB (application) + space for indexed projects |

---

## 2. Loading a Project

When the app launches, you'll see the **DropZone** — the project input screen. There are two methods to load a codebase:

### Method A: ZIP Upload
1. Compress your project root into a `.zip` file.
2. Drag and drop the ZIP onto the DropZone, or click to browse.
3. The indexing pipeline will begin immediately.

### Method B: GitHub Repository
1. Click the **GitHub** tab in the DropZone.
2. Paste a public repository URL (e.g., `https://github.com/user/repo`).
3. The app will clone the repo in-browser and start indexing.

### Indexing Pipeline
The progress overlay shows six phases:

| Phase | Description |
|---|---|
| **Extracting** | Unpacking ZIP or cloning repository |
| **Parsing** | Tree-sitter WASM parses each file into an AST |
| **Structures** | Extracting classes, functions, methods, interfaces |
| **Relationships** | Resolving imports, calls, inheritance |
| **Communities** | Leiden algorithm groups related symbols |
| **Database** | Loading nodes and edges into LadybugDB |

Typical indexing time: **5–30 seconds** depending on project size.

---

## 3. Navigating the Graph

After indexing completes, the interactive knowledge graph renders automatically.

### Mouse Controls
| Action | Control |
|---|---|
| **Pan** | Click and drag the canvas background |
| **Zoom** | Scroll the mouse wheel |
| **Select node** | Click any node |
| **Drag node** | Click and drag a node to reposition it |

### Visual Encoding
- **Node size** — Proportional to the number of connections (more connected = larger)
- **Node color** — Determined by community cluster (Leiden algorithm groups related symbols)
- **Edge color** — Matches the source node's community color
- **Edge thickness** — Indicates relationship type weight

### Node Types
| Color | Type | Description |
|---|---|---|
| 🔵 Blue | File | Source code files |
| 🟤 Cyan | Folder | Directory structure |
| 🟡 Yellow | Class | Class definitions |
| 🟢 Green | Function | Standalone functions |
| 🟣 Pink | Interface | Interfaces and type definitions |
| 🔷 Teal | Method | Class methods |

---

## 4. File Tree Browser

The **left panel** displays your project's folder structure as a collapsible tree.

- **Click a folder** to expand/collapse its contents
- **Click a file** to focus the graph on that file's node and highlight its connections
- File counts and nesting depth are shown for each directory
- The tree automatically reflects the indexed project structure

---

## 5. Node Inspector & Impact Analysis

Click any node in the graph to open the **Right Panel** showing its 360° context:

### Details Tab
- **Name** — Symbol name
- **Type** — File, Class, Function, Method, Interface
- **File Path** — Location in the project
- **Line Range** — Start and end lines in the source file
- **Source Code** — Extracted code content

### Connections
- **Incoming** — Who calls/imports this symbol (upstream dependencies)
- **Outgoing** — What this symbol calls/imports (downstream dependencies)
- **Confidence Score** — How certain the analysis is about each relationship

### Impact Analysis
Click any connected node to trace the ripple effect through your architecture. This answers:
- *"What would break if I change this function?"*
- *"How deeply is this class coupled into the system?"*

---

## 6. AI Chat

The AI chat tab in the Right Panel lets you ask natural language questions about your codebase.

### Setup
1. Click the **⚙️** icon in the title bar.
2. Select your AI provider (Google Gemini is recommended — has a generous free tier).
3. Paste your API key.
4. Choose a model (e.g., `gemini-2.0-flash`).
5. Click **Save**.

### How It Works
The AI agent uses **Graph RAG** (Retrieval-Augmented Generation):
1. Your question is analyzed to determine which tools are needed.
2. The agent queries the LadybugDB knowledge graph using Cypher.
3. Relevant code symbols, relationships, and source code are retrieved.
4. The LLM synthesizes an answer grounded in your actual codebase.

### Example Queries

| Category | Example |
|---|---|
| **Dependencies** | "What modules depend on the DatabaseService class?" |
| **Architecture** | "Which components have the highest coupling?" |
| **Flow tracing** | "Trace the execution flow from the login handler" |
| **Impact** | "What would break if I rename the fetchData function?" |
| **Discovery** | "Find all classes related to authentication" |
| **Explanation** | "Explain the relationship between UserController and AuthMiddleware" |

### Tips
- Be specific — mention exact symbol names when possible
- The agent can execute multiple tools in sequence to build complex answers
- Ask follow-up questions — the chat history provides context

---

## 7. Cypher Query Console

For advanced analysis, use the **Query** floating button to write direct Cypher queries against the graph database.

### Example Queries

**Find all functions in a file:**
```cypher
MATCH (f:File {name: 'main.ts'})-[:CodeRelation {type: 'DEFINES'}]->(fn:Function)
RETURN fn.name, fn.startLine, fn.endLine
```

**Find what imports a specific file:**
```cypher
MATCH (f:File)-[:CodeRelation {type: 'IMPORTS'}]->(target:File {name: 'utils.ts'})
RETURN f.name, f.filePath
```

**Find the most connected nodes:**
```cypher
MATCH (n)-[r:CodeRelation]-()
RETURN n.name, labels(n)[0] AS type, count(r) AS connections
ORDER BY connections DESC
LIMIT 10
```

**Find circular dependencies:**
```cypher
MATCH (a:File)-[:CodeRelation {type: 'IMPORTS'}]->(b:File)-[:CodeRelation {type: 'IMPORTS'}]->(a)
RETURN a.name, b.name
```

**Find orphan functions (never called):**
```cypher
MATCH (fn:Function)
WHERE NOT ()-[:CodeRelation {type: 'CALLS'}]->(fn)
RETURN fn.name, fn.filePath
LIMIT 20
```

---

## 8. Process Flow Tracing

The **Processes** panel identifies high-level execution flows through your codebase:

1. Click the **Processes** tab in the Right Panel.
2. View detected entry points and their execution chains.
3. Click a process to see a **Mermaid flowchart** of the full call chain.
4. Expand to full-screen for complex flows.

Entry points are scored by their role in the codebase — HTTP handlers, main functions, event listeners, and CLI entry points are ranked highest.

---

## 9. Search

The **search bar** in the header provides hybrid search:

- **Text search** — BM25-based keyword matching across symbol names and file paths
- **Semantic search** — Vector similarity using HuggingFace embeddings (when embeddings are built)
- Results are ranked by combined relevance score
- Click a result to focus the graph on that node

Embeddings are built automatically in the background after indexing. The first run may take a minute; subsequent searches are instant.

---

## 10. Settings & Configuration

Click **⚙️** in the title bar to access settings:

### AI Provider
- Select from: **Google Gemini**, **OpenAI**, **Anthropic**, **Ollama**, **OpenRouter**, **MiniMax**
- Enter API key and select model
- Adjust **temperature** (0.0 = deterministic, 1.0 = creative)
- Set **max tokens** for response length

### Graph Display
- Toggle community clustering visibility
- Adjust layout simulation parameters
- Configure edge rendering style

### Intelligent Clustering
- Enable LLM-powered cluster naming (uses the selected AI provider)
- When enabled, community clusters receive semantic labels like *"Authentication Layer"* instead of *"Cluster 3"*

---

## 11. Supported Languages

| Language | Parser | Import Resolution | Call Tracing | Class Detection |
|---|---|---|---|---|
| C | ✅ | ✅ | ✅ | ✅ |
| C++ | ✅ | ✅ | ✅ | ✅ |
| C# | ✅ | ✅ | ✅ | ✅ |
| Go | ✅ | ✅ | ✅ | ✅ |
| Java | ✅ | ✅ | ✅ | ✅ |
| JavaScript | ✅ | ✅ | ✅ | ✅ |
| PHP | ✅ | ✅ | ✅ | ✅ |
| Python | ✅ | ✅ | ✅ | ✅ |
| Ruby | ✅ | ✅ | ✅ | ✅ |
| Rust | ✅ | ✅ | ✅ | ✅ |
| Swift | ✅ | ✅ | ✅ | ✅ |
| TypeScript | ✅ | ✅ | ✅ | ✅ |
| TSX | ✅ | ✅ | ✅ | ✅ |

---

## 12. Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + F` | Focus search bar |
| `Escape` | Close panel / deselect node |
| `Scroll` | Zoom graph |

---

## 13. Troubleshooting

### "Web app not found" on launch
The Vite build output (`dist/`) is missing. Rebuild with:
```powershell
cd ArchitectureVisualizerApp/Assets/WebApp
npm run build
dotnet build
```

### Graph is empty after indexing
- Ensure your project contains files in supported languages
- Check the console (F12 in WebView2) for parsing errors
- Very large projects (50K+ files) may require more time

### AI chat returns errors
- Verify your API key is valid and has quota remaining
- Check internet connectivity (AI providers require API access)
- Try switching to a different model or provider in Settings

### Window is blank/white
WebView2 Runtime may not be installed. Download from [Microsoft](https://developer.microsoft.com/en-us/microsoft-edge/webview2/).

---

<p align="center">
  <strong>Softcurse Corp.</strong> · Built by Dante Berezinsky<br/>
  <a href="https://github.com/Beardicuss/Softcurse-Architecture-Visualizer">GitHub Repository</a>
</p>
