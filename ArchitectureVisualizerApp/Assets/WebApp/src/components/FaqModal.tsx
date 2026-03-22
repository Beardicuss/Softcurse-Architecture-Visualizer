import { X, Zap, Brain, Search, BarChart3, Code2, Globe, Shield, Sparkles, Layers } from 'lucide-react';

interface FaqModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface FaqItem {
    question: string;
    answer: string;
}

const FAQ_SECTIONS: { title: string; icon: React.ReactNode; items: FaqItem[] }[] = [
    {
        title: 'Getting Started',
        icon: <Zap className="w-4 h-4" />,
        items: [
            {
                question: 'How do I load a project?',
                answer: 'There are two ways to load a project:\n\n• **ZIP Upload** — Drag and drop a .zip archive of your project onto the DropZone, or click to browse.\n\n• **GitHub URL** — Switch to the GitHub tab and paste a public repository URL (e.g., https://github.com/user/repo). The app will clone it in-browser and begin indexing.',
            },
            {
                question: 'How long does indexing take?',
                answer: 'Indexing time depends on project size:\n\n• **Small projects** (< 100 files): 5–10 seconds\n• **Medium projects** (100–1,000 files): 10–30 seconds\n• **Large projects** (1,000+ files): 30–120 seconds\n\nThe progress overlay shows the current phase: extracting, parsing, building structures, resolving relationships, detecting communities, and loading the database.',
            },
            {
                question: 'What file formats are supported?',
                answer: 'The app accepts **.zip** archives containing source code. For GitHub, paste any public repository URL. The parser supports 13 programming languages (see Supported Languages section).',
            },
        ],
    },
    {
        title: 'Graph Navigation',
        icon: <Layers className="w-4 h-4" />,
        items: [
            {
                question: 'How do I navigate the graph?',
                answer: '• **Pan** — Click and drag the canvas background\n• **Zoom** — Scroll the mouse wheel\n• **Select a node** — Click any node to inspect it\n• **Drag a node** — Click and drag to reposition\n• **Search** — Use Ctrl+K to focus the search bar and find nodes by name',
            },
            {
                question: 'What do the node colors mean?',
                answer: 'Each node type has a distinct color:\n\n• 🟣 **Magenta** — Project root\n• 💚 **Mint** — Folders\n• 🔵 **Blue** — Files\n• 🟡 **Gold** — Classes\n• 💚 **Neon Green** — Functions\n• 🩵 **Teal** — Methods\n• 💗 **Hot Pink** — Interfaces\n• 🟠 **Orange** — Enums\n\nWhen community detection is active, symbol nodes are colored by their functional cluster instead.',
            },
            {
                question: 'What do the node sizes represent?',
                answer: 'Node size indicates structural importance. Project and Package nodes are the largest; Folders are medium; Files, Classes, and Interfaces are smaller; Functions, Methods, and Variables are the smallest. This creates a clear visual hierarchy.',
            },
            {
                question: 'What are the colored clusters?',
                answer: 'Clusters are detected automatically by the **Leiden community detection algorithm**. It groups code symbols (functions, classes, methods) that work closely together based on CALLS, EXTENDS, and IMPLEMENTS relationships. Each cluster gets a unique color from a 20-color neon palette.',
            },
        ],
    },
    {
        title: 'Softcurse AI',
        icon: <Brain className="w-4 h-4" />,
        items: [
            {
                question: 'How do I set up the AI chat?',
                answer: '1. Click the **⚙️ Settings** button in the header\n2. Select an AI provider (Google Gemini recommended — free tier available)\n3. Paste your API key\n4. Choose a model (e.g., gemini-2.0-flash)\n5. Click **Save**\n\nYour API key is stored locally in your browser and never sent anywhere except to the selected AI provider.',
            },
            {
                question: 'Which AI provider should I use?',
                answer: '**Google Gemini** is recommended for most users — it offers a generous free tier and fast responses.\n\n• **Gemini** — Free tier, fast, good quality\n• **Ollama** — Free, runs 100% locally (requires Ollama installed)\n• **OpenAI** — GPT-4o, paid API\n• **Anthropic** — Claude, paid API\n• **OpenRouter** — Access to 100+ models, pay-per-token\n• **MiniMax** — MiniMax-M2.5, paid API',
            },
            {
                question: 'What kind of questions can I ask?',
                answer: 'The AI agent uses **Graph RAG** to answer questions grounded in your actual codebase:\n\n• *"What depends on UserService?"*\n• *"Trace the login flow from start to finish"*\n• *"What would break if I rename fetchData?"*\n• *"Which components have the highest coupling?"*\n• *"Find all classes related to authentication"*\n• *"Explain the relationship between Controller and Middleware"*\n\nBe specific — mention exact symbol names for best results.',
            },
            {
                question: 'How does Graph RAG work?',
                answer: 'Graph RAG (Retrieval-Augmented Generation) combines the knowledge graph with an LLM:\n\n1. Your question is analyzed to determine needed tools\n2. The agent queries the LadybugDB graph database using Cypher\n3. Relevant code symbols, relationships, and source code are retrieved\n4. The LLM synthesizes an answer grounded in your actual codebase\n\nThis means the AI doesn\'t hallucinate — every answer is backed by real code relationships.',
            },
        ],
    },
    {
        title: 'Search & Analysis',
        icon: <Search className="w-4 h-4" />,
        items: [
            {
                question: 'How does search work?',
                answer: 'The search bar (Ctrl+K) provides **hybrid search**:\n\n• **BM25 text search** — Fast keyword matching via MiniSearch\n• **Vector similarity** — Semantic search via HuggingFace embeddings\n\nResults are ranked by combined relevance. Click a result to focus the graph on that node.',
            },
            {
                question: 'What is Impact Analysis?',
                answer: 'Click any node to see its **360° context** in the right panel:\n\n• **Incoming** — Who calls/imports this symbol (upstream)\n• **Outgoing** — What this symbol calls/imports (downstream)\n• **Confidence Score** — Certainty of each relationship\n\nThis answers: *"What would break if I change this?"*',
            },
            {
                question: 'What is Process Flow Tracing?',
                answer: 'The Processes tab identifies high-level execution flows through your code. Entry points (HTTP handlers, main functions, event listeners) are detected and their call chains traced. Click a process to see a **Mermaid flowchart** of the full execution path.',
            },
        ],
    },
    {
        title: 'Cypher Queries',
        icon: <Code2 className="w-4 h-4" />,
        items: [
            {
                question: 'What are Cypher queries?',
                answer: 'Cypher is a graph query language used to query the LadybugDB knowledge graph directly. Click the **Query** floating button to open the console.\n\nExample: Find the 10 most connected nodes:\n```\nMATCH (n)-[r:CodeRelation]-()\nRETURN n.name, count(r) AS connections\nORDER BY connections DESC LIMIT 10\n```',
            },
            {
                question: 'What relationship types can I query?',
                answer: '• **CONTAINS** — Folder contains File\n• **DEFINES** — File defines Function/Class\n• **IMPORTS** — File imports File\n• **CALLS** — Function calls Function\n• **EXTENDS** — Class extends Class\n• **IMPLEMENTS** — Class implements Interface',
            },
        ],
    },
    {
        title: 'Supported Languages',
        icon: <Globe className="w-4 h-4" />,
        items: [
            {
                question: 'Which programming languages are supported?',
                answer: 'The application uses **Tree-sitter WASM** parsers for deep AST-level analysis of **13 languages**:\n\nC, C++, C#, Go, Java, JavaScript, PHP, Python, Ruby, Rust, Swift, TypeScript, and TSX.\n\nEach parser extracts classes, functions, methods, interfaces, imports, call chains, and inheritance hierarchies.',
            },
        ],
    },
    {
        title: 'Privacy & Security',
        icon: <Shield className="w-4 h-4" />,
        items: [
            {
                question: 'Is my code sent to any server?',
                answer: 'No. **All indexing happens locally** in your browser via WASM. Your source code never leaves your machine. The only external communication is with your selected AI provider when using the chat feature.',
            },
            {
                question: 'Where are my API keys stored?',
                answer: 'API keys are stored in your browser\'s **localStorage** — they are never transmitted anywhere except to the selected LLM provider\'s API endpoint. Keys are never logged, committed, or sent to Softcurse servers.',
            },
            {
                question: 'Does the app collect telemetry?',
                answer: 'No. The application has **zero telemetry**, no analytics, no tracking, and no cloud dependencies. It is a fully offline-capable desktop application.',
            },
        ],
    },
    {
        title: 'Troubleshooting',
        icon: <BarChart3 className="w-4 h-4" />,
        items: [
            {
                question: 'The graph is empty after indexing',
                answer: '• Ensure your project contains files in one of the 13 supported languages\n• Check that the ZIP archive contains actual source code (not just configuration files)\n• Very large projects (50K+ files) may need more time\n• Open the browser console (F12) to check for parsing errors',
            },
            {
                question: 'AI chat returns errors',
                answer: '• Verify your API key is valid and has remaining quota\n• Check your internet connection (AI providers require API access)\n• Try switching to a different model or provider in Settings\n• Gemini free tier has rate limits — wait a moment and retry',
            },
            {
                question: 'The window is blank or white',
                answer: 'WebView2 Runtime may not be installed. Download it from Microsoft\'s website. Windows 11 includes it by default; older Windows 10 versions may need manual installation.',
            },
            {
                question: 'Performance is poor with very large graphs',
                answer: '• Use the **filter toggles** in the left panel to hide node types (e.g., hide Variables and Imports)\n• A GPU with WebGL 2.0 support is required for smooth rendering\n• The Sigma.js WebGL renderer handles 10,000+ nodes at 60fps on modern hardware',
            },
        ],
    },
];

export const FaqModal = ({ isOpen, onClose }: FaqModalProps) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative w-full max-w-3xl max-h-[85vh] bg-deep border border-border-subtle rounded-xl shadow-2xl overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface/50">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 flex items-center justify-center bg-gradient-to-br from-accent to-[#ff3399] rounded-lg">
                            <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-text-primary">Frequently Asked Questions</h2>
                            <p className="text-xs text-text-muted mt-0.5">Softcurse Architecture Visualizer v2.0</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 flex items-center justify-center rounded-lg text-text-muted hover:text-text-primary hover:bg-hover transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-border-subtle">
                    {FAQ_SECTIONS.map((section) => (
                        <div key={section.title}>
                            {/* Section header */}
                            <div className="flex items-center gap-2 mb-3">
                                <span className="text-accent">{section.icon}</span>
                                <h3 className="text-sm font-semibold text-accent uppercase tracking-wider">
                                    {section.title}
                                </h3>
                                <div className="flex-1 h-px bg-border-subtle" />
                            </div>

                            {/* Questions */}
                            <div className="space-y-3">
                                {section.items.map((item, idx) => (
                                    <details
                                        key={idx}
                                        className="group bg-surface/50 border border-border-subtle rounded-lg overflow-hidden hover:border-accent/30 transition-colors"
                                    >
                                        <summary className="flex items-center gap-3 px-4 py-3 cursor-pointer select-none list-none">
                                            <span className="w-5 h-5 flex items-center justify-center rounded-full bg-accent/10 text-accent text-xs font-bold flex-shrink-0 group-open:bg-accent/20 transition-colors">
                                                ?
                                            </span>
                                            <span className="text-sm font-medium text-text-primary group-hover:text-accent transition-colors">
                                                {item.question}
                                            </span>
                                            <span className="ml-auto text-text-muted text-xs group-open:rotate-90 transition-transform">
                                                ▸
                                            </span>
                                        </summary>
                                        <div className="px-4 pb-4 pt-1 ml-8 text-sm text-text-secondary leading-relaxed whitespace-pre-line">
                                            {item.answer.split('\n').map((line, i) => {
                                                // Handle bold text
                                                const parts = line.split(/(\*\*[^*]+\*\*)/g);
                                                return (
                                                    <span key={i}>
                                                        {parts.map((part, j) => {
                                                            if (part.startsWith('**') && part.endsWith('**')) {
                                                                return <strong key={j} className="text-text-primary font-semibold">{part.slice(2, -2)}</strong>;
                                                            }
                                                            // Handle inline code
                                                            const codeParts = part.split(/(`[^`]+`)/g);
                                                            return codeParts.map((cp, k) => {
                                                                if (cp.startsWith('`') && cp.endsWith('`')) {
                                                                    return <code key={k} className="px-1.5 py-0.5 bg-elevated rounded text-accent text-xs font-mono">{cp.slice(1, -1)}</code>;
                                                                }
                                                                // Handle italic text
                                                                const italicParts = cp.split(/(\*[^*]+\*)/g);
                                                                return italicParts.map((ip, l) => {
                                                                    if (ip.startsWith('*') && ip.endsWith('*') && !ip.startsWith('**')) {
                                                                        return <em key={l} className="text-text-muted italic">{ip.slice(1, -1)}</em>;
                                                                    }
                                                                    return <span key={l}>{ip}</span>;
                                                                });
                                                            });
                                                        })}
                                                        {i < item.answer.split('\n').length - 1 && '\n'}
                                                    </span>
                                                );
                                            })}
                                        </div>
                                    </details>
                                ))}
                            </div>
                        </div>
                    ))}

                    {/* Footer */}
                    <div className="text-center pt-4 pb-2 border-t border-border-subtle">
                        <p className="text-xs text-text-muted">
                            Built by <span className="text-accent">Softcurse LAB.</span> · <a href="https://softcurse-website.pages.dev/" target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">softcurse-website.pages.dev</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
