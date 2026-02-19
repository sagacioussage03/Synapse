import React from 'react';

export default function PageSection({ title, subtitle, actions, children }) {
  return (
    <section style={{ marginBottom: 24 }}>
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">{title}</div>
            {subtitle && <div className="card-subtitle">{subtitle}</div>}
          </div>
          {actions && <div>{actions}</div>}
        </div>
        {children}
      </div>
    </section>
  );
}