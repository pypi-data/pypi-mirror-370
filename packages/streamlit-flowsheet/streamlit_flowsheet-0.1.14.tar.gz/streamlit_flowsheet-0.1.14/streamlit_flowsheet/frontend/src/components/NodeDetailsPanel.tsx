import React, { useState } from 'react';
import { X, ChevronDown, ChevronRight, Search } from 'lucide-react';
import { getNodeIcon } from './NodeIcons';

interface NodeDetailsPanelProps {
  node: {
    id: string;
    label: string;
    type: string;
    properties?: any[];
  };
  onClose: () => void;
  theme?: any;
}

const NodeDetailsPanel: React.FC<NodeDetailsPanelProps> = ({ node, onClose, theme = {} }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const Icon = getNodeIcon(node.type);

  const groupedProperties = React.useMemo(() => {
    if (!node.properties) return {};
    
    const groups: Record<string, any[]> = {};
    node.properties.forEach(prop => {
      const category = prop.category || 'General';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(prop);
    });
    return groups;
  }, [node.properties]);

  const filteredProperties = React.useMemo(() => {
    if (!searchTerm) return groupedProperties;
    
    const filtered: Record<string, any[]> = {};
    Object.entries(groupedProperties).forEach(([category, props]) => {
      const filteredProps = props.filter(prop =>
        prop.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        prop.value?.toString().toLowerCase().includes(searchTerm.toLowerCase())
      );
      if (filteredProps.length > 0) {
        filtered[category] = filteredProps;
      }
    });
    return filtered;
  }, [groupedProperties, searchTerm]);

  React.useEffect(() => {
    setExpandedGroups(new Set(Object.keys(groupedProperties)));
  }, [groupedProperties]);

  const toggleGroup = (group: string) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(group)) {
        newSet.delete(group);
      } else {
        newSet.add(group);
      }
      return newSet;
    });
  };

  const formatValue = (value: any) => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'number') {
      return value % 1 === 0 ? value.toString() : value.toFixed(4);
    }
    return value.toString();
  };

  const panelStyle: React.CSSProperties = {
    position: 'absolute',
    right: 0,
    top: 0,
    bottom: 0,
    width: '320px',
    backgroundColor: theme.backgroundColor || '#fff',
    borderLeft: `1px solid ${theme.borderColor || '#e5e7eb'}`,
    display: 'flex',
    flexDirection: 'column',
    zIndex: 10,
    boxShadow: '-2px 0 10px rgba(0,0,0,0.1)',
    color: theme.textColor || '#000',
  };

  const headerStyle: React.CSSProperties = {
    padding: '16px',
    borderBottom: `1px solid ${theme.borderColor || '#e5e7eb'}`,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: theme.secondaryBackgroundColor || '#f9fafb',
  };

  const titleStyle: React.CSSProperties = {
    fontSize: '16px',
    fontWeight: '600',
    color: theme.textColor || '#000',
  };

  const closeButtonStyle: React.CSSProperties = {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    padding: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '4px',
    transition: 'background-color 0.2s',
  };

  const nodeInfoStyle: React.CSSProperties = {
    padding: '16px',
    borderBottom: `1px solid ${theme.borderColor || '#e5e7eb'}`,
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  };

  const searchContainerStyle: React.CSSProperties = {
    padding: '12px 16px',
    borderBottom: `1px solid ${theme.borderColor || '#e5e7eb'}`,
  };

  const searchInputStyle: React.CSSProperties = {
    width: '100%',
    padding: '8px 12px 8px 36px',
    border: `1px solid ${theme.borderColor || '#e5e7eb'}`,
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: theme.backgroundColor || '#fff',
    color: theme.textColor || '#000',
  };

  const contentStyle: React.CSSProperties = {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
  };

  const groupHeaderStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    padding: '8px 0',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    color: theme.textColor || '#000',
  };

  const propertyItemStyle: React.CSSProperties = {
    padding: '8px 0 8px 20px',
    borderBottom: `1px solid ${theme.borderColor || '#f3f4f6'}`,
    fontSize: '13px',
  };

  const propertyNameStyle: React.CSSProperties = {
    color: theme.secondaryTextColor || '#6b7280',
    marginBottom: '2px',
  };

  const propertyValueStyle: React.CSSProperties = {
    color: theme.textColor || '#000',
    fontWeight: '500',
  };

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        <h3 style={titleStyle}>Node Details</h3>
        <button
          style={closeButtonStyle}
          onClick={onClose}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = theme.hoverBackgroundColor || '#e5e7eb';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          <X size={20} color={theme.textColor || '#000'} />
        </button>
      </div>
      
      <div style={nodeInfoStyle}>
        <Icon size={32} color={theme.primaryColor || '#0ea5e9'} />
        <div>
          <div style={{ fontWeight: '600', fontSize: '14px', color: theme.textColor || '#000' }}>{node.label}</div>
          <div style={{ fontSize: '12px', color: theme.secondaryTextColor || '#6b7280' }}>Type: {node.type}</div>
          <div style={{ fontSize: '11px', color: theme.secondaryTextColor || '#9ca3af' }}>ID: {node.id}</div>
        </div>
      </div>

      {node.properties && node.properties.length > 0 && (
        <>
          <div style={searchContainerStyle}>
            <div style={{ position: 'relative' }}>
              <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} color={theme.secondaryTextColor || '#9ca3af'} />
              <input
                type="text"
                placeholder="Search properties..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={searchInputStyle}
              />
            </div>
          </div>

          <div style={contentStyle}>
            {Object.entries(filteredProperties).length === 0 ? (
              <div style={{ textAlign: 'center', color: theme.secondaryTextColor || '#9ca3af', padding: '20px' }}>
                No properties found
              </div>
            ) : (
              Object.entries(filteredProperties).map(([category, props]) => (
                <div key={category}>
                  <div style={groupHeaderStyle} onClick={() => toggleGroup(category)}>
                    {expandedGroups.has(category) ? (
                      <ChevronDown size={16} color={theme.textColor || '#000'} />
                    ) : (
                      <ChevronRight size={16} color={theme.textColor || '#000'} />
                    )}
                    <span>{category} ({props.length})</span>
                  </div>
                  
                  {expandedGroups.has(category) && (
                    <div>
                      {props.map((prop, index) => (
                        <div key={index} style={propertyItemStyle}>
                          <div style={propertyNameStyle}>{prop.name}</div>
                          <div style={propertyValueStyle}>{formatValue(prop.value)}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default NodeDetailsPanel;