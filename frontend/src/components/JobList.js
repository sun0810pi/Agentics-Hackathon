import React, { useState, useEffect } from 'react';
import api from '../services/api';

function JobList() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await api.get('/api/jobs/list?limit=10');
      setJobs(response.data.jobs);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={styles.loading}>Loading jobs...</div>;
  }

  if (jobs.length === 0) {
    return <div style={styles.empty}>No jobs yet. Upload an invoice to get started!</div>;
  }

  return (
    <div style={styles.container}>
      {jobs.map(job => (
        <div key={job.job_id} style={styles.jobCard}>
          <div style={styles.jobHeader}>
            <div style={styles.fileName}>📄 {job.file_name}</div>
            <div style={getStatusStyle(job.status)}>{job.status}</div>
          </div>
          <div style={styles.jobDetails}>
            <span>Job ID: {job.job_id}</span>
            <span>Size: {(job.file_size / 1024).toFixed(2)} KB</span>
            <span>Created: {new Date(job.created_at).toLocaleString()}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

const getStatusStyle = (status) => {
  const baseStyle = {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 'bold'
  };

  if (status.includes('SUCCESS')) {
    return { ...baseStyle, background: '#d1fae5', color: '#065f46' };
  } else if (status.includes('HIGH_RISK')) {
    return { ...baseStyle, background: '#fee2e2', color: '#991b1b' };
  } else if (status.includes('PROCESSING')) {
    return { ...baseStyle, background: '#dbeafe', color: '#1e40af' };
  }
  return { ...baseStyle, background: '#e5e7eb', color: '#374151' };
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px'
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    color: '#666'
  },
  empty: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#666',
    fontSize: '16px'
  },
  jobCard: {
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '16px',
    transition: 'box-shadow 0.2s'
  },
  jobHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px'
  },
  fileName: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#333'
  },
  jobDetails: {
    display: 'flex',
    gap: '16px',
    fontSize: '13px',
    color: '#666'
  }
};

export default JobList;