import { Link } from 'react-router-dom';

export default function NavBar() {
  return (
    <nav style={{ background: '#222', padding: '15px', display: 'flex', gap: '20px', borderBottom: '2px solid #444' }}>
      <Link to="/" style={{ color: '#00ff00', textDecoration: 'none', fontSize: '18px', fontWeight: 'bold' }}>
        🎛️ Control Core
      </Link>
      <Link to="/camera" style={{ color: '#00ff00', textDecoration: 'none', fontSize: '18px', fontWeight: 'bold' }}>
        👁️ Live Feed
      </Link>
    </nav>
  );
}