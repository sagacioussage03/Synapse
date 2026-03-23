import { useEffect, useState } from 'react';
import PageSection from '../../components/layout/PageSection';
import { configApi } from '../../services/api';

export default function ServicesPage() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    configApi.getServices()
      .then((res) => setServices(res.data.services || []))
      .catch(() => setServices([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="app-main">
        <PageSection title="Services" subtitle="Loading...">
          <div className="empty-state">
            <span className="empty-state-icon">⏳</span>
          </div>
        </PageSection>
      </div>
    );
  }

  if (services.length === 0) {
    return (
      <div className="app-main">
        <PageSection
          title="Managed Services"
          subtitle="Apps, databases, and companion services you control"
        >
          <div className="empty-state">
            <span className="empty-state-icon">🔗</span>
            <h3>No services configured</h3>
            <p>
              Add services to <code>config.yaml</code> and they will appear here.
              <br />
              Synapse can track health of any HTTP service, SQL server, or companion app.
            </p>
          </div>
        </PageSection>
      </div>
    );
  }

  return (
    <div className="app-main">
      <PageSection
        title="Managed Services"
        subtitle="Apps, databases, and companion services you control"
      >
        <div className="services-grid">
          {services.map((svc, i) => (
            <div key={i} className="service-card">
              <div className="service-card-header">
                <span className="service-name">{svc.name}</span>
                <span className="service-badge">configured</span>
              </div>
              {svc.description && (
                <p className="service-desc">{svc.description}</p>
              )}
              <div className="service-meta">
                <span>{svc.url}</span>
                {svc.health_check && <span>Health: {svc.health_check}</span>}
              </div>
            </div>
          ))}
        </div>
      </PageSection>
    </div>
  );
}