import { useState } from 'react';
import { hardwareApi, systemApi } from '../../services/api';

export default function DashboardPage() {
  const [speechText, setSpeechText] = useState('');
  const [processList, setProcessList] = useState([]);

  const handleSpeak = async () => {
    if (speechText) await hardwareApi.speak(speechText);
    setSpeechText('');
  };

  const fetchProcesses = async () => {
    const res = await systemApi.getProcesses();
    setProcessList(res.data.processes); 
  };

  return (
    <div style={{ padding: '20px' }}>
      <div className="card">
        <h2>Hardware Control</h2>
        <div className="button-group">
          <button onClick={() => hardwareApi.toggleTorch('on')}>🔦 Torch ON</button>
          <button onClick={() => hardwareApi.toggleTorch('off')}>Torch OFF</button>
          <button onClick={() => hardwareApi.vibrate()}>📳 Vibrate</button>
        </div>

        <div className="input-group" style={{ marginTop: '15px' }}>
          <input 
            type="text" 
            placeholder="What should I say?" 
            value={speechText}
            onChange={(e) => setSpeechText(e.target.value)}
          />
          <button onClick={handleSpeak}>🗣️ Speak</button>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h2>System Monitor</h2>
        <button onClick={fetchProcesses}>🔍 Scan Processes</button>
        
        {processList.length > 0 && (
          <div className="process-list" style={{ maxHeight: '200px', overflowY: 'auto', marginTop: '10px', textAlign: 'left', background: '#222', padding: '10px', borderRadius: '5px' }}>
            <p>Total: {processList.length}</p>
            <ul>
              {processList.map((proc, index) => (
                <li key={index} style={{ fontSize: '12px', listStyle: 'none' }}>
                  <strong>PID {proc.pid}:</strong> {proc.name} <em>({proc.username})</em>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}