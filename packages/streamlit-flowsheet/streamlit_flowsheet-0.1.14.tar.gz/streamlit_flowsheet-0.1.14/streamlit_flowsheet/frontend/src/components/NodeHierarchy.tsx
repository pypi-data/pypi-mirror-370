import React from 'react';
import { getNodeIcon } from './NodeIcons';
import type { SimulatorObjectNode } from '../types/flowsheet';

interface NodeHierarchyProps {
  nodes: SimulatorObjectNode[];
  selectedNodeId?: string | null;
  onNodeSelect: (node: SimulatorObjectNode) => void;
  theme?: any;
}

interface GroupedNodes {
  [key: string]: SimulatorObjectNode[];
}

const NodeHierarchy: React.FC<NodeHierarchyProps> = ({ nodes, selectedNodeId, onNodeSelect, theme = {} }) => {
  // Group nodes by type
  const groupedNodes: GroupedNodes = React.useMemo(() => {
    return nodes.reduce((acc, node) => {
      const type = node.type;
      if (!acc[type]) {
        acc[type] = [];
      }
      acc[type].push(node);
      return acc;
    }, {} as GroupedNodes);
  }, [nodes]);

  // Sort groups by type name and nodes within groups by name
  const sortedGroups = React.useMemo(() => {
    return Object.keys(groupedNodes)
      .sort()
      .map(type => ({
        type,
        nodes: groupedNodes[type].sort((a, b) => {
          const nameA = a.name || '';
          const nameB = b.name || '';
          return nameA.localeCompare(nameB);
        })
      }));
  }, [groupedNodes]);

  const handleNodeClick = (node: SimulatorObjectNode) => {
    onNodeSelect(node);
  };

  const containerStyle: React.CSSProperties = {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: theme.backgroundColor || '#fff',
    color: theme.textColor || '#000',
    overflow: 'hidden',
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px',
    borderBottom: `1px solid ${theme.borderColor || '#e5e7eb'}`,
    backgroundColor: theme.secondaryBackgroundColor || '#f9fafb',
  };

  const headerTitleStyle: React.CSSProperties = {
    margin: 0,
    fontSize: '14px',
    fontWeight: '600',
    color: theme.textColor || '#000',
  };

  const totalCountStyle: React.CSSProperties = {
    fontSize: '12px',
    color: theme.secondaryTextColor || '#6b7280',
  };

  const contentStyle: React.CSSProperties = {
    flex: 1,
    overflowY: 'auto',
    padding: '12px 0',
  };

  const typeGroupStyle: React.CSSProperties = {
    marginBottom: '4px',
  };

  const typeHeaderStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    backgroundColor: theme.secondaryBackgroundColor || '#f9fafb',
    borderBottom: `1px solid ${theme.borderColor || '#e5e7eb'}`,
    fontSize: '12px',
    fontWeight: '600',
    color: theme.textColor || '#000',
    cursor: 'default',
  };

  const typeIconStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    color: theme.secondaryTextColor || '#6b7280',
  };

  const typeNameStyle: React.CSSProperties = {
    flex: 1,
    textTransform: 'capitalize',
  };

  const typeCountStyle: React.CSSProperties = {
    color: theme.secondaryTextColor || '#6b7280',
    fontWeight: 'normal',
  };

  const typeNodesStyle: React.CSSProperties = {
    backgroundColor: theme.backgroundColor || '#fff',
  };

  const nodeItemStyle = (isSelected: boolean): React.CSSProperties => ({
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '6px 16px 6px 32px',
    fontSize: '11px',
    color: isSelected ? (theme.primaryColor || '#3b82f6') : (theme.secondaryTextColor || '#6b7280'),
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    position: 'relative',
    backgroundColor: isSelected ? `${theme.primaryColor || '#3b82f6'}1a` : 'transparent',
    fontWeight: isSelected ? '500' : 'normal',
  });

  const nodeConnectorStyle: React.CSSProperties = {
    width: '12px',
    height: '1px',
    backgroundColor: theme.borderColor || '#e5e7eb',
    position: 'relative',
  };

  const nodeNameStyle: React.CSSProperties = {
    flex: 1,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  };

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <h3 style={headerTitleStyle}>Nodes</h3>
        <span style={totalCountStyle}>({nodes.length})</span>
      </div>
      
      <div style={contentStyle}>
        {sortedGroups.map(({ type, nodes: typeNodes }) => {
          const Icon = getNodeIcon(type);
          
          return (
            <div key={type} style={typeGroupStyle}>
              <div style={typeHeaderStyle}>
                <div style={typeIconStyle}>
                  <Icon size={16} />
                </div>
                <span style={typeNameStyle}>{type}</span>
                <span style={typeCountStyle}>({typeNodes.length})</span>
              </div>
              
              <div style={typeNodesStyle}>
                {typeNodes.map((node) => (
                  <div
                    key={node.id}
                    style={nodeItemStyle(selectedNodeId === node.id)}
                    onClick={() => handleNodeClick(node)}
                    onMouseEnter={(e) => {
                      if (selectedNodeId !== node.id) {
                        e.currentTarget.style.backgroundColor = theme.secondaryBackgroundColor || '#f9fafb';
                        e.currentTarget.style.color = theme.textColor || '#000';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (selectedNodeId !== node.id) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = theme.secondaryTextColor || '#6b7280';
                      }
                    }}
                  >
                    <div style={nodeConnectorStyle}></div>
                    <span style={nodeNameStyle}>{node.name || node.id}</span>
                    {selectedNodeId === node.id && (
                      <div style={{
                        position: 'absolute',
                        left: 0,
                        top: 0,
                        bottom: 0,
                        width: '3px',
                        backgroundColor: theme.primaryColor || '#3b82f6',
                      }}></div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default NodeHierarchy;