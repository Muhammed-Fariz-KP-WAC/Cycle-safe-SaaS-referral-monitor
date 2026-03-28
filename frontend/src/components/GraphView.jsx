import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const NODE_WIDTH = 190;
const NODE_HEIGHT = 104;
const HORIZONTAL_GAP = 260;
const VERTICAL_GAP = 150;

function shortenId(value) {
  if (!value) {
    return "Unknown";
  }

  if (value.length <= 12) {
    return value;
  }

  return `${value.slice(0, 8)}...${value.slice(-4)}`;
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

function buildReactFlowNodes(nodes, rootId) {
  const depthMap = buildDepthMap(nodes);
  const sortedDepths = [...depthMap.keys()].sort((left, right) => left - right);

  return sortedDepths.flatMap((depth) => {
    const depthNodes = [...(depthMap.get(depth) || [])].sort((left, right) =>
      left.data.label.localeCompare(right.data.label),
    );
    const totalHeight = Math.max(0, (depthNodes.length - 1) * VERTICAL_GAP);
    const offsetY = totalHeight / 2;

    return depthNodes.map((node, index) => {
      const isRoot = node.id === rootId;
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
        style: {
          width: NODE_WIDTH,
          minHeight: NODE_HEIGHT,
        },
        className: `graph-flow-node depth-${node.data.depth}${isRoot ? " is-root" : ""}`,
        sourcePosition: "right",
        targetPosition: "left",
      };
    });
  });
}

function buildReactFlowEdges(edges) {
  return edges.map((edge) => {
    const isSecondary = edge.type === "secondary";

    return {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: "smoothstep",
      animated: isSecondary,
      label: isSecondary ? "secondary" : "reward",
      labelStyle: {
        fill: isSecondary ? "#8f5a28" : "#165d50",
        fontSize: 11,
        fontWeight: 600,
      },
      style: {
        stroke: isSecondary ? "#c3844c" : "#165d50",
        strokeWidth: isSecondary ? 2 : 2.5,
        strokeDasharray: isSecondary ? "7 5" : undefined,
      },
      markerEnd: {
        type: "arrowclosed",
        color: isSecondary ? "#c3844c" : "#165d50",
      },
    };
  });
}

function GraphCanvas({ graph }) {
  const nodes = buildReactFlowNodes(graph.nodes, graph.root.id);
  const edges = buildReactFlowEdges(graph.edges);

  return (
    <div className="graph-canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.18, minZoom: 0.55 }}
        minZoom={0.35}
        maxZoom={1.5}
        nodesConnectable={false}
        nodesDraggable={false}
        elementsSelectable
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={18} size={1} color="#d8c9b3" />
        <MiniMap
          pannable
          zoomable
          nodeColor={(node) => {
            if (node.className?.includes("is-root")) {
              return "#7c6f64";
            }

            if (node.className?.includes("depth-1")) {
              return "#165d50";
            }

            return "#c3844c";
          }}
        />
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
        {graph ? (
          <span className="live-pill">
            Depth {graph.total_depth} · {graph.total_descendants} descendants
          </span>
        ) : null}
      </div>
      <div className="graph-selector-grid">
        <label className="field">
          <span>View graph for user</span>
          <select value={selectedUserId} onChange={(event) => onSelectUserId(event.target.value)}>
            <option value="">Choose user</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name} ({user.referral_code})
              </option>
            ))}
          </select>
        </label>
        {selectedUser ? (
          <article className="graph-selected-user">
            <p>Selected</p>
            <strong>{selectedUser.name}</strong>
            <small>
              {selectedUser.referral_code} · Rs {selectedUser.reward_balance}
            </small>
          </article>
        ) : null}
      </div>
      <label className="field">
        <span>Selected user ID</span>
        <input
          value={selectedUserId}
          onChange={(event) => onSelectUserId(event.target.value)}
          placeholder="Paste user UUID"
        />
      </label>
      {!graph ? (
        <p className="empty-state">
          Choose a user from the dropdown or paste a user ID to inspect that individual referral tree.
        </p>
      ) : (
        <>
          <div className="graph-toolbar">
            <article className="graph-summary-card">
              <p>Root user</p>
              <strong>{graph.root.name}</strong>
              <small>{shortenId(graph.root.id)}</small>
            </article>
            <article className="graph-summary-card">
              <p>Reward balance</p>
              <strong>Rs {graph.root.reward_balance}</strong>
              <small>{graph.root.status}</small>
            </article>
            <article className="graph-summary-card">
              <p>Legend</p>
              <strong>Solid = reward</strong>
              <small>Dashed = secondary</small>
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
