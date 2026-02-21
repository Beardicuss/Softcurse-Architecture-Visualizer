// Calculate node degrees immediately so they are available for rendering
data.nodes.forEach(node => {
  node.degree = data.links.filter(l =>
    (l.source.id || l.source) === node.id ||
    (l.target.id || l.target) === node.id
  ).length;
});

let simulation = null;
let adjacency = {};
let nodeSelection = null;
let linkSelection = null;
let mainSvg = null;
let mainGroup = null;
let currentTransform = d3.zoomIdentity;
let centralityData = null;
let performanceMode = "auto";
let currentForceMode = null; // Manual mode override (null = auto)

// Focus mode variables
let focusIntensity = 0.85; // Default: 85% dimming (15% opacity for unfocused)
let show2HopNeighbors = false;
let currentFocusedNode = null;
let selectedNodes = new Set();
let isMultiSelectMode = false;

// DAG layout mode
let currentLayoutMode = 'force'; // 'force' or 'dag'

// Level of Detail (LOD) system
let currentZoomLevel = 1;
let labelsVisible = true;
const LOD_THRESHOLDS = {
  hideLabels: 0.5,      // Hide labels when zoomed out below 0.5x
  showLabels: 0.8,      // Show labels when zoomed in above 0.8x
  simplifyNodes: 0.3    // Simplify node rendering below 0.3x
};

// Update LOD based on zoom level
function updateLOD(zoomLevel) {
  currentZoomLevel = zoomLevel;

  // Hide/show labels based on zoom
  if (zoomLevel < LOD_THRESHOLDS.hideLabels && labelsVisible) {
    labelsVisible = false;
    if (nodeSelection) {
      nodeSelection.selectAll('text').style('opacity', 0);
    }
  } else if (zoomLevel > LOD_THRESHOLDS.showLabels && !labelsVisible) {
    labelsVisible = true;
    if (nodeSelection) {
      nodeSelection.selectAll('text').style('opacity', 1);
    }
  }

  // Simplify node rendering at very low zoom
  if (nodeSelection) {
    if (zoomLevel < LOD_THRESHOLDS.simplifyNodes) {
      // Hide node strokes for performance
      nodeSelection.selectAll('circle').attr('stroke-width', 0);
    } else {
      // Restore node strokes
      nodeSelection.selectAll('circle').attr('stroke-width', d => {
        if (d.in_cycle || d.is_god_module) return 3;
        return 2;
      });
    }
  }
}

// Progressive rendering for large graphs
function showLoadingOverlay() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.style.display = 'flex';
}

function hideLoadingOverlay() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.style.display = 'none';
}

function updateLoadingProgress(current, total) {
  const progress = document.getElementById('loading-progress');
  const bar = document.getElementById('loading-bar');
  if (progress) progress.textContent = current;
  if (bar) bar.style.width = `${(current / total) * 100}%`;
}

function renderNodesProgressively(nodeData, batchSize = 100) {
  return new Promise((resolve) => {
    let currentIndex = 0;
    const total = nodeData.length;

    function renderBatch() {
      const endIndex = Math.min(currentIndex + batchSize, total);
      updateLoadingProgress(endIndex, total);

      currentIndex = endIndex;

      if (currentIndex < total) {
        requestAnimationFrame(renderBatch);
      } else {
        resolve();
      }
    }

    renderBatch();
  });
}

// ============================================================
// ADAPTIVE FORCE LAYOUT CONFIGURATION
// ============================================================
function getAdaptiveForceConfig(nodeCount, manualMode = null) {
  // Auto-detect mode based on node count if no manual override
  const selectedMode = manualMode || currentForceMode || (
    nodeCount > 350 ? "extreme" :
      nodeCount > 150 ? "large" :
        nodeCount > 50 ? "medium" : "balanced"
  );

  // Base configuration (Balanced)
  const config = {
    mode: selectedMode,
    chargeStrength: -300,      // Strong repulsion for good spacing
    linkDistance: 100,         // Comfortable distance
    linkStrength: 0.6,         // Flexible links
    alphaDecay: 0.02,          // Slow decay for better stabilization
    velocityDecay: 0.4,        // Low friction for movement
    centerStrength: 0.05,      // Weak center pull
    collisionRadius: 15        // Good buffer between nodes
  };

  if (selectedMode === "medium") {
    config.chargeStrength = -250;
    config.linkDistance = 135;
    config.linkStrength = 0.65;
    config.alphaDecay = 0.025;
    config.velocityDecay = 0.45;
    config.centerStrength = 0.06;
    config.collisionRadius = 12;
  } else if (selectedMode === "large") {
    config.chargeStrength = -150;
    config.linkDistance = 165;
    config.linkStrength = 0.75;
    config.alphaDecay = 0.04;
    config.velocityDecay = 0.55;
    config.centerStrength = 0.1;
    config.collisionRadius = 8;
  } else if (selectedMode === "extreme") {
    config.chargeStrength = -80;
    config.linkDistance = 200;
    config.linkStrength = 0.85;
    config.alphaDecay = 0.08;
    config.velocityDecay = 0.65;
    config.centerStrength = 0.15;
    config.collisionRadius = 4;
  }

  return config;
}

// ============================================================
// DAG LAYOUT - HIERARCHICAL TOPOLOGICAL SORT
// ============================================================
function computeDAGLayout(data, width, height) {
  const nodes = data.nodes;
  const links = data.links;

  // Build adjacency for topological sort
  const inDegree = {};
  const outgoing = {};

  nodes.forEach(n => {
    inDegree[n.id] = 0;
    outgoing[n.id] = [];
  });

  links.forEach(l => {
    const source = typeof l.source === 'string' ? l.source : l.source.id;
    const target = typeof l.target === 'string' ? l.target : l.target.id;
    if (inDegree[target] !== undefined) inDegree[target]++;
    if (outgoing[source]) outgoing[source].push(target);
  });

  // Topological sort using Kahn's algorithm
  const layers = [];
  const nodeLayer = {};
  const queue = [];

  // Start with nodes that have no dependencies
  Object.keys(inDegree).forEach(id => {
    if (inDegree[id] === 0) queue.push(id);
  });

  while (queue.length > 0) {
    const currentLayer = [];
    const nextQueue = [];

    queue.forEach(nodeId => {
      currentLayer.push(nodeId);
      nodeLayer[nodeId] = layers.length;

      // Reduce in-degree for children
      (outgoing[nodeId] || []).forEach(childId => {
        inDegree[childId]--;
        if (inDegree[childId] === 0) {
          nextQueue.push(childId);
        }
      });
    });

    if (currentLayer.length > 0) {
      layers.push(currentLayer);
    }
    queue.length = 0;
    queue.push(...nextQueue);
  }

  // Handle cycles - put remaining nodes in final layer
  const processedNodes = new Set(Object.keys(nodeLayer));
  const remainingNodes = nodes.filter(n => !processedNodes.has(n.id));
  if (remainingNodes.length > 0) {
    layers.push(remainingNodes.map(n => n.id));
    remainingNodes.forEach(n => nodeLayer[n.id] = layers.length - 1);
  }

  // Position nodes with better spacing
  const minLayerHeight = 150; // Minimum vertical spacing between layers
  const minNodeSpacing = 120; // Minimum horizontal spacing between nodes
  const layerHeight = Math.max(minLayerHeight, height / (layers.length + 1));

  nodes.forEach(node => {
    const layer = nodeLayer[node.id] || 0;
    const layerNodes = layers[layer] || [];
    const positionInLayer = layerNodes.indexOf(node.id);

    // Calculate horizontal spacing based on layer width and minimum spacing
    const totalMinWidth = layerNodes.length * minNodeSpacing;
    const availableWidth = width - 100; // Leave margins
    const effectiveWidth = Math.max(totalMinWidth, availableWidth);
    const nodeSpacing = effectiveWidth / (layerNodes.length + 1);

    // Position with spacing and small random offset to prevent exact overlaps
    const randomOffset = (Math.random() - 0.5) * 20;
    node.x = 50 + nodeSpacing * (positionInLayer + 1) + randomOffset;
    node.y = layerHeight * (layer + 1);
    node.fx = node.x; // Fix positions for DAG mode
    node.fy = node.y;
  });

  return { layers, nodeLayer };
}

// Language zone clustering force - WEAKENED for better spacing
function forceCluster() {
  const strength = 0.05;  // Reduced from 0.2 to 0.05 for subtle clustering
  let nodes;

  function force(alpha) {
    const clusterCenters = {};
    const clusterCounts = {};

    // Calculate cluster centers by language
    for (const d of nodes) {
      const lang = d.language || 'unknown';
      if (!clusterCenters[lang]) {
        clusterCenters[lang] = { x: 0, y: 0 };
        clusterCounts[lang] = 0;
      }
      clusterCenters[lang].x += d.x;
      clusterCenters[lang].y += d.y;
      clusterCounts[lang]++;
    }

    for (const lang in clusterCenters) {
      clusterCenters[lang].x /= clusterCounts[lang];
      clusterCenters[lang].y /= clusterCounts[lang];
    }

    // Pull nodes toward their language cluster center
    for (const d of nodes) {
      const lang = d.language || 'unknown';
      const center = clusterCenters[lang];
      if (center) {
        d.vx += (center.x - d.x) * strength * alpha;
        d.vy += (center.y - d.y) * strength * alpha;
      }
    }
  }

  force.initialize = function (_nodes) {
    nodes = _nodes;
  };

  return force;
}

// Find neighbors up to N hops away
function findNeighbors(nodeId, maxHops) {
  const neighbors = new Set([nodeId]);
  const links = new Set();

  if (maxHops >= 1) {
    // 1-hop neighbors
    data.links.forEach(l => {
      const s = typeof l.source === "string" ? l.source : l.source.id;
      const t = typeof l.target === "string" ? l.target : l.target.id;
      if (s === nodeId) {
        neighbors.add(t);
        links.add(l);
      }
      if (t === nodeId) {
        neighbors.add(s);
        links.add(l);
      }
    });
  }

  if (maxHops >= 2) {
    // 2-hop neighbors
    const firstHop = new Set(neighbors);
    firstHop.delete(nodeId); // Don't search from original node

    firstHop.forEach(neighborId => {
      data.links.forEach(l => {
        const s = typeof l.source === "string" ? l.source : l.source.id;
        const t = typeof l.target === "string" ? l.target : l.target.id;
        if (s === neighborId && !neighbors.has(t)) {
          neighbors.add(t);
          links.add(l);
        }
        if (t === neighborId && !neighbors.has(s)) {
          neighbors.add(s);
          links.add(l);
        }
      });
    });
  }

  return { neighbors, links };
}

function updatePerformanceDisplay(config, nodeCount) {
  // Only update if values actually changed
  const currentState = `${config.mode}-${nodeCount}-${config.chargeStrength}-${config.alphaDecay}-${config.velocityDecay}`;
  if (this._lastState === currentState) return;
  this._lastState = currentState;

  const perfMode = document.getElementById("perf-mode");
  const perfStatus = document.getElementById("perf-status");

  if (perfMode) {
    perfMode.textContent = config.mode.toUpperCase();
    perfMode.className = `perf-badge ${config.mode}`;
  }

  if (perfStatus) {
    perfStatus.textContent = `${config.mode} (${nodeCount}n) C:${config.chargeStrength} A:${config.alphaDecay} F:${config.velocityDecay}`;
  }
}

function initStats(data) {
  document.getElementById("stat-files").textContent = data.metadata.total_files || data.nodes.length;
  document.getElementById("stat-functions").textContent = data.metrics.total_functions || "0";
  document.getElementById("stat-classes").textContent = data.metrics.total_classes || "0";
  document.getElementById("stat-deps").textContent = data.links.length;
}

function buildAdjacency(data) {
  adjacency = {};
  data.nodes.forEach(n => {
    adjacency[n.id] = { incoming: [], outgoing: [] };
  });
  data.links.forEach(l => {
    const s = typeof l.source === "string" ? l.source : l.source.id;
    const t = typeof l.target === "string" ? l.target : l.target.id;
    if (!adjacency[s]) adjacency[s] = { incoming: [], outgoing: [] };
    if (!adjacency[t]) adjacency[t] = { incoming: [], outgoing: [] };
    adjacency[s].outgoing.push(t);
    adjacency[t].incoming.push(s);
  });
}

function computeCentrality(data) {
  const res = {};
  data.nodes.forEach(n => {
    const adj = adjacency[n.id] || { incoming: [], outgoing: [] };
    const inDeg = adj.incoming.length;
    const outDeg = adj.outgoing.length;
    const total = inDeg + outDeg;
    const score = total;
    n.inDegree = inDeg;
    n.outDegree = outDeg;
    n.centralityScore = score;
    res[n.id] = { id: n.id, inDeg, outDeg, total, score };
  });
  return res;
}

function getLangIndicator(lang) {
  return `<span class="lang-indicator lang-${lang}">${lang}</span>`;
}

function updateDetails(mod) {
  if (!mod) return;
  const detailsBody = document.getElementById("details-body");
  const adj = adjacency[mod.id] || { incoming: [], outgoing: [] };

  let html = `
    <div class="detail-section">
      <div class="detail-title">Module</div>
      <div class="detail-content">
        ${mod.id}
        ${getLangIndicator(mod.language)}
        ${mod.disconnected ? '<span class="disconnected-badge">ISOLATED</span>' : ''}
      </div>
    </div>
    <div class="detail-section">
      <div class="detail-title">File</div>
      <div class="detail-content">${mod.file}</div>
    </div>`;

  if (mod.docstring) {
    html += `
    <div class="detail-section">
      <div class="detail-title">Description</div>
      <div class="detail-content">${mod.docstring}</div>
    </div>`;
  }

  if (mod.functions && mod.functions.length) {
    html += `
    <div class="detail-section">
      <div class="detail-title">Functions (${mod.functions.length})</div>
      <ul class="detail-list">
        ${mod.functions.map(f => `<li>${f}</li>`).join("")}
      </ul>
    </div>`;
  }

  if (mod.classes && mod.classes.length) {
    html += `
    <div class="detail-section">
      <div class="detail-title">Classes (${mod.classes.length})</div>
      <ul class="detail-list">
        ${mod.classes.map(c => `
          <li class="class-item">${c.name}
            ${c.methods && c.methods.length ? `
              <ul class="method-list">
                ${c.methods.map(m => `<li>${m}</li>`).join("")}
              </ul>` : ""}
          </li>`).join("")}
      </ul>
    </div>`;
  }

  if (adj.outgoing && adj.outgoing.length) {
    html += `
    <div class="detail-section">
      <div class="detail-title">Imports (${adj.outgoing.length})</div>
      <ul class="detail-list">
        ${adj.outgoing.map(m => `<li>${m}</li>`).join("")}
      </ul>
    </div>`;
  }

  if (adj.incoming && adj.incoming.length) {
    html += `
    <div class="detail-section">
      <div class="detail-title">Imported By (${adj.incoming.length})</div>
      <ul class="detail-list">
        ${adj.incoming.map(m => `<li>${m}</li>`).join("")}
      </ul>
    </div>`;
  }

  detailsBody.innerHTML = html;
}

function updateMiniCard(mod) {
  const mini = document.getElementById("mini-card-body");
  if (!mini) return;

  if (!mod) {
    mini.innerHTML = '<div class="empty-state">Select a module to see a quick file card.</div>';
    return;
  }

  const inDeg = mod.inDegree || 0;
  const outDeg = mod.outDegree || 0;
  const total = mod.centralityScore || (inDeg + outDeg);
  const fnCount = (mod.functions || []).length;
  const clsCount = (mod.classes || []).length;

  const shortName = mod.id.split(".").slice(-1)[0];
  const barPercent = Math.min(100, total * 5);

  mini.innerHTML = `
    <div class="detail-section">
      <div class="detail-title">Module</div>
      <div class="detail-content">
        ${shortName}
        ${getLangIndicator(mod.language)}
        ${mod.disconnected ? '<span class="disconnected-badge">ISOLATED</span>' : ''}
      </div>
    </div>
    <div class="detail-section">
      <div class="detail-title">Path</div>
      <div class="detail-content" style="font-size:11px;">${mod.file}</div>
    </div>
    <div class="mini-stat-grid">
      <div class="mini-stat">
        <div class="mini-stat-label">Functions</div>
        <div class="mini-stat-value">${fnCount}</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-label">Classes</div>
        <div class="mini-stat-value">${clsCount}</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-label">In</div>
        <div class="mini-stat-value">${inDeg}</div>
      </div>
      <div class="mini-stat">
        <div class="mini-stat-label">Out</div>
        <div class="mini-stat-value">${outDeg}</div>
      </div>
    </div>
    <div class="detail-section">
      <div class="detail-title">Connectivity Score</div>
      <div class="detail-content">
        ${total}
        <div class="mini-bar">
          <div class="mini-bar-fill" style="width:${barPercent}%;"></div>
        </div>
      </div>
    </div>
  `;
}

function updateAnalysisPanel() {
  const panel = document.getElementById("analysis-body");
  if (!panel) return;

  if (!centralityData) {
    panel.innerHTML = '<div class="empty-state">No connectivity data.</div>';
    return;
  }

  const all = Object.values(centralityData);
  if (!all.length) {
    panel.innerHTML = '<div class="empty-state">No modules found.</div>';
    return;
  }

  const shortName = id => id.split(".").slice(-1)[0];

  const byTotal = [...all].sort((a, b) => b.total - a.total).slice(0, 5);
  const byIn = [...all].sort((a, b) => b.inDeg - a.inDeg).slice(0, 5);
  const byOut = [...all].sort((a, b) => b.outDeg - a.outDeg).slice(0, 5);

  const disconnectedCount = data.nodes.filter(n => n.disconnected).length;

  let html = `
    <div class="detail-section">
      <div class="detail-title">Core Influence Map</div>
      <div class="detail-content" style="font-size:11px;">
        Total modules: ${all.length}<br>
        Max degree: ${byTotal.length ? byTotal[0].total : 0}<br>
        Isolated modules: ${disconnectedCount}
      </div>
    </div>

    <div class="detail-section">
      <div class="detail-title">Most Connected</div>
      <ul class="detail-list">
        ${byTotal.map(x => `<li>${shortName(x.id)}  (deg: ${x.total})</li>`).join("")}
      </ul>
    </div>

    <div class="detail-section">
      <div class="detail-title">Most Imported (In)</div>
      <ul class="detail-list">
        ${byIn.map(x => `<li>${shortName(x.id)}  (in: ${x.inDeg})</li>`).join("")}
      </ul>
    </div>

    <div class="detail-section">
      <div class="detail-title">Most Importing (Out)</div>
      <ul class="detail-list">
        ${byOut.map(x => `<li>${shortName(x.id)}  (out: ${x.outDeg})</li>`).join("")}
      </ul>
    </div>
  `;

  panel.innerHTML = html;
}

function initFilters(data) {
  // Language filters
  const languages = [...new Set(data.nodes.map(n => n.language))].sort();
  const langContainer = document.getElementById("lang-filters");
  langContainer.innerHTML = "";

  languages.forEach(lang => {
    const btn = document.createElement("button");
    btn.className = "filter-pill active";
    btn.dataset.type = "lang";
    btn.dataset.value = lang;
    btn.textContent = lang;
    btn.onclick = () => {
      btn.classList.toggle("active");
      applyFilters();
    };
    langContainer.appendChild(btn);
  });

  // Group filters
  const groups = [...new Set(data.nodes.map(n => n.group))].sort();
  const container = document.getElementById("group-filters");
  container.innerHTML = "";

  groups.forEach(g => {
    const btn = document.createElement("button");
    btn.className = "filter-pill active";
    btn.dataset.type = "group";
    btn.dataset.value = g;
    btn.textContent = g;
    btn.onclick = () => {
      btn.classList.toggle("active");
      applyFilters();
    };
    container.appendChild(btn);
  });
}

function getActiveFilters() {
  const pills = document.querySelectorAll(".filter-pill");
  const activeLangs = [];
  const activeGroups = [];

  pills.forEach(p => {
    if (p.classList.contains("active")) {
      if (p.dataset.type === "lang") activeLangs.push(p.dataset.value);
      if (p.dataset.type === "group") activeGroups.push(p.dataset.value);
    }
  });
  return { languages: activeLangs, groups: activeGroups };
}

function applyFilters() {
  if (!nodeSelection || !linkSelection) return;
  const { languages, groups } = getActiveFilters();
  const query = document.getElementById("search").value.toLowerCase();
  const complexityThreshold = parseInt(document.getElementById("complexity-slider").value) || 0;
  const activePreset = getActivePreset();
  const visibleNodes = new Set();

  nodeSelection.style("opacity", d => {
    // Basic filters
    const langOk = !languages.length || languages.includes(d.language);
    const groupOk = !groups.length || groups.includes(d.group);
    const searchOk = !query || d.id.toLowerCase().includes(query) || d.file.toLowerCase().includes(query);

    // Complexity filter
    const connections = (d.inDegree || 0) + (d.outDegree || 0);
    const complexityOk = connections >= complexityThreshold;

    // Preset filters
    let presetOk = true;
    if (activePreset) {
      switch (activePreset) {
        case 'hotspots':
          // God modules OR in cycles
          presetOk = d.is_god_module || d.in_cycle;
          break;
        case 'core':
          // High connection count (top 20%)
          presetOk = connections >= 10;
          break;
        case 'leaves':
          // Low outgoing dependencies
          presetOk = (d.outDegree || 0) <= 2;
          break;
        case 'isolated':
          // Orphan nodes
          presetOk = d.disconnected;
          break;
      }
    }

    const visible = langOk && groupOk && searchOk && complexityOk && presetOk;
    if (visible) visibleNodes.add(d.id);
    return visible ? 1 : 0.08;
  });

  linkSelection.style("opacity", l => {
    const s = typeof l.source === "string" ? l.source : l.source.id;
    const t = typeof l.target === "string" ? l.target : l.target.id;
    return (visibleNodes.has(s) && visibleNodes.has(t)) ? 0.8 : 0.05;
  });
}

function getActivePreset() {
  const presets = document.querySelectorAll('[data-preset]');
  for (const preset of presets) {
    if (preset.classList.contains('active')) {
      return preset.dataset.preset;
    }
  }
  return null;
}

function renderGraph(data) {
  const container = document.getElementById("graph");
  const rect = container.getBoundingClientRect();
  const width = rect.width || (window.innerWidth - 320 - 260);
  const height = rect.height || (window.innerHeight - 44);

  // Show loading overlay for large graphs
  const nodeCount = data.nodes.length;
  if (nodeCount > 500) {
    showLoadingOverlay();
    // Use setTimeout to allow UI to update
    setTimeout(() => {
      continueRenderGraph(data, container, width, height);
    }, 50);
  } else {
    continueRenderGraph(data, container, width, height);
  }
}

function continueRenderGraph(data, container, width, height) {
  container.innerHTML = "";
  const tooltip = d3.select("#tooltip");

  mainSvg = d3.select("#graph").append("svg")
    .attr("width", width)
    .attr("height", height);

  mainGroup = mainSvg.append("g");

  const groups = [...new Set(data.nodes.map(n => n.group))];
  const colorGroup = d3.scaleOrdinal()
    .domain(groups)
    .range(["#38bdf8", "#f97316", "#22c55e", "#e11d48", "#a855f7", "#eab308", "#14b8a6", "#f59e0b"]);

  const legendContent = document.getElementById("legend-content");
  legendContent.innerHTML = groups.map(g => `
    <div class="legend-item">
      <div class="legend-circle" style="background:${colorGroup(g)};"></div>
      <span>${g}</span>
    </div>
  `).join("") + `
    <div class="legend-item">
      <div class="legend-circle" style="background:#cbd5e1;"></div>
      <span>disconnected</span>
    </div>
  `;

  linkSelection = mainGroup.append("g")
    .selectAll("line")
    .data(data.links)
    .enter()
    .append("line")
    .attr("stroke", d => {
      const source = typeof d.source === 'string' ? data.nodes.find(n => n.id === d.source) : d.source;
      const target = typeof d.target === 'string' ? data.nodes.find(n => n.id === d.target) : d.target;
      if (source && target && source.language !== target.language) {
        return "#0ff";  // Cyan for cross-language
      }
      return "#08f";
    })
    .attr("stroke-width", d => d.value || 1)
    .attr("stroke-dasharray", d => {
      const source = typeof d.source === 'string' ? data.nodes.find(n => n.id === d.source) : d.source;
      const target = typeof d.target === 'string' ? data.nodes.find(n => n.id === d.target) : d.target;
      if (source && target && source.language !== target.language) {
        return "5,5";  // Dotted for cross-language
      }
      return "0";
    })
    .attr("opacity", 0.4);

  nodeSelection = mainGroup.append("g")
    .selectAll("g")
    .data(data.nodes)
    .enter()
    .append("g")
    .call(
      d3.drag()
        .on("start", dragStart)
        .on("drag", dragged)
        .on("end", dragEnd)
    );

  nodeSelection.append("circle")
    .attr("r", d => {
      const baseSiz = 5;
      const degree = d.degree || 1;
      return Math.min(baseSiz + Math.sqrt(degree) * 2, 15);
    })
    .attr("fill", d => d.disconnected ? "#08f" : colorGroup(d.group))
    .attr("stroke", "#020202")
    .attr("stroke-width", 2);

  nodeSelection.append("text")
    .text(d => d.id.split(".").slice(-1)[0])
    .attr("x", d => {
      const degree = d.degree || 1;
      const radius = Math.min(5 + Math.sqrt(degree) * 2, 15);
      return radius + 4;
    })
    .attr("y", 3)
    .attr("font-size", d => {
      const degree = d.degree || 1;
      return degree > 10 ? "11px" : "10px";
    })
    .attr("font-weight", d => {
      const degree = d.degree || 1;
      return degree > 10 ? "600" : "400";
    })
    .attr("fill", "#0ff")
    .attr("font-family", "Consolas, monospace")
    .style("opacity", d => {
      const degree = d.degree || 1;
      if (degree > 10) return 1;      // Always show important nodes
      if (degree > 5) return 0.8;     // Show medium nodes
      return 0;                        // Hide low-degree nodes (show on hover)
    });

  nodeSelection
    .on("mouseover", function (event, d) {
      // Show label on hover
      d3.select(this).select("text")
        .style("opacity", 1)
        .style("font-weight", "600");

      const inDeg = d.inDegree || 0;
      const outDeg = d.outDegree || 0;
      const total = d.centralityScore || (inDeg + outDeg);
      tooltip
        .style("display", "block")
        .html(
          `<strong>${d.id}</strong><br>` +
          `Language: ${d.language}<br>` +
          `Group: ${d.group}<br>` +
          `Functions: ${d.functions.length}<br>` +
          `Classes: ${d.classes.length}<br>` +
          `In: ${inDeg} | Out: ${outDeg} | Total: ${total}` +
          (d.disconnected ? `<br><span style="color:#cbd5e1;">⚠ Disconnected</span>` : '')
        );
    })
    .on("mousemove", (event) => {
      tooltip
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY + 10) + "px");
    })
    .on("mouseleave", function (event, d) {
      // Restore label opacity
      const degree = d.degree || 1;
      d3.select(this).select("text")
        .style("opacity", degree > 5 ? (degree > 10 ? 1 : 0.8) : 0)
        .style("font-weight", degree > 10 ? "600" : "400");

      tooltip.style("display", "none");
    })
    .on("click", (event, d) => {
      // Check for multi-select mode (Ctrl/Cmd + Click)
      if (event.ctrlKey || event.metaKey) {
        // Multi-select mode
        isMultiSelectMode = true;

        if (selectedNodes.has(d.id)) {
          selectedNodes.delete(d.id);
        } else {
          selectedNodes.add(d.id);
        }

        if (selectedNodes.size === 0) {
          // No nodes selected, reset view
          resetFocusMode();
          return;
        }

        applyMultiSelectFocus();
      } else {
        // Single select mode
        isMultiSelectMode = false;
        selectedNodes.clear();
        currentFocusedNode = d;
        applyFocusMode(d);
      }
    });



  const zoomBehavior = d3.zoom()
    .scaleExtent([0.2, 3])
    .on("zoom", (event) => {
      currentTransform = event.transform;
      mainGroup.attr("transform", currentTransform);

      // Update Level of Detail based on zoom
      updateLOD(event.transform.k);
    });

  mainSvg.call(zoomBehavior);

  // ============================================================
  // ADAPTIVE FORCE LAYOUT - AUTO-OPTIMIZED FOR GRAPH SIZE
  // ============================================================
  const nodeCount = data.nodes.length;
  const forceConfig = getAdaptiveForceConfig(nodeCount);

  updatePerformanceDisplay(forceConfig, nodeCount);

  console.log(`[Performance] Initializing ${forceConfig.mode} mode for ${nodeCount} nodes`);
  console.log(`[Performance] Config:`, forceConfig);

  // Initialize nodes with random positions to prevent clustering at startup
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 3;

  // Check if DAG layout mode is active
  if (currentLayoutMode === 'dag') {
    console.log('[DAG] Computing hierarchical layout...');
    computeDAGLayout(data, width, height);
  } else {
    // Standard force layout - clear any fixed positions first
    data.nodes.forEach(node => {
      node.fx = null;
      node.fy = null;
    });

    // Distribute nodes in a circle initially
    data.nodes.forEach((node, i) => {
      const angle = (i / nodeCount) * 2 * Math.PI;
      const r = radius * Math.sqrt(Math.random());
      node.x = centerX + r * Math.cos(angle);
      node.y = centerY + r * Math.sin(angle);
    });
  }

  simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links)
      .id(d => d.id)
      .distance(forceConfig.linkDistance)
      .strength(forceConfig.linkStrength))
    .force("charge", d3.forceManyBody()
      .strength(forceConfig.chargeStrength))
    .force("center", d3.forceCenter(width / 2, height / 2)
      .strength(forceConfig.centerStrength || 0.05))
    .force("collision", d3.forceCollide()
      .radius(d => {
        const baseSiz = 5;
        const degree = d.degree || 1;
        const nodeRadius = Math.min(baseSiz + Math.sqrt(degree) * 2, 15);
        return nodeRadius + forceConfig.collisionRadius;
      })
      .strength(nodeCount > 200 ? 0.5 : 0.8)
      .iterations(nodeCount > 200 ? 1 : 2))
    .force("cluster", currentLayoutMode === 'dag' ? null : forceCluster())
    .alphaDecay(forceConfig.alphaDecay)
    .velocityDecay(forceConfig.velocityDecay);

  // Check for pre-calculated layout (GPU)
  if (data.layout_precalculated) {
    console.log("[Init] Using pre-calculated GPU layout");
    // Stop simulation immediately to preserve positions
    simulation.stop();

    // Center the pre-calculated layout
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    data.nodes.forEach(d => {
      if (d.x < minX) minX = d.x;
      if (d.x > maxX) maxX = d.x;
      if (d.y < minY) minY = d.y;
      if (d.y > maxY) maxY = d.y;
    });

    const layoutCenterX = (minX + maxX) / 2;
    const layoutCenterY = (minY + maxY) / 2;
    const offsetX = (width / 2) - layoutCenterX;
    const offsetY = (height / 2) - layoutCenterY;

    // Apply offset and release fixed positions
    data.nodes.forEach(d => {
      d.x += offsetX;
      d.y += offsetY;
      d.fx = null;
      d.fy = null;
    });

    // Run a few ticks to stabilize collisions but keep general shape
    simulation.alpha(0.1).restart();

    // Hide loading overlay immediately
    hideLoadingOverlay();
  }

  // In DAG mode, stop simulation and render static layout
  if (currentLayoutMode === 'dag') {
    simulation.stop();
    // Manually trigger one tick to position elements
    linkSelection
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
    nodeSelection.attr("transform", d => `translate(${d.x},${d.y})`);
  }

  // Performance optimization: ultra-aggressive throttling for target FPS
  // Target: 200n=60fps, 350n=50fps, 500n=40fps, 1000n=30fps
  if (nodeCount > 150) {
    let tickCount = 0;
    let rafPending = false;

    // Ultra-aggressive throttling for target FPS
    const tickInterval =
      nodeCount > 1000 ? 8 :   // 1000+ nodes: ~30 FPS
        nodeCount > 500 ? 6 :    // 500-1000 nodes: ~40 FPS
          nodeCount > 350 ? 5 :    // 350-500 nodes: ~50 FPS
            nodeCount > 200 ? 3 : 1; // 200-350 nodes: ~60 FPS, <200: full speed

    simulation.on("tick", () => {
      tickCount++;
      if (tickCount % tickInterval !== 0) return;

      // Use requestAnimationFrame to sync with browser refresh rate
      if (!rafPending) {
        rafPending = true;
        requestAnimationFrame(() => {
          linkSelection
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
          nodeSelection.attr("transform", d => `translate(${d.x},${d.y})`);
          rafPending = false;
        });
      }
    });
  } else {
    let rafPending = false;

    simulation.on("tick", () => {
      // Use requestAnimationFrame for smooth rendering
      if (!rafPending) {
        rafPending = true;
        requestAnimationFrame(() => {
          linkSelection
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
          nodeSelection.attr("transform", d => `translate(${d.x},${d.y})`);
          rafPending = false;
        });
      }
    });
  }

  // Performance monitoring
  const startTime = performance.now();
  let frameCount = 0;

  simulation.on("end", () => {
    const endTime = performance.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    console.log(`[Performance] Simulation complete in ${duration}s (${frameCount} frames)`);

    const perfStatus = document.getElementById("perf-status");
    if (perfStatus) {
      perfStatus.innerHTML += `<br>Stabilized in ${duration}s`;
    }

    // Hide loading overlay when simulation completes
    hideLoadingOverlay();
  });

  // Count frames for performance analysis
  const originalTick = simulation.on("tick");
  simulation.on("tick", function () {
    frameCount++;
    if (originalTick) originalTick.apply(this, arguments);
  });


}

// ============================================================
// FOCUS & DRAG FUNCTIONS (Global Scope)
// ============================================================

function dragStart(event, d) {
  if (!event.active && simulation) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragEnd(event, d) {
  if (!event.active && simulation) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

// Helper function to apply focus mode for a single node
function applyFocusMode(node) {
  const maxHops = show2HopNeighbors ? 2 : 1;
  const result = findNeighbors(node.id, maxHops);
  const unfocusedOpacity = 1 - focusIntensity;

  // Apply styling
  nodeSelection
    .style("opacity", n => result.neighbors.has(n.id) ? 1 : unfocusedOpacity)
    .select("circle")
    .attr("stroke", n => n.id === node.id ? "#f97316" : "#020617")
    .attr("stroke-width", n => n.id === node.id ? 3 : 2);

  nodeSelection.select("text")
    .style("opacity", n => result.neighbors.has(n.id) ? 1 : unfocusedOpacity);

  linkSelection
    .style("opacity", l => result.links.has(l) ? 0.8 : 0.05)
    .attr("stroke", l => {
      const s = typeof l.source === "string" ? l.source : l.source.id;
      const t = typeof l.target === "string" ? l.target : l.target.id;
      return (s === node.id || t === node.id) ? "#f97316" : "#334155";
    })
    .attr("stroke-width", l => result.links.has(l) ? 2 : 1);

  // Show controls
  document.getElementById("reset-focus").style.display = "block";
  document.getElementById("export-focus").style.display = "block";
  document.getElementById("focus-controls").style.display = "flex";

  updateDetails(node);
  updateMiniCard(node);

  // Save state
  saveFocusState();
}

// Helper function to apply focus mode for multiple nodes
function applyMultiSelectFocus() {
  const allConnected = new Set();
  const allLinks = new Set();
  const maxHops = show2HopNeighbors ? 2 : 1;

  // Gather all neighbors of all selected nodes
  selectedNodes.forEach(nodeId => {
    const result = findNeighbors(nodeId, maxHops);
    result.neighbors.forEach(n => allConnected.add(n));
    result.links.forEach(l => allLinks.add(l));
  });

  const unfocusedOpacity = 1 - focusIntensity;

  // Apply styling
  nodeSelection
    .style("opacity", n => allConnected.has(n.id) ? 1 : unfocusedOpacity)
    .select("circle")
    .attr("stroke", n => selectedNodes.has(n.id) ? "#f97316" : "#020617")
    .attr("stroke-width", n => selectedNodes.has(n.id) ? 3 : 2);

  nodeSelection.select("text")
    .style("opacity", n => allConnected.has(n.id) ? 1 : unfocusedOpacity);

  linkSelection
    .style("opacity", l => allLinks.has(l) ? 0.8 : 0.05)
    .attr("stroke", "#f97316")
    .attr("stroke-width", l => allLinks.has(l) ? 2 : 1);

  // Show controls
  document.getElementById("reset-focus").style.display = "block";
  document.getElementById("export-focus").style.display = "block";
  document.getElementById("focus-controls").style.display = "flex";

  // Update details panel to show multi-select info
  updateMultiSelectDetails(Array.from(selectedNodes));

  // Save state
  saveFocusState();
}

// Helper function to update details for multi-select
function updateMultiSelectDetails(nodeIds) {
  const detailsBody = document.getElementById("details-body");
  const nodeCount = nodeIds.length;

  let html = `
    <div class="detail-section">
      <div class="detail-title">Multi-Select Mode</div>
      <div class="detail-content">
        ${nodeCount} node${nodeCount > 1 ? 's' : ''} selected
      </div>
    </div>
  `;

  // Show list of selected nodes
  html += `
    <div class="detail-section">
      <div class="detail-title">Selected Modules</div>
      <ul class="detail-list">
        ${nodeIds.map(id => `<li>${id}</li>`).join("")}
      </ul>
    </div>
  `;

  detailsBody.innerHTML = html;
}

// Helper function to reset focus mode
function resetFocusMode() {
  currentFocusedNode = null;
  selectedNodes.clear();
  isMultiSelectMode = false;

  // Reset all nodes and links to normal state
  nodeSelection
    .style("opacity", 1)
    .select("circle")
    .attr("stroke", "#020617")
    .attr("stroke-width", 2);

  // Restore smart label visibility
  nodeSelection.select("text")
    .style("opacity", d => {
      const degree = d.degree || 1;
      if (degree > 10) return 1;
      if (degree > 5) return 0.8;
      return 0;
    });

  linkSelection
    .style("opacity", 0.4)
    .attr("stroke", d => {
      const source = typeof d.source === 'string' ? data.nodes.find(n => n.id === d.source) : d.source;
      const target = typeof d.target === 'string' ? data.nodes.find(n => n.id === d.target) : d.target;
      if (source && target && source.language !== target.language) {
        return "#38bdf8";
      }
      return "#334155";
    })
    .attr("stroke-width", d => d.value || 1);

  // Hide controls
  document.getElementById("reset-focus").style.display = "none";
  document.getElementById("export-focus").style.display = "none";
  document.getElementById("focus-controls").style.display = "none";

  // Reapply filters
  applyFilters();
}

// ============================================================
// PERSISTENT STATE & EXPORT FUNCTIONALITY
// ============================================================

// Save focus state to localStorage
function saveFocusState() {
  const state = {
    focusedNode: currentFocusedNode ? currentFocusedNode.id : null,
    selectedNodes: Array.from(selectedNodes),
    focusIntensity: focusIntensity,
    show2Hop: show2HopNeighbors,
    forceMode: currentForceMode,
    timestamp: Date.now()
  };

  try {
    localStorage.setItem('visualizer_focus_state', JSON.stringify(state));
    console.log('[State] Focus state saved');
  } catch (e) {
    if (e.name === 'QuotaExceededError') {
      console.warn('[State] localStorage quota exceeded, clearing old data');
      localStorage.removeItem('visualizer_focus_state');
      // Try again after clearing
      try {
        localStorage.setItem('visualizer_focus_state', JSON.stringify(state));
      } catch (e2) {
        console.error('[State] Failed to save state even after clearing:', e2);
      }
    } else {
      console.error('[State] Failed to save focus state:', e);
    }
  }
}

// Restore focus state from localStorage
function restoreFocusState() {
  const saved = localStorage.getItem('visualizer_focus_state');
  if (!saved) return;

  try {
    const state = JSON.parse(saved);

    // Only restore if less than 1 hour old
    if (Date.now() - state.timestamp > 3600000) {
      localStorage.removeItem('visualizer_focus_state');
      console.log('[State] Focus state expired (>1 hour)');
      return;
    }

    // Restore settings
    focusIntensity = state.focusIntensity || 0.85;
    show2HopNeighbors = state.show2Hop || false;
    currentForceMode = state.forceMode || null;

    // Update UI controls
    document.getElementById("focus-intensity").value = focusIntensity * 100;
    document.getElementById("intensity-value").textContent = (focusIntensity * 100) + "%";

    if (show2HopNeighbors) {
      document.getElementById("toggle-2hop").classList.add("active");
      document.getElementById("hop-icon").textContent = "2";
    }

    // Restore focused node(s)
    if (state.selectedNodes && state.selectedNodes.length > 0) {
      state.selectedNodes.forEach(nodeId => {
        const node = data.nodes.find(n => n.id === nodeId);
        if (node) selectedNodes.add(nodeId);
      });

      if (selectedNodes.size > 0) {
        isMultiSelectMode = true;
        applyMultiSelectFocus();
        console.log(`[State] Restored ${selectedNodes.size} selected nodes`);
      }
    } else if (state.focusedNode) {
      const node = data.nodes.find(n => n.id === state.focusedNode);
      if (node) {
        currentFocusedNode = node;
        applyFocusMode(node);
        console.log(`[State] Restored focused node: ${state.focusedNode}`);
      }
    }
  } catch (e) {
    console.error("[State] Failed to restore focus state:", e);
    localStorage.removeItem('visualizer_focus_state');
  }
}

// Export focused subgraph as JSON
function exportFocusSubgraph() {
  if (!currentFocusedNode && selectedNodes.size === 0) {
    console.warn('[Export] No nodes selected for export');
    return;
  }

  // Gather focused nodes and links
  const focusedNodeIds = selectedNodes.size > 0
    ? Array.from(selectedNodes)
    : [currentFocusedNode.id];

  const allConnected = new Set();
  const allLinks = new Set();
  const maxHops = show2HopNeighbors ? 2 : 1;

  focusedNodeIds.forEach(nodeId => {
    const result = findNeighbors(nodeId, maxHops);
    result.neighbors.forEach(n => allConnected.add(n));
    result.links.forEach(l => allLinks.add(l));
  });

  // Create subgraph data
  const subgraphNodes = data.nodes.filter(n => allConnected.has(n.id));
  const subgraphLinks = Array.from(allLinks).map(l => ({
    source: typeof l.source === "string" ? l.source : l.source.id,
    target: typeof l.target === "string" ? l.target : l.target.id,
    value: l.value
  }));

  const subgraph = {
    project_name: data.project_name + " (Focused Subgraph)",
    languages: [...new Set(subgraphNodes.map(n => n.language))],
    stats: {
      total_files: subgraphNodes.length,
      total_functions: subgraphNodes.reduce((sum, n) => sum + (n.functions?.length || 0), 0),
      total_classes: subgraphNodes.reduce((sum, n) => sum + (n.classes?.length || 0), 0)
    },
    nodes: subgraphNodes,
    links: subgraphLinks
  };

  // Download as JSON
  const blob = new Blob([JSON.stringify(subgraph, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  a.download = `subgraph_${focusedNodeIds.join('_').slice(0, 30)}_${timestamp}.json`;
  a.click();
  URL.revokeObjectURL(url);

  console.log(`[Export] Exported subgraph: ${subgraphNodes.length} nodes, ${subgraphLinks.length} links`);
  showNotification(`Exported ${subgraphNodes.length} nodes and ${subgraphLinks.length} links!`);
}

// Show notification message
function showNotification(message) {
  const notification = document.createElement('div');
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 60px;
    right: 20px;
    background: #22c55e;
    color: #000;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    z-index: 10000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    animation: slideIn 0.3s ease-out;
  `;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = 'fadeOut 0.3s ease-in';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

function init() {
  console.log(`[Init] Starting visualization with ${data.nodes.length} nodes and ${data.links.length} links`);

  initStats(data);
  buildAdjacency(data);
  centralityData = computeCentrality(data);
  initFilters(data);
  renderGraph(data);
  applyFilters();
  updateAnalysisPanel();

  // Restore focus state after graph is rendered
  setTimeout(() => restoreFocusState(), 500);

  document.getElementById("search").addEventListener("input", () => applyFilters());

  // Reset focus mode button handler
  document.getElementById("reset-focus").addEventListener("click", () => {
    localStorage.removeItem('visualizer_focus_state'); // Clear saved state
    resetFocusMode();
  });

  // Export subgraph button handler
  document.getElementById("export-focus").addEventListener("click", () => {
    exportFocusSubgraph();
  });

  // Focus intensity slider handler
  document.getElementById("focus-intensity").addEventListener("input", (e) => {
    focusIntensity = parseInt(e.target.value) / 100;
    document.getElementById("intensity-value").textContent = e.target.value + "%";

    // If focus mode is active, reapply with new intensity
    if (currentFocusedNode) {
      applyFocusMode(currentFocusedNode);
    } else if (selectedNodes.size > 0) {
      applyMultiSelectFocus();
    }
  });

  // 2-hop toggle button handler
  document.getElementById("toggle-2hop").addEventListener("click", () => {
    show2HopNeighbors = !show2HopNeighbors;
    const btn = document.getElementById("toggle-2hop");
    const icon = document.getElementById("hop-icon");

    if (show2HopNeighbors) {
      btn.classList.add("active");
      icon.textContent = "2";
    } else {
      btn.classList.remove("active");
      icon.textContent = "1";
    }

    // Reapply focus mode with new hop count
    if (currentFocusedNode) {
      applyFocusMode(currentFocusedNode);
    } else if (selectedNodes.size > 0) {
      applyMultiSelectFocus();
    }
  });

  // Mode switcher click handler
  document.getElementById("perf-mode").addEventListener("click", () => {
    const modes = ["balanced", "medium", "large", "extreme"];
    const currentIndex = modes.indexOf(currentForceMode || "balanced");
    const nextIndex = (currentIndex + 1) % modes.length;
    currentForceMode = modes[nextIndex];

    // Restart simulation with new mode
    restartSimulation();
  });

  // DAG layout toggle handler
  document.getElementById("dag-toggle").addEventListener("click", () => {
    currentLayoutMode = currentLayoutMode === 'force' ? 'dag' : 'force';
    const btn = document.getElementById("dag-toggle");
    btn.textContent = currentLayoutMode === 'dag' ? '🔄 Force Layout' : '📊 DAG Layout';
    btn.style.background = currentLayoutMode === 'dag' ? '#22c55e' : '#1e293b';

    console.log(`[Layout] Switching to ${currentLayoutMode.toUpperCase()} mode`);

    // Re-render graph with new layout
    renderGraph(data);
    applyFilters();
  });

  // Complexity slider handler
  document.getElementById("complexity-slider").addEventListener("input", (e) => {
    document.getElementById("complexity-value").textContent = e.target.value;
    applyFilters();
  });

  // Preset button handlers
  document.querySelectorAll('[data-preset]').forEach(btn => {
    btn.addEventListener("click", () => {
      // Toggle active state
      if (btn.classList.contains('active')) {
        btn.classList.remove('active');
      } else {
        // Deactivate other presets
        document.querySelectorAll('[data-preset]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }
      applyFilters();
    });
  });

  console.log(`[Init] Visualization ready`);
}

// Function to restart simulation with new force configuration
function restartSimulation() {
  if (!simulation) return;

  const nodeCount = data.nodes.length;
  const forceConfig = getAdaptiveForceConfig(nodeCount, currentForceMode);

  // Update performance display
  updatePerformanceDisplay(forceConfig, nodeCount);

  // Update mode badge styling
  const perfMode = document.getElementById("perf-mode");
  perfMode.className = `perf-badge ${forceConfig.mode}`;

  console.log(`[Mode Switch] Switching to ${forceConfig.mode.toUpperCase()} mode`);
  console.log(`[Mode Switch] Config:`, forceConfig);

  // Stop current simulation
  simulation.stop();

  // Update forces with new configuration - must get the force objects and update them
  const linkForce = simulation.force("link");
  if (linkForce) {
    linkForce.distance(forceConfig.linkDistance).strength(forceConfig.linkStrength);
  }

  const chargeForce = simulation.force("charge");
  if (chargeForce) {
    chargeForce.strength(forceConfig.chargeStrength);
  }

  const collisionForce = simulation.force("collision");
  if (collisionForce) {
    collisionForce.radius(d => {
      const baseSiz = 5;
      const degree = d.degree || 1;
      const nodeRadius = Math.min(baseSiz + Math.sqrt(degree) * 2, 15);
      return nodeRadius + forceConfig.collisionRadius;
    });
  }

  // Update simulation parameters
  simulation
    .alphaDecay(forceConfig.alphaDecay)
    .velocityDecay(forceConfig.velocityDecay);

  // Restart simulation with full alpha for smooth transition
  simulation.alpha(1).restart();
}

// Handle window resize
window.addEventListener('resize', () => {
  const width = window.innerWidth;
  const height = window.innerHeight;

  if (mainSvg) {
    mainSvg.attr("width", width).attr("height", height);
  }

  if (simulation) {
    simulation.force("center", d3.forceCenter(width / 2, height / 2));
    simulation.alpha(0.3).restart();
  }
});

// API Integration
const API_URL = 'http://localhost:5000';
let isApiOnline = false;

async function checkApiStatus() {
  try {
    const response = await fetch(`${API_URL}/status`);
    const status = await response.json();
    isApiOnline = true;
    updateApiUI(true);
  } catch (e) {
    isApiOnline = false;
    updateApiUI(false);
  }
}

function updateApiUI(online) {
  const refreshBtn = document.getElementById('refresh-btn');
  if (refreshBtn) refreshBtn.style.display = online ? 'flex' : 'none';

  const statusDot = document.getElementById('api-status-dot');
  if (statusDot) {
    statusDot.className = `api-status-dot ${online ? 'online' : 'offline'}`;
    statusDot.title = online ? "API Online" : "API Offline";
  }
}

async function refreshData() {
  if (!isApiOnline) return;

  const btn = document.getElementById('refresh-btn');
  const originalText = btn.innerHTML;
  btn.innerHTML = '⏳ Refreshing...';
  btn.disabled = true;

  try {
    // Trigger analysis
    const path = data.metadata?.project_path || document.title; // Fallback
    await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: path, use_cache: true })
    });

    // Poll for completion (simple delay for now, ideally websocket or polling status)
    await new Promise(r => setTimeout(r, 2000));

    // Fetch new graph
    const response = await fetch(`${API_URL}/graph`);
    const newData = await response.json();

    // Update data and re-render
    data = newData;
    initStats();
    renderGraph(data);
    applyFilters();

    console.log('Graph refreshed from API');
  } catch (e) {
    console.error('Refresh failed:', e);
    alert('Failed to refresh data from API');
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

// Context Menu Logic
function initContextMenu() {
  const menu = document.createElement('div');
  menu.className = 'context-menu';
  menu.id = 'node-context-menu';
  document.body.appendChild(menu);

  document.addEventListener('click', () => {
    menu.style.display = 'none';
  });

  return menu;
}

function showContextMenu(e, d) {
  e.preventDefault();
  const menu = document.getElementById('node-context-menu') || initContextMenu();

  menu.innerHTML = `
      <div class="context-menu-item" onclick="window.open('vscode://file/${d.id}')">
        📝 Open in Editor
      </div>
      ${isApiOnline ? `
      <div class="context-menu-separator"></div>
      <div class="context-menu-item" onclick="triggerSingleAnalysis('${d.id}')">
        🔄 Re-analyze File
      </div>
      ` : ''}
    `;

  menu.style.left = `${e.pageX}px`;
  menu.style.top = `${e.pageY}px`;
  menu.style.display = 'block';
}

// Expose for context menu
window.triggerSingleAnalysis = async (path) => {
  if (!isApiOnline) return;
  console.log(`Triggering analysis for ${path}`);
  // For now, just trigger full incremental analysis as per current backend capability
  await refreshData();
};

// Initialize API features
setInterval(checkApiStatus, 5000);
checkApiStatus();

// Add Refresh Button to Controls
const controls = document.querySelector('.controls');
if (controls) {
  const refreshBtn = document.createElement('button');
  refreshBtn.id = 'refresh-btn';
  refreshBtn.className = 'refresh-btn';
  refreshBtn.innerHTML = '🔄 Refresh';
  refreshBtn.onclick = refreshData;
  controls.appendChild(refreshBtn);

  const statusDot = document.createElement('div');
  statusDot.id = 'api-status-dot';
  statusDot.className = 'api-status-dot offline';
  controls.appendChild(statusDot);
}

init();
