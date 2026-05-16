import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8001';

export default function UploadPanel() {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState('No files selected.');
  const [loading, setLoading] = useState(false);

  const upload = async () => {
    if (!files.length) {
      setStatus('Select one or more PDFs first.');
      return;
    }

    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append('files', file));

    setLoading(true);
    setStatus('Uploading and indexing documents...');

    try {
      const response = await axios.post(`${API_BASE_URL}/documents/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStatus(response.data.message || 'Documents uploaded successfully.');
    } catch (error) {
      setStatus('Upload failed. Check the backend server and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-box">
      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={(event) => setFiles(event.target.files || [])}
      />
      <button className="primary-button full-width" type="button" onClick={upload} disabled={loading}>
        {loading ? 'Indexing...' : 'Upload and Index'}
      </button>
      <p className="helper-text">{status}</p>
    </div>
  );
}