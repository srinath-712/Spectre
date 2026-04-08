import { Sidebar } from './components/layout/Sidebar';
import { DocumentViewer } from './components/layout/DocumentViewer';
import { ForensicPanel } from './components/layout/ForensicPanel';
import { BottomBar } from './components/layout/BottomBar';

function App() {
  return (
    <div className="flex h-dvh w-full flex-col overflow-hidden bg-spectre-bg text-spectre-text selection:bg-spectre-accent/30 lg:flex-row">
      {/* 3-Panel Core Layout */}
      <Sidebar />

      <div className="relative min-h-[40vh] min-w-0 flex-1 flex-col lg:flex">
        <DocumentViewer />
        <BottomBar />
      </div>

      <ForensicPanel />
    </div>
  );
}

export default App;
