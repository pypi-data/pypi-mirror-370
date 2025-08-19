import React from 'react';
import { Handle, Position } from 'reactflow';
import type { NodeProps } from 'reactflow';
import { getNodeIcon } from './NodeIcons';

interface CustomNodeData {
  label: string;
  type: string;
  properties?: any[];
  showBox: boolean;
  onNodeClick?: (nodeData: any) => void;
  theme?: any;
}

const CustomNode: React.FC<NodeProps<CustomNodeData>> = ({ id, data, selected }) => {
  const Icon = getNodeIcon(data.type);
  const theme = data.theme || {};
  
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (data.onNodeClick) {
      data.onNodeClick({
        id,
        label: data.label,
        type: data.type,
        properties: data.properties,
      });
    }
  };

  const nodeStyle = {
    padding: '10px',
    borderRadius: '8px',
    background: theme.backgroundColor || '#fff',
    border: data.showBox ? `2px solid ${selected ? theme.primaryColor || '#0ea5e9' : theme.textColor || '#d1d5db'}` : 'none',
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: selected ? `0 0 0 2px ${theme.primaryColor || '#0ea5e9'}33` : undefined,
  };

  const labelStyle = {
    marginTop: '8px',
    fontSize: '12px',
    fontWeight: selected ? '600' : '500',
    textAlign: 'center' as const,
    color: theme.textColor || '#000',
  };

  const iconColor = selected ? (theme.primaryColor || '#0ea5e9') : (theme.textColor || '#6b7280');

  // Invisible handle style - positioned at center
  const handleStyle = {
    background: 'transparent',
    border: 'none',
    width: '1px',
    height: '1px',
    minWidth: '1px',
    minHeight: '1px',
  };

  return (
    <div style={nodeStyle} onClick={handleClick}>
      {/* Single source and target handle at the center */}
      <Handle 
        type="source" 
        position={Position.Right}
        style={{
          ...handleStyle,
          right: '50%',
          top: '50%',
          transform: 'translate(50%, -50%)',
        }}
      />
      <Handle 
        type="target" 
        position={Position.Left}
        style={{
          ...handleStyle,
          left: '50%',
          top: '50%',
          transform: 'translate(-50%, -50%)',
        }}
      />
      
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Icon size={40} color={iconColor} />
        <div style={labelStyle}>{data.label}</div>
      </div>
    </div>
  );
};

export default CustomNode;