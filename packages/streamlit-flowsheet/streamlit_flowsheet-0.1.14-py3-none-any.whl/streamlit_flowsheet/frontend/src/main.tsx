import React from "react";
import ReactDOM from "react-dom/client";
import StreamlitFlowsheet from "./StreamlitFlowsheet";
import "./index.css";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <React.StrictMode>
    <StreamlitFlowsheet />
  </React.StrictMode>
);