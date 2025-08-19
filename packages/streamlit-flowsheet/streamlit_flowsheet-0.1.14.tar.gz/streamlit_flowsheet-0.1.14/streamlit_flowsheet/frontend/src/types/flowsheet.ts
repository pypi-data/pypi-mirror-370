export interface Position {
  x: number;
  y: number;
}

export interface GraphicalObject {
  position: Position;
}

export interface ReferenceObject {
  address: string;
}

export interface Property {
  name: string;
  referenceObject?: ReferenceObject;
  valueType?: string;
  value?: number | string;
}

export interface SimulatorObjectNode {
  id: string;
  name: string;
  type: string;
  graphicalObject?: GraphicalObject;
  properties?: Property[];
}

export interface SimulatorObjectEdge {
  id: string;
  source: string;
  target: string;
  sourcePort?: string;
  targetPort?: string;
}

export interface FlowsheetData {
  simulatorObjectNodes?: SimulatorObjectNode[];
  simulatorObjectEdges?: SimulatorObjectEdge[];
}