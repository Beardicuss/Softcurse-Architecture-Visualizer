import { useEffect, useCallback, useMemo, useState, useRef, forwardRef, useImperativeHandle } from 'react';
import { ZoomIn, ZoomOut, Maximize2, Focus, RotateCcw, Play, Pause, Lightbulb, LightbulbOff, GitBranch, Shuffle } from 'lucide-react';
import { useSigma } from '../hooks/useSigma';
import { useAppState } from '../hooks/useAppState';
import { knowledgeGraphToGraphology, filterGraphByDepth, SigmaNodeAttributes, SigmaEdgeAttributes } from '../lib/graph-adapter';
import { QueryFAB } from './QueryFAB';
import Graph from 'graphology';

export interface GraphCanvasHandle {
  focusNode: (nodeId: string) => void;
  toggleLayout: () => void;
}

export const GraphCanvas = forwardRef<GraphCanvasHandle>((_, ref) => {
  const {
    graph,
    setSelectedNode,
    selectedNode: appSelectedNode,
    visibleLabels,
    visibleEdgeTypes,
    openCodePanel,
    depthFilter,
    highlightedNodeIds,
    setHighlightedNodeIds,
    aiCitationHighlightedNodeIds,
    aiToolHighlightedNodeIds,
    blastRadiusNodeIds,
    isAIHighlightsEnabled,
    toggleAIHighlights,
    animatedNodes,
  } = useAppState();
  const [hoveredNodeName, setHoveredNodeName] = useState<string | null>(null);
  const bgCanvasRef = useRef<HTMLCanvasElement>(null);
  const packetCanvasRef = useRef<HTMLCanvasElement>(null);
  const packetsRef = useRef<Array<{ax:number,ay:number,bx:number,by:number,progress:number,speed:number,color:string,size:number}>>([]);

  const effectiveHighlightedNodeIds = useMemo(() => {
    if (!isAIHighlightsEnabled) return highlightedNodeIds;
    const next = new Set(highlightedNodeIds);
    for (const id of aiCitationHighlightedNodeIds) next.add(id);
    for (const id of aiToolHighlightedNodeIds) next.add(id);
    // Note: blast radius nodes are handled separately with red color
    return next;
  }, [highlightedNodeIds, aiCitationHighlightedNodeIds, aiToolHighlightedNodeIds, isAIHighlightsEnabled]);

  // Blast radius nodes (only when AI highlights enabled)
  const effectiveBlastRadiusNodeIds = useMemo(() => {
    if (!isAIHighlightsEnabled) return new Set<string>();
    return blastRadiusNodeIds;
  }, [blastRadiusNodeIds, isAIHighlightsEnabled]);

  // Animated nodes (only when AI highlights enabled)
  const effectiveAnimatedNodes = useMemo(() => {
    if (!isAIHighlightsEnabled) return new Map();
    return animatedNodes;
  }, [animatedNodes, isAIHighlightsEnabled]);

  const handleNodeClick = useCallback((nodeId: string) => {
    if (!graph) return;
    const node = graph.nodes.find(n => n.id === nodeId);
    if (node) {
      setSelectedNode(node);
      openCodePanel();
    }
  }, [graph, setSelectedNode, openCodePanel]);

  const handleNodeHover = useCallback((nodeId: string | null) => {
    if (!nodeId || !graph) {
      setHoveredNodeName(null);
      return;
    }
    const node = graph.nodes.find(n => n.id === nodeId);
    if (node) {
      setHoveredNodeName(node.properties.name);
    }
  }, [graph]);

  const handleStageClick = useCallback(() => {
    setSelectedNode(null);
  }, [setSelectedNode]);

  const {
    containerRef,
    sigmaRef,
    setGraph: setSigmaGraph,
    zoomIn,
    zoomOut,
    resetZoom,
    focusNode,
    isLayoutRunning,
    startLayout,
    stopLayout,
    isDagLayout,
    applyDagLayout,
    selectedNode: sigmaSelectedNode,
    setSelectedNode: setSigmaSelectedNode,
  } = useSigma({
    onNodeClick: handleNodeClick,
    onNodeHover: handleNodeHover,
    onStageClick: handleStageClick,
    highlightedNodeIds: effectiveHighlightedNodeIds,
    blastRadiusNodeIds: effectiveBlastRadiusNodeIds,
    animatedNodes: effectiveAnimatedNodes,
    visibleEdgeTypes,
  });

  // Expose focusNode to parent via ref
  useImperativeHandle(ref, () => ({
    focusNode: (nodeId: string) => {
      if (graph) {
        const node = graph.nodes.find(n => n.id === nodeId);
        if (node) {
          setSelectedNode(node);
          openCodePanel();
        }
      }
      focusNode(nodeId);
    },
    toggleLayout: () => {
      if (isDagLayout) {
        startLayout();
      } else {
        applyDagLayout();
      }
    },
  }), [focusNode, graph, setSelectedNode, openCodePanel, isDagLayout, startLayout, applyDagLayout]);

  // Update Sigma graph when KnowledgeGraph changes
  useEffect(() => {
    if (!graph) return;

    // Build communityMemberships map from MEMBER_OF relationships
    // MEMBER_OF edges: nodeId -> communityId (stored as targetId)
    const communityMemberships = new Map<string, number>();
    graph.relationships.forEach(rel => {
      if (rel.type === 'MEMBER_OF') {
        // Find the community node to get its index
        const communityNode = graph.nodes.find(n => n.id === rel.targetId && n.label === 'Community');
        if (communityNode) {
          // Extract community index from id (e.g., "comm_5" -> 5)
          const communityIdx = parseInt(rel.targetId.replace('comm_', ''), 10) || 0;
          communityMemberships.set(rel.sourceId, communityIdx);
        }
      }
    });

    const sigmaGraph = knowledgeGraphToGraphology(graph, communityMemberships);
    setSigmaGraph(sigmaGraph);
  }, [graph, setSigmaGraph]);

  // Update node visibility when filters change
  useEffect(() => {
    const sigma = sigmaRef.current;
    if (!sigma) return;

    const sigmaGraph = sigma.getGraph() as Graph<SigmaNodeAttributes, SigmaEdgeAttributes>;
    if (sigmaGraph.order === 0) return; // Don't filter empty graph

    filterGraphByDepth(sigmaGraph, appSelectedNode?.id || null, depthFilter, visibleLabels);
    sigma.refresh();
  }, [visibleLabels, depthFilter, appSelectedNode, sigmaRef]);

  // Sync app selected node with sigma
  useEffect(() => {
    if (appSelectedNode) {
      setSigmaSelectedNode(appSelectedNode.id);
    } else {
      setSigmaSelectedNode(null);
    }
  }, [appSelectedNode, setSigmaSelectedNode]);

  // Focus on selected node
  const handleFocusSelected = useCallback(() => {
    if (appSelectedNode) {
      focusNode(appSelectedNode.id);
    }
  }, [appSelectedNode, focusNode]);

  // Clear selection
  const handleClearSelection = useCallback(() => {
    setSelectedNode(null);
    setSigmaSelectedNode(null);
    resetZoom();
  }, [setSelectedNode, setSigmaSelectedNode, resetZoom]);


  // ── OmniSwarm background canvas: grid + radial glow ──────────────────────
  useEffect(() => {
    const canvas = bgCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    let raf: number;
    const draw = () => {
      const w = canvas.offsetWidth, h = canvas.offsetHeight;
      if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
      ctx.clearRect(0, 0, w, h);
      // Background
      ctx.fillStyle = '#050810';
      ctx.fillRect(0, 0, w, h);
      // Grid
      const g = 40;
      ctx.strokeStyle = 'rgba(0,255,200,0.07)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = 0; x <= w; x += g) { ctx.moveTo(x, 0); ctx.lineTo(x, h); }
      for (let y = 0; y <= h; y += g) { ctx.moveTo(0, y); ctx.lineTo(w, y); }
      ctx.stroke();
      // Radial glow
      const grd = ctx.createRadialGradient(w/2, h/2, 0, w/2, h/2, Math.max(w, h) * 0.55);
      grd.addColorStop(0, 'rgba(0,255,200,0.05)');
      grd.addColorStop(1, 'transparent');
      ctx.fillStyle = grd;
      ctx.fillRect(0, 0, w, h);
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => cancelAnimationFrame(raf);
  }, []);

  // ── OmniSwarm packet animation: dots moving along graph edges ────────────
  useEffect(() => {
    const canvas = packetCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    let raf: number;
    let frame = 0;

    // Convert graph-space coords to canvas pixels using sigma's framedGraphToViewport
    const toPixel = (gx: number, gy: number) => {
      const sigma = sigmaRef.current;
      if (!sigma) return null;
      try {
        return sigma.framedGraphToViewport({ x: gx, y: gy });
      } catch {
        return null;
      }
    };

    const animate = () => {
      raf = requestAnimationFrame(animate);
      frame++;
      // Size canvas to match its rendered size
      const w = canvas.parentElement?.clientWidth || canvas.offsetWidth;
      const h = canvas.parentElement?.clientHeight || canvas.offsetHeight;
      if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
      ctx.clearRect(0, 0, w, h);

      // Spawn packets every 8 frames along real edges
      if (frame % 8 === 0) {
        const sigma = sigmaRef.current;
        const g = sigma?.getGraph();
        if (sigma && g && g.order > 1) {
          const edges = g.edges();
          if (edges.length > 0) {
            for (let k = 0; k < 5; k++) {
              const edge = edges[Math.floor(Math.random() * edges.length)];
              const [s, t] = g.extremities(edge);
              // Use raw graph attributes — FA2 writes x/y directly here
              const sA = g.getNodeAttributes(s);
              const tA = g.getNodeAttributes(t);
              if (!sA || !tA) continue;
              const sp = toPixel(sA.x, sA.y);
              const tp = toPixel(tA.x, tA.y);
              if (!sp || !tp) continue;
              // Guard: skip if layout hasn't spread nodes yet
              if (Math.hypot(sp.x - tp.x, sp.y - tp.y) < 5) continue;
              // coords from framedGraphToViewport are already in canvas space
              const color = Math.random() > 0.4 ? '#00ffc8' : '#ff6b35';
              packetsRef.current.push({
                ax: sp.x, ay: sp.y,
                bx: tp.x, by: tp.y,
                progress: 0,
                speed: 0.007 + Math.random() * 0.011,
                color,
                size: 3.5 + Math.random() * 2.5,
              });
            }
            if (packetsRef.current.length > 150) packetsRef.current.splice(0, packetsRef.current.length - 150);
          }
        }
      }

      // Draw packets with glow trail
      packetsRef.current = packetsRef.current.filter(p => {
        const x = p.ax + (p.bx - p.ax) * p.progress;
        const y = p.ay + (p.by - p.ay) * p.progress;
        const rgba = p.color === '#00ffc8' ? 'rgba(0,255,200,' : 'rgba(255,107,53,';
        for (let i = 1; i <= 5; i++) {
          const tp2 = Math.max(0, p.progress - p.speed * i * 5);
          const tx = p.ax + (p.bx - p.ax) * tp2;
          const ty = p.ay + (p.by - p.ay) * tp2;
          ctx.beginPath();
          ctx.arc(tx, ty, p.size * (1 - i * 0.16), 0, Math.PI * 2);
          ctx.fillStyle = rgba + (0.4 - i * 0.07) + ')';
          ctx.fill();
        }
        ctx.beginPath();
        ctx.arc(x, y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.shadowBlur = 14;
        ctx.shadowColor = p.color;
        ctx.fill();
        ctx.shadowBlur = 0;
        p.progress += p.speed;
        return p.progress < 1;
      });
    };

    animate();
    return () => cancelAnimationFrame(raf);
  }, [sigmaRef]);

  return (
    <div className="relative w-full h-full" style={{background: '#050810'}}>
      {/* OmniSwarm background: grid + radial glow on canvas */}
      <canvas
        ref={bgCanvasRef}
        className="absolute inset-0 pointer-events-none"
        style={{zIndex: 0, width: '100%', height: '100%'}}
      />

      {/* Sigma container */}
      <div
        ref={containerRef}
        className="sigma-container w-full h-full cursor-grab active:cursor-grabbing"
        style={{position: 'relative', zIndex: 1}}
      />

      {/* Packet animation canvas — ON TOP of Sigma */}
      <canvas
        ref={packetCanvasRef}
        className="absolute inset-0 pointer-events-none"
        style={{zIndex: 2, width: '100%', height: '100%'}}
      />

      {/* Hovered node tooltip - only show when NOT selected */}
      {hoveredNodeName && !sigmaSelectedNode && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-elevated/95 border border-border-subtle rounded-lg backdrop-blur-sm z-20 pointer-events-none animate-fade-in">
          <span className="font-mono text-sm text-text-primary">{hoveredNodeName}</span>
        </div>
      )}

      {/* Selection info bar */}
      {sigmaSelectedNode && appSelectedNode && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2 bg-accent/20 border border-accent/30 rounded-xl backdrop-blur-sm z-20 animate-slide-up">
          <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
          <span className="font-mono text-sm text-text-primary">
            {appSelectedNode.properties.name}
          </span>
          <span className="text-xs text-text-muted">
            ({appSelectedNode.label})
          </span>
          <button
            onClick={handleClearSelection}
            className="ml-2 px-2 py-0.5 text-xs text-text-secondary hover:text-text-primary hover:bg-white/10 rounded transition-colors"
          >
            Clear
          </button>
        </div>
      )}

      {/* Graph Controls - Bottom Right */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-1 z-10">
        <button
          onClick={zoomIn}
          className="w-9 h-9 flex items-center justify-center bg-elevated border border-border-subtle rounded-md text-text-secondary hover:bg-hover hover:text-text-primary transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={zoomOut}
          className="w-9 h-9 flex items-center justify-center bg-elevated border border-border-subtle rounded-md text-text-secondary hover:bg-hover hover:text-text-primary transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={resetZoom}
          className="w-9 h-9 flex items-center justify-center bg-elevated border border-border-subtle rounded-md text-text-secondary hover:bg-hover hover:text-text-primary transition-colors"
          title="Fit to Screen"
        >
          <Maximize2 className="w-4 h-4" />
        </button>

        {/* Divider */}
        <div className="h-px bg-border-subtle my-1" />

        {/* Focus on selected */}
        {appSelectedNode && (
          <button
            onClick={handleFocusSelected}
            className="w-9 h-9 flex items-center justify-center bg-accent/20 border border-accent/30 rounded-md text-accent hover:bg-accent/30 transition-colors"
            title="Focus on Selected Node"
          >
            <Focus className="w-4 h-4" />
          </button>
        )}

        {/* Clear selection */}
        {sigmaSelectedNode && (
          <button
            onClick={handleClearSelection}
            className="w-9 h-9 flex items-center justify-center bg-elevated border border-border-subtle rounded-md text-text-secondary hover:bg-hover hover:text-text-primary transition-colors"
            title="Clear Selection"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        )}

        {/* Divider */}
        <div className="h-px bg-border-subtle my-1" />

        {/* Layout control */}
        <button
          onClick={isLayoutRunning ? stopLayout : startLayout}
          className={`
            w-9 h-9 flex items-center justify-center border rounded-md transition-all
            ${isLayoutRunning
              ? 'bg-accent border-accent text-white shadow-glow animate-pulse'
              : 'bg-elevated border-border-subtle text-text-secondary hover:bg-hover hover:text-text-primary'
            }
          `}
          title={isLayoutRunning ? 'Stop Layout' : 'Run Layout Again'}
        >
          {isLayoutRunning ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4" />
          )}
        </button>

        {/* Divider */}
        <div className="h-px bg-border-subtle my-1" />

        {/* DAG / Force layout toggle */}
        <button
          onClick={isDagLayout ? startLayout : applyDagLayout}
          className={`
            w-9 h-9 flex items-center justify-center border rounded-md transition-all
            ${isDagLayout
              ? 'bg-cyan-500/20 border-cyan-400/40 text-cyan-300 hover:bg-cyan-500/30'
              : 'bg-elevated border-border-subtle text-text-secondary hover:bg-hover hover:text-text-primary'
            }
          `}
          title={isDagLayout ? 'Switch to Force Layout' : 'Switch to DAG (Hierarchical) Layout'}
        >
          {isDagLayout ? <Shuffle className="w-4 h-4" /> : <GitBranch className="w-4 h-4" />}
        </button>
      </div>

      {/* Layout running indicator */}
      {isLayoutRunning && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-3 py-1.5 bg-emerald-500/20 border border-emerald-500/30 rounded-full backdrop-blur-sm z-10 animate-fade-in">
          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-ping" />
          <span className="text-xs text-emerald-400 font-medium">Layout optimizing...</span>
        </div>
      )}

      {/* Query FAB */}
      <QueryFAB />

      {/* AI Highlights toggle - Top Right */}
      <div className="absolute top-4 right-4 z-20">
        <button
          onClick={() => {
            // If turning off, also clear process highlights
            if (isAIHighlightsEnabled) {
              setHighlightedNodeIds(new Set());
            }
            toggleAIHighlights();
          }}
          className={
            isAIHighlightsEnabled
              ? 'w-10 h-10 flex items-center justify-center bg-cyan-500/15 border border-cyan-400/40 rounded-lg text-cyan-200 hover:bg-cyan-500/20 hover:border-cyan-300/60 transition-colors'
              : 'w-10 h-10 flex items-center justify-center bg-elevated border border-border-subtle rounded-lg text-text-muted hover:bg-hover hover:text-text-primary transition-colors'
          }
          title={isAIHighlightsEnabled ? 'Turn off all highlights' : 'Turn on AI highlights'}
        >
          {isAIHighlightsEnabled ? <Lightbulb className="w-4 h-4" /> : <LightbulbOff className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
});

GraphCanvas.displayName = 'GraphCanvas';
