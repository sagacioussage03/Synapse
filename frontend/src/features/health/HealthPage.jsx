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

export default function HealthPage() {
  const [health, setHealth] = useState(null);
  const [battery, setBattery] = useState(null);
  const [network, setNetwork] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAll = async () => {
    setLoading(true);
    try {
      // 🟢 Promise.allSettled won't crash if one endpoint fails
      const results = await Promise.allSettled([
        systemApi.getHealth(),
        systemApi.getBattery(),
        systemApi.getNetwork(),
      ]);

      // Grab data if fulfilled, otherwise return null
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
  const mem = health?.memory;
  const disk = health?.disk;
  const netIo = health?.network;

  return (
    <div className="app-main">
      <PageSection
        title="Phone Overview"
        subtitle="CPU, memory, storage and uptime for your Termux host"
        actions={
          <Button variant="primary" onClick={fetchAll} disabled={loading}>
            {loading ? 'Refreshing…' : '↻ Refresh'}
          </Button>
        }
      >
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
          <div>
            <div className="card-subtitle">CPU Usage</div>
            <div style={{ fontSize: '1.6rem', marginTop: 4 }}>{cpuPercent.toFixed(0)}%</div>
            <div className="card-subtitle">
              Cores: {health?.cpu?.cores ?? '-'}
            </div>
            <div
              style={{
                marginTop: 8,
                height: 6,
                borderRadius: 999,
                background: '#111827',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${Math.min(cpuPercent, 100)}%`,
                  height: '100%',
                  background:
                    cpuPercent > 80
                      ? 'linear-gradient(90deg, #f97373, #facc15)'
                      : 'linear-gradient(90deg, #22c55e, #22d3ee)',
                  transition: 'width 0.2s ease-out',
                }}
              />
            </div>
          </div>

          <div>
            <div className="card-subtitle">Memory</div>
            <div style={{ marginTop: 4 }}>
              {formatBytes(mem?.used)} / {formatBytes(mem?.total)}
            </div>
            <div className="card-subtitle">
              Used: {mem ? `${mem.percent.toFixed(0)}%` : '-'}
            </div>
          </div>

          <div>
            <div className="card-subtitle">Storage</div>
            <div style={{ marginTop: 4 }}>
              {formatBytes(disk?.used)} / {formatBytes(disk?.total)}
            </div>
            <div className="card-subtitle">
              Free: {formatBytes(disk?.free)} ({disk ? `${disk.percent.toFixed(0)}% used` : '-'})
            </div>
          </div>

          <div>
            <div className="card-subtitle">Uptime</div>
            <div style={{ marginTop: 4, fontSize: '1.1rem' }}>
              {health?.uptime
                ? formatDuration(health.uptime.uptime_seconds)
                : '-'}
            </div>
          </div>
        </div>
      </PageSection>

      <PageSection
        title="Battery"
        subtitle="Reported by Termux • termux-battery-status"
      >
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24 }}>
          <div>
            <div className="card-subtitle">Level</div>
            <div style={{ fontSize: '1.5rem', marginTop: 4 }}>
              {battery?.percentage ?? '-'}%
            </div>
          </div>
          <div>
            <div className="card-subtitle">Status</div>
            <div style={{ marginTop: 4 }}>
              {battery?.status ?? battery?.health ?? '-'}
            </div>
          </div>
          <div>
            <div className="card-subtitle">Plugged</div>
            <div style={{ marginTop: 4 }}>
              {battery?.plugged ?? '-'}
            </div>
          </div>
          <div>
            <div className="card-subtitle">Temperature</div>
            <div style={{ marginTop: 4 }}>
              {battery?.temperature != null ? `${battery.temperature}°C` : '-'}
            </div>
          </div>
        </div>
      </PageSection>

      <PageSection
        title="Network"
        subtitle="Wi‑Fi status and traffic • termux-wifi-connectioninfo / psutil"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div>
            <div className="card-subtitle">Wi‑Fi Connection</div>
            <pre
              style={{
                marginTop: 4,
                background: '#020617',
                borderRadius: 8,
                padding: 10,
                fontSize: 11,
                maxHeight: 180,
                overflow: 'auto',
              }}
            >
              {network?.wifi
                ? JSON.stringify(network.wifi, null, 2)
                : network?.wifi_error || 'No Wi‑Fi data'}
            </pre>
          </div>

          <div>
            <div className="card-subtitle">Traffic (since boot)</div>
            <div style={{ marginTop: 4, fontSize: '0.9rem' }}>
              Sent: {formatBytes(netIo?.bytes_sent)} • Received:{' '}
              {formatBytes(netIo?.bytes_recv)}
            </div>
          </div>
        </div>
      </PageSection>
    </div>
  );
}