import React, { useEffect, useState } from "react";
import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
  ComponentProps,
  Theme,
} from "streamlit-component-lib";
import FlowsheetRenderer from "./components/FlowsheetRenderer";
import type { FlowsheetData } from "./types/flowsheet";

interface StreamlitFlowsheetState {
  selectedNodes: any[];
}

class StreamlitFlowsheet extends StreamlitComponentBase<StreamlitFlowsheetState> {
  public state: StreamlitFlowsheetState = {
    selectedNodes: [],
  };

  private getThemeColors = (theme?: Theme) => {
    if (!theme) {
      return {
        backgroundColor: "#ffffff",
        textColor: "#262730",
        primaryColor: "#ff4b4b",
        secondaryBackgroundColor: "#f0f2f6",
        secondaryTextColor: "#808495",
        borderColor: "#e0e2e9",
        hoverBackgroundColor: "#f0f2f6",
        dotColor: "#e0e2e9",
      };
    }

    const isDark = theme.base === "dark";
    
    return {
      backgroundColor: theme.backgroundColor,
      textColor: theme.textColor,
      primaryColor: theme.primaryColor,
      secondaryBackgroundColor: theme.secondaryBackgroundColor,
      secondaryTextColor: isDark ? "#8b92a5" : "#808495",
      borderColor: isDark ? "#3f4458" : "#e0e2e9",
      hoverBackgroundColor: isDark ? "#262c3d" : "#f0f2f6",
      dotColor: isDark ? "#3f4458" : "#e0e2e9",
    };
  };

  private handleSelectionChange = (selection: any[]) => {
    this.setState({ selectedNodes: selection });
    Streamlit.setComponentValue(selection);
  };

  public componentDidMount = () => {
    const height = this.props.args["height"] ?? 800;
    Streamlit.setFrameHeight(height + 2);
  };

  public componentDidUpdate = (prevProps: any) => {
    const height = this.props.args["height"] ?? 800;
    const prevHeight = prevProps.args["height"] ?? 800;
    
    if (height !== prevHeight) {
      Streamlit.setFrameHeight(height + 2);
    }
  };

  public render = (): React.ReactNode => {
    const { theme, args } = this.props;
    const themeColors = this.getThemeColors(theme);
    
    const data: FlowsheetData = args["data"];
    const showNavigationPanel = args["show_navigation_panel"] ?? true;
    const showProperties = args["show_properties"] ?? true;
    const showBorder = args["show_border"] ?? true;
    const height = args["height"] ?? 800;

    const containerStyle: React.CSSProperties = {
      height: `${height}px`,
      width: "100%",
      border: `1px solid ${themeColors.borderColor}`,
      borderRadius: "4px",
      overflow: "hidden",
      boxSizing: "border-box",
    };

    return (
      <div style={containerStyle}>
        <FlowsheetRenderer
          data={data}
          showNavigationPanel={showNavigationPanel}
          showProperties={showProperties}
          showBorder={showBorder}
          theme={themeColors}
          onSelectionChange={this.handleSelectionChange}
        />
      </div>
    );
  };
}

export default withStreamlitConnection(StreamlitFlowsheet);