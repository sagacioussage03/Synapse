import { BrowserRouter, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import DashboardPage from './features/dashboard/DashboardPage';
import CameraPage from './features/camera/CameraPage';
import HealthPage from './features/health/HealthPage';
import ServicesPage from './features/bots/BotsPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <NavBar />
        <main>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/camera" element={<CameraPage />} />
            <Route path="/health" element={<HealthPage />} />
            <Route path="/services" element={<ServicesPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;