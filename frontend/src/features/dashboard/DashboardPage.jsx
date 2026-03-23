import { useState } from 'react';
import { hardwareApi, systemApi } from '../../services/api';
import PageSection from '../../components/layout/PageSection';
import Button from '../../components/ui/Button';

export default function DashboardPage() {
  const [speechText, setSpeechText] = useState('');
  const [processList, setProcessList] = useState([]);
  const [scanning, setScanning] = useState(false);

  const handleSpeak = async () => {
    if (!speechText) return;
    await hardwareApi.speak(speechText);
    setSpeechText('');
  };

  const fetchProcesses = async () => {
    setScanning(true);
    try {
      const res = await systemApi.getProcesses();
      setProcessList(res.data.processes);
    } catch (e) {
      console.error('Failed to fetch processes', e);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="app-main">
      <PageSection
        title="Hardware Control"
        subtitle="Torch, vibration, and voice output on your phone"
      >
        <div className="button-group">
          <Button onClick={() => hardwareApi.toggleTorch('on')}>🔦 Torch ON</Button>
          <Button onClick={() => hardwareApi.toggleTorch('off')}>Torch OFF</Button>
          <Button onClick={() => hardwareApi.vibrate()}>📳 Vibrate</Button>
        </div>

        <div className="input-group">
          <input
            type="text"
            placeholder="What should Synapse say?"
            value={speechText}
            onChange={(e) => setSpeechText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSpeak()}
          />
          <Button variant="primary" onClick={handleSpeak}>
            🗣️ Speak
          </Button>
        </div>
      </PageSection>

      <PageSection
        title="System Monitor"
        subtitle="Processes running on your phone (Termux environment)"
        actions={
          <Button variant="primary" onClick={fetchProcesses} disabled={scanning}>
            {scanning ? '⏳ Scanning…' : '🔍 Scan Processes'}
          </Button>
        }
      >
        {processList.length > 0 && (
          <div className="process-list">
            <p>Total: {processList.length}</p>
            <ul>
              {processList.map((proc, index) => (
                <li key={index}>
                  <strong>PID {proc.pid}:</strong> {proc.name}{' '}
                  {proc.username && <em>({proc.username})</em>}
                </li>
              ))}
            </ul>
          </div>
        )}
      </PageSection>
    </div>
  );
}