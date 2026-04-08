import React from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { DocumentViewer } from './components/layout/DocumentViewer';
import { ForensicPanel } from './components/layout/ForensicPanel';
import { BottomBar } from './components/layout/BottomBar';

function App() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-spectre-bg text-spectre-text selection:bg-spectre-accent/30">
      
      {/* 3-Panel Core Layout */}
      <Sidebar />
      
      <div className="flex-1 flex flex-col relative min-w-0">
        <DocumentViewer />
        <BottomBar />
      </div>

      <ForensicPanel />
      
    </div>
  );
}

export default App;
