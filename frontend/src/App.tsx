import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import BookList from './pages/books/BookList';
import BookUpload from './pages/books/BookUpload';
import BookDetail from './pages/books/BookDetail';
import PersonaList from './pages/personas/PersonaList';
import PersonaDetail from './pages/personas/PersonaDetail';
import AudienceList from './pages/audiences/AudienceList';
import AudienceDetail from './pages/audiences/AudienceDetail';
import OutlineList from './pages/outlines/OutlineList';
import OutlineDetail from './pages/outlines/OutlineDetail';
import OutputList from './pages/outputs/OutputList';
import OutputGenerate from './pages/outputs/OutputGenerate';
import OutputDetail from './pages/outputs/OutputDetail';
import DiffView from './pages/outputs/DiffView';
import HeatmapView from './pages/outputs/HeatmapView';
import EvidenceSearch from './pages/evidence/EvidenceSearch';
import ScriptGenerator from './pages/scripts/ScriptGenerator';
import ScriptViewer from './pages/scripts/ScriptViewer';
import Settings from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="books" element={<BookList />} />
          <Route path="books/upload" element={<BookUpload />} />
          <Route path="books/:bookId" element={<BookDetail />} />
          <Route path="personas" element={<PersonaList />} />
          <Route path="personas/:personaId" element={<PersonaDetail />} />
          <Route path="audiences" element={<AudienceList />} />
          <Route path="audiences/:audienceId" element={<AudienceDetail />} />
          <Route path="outlines" element={<OutlineList />} />
          <Route path="outlines/:outlineId" element={<OutlineDetail />} />
          <Route path="outputs" element={<OutputList />} />
          <Route path="outputs/generate" element={<OutputGenerate />} />
          <Route path="outputs/diff" element={<DiffView />} />
          <Route path="outputs/heatmap" element={<HeatmapView />} />
          <Route path="outputs/:artifactId" element={<OutputDetail />} />
          <Route path="evidence" element={<EvidenceSearch />} />
          <Route path="scripts" element={<ScriptGenerator />} />
          <Route path="scripts/:scriptId" element={<ScriptViewer />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
