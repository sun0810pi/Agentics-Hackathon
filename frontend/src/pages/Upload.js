import React from 'react';
import FileUpload from '../components/FileUpload';

function Upload() {
  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <h1 style={styles.title}>📤 Upload Invoice</h1>
        <p style={styles.subtitle}>Upload Excel or CSV file to start processing</p>
        <FileUpload />
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '40px 20px'
  },
  content: {
    background: 'white',
    padding: '48px',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '8px'
  },
  subtitle: {
    fontSize: '16px',
    color: '#666',
    marginBottom: '32px'
  }
};

export default Upload;