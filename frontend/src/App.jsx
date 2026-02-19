import { BrowserRouter, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import DashboardPage from './features/dashboard/DashboardPage';
import CameraPage from './features/camera/CameraPage';
import HealthPage from './features/health/HealthPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        {/* The NavBar stays at the top of every page */}
        <NavBar /> 
        
        {/* The Routes dynamically swap out the page content below the NavBar */}
        <main>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/camera" element={<CameraPage />} />
            <Route path="/health" element={<HealthPage />} />
            <Route path="/bots" element={<BotsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;