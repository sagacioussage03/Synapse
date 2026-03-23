import { useEffect, useState } from 'react';
import PageSection from '../../components/layout/PageSection';
import Button from '../../components/ui/Button';
import { systemApi } from '../../services/api';

function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return '-';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = bytes;
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i++;
  }
  return `${value.toFixed(1)} ${units[i]}`;
}

function formatDuration(seconds) {
  if (!seconds && seconds !== 0) return '-';
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const parts = [];
  if (d) parts.push(`${d}d`);
  if (h) parts.push(`${h}h`);
  if (m) parts.push(`${m}m`);
  if (!parts.length) parts.push(`${seconds}s`);
  return parts.join(' ');
}

function progressColor(pct) {
  if (pct > 85) return 'red';
  if (pct > 60) return 'yellow';
  return 'green';
}

export default function HealthPage() {
  const [health, setHealth] = useState(null);
  const [battery, setBattery] = useState(null);
  const [network, setNetwork] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        systemApi.getHealth(),
        systemApi.getBattery(),
        systemApi.getNetwork(),
      ]);

      setHealth(results[0].status === 'fulfilled' ? results[0].value.data : null);
      setBattery(results[1].status === 'fulfilled' ? results[1].value.data : null);
      setNetwork(results[2].status === 'fulfilled' ? results[2].value.data : null);
    } catch (e) {
      console.error('Critical failure in fetching data', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const cpuPercent = health?.cpu?.percent ?? 0;
  const memPercent = health?.memory?.percent ?? 0;
  const diskPercent = health?.disk?.percent ?? 0;
  const mem = health?.memory;
  const disk = health?.disk;
  const netIo = health?.network;

  return (
    <div className="app-main">
      <PageSection
        title="System Health"
        subtitle="CPU, memory, storage and uptime for your Termux host"
        actions={
          <Button variant="primary" onClick={fetchAll} disabled={loading}>
            {loading ? '⏳ Refreshing…' : '↻ Refresh'}
          </Button>
        }
      >
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">CPU Usage</div>
            <div className="stat-value">{cpuPercent.toFixed(0)}%</div>
            <div className="stat-detail">
              Cores: {health?.cpu?.cores ?? '-'}
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${progressColor(cpuPercent)}`}
                style={{ width: `${Math.min(cpuPercent, 100)}%` }}
              />
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Memory</div>
            <div className="stat-value">{memPercent.toFixed(0)}%</div>
            <div className="stat-detail">
              {formatBytes(mem?.used)} / {formatBytes(mem?.total)}
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${progressColor(memPercent)}`}
                style={{ width: `${Math.min(memPercent, 100)}%` }}
              />
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Storage</div>
            <div className="stat-value">{diskPercent.toFixed(0)}%</div>
            <div className="stat-detail">
              {formatBytes(disk?.free)} free of {formatBytes(disk?.total)}
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${progressColor(diskPercent)}`}
                style={{ width: `${Math.min(diskPercent, 100)}%` }}
              />
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">Uptime</div>
            <div className="stat-value">
              {health?.uptime
                ? formatDuration(health.uptime.uptime_seconds)
                : '-'}
            </div>
            <div className="stat-detail">Since boot</div>
          </div>
        </div>
      </PageSection>

      <PageSection
        title="Battery"
        subtitle="Reported by Termux — termux-battery-status"
      >
        <div className="battery-grid">
          <div className="battery-item">
            <div className="stat-label">Level</div>
            <div className="battery-level">
              {battery?.percentage ?? '-'}%
            </div>
          </div>
          <div className="battery-item">
            <div className="stat-label">Status</div>
            <div style={{ marginTop: 4, fontSize: '1rem' }}>
              {battery?.status ?? battery?.health ?? '-'}
            </div>
          </div>
          <div className="battery-item">
            <div className="stat-label">Plugged</div>
            <div style={{ marginTop: 4 }}>
              {battery?.plugged ?? '-'}
            </div>
          </div>
          <div className="battery-item">
            <div className="stat-label">Temperature</div>
            <div style={{ marginTop: 4 }}>
              {battery?.temperature != null ? `${battery.temperature}°C` : '-'}
            </div>
          </div>
        </div>
      </PageSection>

      <PageSection
        title="Network"
        subtitle="Wi‑Fi status and traffic — termux-wifi-connectioninfo / psutil"
      >
        <div className="network-section">
          <div>
            <div className="stat-label">Wi‑Fi Connection</div>
            <pre className="data-block">
              {network?.wifi
                ? JSON.stringify(network.wifi, null, 2)
                : network?.wifi_error || 'No Wi‑Fi data'}
            </pre>
          </div>

          <div>
            <div className="stat-label">Traffic (since boot)</div>
            <div className="traffic-stats">
              <span>⬆ Sent: {formatBytes(netIo?.bytes_sent)}</span>
              <span>⬇ Received: {formatBytes(netIo?.bytes_recv)}</span>
            </div>
          </div>
        </div>
      </PageSection>
    </div>
  );
}