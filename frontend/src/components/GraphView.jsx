import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import { useEffect, useState, useMemo } from "react";
import "@xyflow/react/dist/style.css";

const NODE_WIDTH = 190;
const NODE_HEIGHT = 104;
const HORIZONTAL_GAP = 260;
const VERTICAL_GAP = 150;

function shortenId(value) {
  if (!value) return "Unknown";
  return value.length <= 12 ? value : `${value.slice(0, 8)}...${value.slice(-4)}`;
}

function buildDepthMap(nodes) {
  const grouped = new Map();
  nodes.forEach((node) => {
    const depth = Number(node.data?.depth || 0);
    const current = grouped.get(depth) || [];
    current.push(node);
    grouped.set(depth, current);
  });
  return grouped;
}

function GraphCanvas({ graph }) {
  const [highlightedNodeId, setHighlightedNodeId] = useState(null);

  const ancestryMap = useMemo(() => {
    const map = new Map();
    graph.nodes.forEach(n => map.set(n.id, n.data.ancestry || []));
    return map;
  }, [graph.nodes]);

  const initialNodes = useMemo(() => {
    const depthMap = buildDepthMap(graph.nodes);
    const sortedDepths = [...depthMap.keys()].sort((a, b) => a - b);

    return sortedDepths.flatMap((depth) => {
      const depthNodes = [...(depthMap.get(depth) || [])].sort((a, b) =>
        a.data.label.localeCompare(b.data.label)
      );
      const totalHeight = (depthNodes.length - 1) * VERTICAL_GAP;
      const offsetY = totalHeight / 2;

      return depthNodes.map((node, index) => {
        const isRoot = node.id === graph.root.id;
        const isInactive = node.data.status !== "active";

        return {
          id: node.id,
          position: {
            x: depth * HORIZONTAL_GAP,
            y: index * VERTICAL_GAP - offsetY,
          },
          draggable: false,
          selectable: true,
          data: {
            ...node.data,
            label: (
              <div className="graph-card">
                <div className="graph-card-head">
                  <strong>{node.data.label}</strong>
                  <span className={`status-chip ${isInactive ? "is-muted" : "is-live"}`}>
                    {node.data.status}
                  </span>
                </div>
                <p>{shortenId(node.id)}</p>
                <div className="graph-card-meta">
                  <small>Depth {node.data.depth}</small>
                  <small>Rs {node.data.reward_balance}</small>
                </div>
              </div>
            ),
          },
          style: { width: NODE_WIDTH, minHeight: NODE_HEIGHT },
          className: `graph-flow-node depth-${node.data.depth}${isRoot ? " is-root" : ""}`,
          sourcePosition: "right",
          targetPosition: "left",
        };
      });
    });
  }, [graph.nodes, graph.root.id]);

  const initialEdges = useMemo(() => {
    return graph.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: "smoothstep",
      label: "reward",
      labelStyle: { fill: "var(--accent)", fontSize: 11, fontWeight: 800 },
      style: { stroke: "var(--line)", strokeWidth: 3 },
      markerEnd: { type: "arrowclosed", color: "var(--line)" },
    }));
  }, [graph.edges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
    setHighlightedNodeId(null);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  useEffect(() => {
    const activeAncestry = highlightedNodeId ? (ancestryMap.get(highlightedNodeId) || []) : [];
    
    setNodes((nds) => nds.map((node) => {
      const isHighlighted = activeAncestry.includes(node.id) || node.id === highlightedNodeId;
      const opacity = highlightedNodeId ? (isHighlighted ? 1 : 0.3) : 1;
      const borderColor = isHighlighted ? "var(--accent)" : "var(--line)";
      const borderSize = isHighlighted ? "3px" : "2px";

      return {
        ...node,
        style: { ...node.style, opacity, borderColor, borderWidth: borderSize, transition: 'all 0.3s ease' },
      };
    }));

    setEdges((eds) => eds.map((edge) => {
      const isPath = activeAncestry.includes(edge.source) && activeAncestry.includes(edge.target);
      const isDirect = activeAncestry.includes(edge.source) && edge.target === highlightedNodeId;
      const isHighlighted = isPath || isDirect;
      
      const opacity = highlightedNodeId ? (isHighlighted ? 1 : 0.15) : 1;
      const stroke = isHighlighted ? "var(--accent)" : "var(--line)";
      const strokeWidth = isHighlighted ? 4 : 3;

      return {
        ...edge,
        animated: isHighlighted,
        style: { ...edge.style, stroke, strokeWidth, opacity, transition: 'all 0.3s ease' },
        markerEnd: { ...edge.markerEnd, color: stroke },
      };
    }));
  }, [highlightedNodeId, ancestryMap, setNodes, setEdges]);

  return (
    <div className="graph-canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={(_, node) => setHighlightedNodeId(node.id)}
        onPaneClick={() => setHighlightedNodeId(null)}
        fitView
        fitViewOptions={{ padding: 0.2, minZoom: 0.5 }}
        minZoom={0.2}
        maxZoom={2}
        nodesConnectable={false}
        nodesDraggable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={24} size={1} color="var(--line)" />
        <MiniMap pannable zoomable />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

export default function GraphView({ graph, users, selectedUserId, onSelectUserId }) {
  const selectedUser = users.find((user) => user.id === selectedUserId);

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Referral Graph</h2>
        {graph && (
          <span className="live-pill">
            Depth {graph.total_depth} · {graph.total_descendants} descendants
          </span>
        )}
      </div>
      <div className="graph-selector-grid">
        <label className="field">
          <span>View graph for user</span>
          <select value={selectedUserId} onChange={(e) => onSelectUserId(e.target.value)}>
            <option value="">Choose user</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name} ({u.referral_code})
              </option>
            ))}
          </select>
        </label>
        {selectedUser && (
          <article className="graph-selected-user">
            <p>Root context</p>
            <strong>{selectedUser.name}</strong>
            <small>{selectedUser.referral_code} · Rs {selectedUser.reward_balance}</small>
          </article>
        )}
      </div>
      {!graph ? (
        <p className="empty-state">Choose a user to inspect their referral tree.</p>
      ) : (
        <>
          <div className="graph-toolbar">
            <article className="graph-summary-card">
              <p>Graph root</p>
              <strong>{graph.root.name}</strong>
              <small>{shortenId(graph.root.id)}</small>
            </article>
            <article className="graph-summary-card">
              <p>Reward total</p>
              <strong>Rs {graph.root.reward_balance}</strong>
              <small>System {graph.root.status}</small>
            </article>
            <article className="graph-summary-card">
              <p>Interaction</p>
              <strong>Click a node</strong>
              <small>to trace its path</small>
            </article>
          </div>
          <ReactFlowProvider>
            <GraphCanvas graph={graph} />
          </ReactFlowProvider>
        </>
      )}
    </section>
  );
}
