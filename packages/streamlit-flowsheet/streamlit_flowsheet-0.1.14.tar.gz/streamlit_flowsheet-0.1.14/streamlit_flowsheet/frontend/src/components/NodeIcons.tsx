import React from 'react';

interface IconProps {
  size?: number;
  color?: string;
}

export const TankIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="5" y="10" width="30" height="20" rx="4" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M5 15 L35 15" stroke={color} strokeWidth="1" strokeDasharray="2 2"/>
    <circle cx="20" cy="22" r="2" fill={color}/>
  </svg>
);

export const WellIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 5 L20 35" stroke={color} strokeWidth="2"/>
    <path d="M15 10 L20 5 L25 10" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <rect x="16" y="25" width="8" height="10" fill={color}/>
    <path d="M10 20 L30 20" stroke={color} strokeWidth="1"/>
  </svg>
);

export const SeparatorIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="20" r="15" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M8 20 L32 20" stroke={color} strokeWidth="1" strokeDasharray="3 2"/>
    <path d="M20 5 L20 12" stroke={color} strokeWidth="2"/>
    <path d="M12 32 L12 28" stroke={color} strokeWidth="2"/>
    <path d="M28 32 L28 28" stroke={color} strokeWidth="2"/>
  </svg>
);

export const JointIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="20" r="8" stroke={color} strokeWidth="2" fill={color} fillOpacity="0.2"/>
    <path d="M20 12 L20 5" stroke={color} strokeWidth="2"/>
    <path d="M20 28 L20 35" stroke={color} strokeWidth="2"/>
    <path d="M12 20 L5 20" stroke={color} strokeWidth="2"/>
    <path d="M28 20 L35 20" stroke={color} strokeWidth="2"/>
  </svg>
);

export const PipeIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="5" y="16" width="30" height="8" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M5 20 L35 20" stroke={color} strokeWidth="1" strokeDasharray="4 2"/>
    <circle cx="10" cy="20" r="2" fill={color}/>
    <circle cx="30" cy="20" r="2" fill={color}/>
  </svg>
);

export const InletGeneratorIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="20" height="20" rx="2" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M15 20 L25 20 M20 15 L20 25" stroke={color} strokeWidth="2" strokeLinecap="round"/>
    <path d="M30 20 L35 20" stroke={color} strokeWidth="2"/>
    <path d="M33 17 L35 20 L33 23" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const getNodeIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'tank':
      return TankIcon;
    case 'well':
      return WellIcon;
    case 'sep':
    case 'separator':
      return SeparatorIcon;
    case 'joint':
      return JointIcon;
    case 'pipe':
      return PipeIcon;
    case 'inlgen':
    case 'inlet':
      return InletGeneratorIcon;
    default:
      return JointIcon;
  }
};