import PageSection from '../../components/layout/PageSection';

export default function CameraPage() {
  const streamUrl = 'http://192.168.1.84:8081/video';

  return (
    <div className="app-main">
      <PageSection
        title="Security Monitor"
        subtitle="Live feed from your phone camera"
      >
        <div
          style={{
            backgroundColor: '#000',
            borderRadius: '12px',
            overflow: 'hidden',
            maxWidth: '900px',
            marginTop: '8px',
          }}
        >
          <img
            src={streamUrl}
            alt="Live Camera Feed"
            style={{ width: '100%', display: 'block' }}
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
          <p
            style={{
              display: 'none',
              color: '#ff7171',
              padding: '20px',
              textAlign: 'center',
              fontSize: '0.9rem',
            }}
          >
            Video server offline. Please start IP Webcam on port 8081.
          </p>
        </div>
      </PageSection>
    </div>
  );
}