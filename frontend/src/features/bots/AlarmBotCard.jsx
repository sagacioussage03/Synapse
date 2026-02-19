// frontend/src/features/bots/AlarmBotCard.jsx
import { useEffect, useRef, useState } from 'react';
import PageSection from '../../components/layout/PageSection';
import Button from '../../components/ui/Button';
import { alarmApi } from '../../services/api';

const DEFAULT_TIME = '07:00';

export default function AlarmBotCard() {
  const [alarm, setAlarm] = useState({ time: DEFAULT_TIME, active: false });
  const [selectedDate, setSelectedDate] = useState(() => {
    // default to today in YYYY-MM-DD
    const d = new Date();
    return d.toISOString().slice(0, 10);
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [now, setNow] = useState(new Date());
  const saveTimeoutRef = useRef(null);

  // Live clock
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  // Load current alarm config
  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await alarmApi.getAlarm();
        const time = res.data.time || DEFAULT_TIME;
        const active = Boolean(res.data.active);
        setAlarm({ time, active });
      } catch (e) {
        console.error(e);
        setError('Could not load alarm config from phone.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Debounced save of alarm.time + alarm.active
  const scheduleSave = (nextAlarm) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
    saveTimeoutRef.current = setTimeout(async () => {
      setSaving(true);
      setError('');
      try {
        // NOTE: backend currently only expects time + active
        await alarmApi.setAlarm(nextAlarm);
      } catch (e) {
        console.error(e);
        setError('Failed to save alarm to backend.');
      } finally {
        setSaving(false);
      }
    }, 300);
  };

  const handleTimeChange = (e) => {
    const newTime = e.target.value;
    const next = { ...alarm, time: newTime };
    setAlarm(next);
    scheduleSave(next);
  };

  const handleToggle = () => {
    const next = { ...alarm, active: !alarm.active };
    setAlarm(next);
    scheduleSave(next);
  };

  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
    // For now, date is only used for UI / future extension,
    // not yet sent to the backend.
  };

  const formattedNow = now.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
  const formattedDay = now.toLocaleDateString([], {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  });

  // Convenience combined string for display
  const combinedDateTime = `${selectedDate} ${alarm.time}`;

  return (
    <PageSection
      title="Alarm Bot"
      subtitle="Configure your Termux alarm daemon"
      actions={
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Local time: <strong>{formattedNow}</strong> • {formattedDay}
        </span>
      }
    >
      {loading ? (
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Loading alarm settings…
        </p>
      ) : (
        <>
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 18,
              alignItems: 'flex-end',
              marginBottom: 10,
            }}
          >
            <div>
              <div className="card-subtitle">Date</div>
              <input
                type="date"
                value={selectedDate}
                onChange={handleDateChange}
                style={{
                  marginTop: 6,
                  padding: '8px 10px',
                  borderRadius: 10,
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-elevated-soft)',
                  color: 'var(--text-main)',
                  fontSize: '0.9rem',
                }}
              />
            </div>

            <div>
              <div className="card-subtitle">Time</div>
              <input
                type="time"
                value={alarm.time}
                onChange={handleTimeChange}
                style={{
                  marginTop: 6,
                  padding: '8px 10px',
                  borderRadius: 10,
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-elevated-soft)',
                  color: 'var(--text-main)',
                  fontSize: '0.9rem',
                }}
              />
            </div>

            <div>
              <div className="card-subtitle">Status</div>
              <Button
                variant={alarm.active ? 'primary' : 'default'}
                onClick={handleToggle}
                style={{ marginTop: 6 }}
              >
                {alarm.active ? '⏰ Alarm ON' : 'Alarm OFF'}
              </Button>
            </div>
          </div>

          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Next alarm target (UI only): <strong>{combinedDateTime}</strong>
          </p>

          {saving && (
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Saving…
            </p>
          )}
          {error && (
            <p style={{ fontSize: '0.8rem', color: '#f97373' }}>{error}</p>
          )}

          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 8 }}>
            Currently, only the <code>time</code> and <code>active</code> fields
            are sent to your FastAPI backend to keep compatibility with
            <code>alarm_config.json</code>. When you’re ready for per-day or
            multiple alarms, we can extend the backend and your daemon to
            accept a richer JSON structure (e.g. an array of alarms with
            date/day info) while keeping this UI.
          </p>
        </>
      )}
    </PageSection>
  );
}