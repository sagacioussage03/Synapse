export default function CameraPage() {
  // Pointing directly to your phone's IP Webcam app running on port 8081
  const streamUrl = "http://192.168.1.84:8081/video"; 

  return (
    <div className="page-container" style={{ padding: '20px' }}>
      <h2>Security Monitor</h2>
      <div style={{ backgroundColor: '#000', borderRadius: '8px', overflow: 'hidden', maxWidth: '800px' }}>
        <img 
          src={streamUrl} 
          alt="Live Camera Feed" 
          style={{ width: '100%', display: 'block' }}
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'block';
          }}
        />
        <p style={{ display: 'none', color: '#ff4444', padding: '20px', textAlign: 'center' }}>
          Video server offline. Please start IP Webcam on port 8081.
        </p>
      </div>
    </div>
  );
}