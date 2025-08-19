import React, { useState, useCallback, useMemo, useEffect } from 'react';
import ReactFlow, {
  Controls,
  MiniMap,
  Background,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  BackgroundVariant,
  Panel,
} from 'reactflow';
import type { Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import { PanelLeft, PanelLeftClose } from 'lucide-react';
import CustomNode from './CustomNode';
import NodeDetailsPanel from './NodeDetailsPanel';
import NodeHierarchy from './NodeHierarchy';
import type { FlowsheetData, SimulatorObjectNode } from '../types/flowsheet';

interface FlowsheetRendererProps {
  data?: FlowsheetData;
  showNavigationPanel?: boolean;
  showProperties?: boolean;
  showBorder?: boolean;
  theme?: any;
  onSelectionChange?: (selection: any[]) => void;
}

const nodeTypes = {
  custom: CustomNode,
};

const FlowsheetRendererInner: React.FC<FlowsheetRendererProps> = ({ 
  data, 
  showNavigationPanel = true,
  showProperties = true,
  showBorder = true,
  theme = {},
  onSelectionChange
}) => {
  const [currentData] = useState<FlowsheetData | null>(data || null);
  const [selectedNode, setSelectedNode] = useState<{ id: string; label: string; type: string; properties?: any[] } | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [isHierarchyOpen, setIsHierarchyOpen] = useState(showNavigationPanel);

  const handleNodeClick = useCallback((nodeData: { id: string; label: string; type: string; properties?: any[] }) => {
    setSelectedNode(nodeData);
    if (showProperties) {
      setIsPanelOpen(true);
    }
    
    if (onSelectionChange) {
      const nodes = currentData?.simulatorObjectNodes;
      if (nodes) {
        const selectedNodeFull = nodes.find(n => n.id === nodeData.id);
        if (selectedNodeFull) {
          onSelectionChange([{
            id: selectedNodeFull.id,
            name: selectedNodeFull.name,
            type: selectedNodeFull.type,
            properties: selectedNodeFull.properties || []
          }]);
        }
      }
    }
  }, [showProperties, onSelectionChange, currentData]);

  const handlePanelClose = useCallback(() => {
    setIsPanelOpen(false);
    setSelectedNode(null);
    if (onSelectionChange) {
      onSelectionChange([]);
    }
  }, [onSelectionChange]);

  const handlePaneClick = useCallback(() => {
    setIsPanelOpen(false);
    setSelectedNode(null);
    if (onSelectionChange) {
      onSelectionChange([]);
    }
  }, [onSelectionChange]);

  const handleHierarchyNodeSelect = useCallback((node: SimulatorObjectNode) => {
    const nodeData = {
      id: node.id,
      label: node.name,
      type: node.type,
      properties: node.properties,
    };
    handleNodeClick(nodeData);
    
    if (reactFlowInstance.current) {
      const nodeElement = reactFlowInstance.current.getNode(node.id);
      if (nodeElement) {
        reactFlowInstance.current.fitView({
          padding: 0.5,
          duration: 800,
          nodes: [nodeElement],
        });
      }
    }
  }, [handleNodeClick]);

  const reactFlowInstance = React.useRef<any>(null);

  const { nodes: reactFlowNodes, edges: reactFlowEdges } = useMemo(() => {
    if (!currentData) {
      return { nodes: [], edges: [] };
    }
    
    // Handle missing or empty simulatorObjectNodes
    if (!currentData.simulatorObjectNodes || currentData.simulatorObjectNodes.length === 0) {
      return { nodes: [], edges: [] };
    }
    
    const POSITION_SCALE = 2.5;
    const nodes: Node[] = currentData.simulatorObjectNodes.map((node: SimulatorObjectNode) => {
      const originalPos = node.graphicalObject?.position || { x: 0, y: 0 };
      return {
        id: node.id,
        type: 'custom',
        position: { 
          x: originalPos.x * POSITION_SCALE, 
          y: originalPos.y * POSITION_SCALE 
        },
        data: {
          label: node.name,
          type: node.type,
          properties: node.properties,
          showBox: showBorder,
          onNodeClick: handleNodeClick,
          theme: theme,
        },
        selected: selectedNode?.id === node.id,
      };
    });

    // Handle missing or empty simulatorObjectEdges
    const edgesArray = currentData.simulatorObjectEdges || [];
    const edges: Edge[] = edgesArray.map((edge: any) => {
      return {
        id: edge.id,
        source: edge.sourceId,
        target: edge.targetId,
        type: 'straight', // Straight lines connecting node centers
        animated: false,
        style: { 
          stroke: theme.textColor || '#6b7280',
          strokeWidth: 2,
        },
      };
    });

    return { nodes, edges };
  }, [currentData, selectedNode, handleNodeClick, showBorder, theme]);

  const [nodes, setNodes, onNodesChange] = useNodesState(reactFlowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(reactFlowEdges);

  useEffect(() => {
    setNodes(reactFlowNodes);
    setEdges(reactFlowEdges);
  }, [reactFlowNodes, reactFlowEdges, setNodes, setEdges]);

  const onInit = useCallback((instance: any) => {
    reactFlowInstance.current = instance;
    setTimeout(() => {
      instance.fitView({ padding: 0.1 });
    }, 100);
  }, []);

  const containerStyle: React.CSSProperties = {
    width: '100%',
    height: '100%',
    display: 'flex',
    position: 'relative',
    backgroundColor: theme.backgroundColor || '#fff',
  };

  const hierarchyContainerStyle: React.CSSProperties = {
    width: isHierarchyOpen ? '250px' : '0',
    borderRight: isHierarchyOpen ? `1px solid ${theme.borderColor || '#e5e7eb'}` : 'none',
    transition: 'width 0.3s ease',
    overflow: 'hidden',
    backgroundColor: theme.secondaryBackgroundColor || '#f9fafb',
  };

  const flowContainerStyle: React.CSSProperties = {
    flex: 1,
    position: 'relative',
  };

  const toggleButtonStyle: React.CSSProperties = {
    background: theme.backgroundColor || '#fff',
    border: `1px solid ${theme.borderColor || '#e5e7eb'}`,
    borderRadius: '6px',
    padding: '8px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s',
  };

  return (
    <div style={containerStyle}>
      {showNavigationPanel && (
        <div style={hierarchyContainerStyle}>
          {currentData && isHierarchyOpen && currentData.simulatorObjectNodes && (
            <NodeHierarchy
              nodes={currentData.simulatorObjectNodes}
              selectedNodeId={selectedNode?.id}
              onNodeSelect={handleHierarchyNodeSelect}
              theme={theme}
            />
          )}
        </div>
      )}
      
      <div style={flowContainerStyle}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onInit={onInit}
          onPaneClick={handlePaneClick}
          nodeTypes={nodeTypes}
          fitView
          style={{ backgroundColor: theme.backgroundColor || '#fff' }}
        >
          <Background 
            variant={BackgroundVariant.Dots} 
            gap={12} 
            size={1} 
            color={theme.dotColor || '#e5e7eb'}
          />
          <Controls />
          <MiniMap 
            nodeColor={() => theme.primaryColor || '#0ea5e9'}
            style={{
              backgroundColor: theme.backgroundColor || '#fff',
              border: `1px solid ${theme.borderColor || '#e5e7eb'}`,
            }}
          />
          
          {showNavigationPanel && (
            <Panel position="top-left">
              <button
                style={toggleButtonStyle}
                onClick={() => setIsHierarchyOpen(!isHierarchyOpen)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = theme.hoverBackgroundColor || '#f3f4f6';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = theme.backgroundColor || '#fff';
                }}
              >
                {isHierarchyOpen ? (
                  <PanelLeftClose size={18} color={theme.textColor || '#000'} />
                ) : (
                  <PanelLeft size={18} color={theme.textColor || '#000'} />
                )}
              </button>
            </Panel>
          )}
        </ReactFlow>
        
        {showProperties && isPanelOpen && selectedNode && (
          <NodeDetailsPanel 
            node={selectedNode} 
            onClose={handlePanelClose}
            theme={theme}
          />
        )}
      </div>
    </div>
  );
};

const FlowsheetRenderer: React.FC<FlowsheetRendererProps> = (props) => {
  return (
    <ReactFlowProvider>
      <FlowsheetRendererInner {...props} />
    </ReactFlowProvider>
  );
};

export default FlowsheetRenderer;