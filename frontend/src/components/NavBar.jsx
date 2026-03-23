import { Link, useLocation } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard', icon: '⚡' },
  { to: '/camera', label: 'Live Feed', icon: '👁️' },
  { to: '/health', label: 'Health', icon: '📊' },
  { to: '/services', label: 'Services', icon: '🔗' },
];

export default function NavBar() {
  const location = useLocation();

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        🎛️ Synapse
      </Link>

      <div className="navbar-links">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`nav-link${location.pathname === link.to ? ' active' : ''}`}
          >
            <span>{link.icon}</span>
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}