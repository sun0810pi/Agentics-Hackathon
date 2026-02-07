import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import JobList from '../components/JobList';

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await api.get('/api/dashboard/metrics');
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={styles.loading}>Loading...</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>📊 Dashboard</h1>
        <Link to="/upload" style={styles.uploadButton}>
          📤 Upload Invoice
        </Link>
      </div>

      <div style={styles.metricsGrid}>
        <div style={{...styles.metricCard, borderLeft: '4px solid #667eea'}}>
          <div style={styles.metricValue}>{metrics?.total_jobs || 0}</div>
          <div style={styles.metricLabel}>Total Jobs</div>
        </div>

        <div style={{...styles.metricCard, borderLeft: '4px solid #10b981'}}>
          <div style={styles.metricValue}>{metrics?.completed_jobs || 0}</div>
          <div style={styles.metricLabel}>Completed</div>
        </div>

        <div style={{...styles.metricCard, borderLeft: '4px solid #f59e0b'}}>
          <div style={styles.metricValue}>{metrics?.high_risk_jobs || 0}</div>
          <div style={styles.metricLabel}>High Risk</div>
        </div>

        <div style={{...styles.metricCard, borderLeft: '4px solid #8b5cf6'}}>
          <div style={styles.metricValue}>{metrics?.success_rate || 0}%</div>
          <div style={styles.metricLabel}>Success Rate</div>
        </div>
      </div>

      <div style={styles.jobsSection}>
        <h2 style={styles.sectionTitle}>Recent Jobs</h2>
        <JobList />
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '40px 20px'
  },
  loading: {
    textAlign: 'center',
    padding: '100px 20px',
    fontSize: '18px',
    color: '#666'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '32px'
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#333'
  },
  uploadButton: {
    padding: '12px 24px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    textDecoration: 'none',
    borderRadius: '8px',
    fontWeight: 'bold',
    transition: 'transform 0.2s'
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
    marginBottom: '40px'
  },
  metricCard: {
    background: 'white',
    padding: '24px',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  metricValue: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '8px'
  },
  metricLabel: {
    fontSize: '14px',
    color: '#666',
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  },
  jobsSection: {
    background: 'white',
    padding: '32px',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  sectionTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '24px'
  }
};

export default Dashboard;