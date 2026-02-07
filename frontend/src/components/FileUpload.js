import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (!selectedFile) return;
    
    const validExtensions = ['.xlsx', '.xls', '.csv'];
    const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
    
    if (!validExtensions.includes(fileExtension)) {
      setError('Invalid file type. Only Excel/CSV files allowed.');
      return;
    }
    
    if (selectedFile.size > 50 * 1024 * 1024) { // 50MB
      setError('File too large. Maximum size is 50MB.');
      return;
    }
    
    setFile(selectedFile);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('/api/jobs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div 
        style={styles.dropZone}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          const droppedFile = e.dataTransfer.files[0];
          if (droppedFile) {
            setFile(droppedFile);
          }
        }}
      >
        <input
          type="file"
          accept=".xlsx,.xls,.csv"
          onChange={handleFileChange}
          style={styles.fileInput}
          id="file-upload"
        />
        
        <label htmlFor="file-upload" style={styles.label}>
          📁 {file ? file.name : 'Click or drag file here'}
        </label>
        
        {file && (
          <div style={styles.fileInfo}>
            Size: {(file.size / 1024).toFixed(2)} KB
          </div>
        )}
      </div>

      {error && <div style={styles.error}>{error}</div>}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        style={{
          ...styles.button,
          opacity: (!file || uploading) ? 0.5 : 1,
          cursor: (!file || uploading) ? 'not-allowed' : 'pointer'
        }}
      >
        {uploading ? 'Uploading...' : 'Upload & Process'}
      </button>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px'
  },
  dropZone: {
    border: '2px dashed #667eea',
    borderRadius: '12px',
    padding: '60px 20px',
    textAlign: 'center',
    background: '#f8f9fa',
    cursor: 'pointer',
    transition: 'all 0.3s'
  },
  fileInput: {
    display: 'none'
  },
  label: {
    fontSize: '18px',
    color: '#667eea',
    cursor: 'pointer',
    fontWeight: '600'
  },
  fileInfo: {
    marginTop: '12px',
    fontSize: '14px',
    color: '#666'
  },
  button: {
    padding: '14px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 'bold',
    transition: 'transform 0.2s'
  },
  error: {
    padding: '12px',
    background: '#fee',
    color: '#c33',
    borderRadius: '8px',
    fontSize: '14px'
  }
};

export default FileUpload;