// frontend/src/features/bots/BotsPage.jsx

export default function BotsPage() {
  return (
    <div className="app-main">
      <div style={{
        textAlign: 'center',
        padding: '60px 20px',
        color: 'var(--text-muted)',
      }}>
        <h2 style={{ color: 'var(--text-main)', marginBottom: 12 }}>📦 Apps</h2>
        <p style={{ maxWidth: 420, margin: '0 auto', lineHeight: 1.6 }}>
          This is your app launcher. Companion apps you build
          (e.g. cloud storage uploader) will appear here.
        </p>
      </div>
    </div>
  );
}