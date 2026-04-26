import { useEffect, useState, useCallback } from 'react';
import PageSection from '../../components/layout/PageSection';
import Button from '../../components/ui/Button';
import { servicesApi } from '../../services/api';

// ── ServiceCard Component ──────────────────────────────

function StatusDot({ status }) {
  const cls =
    status === 'running' ? 'status-dot running' :
    status === 'loading' ? 'status-dot loading' :
    'status-dot stopped';
  return <span className={cls} />;
}

function DependencyPill({ name, icon, met }) {
  return (
    <span className={`dependency-pill ${met ? 'met' : 'unmet'}`}>
      {icon} {name}
    </span>
  );
}

function ServiceCard({ service, allServices, onToggle, actionState }) {
  const [logsOpen, setLogsOpen] = useState(false);
  const isLoading = actionState?.loading;
  const lastResult = actionState?.result;
  const displayStatus = isLoading ? 'loading' : service.running ? 'running' : 'stopped';

  // Build dependency info
  const deps = (service.dependencies || []).map((depId) => {
    const dep = allServices.find((s) => s.id === depId);
    return {
      id: depId,
      name: dep?.name || depId,
      icon: dep?.icon || '❓',
      met: dep?.running || false,
    };
  });
  const hasUnmetDeps = deps.some((d) => !d.met);

  // Auto-expand logs when there's a new result
  useEffect(() => {
    if (lastResult) setLogsOpen(true);
  }, [lastResult]);

  const portLabel = (service.ports || []).join(', ');

  return (
    <div className={`svc-card ${service.running ? 'svc-card--running' : ''}`} id={`service-${service.id}`}>
      <div className="svc-card-header">
        <div className="svc-card-identity">
          <span className="svc-card-icon">{service.icon}</span>
          <div>
            <h3 className="svc-card-name">{service.name}</h3>
            <p className="svc-card-meta">
              {service.description}
              {portLabel && <span className="svc-card-port">Port {portLabel}</span>}
            </p>
          </div>
        </div>

        <div className="svc-card-controls">
          <div className="svc-status-label">
            <StatusDot status={displayStatus} />
            <span className="svc-status-text">
              {isLoading ? 'Working…' : service.running ? 'Running' : 'Stopped'}
            </span>
          </div>
          <button
            className={`svc-toggle ${service.running ? 'svc-toggle--on' : ''}`}
            onClick={() => onToggle(service.id, service.running)}
            disabled={isLoading || (!service.running && hasUnmetDeps)}
            title={
              hasUnmetDeps && !service.running
                ? `Requires: ${deps.filter((d) => !d.met).map((d) => d.name).join(', ')}`
                : service.running ? 'Stop service' : 'Start service'
            }
            aria-label={`Toggle ${service.name}`}
          >
            <span className="svc-toggle-knob" />
          </button>
        </div>
      </div>

      {/* Dependency badges */}
      {deps.length > 0 && (
        <div className="svc-deps">
          <span className="svc-deps-label">Requires:</span>
          {deps.map((d) => (
            <DependencyPill key={d.id} name={d.name} icon={d.icon} met={d.met} />
          ))}
        </div>
      )}

      {/* Unmet dependency warning */}
      {hasUnmetDeps && !service.running && (
        <div className="svc-banner svc-banner--warn">
          ⚠️ Cannot start — {deps.filter((d) => !d.met).map((d) => d.name).join(' and ')} must be running first
        </div>
      )}

      {/* Last action result banner */}
      {lastResult && !isLoading && (
        <div className={`svc-banner ${lastResult.success ? 'svc-banner--ok' : 'svc-banner--err'}`}>
          {lastResult.success ? '✓' : '✗'} {lastResult.message}
        </div>
      )}

      {/* Logs section */}
      {lastResult?.logs && (
        <div className="svc-logs-section">
          <button
            className="svc-logs-toggle"
            onClick={() => setLogsOpen(!logsOpen)}
          >
            {logsOpen ? '▾' : '▸'} Logs
          </button>
          {logsOpen && (
            <pre className={`svc-logs ${!lastResult.success ? 'svc-logs--error' : ''}`}>
              {lastResult.logs}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}


// ── Main Page ──────────────────────────────────────────

export default function ServicesPage() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Per-service action state: { [id]: { loading, result } }
  const [actionStates, setActionStates] = useState({});

  const fetchStatus = useCallback(async () => {
    try {
      setError(null);
      const res = await servicesApi.getStatus();
      setServices(res.data.services || []);
    } catch (e) {
      console.error('Failed to fetch service status', e);
      setError('Could not reach Synapse backend. Is the server running?');
      setServices([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const handleToggle = async (serviceId, currentlyRunning) => {
    setActionStates((prev) => ({
      ...prev,
      [serviceId]: { loading: true, result: null },
    }));

    try {
      const action = currentlyRunning ? servicesApi.stop : servicesApi.start;
      const res = await action(serviceId);

      setActionStates((prev) => ({
        ...prev,
        [serviceId]: { loading: false, result: res.data },
      }));
    } catch (e) {
      const detail = e.response?.data?.detail;
      const errorResult = typeof detail === 'object' ? detail : {
        success: false,
        message: typeof detail === 'string' ? detail : (e.message || 'An unknown error occurred'),
        logs: '',
      };

      setActionStates((prev) => ({
        ...prev,
        [serviceId]: { loading: false, result: errorResult },
      }));
    }

    // Refresh all statuses after action
    setTimeout(fetchStatus, 500);
  };

  if (loading) {
    return (
      <div className="app-main">
        <PageSection title="Managed Services" subtitle="Loading service status…">
          <div className="empty-state">
            <span className="empty-state-icon">⏳</span>
          </div>
        </PageSection>
      </div>
    );
  }

  return (
    <div className="app-main">
      {error && (
        <div className="svc-global-error">
          <span>⚠️ {error}</span>
          <Button variant="ghost" onClick={fetchStatus}>Retry</Button>
        </div>
      )}

      <PageSection
        title="Managed Services"
        subtitle="Start, stop, and monitor your Termux services"
        actions={
          <Button variant="primary" onClick={fetchStatus} disabled={loading}>
            ↻ Refresh
          </Button>
        }
      >
        {services.length === 0 && !error ? (
          <div className="empty-state">
            <span className="empty-state-icon">🔗</span>
            <h3>No services registered</h3>
            <p>Service handlers are not loaded. Check the backend configuration.</p>
          </div>
        ) : (
          <div className="svc-stack">
            {services.map((svc) => (
              <ServiceCard
                key={svc.id}
                service={svc}
                allServices={services}
                onToggle={handleToggle}
                actionState={actionStates[svc.id]}
              />
            ))}
          </div>
        )}
      </PageSection>
    </div>
  );
}