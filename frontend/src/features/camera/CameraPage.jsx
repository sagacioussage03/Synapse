import PageSection from '../../components/layout/PageSection';

export default function CameraPage() {
  const streamUrl = import.meta.env.VITE_API_BASE
    ? `${import.meta.env.VITE_API_BASE.replace(':8000', ':8081')}/video`
    : 'http://localhost:8081/video';

  return (
    <div className="app-main">
      <PageSection
        title="Security Monitor"
        subtitle="Live feed from your phone camera"
      >
        <div className="camera-container">
          <img
            src={streamUrl}
            alt="Live Camera Feed"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
          <div className="camera-offline">
            <span className="camera-offline-icon">📷</span>
            Video server offline. Please start IP Webcam on port 8081.
          </div>
        </div>
      </PageSection>
    </div>
  );
}