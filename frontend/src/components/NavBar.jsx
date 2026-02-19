import { Link, useLocation } from 'react-router-dom';

export default function NavBar() {
  const location = useLocation();

  const linkBaseStyle = {
    color: 'var(--text-muted)',
    textDecoration: 'none',
    fontSize: '0.95rem',
    fontWeight: 500,
    padding: '6px 14px',
    borderRadius: '999px',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
  };

  const makeLinkStyle = (path) => ({
    ...linkBaseStyle,
    ...(location.pathname === path && {
      background: 'var(--accent-soft)',
      color: 'var(--accent)',
    }),
  });

  return (
    <nav
      style={{
        background: 'rgba(3, 9, 25, 0.98)',
        padding: '14px 24px',
        display: 'flex',
        gap: '18px',
        borderBottom: '1px solid var(--border-subtle)',
        alignItems: 'center',
        justifyContent: 'space-between',
        backdropFilter: 'blur(16px)',
      }}
    >
      <Link
        to="/"
        style={{
          color: 'var(--accent)',
          fontSize: '1.1rem',
          fontWeight: 700,
          letterSpacing: '0.04em',
        }}
      >
        🎛️ Synapse Core
      </Link>

      <div style={{ display: 'flex', gap: '8px' }}>
        <Link to="/" style={makeLinkStyle('/')}>
          Control Core
        </Link>
        <Link to="/camera" style={makeLinkStyle('/camera')}>
          👁️ Live Feed
        </Link>
      </div>
    </nav>
  );
}