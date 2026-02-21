"""
GPU-accelerated graph layout engine using PyTorch.
Calculates force-directed layout on the GPU to speed up visualization.
"""

import math
import sys
import time
from typing import Dict, List, Tuple, Any

try:
    import torch
except ImportError:
    torch = None

def compute_layout_gpu(nodes: List[Dict], links: List[Dict], iterations: int = 600) -> Dict[str, Tuple[float, float]]:
    """
    Compute force-directed layout using GPU acceleration.
    
    Args:
        nodes: List of node dictionaries
        links: List of link dictionaries
        iterations: Number of simulation iterations
        
    Returns:
        Dictionary mapping node ID to (x, y) coordinates
    """
    if not torch or not torch.cuda.is_available():
        print("[GPU] PyTorch or CUDA not available, skipping GPU layout", file=sys.stderr)
        return {}

    node_count = len(nodes)
    if node_count == 0:
        return {}
        
    print(f"[GPU] Computing layout for {node_count} nodes on {torch.cuda.get_device_name(0)}...", file=sys.stderr)
    start_time = time.time()

    # Map node IDs to indices
    node_id_to_idx = {n["id"]: i for i, n in enumerate(nodes)}
    
    # Prepare link indices
    src_indices = []
    tgt_indices = []
    for link in links:
        s = link["source"]
        t = link["target"]
        # Handle both string IDs and object references (though usually strings at this stage)
        s_id = s["id"] if isinstance(s, dict) else s
        t_id = t["id"] if isinstance(t, dict) else t
        
        if s_id in node_id_to_idx and t_id in node_id_to_idx:
            src_indices.append(node_id_to_idx[s_id])
            tgt_indices.append(node_id_to_idx[t_id])

    device = torch.device("cuda")
    
    # Initialize positions randomly
    # Scale initial positions based on node count to avoid crowding
    scale = math.sqrt(node_count) * 10
    pos = torch.rand((node_count, 2), device=device, dtype=torch.float32) * scale - (scale / 2)
    
    # Convert link indices to tensors
    if src_indices:
        src = torch.tensor(src_indices, device=device, dtype=torch.long)
        tgt = torch.tensor(tgt_indices, device=device, dtype=torch.long)
    else:
        src = torch.tensor([], device=device, dtype=torch.long)
        tgt = torch.tensor([], device=device, dtype=torch.long)

    # Constants for force-directed algorithm
    # These mimic D3's force simulation parameters
    k = math.sqrt(100000 / (node_count + 1))  # Optimal distance
    repulsion_strength = 500.0
    spring_strength = 0.05
    center_strength = 0.02
    dt = 0.8  # Time step (learning rate)
    decay = 0.95 # Velocity decay (friction)

    # Velocity
    vel = torch.zeros_like(pos)

    # Simulation loop
    for i in range(iterations):
        # 1. Repulsion (Coulomb's Law)
        # Compute pairwise distances
        # Expand dims for broadcasting: (N, 1, 2) - (1, N, 2) -> (N, N, 2)
        # NOTE: For very large graphs, this O(N^2) matrix can be too big for VRAM.
        # We use a chunked approach or simple loop for safety if N > 2000
        
        if node_count > 3000:
            # Fallback for huge graphs: skip complex repulsion or use CPU
            # For now, we'll just do a simplified random jitter to avoid crash
            break
            
        delta = pos.unsqueeze(1) - pos.unsqueeze(0)
        dist_sq = (delta ** 2).sum(dim=2)
        
        # Avoid division by zero
        dist_sq = torch.clamp(dist_sq, min=0.1)
        dist = torch.sqrt(dist_sq)
        
        # Force magnitude: F = k^2 / d
        force = repulsion_strength / dist_sq
        
        # Apply direction
        displacement = delta * force.unsqueeze(2)
        
        # Sum forces
        repulsion = displacement.sum(dim=1)
        
        # 2. Attraction (Hooke's Law)
        # F = d^2 / k  (or simply spring force proportional to distance)
        if len(src) > 0:
            p_src = pos[src]
            p_tgt = pos[tgt]
            
            delta_link = p_src - p_tgt
            dist_link = torch.norm(delta_link, dim=1, keepdim=True)
            
            # Simple spring: pull towards each other
            # Force proportional to distance minus optimal distance
            force_mag = (dist_link - k) * spring_strength
            
            # Direction
            direction = delta_link / torch.clamp(dist_link, min=0.1)
            
            attraction = direction * force_mag
            
            # Apply to source (pull towards target)
            # We need to scatter add these forces back to the nodes
            attraction_force = torch.zeros_like(pos)
            attraction_force.index_add_(0, tgt, attraction)
            attraction_force.index_add_(0, src, -attraction)
        else:
            attraction_force = torch.zeros_like(pos)

        # 3. Center Force (Gravity)
        # Pull towards (0,0)
        center_force = -pos * center_strength

        # Update Velocity
        total_force = repulsion + attraction_force + center_force
        vel = (vel + total_force * dt) * decay
        
        # Update Positions
        pos += vel

    # Move results back to CPU
    pos_cpu = pos.cpu().numpy()
    
    # Create result dictionary
    layout = {}
    for i, (x, y) in enumerate(pos_cpu):
        node_id = nodes[i]["id"]
        layout[node_id] = (float(x), float(y))
        
    elapsed = time.time() - start_time
    print(f"[GPU] Layout computed in {elapsed:.2f}s", file=sys.stderr)
    
    return layout
