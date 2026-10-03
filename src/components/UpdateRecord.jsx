import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function UpdateRecord() {
  const [id, setId] = useState('');
  const [packageName, setPackageName] = useState('');
  const [cveId, setCveId] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('package_name', packageName);
    formData.append('cve_id', cveId);

    try {
      const res = await fetch(`http://localhost:8804/api/vulnerabilities/${id}`, {
        method: 'PUT',
        body: formData,
        credentials: 'include',
      });

      if (res.ok) {
        navigate('/');
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to update record');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto' }}>
      <h2>Update Vulnerability Record</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '10px' }}>
          <label>Record ID to Update: </label>
          <input
            type="number"
            value={id}
            onChange={(e) => setId(e.target.value)}
            required
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>New Package Name: </label>
          <input
            type="text"
            value={packageName}
            onChange={(e) => setPackageName(e.target.value)}
            required
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>New CVE ID: </label>
          <input
            type="text"
            value={cveId}
            onChange={(e) => setCveId(e.target.value)}
            required
          />
        </div>
        <button type="submit">Update Vulnerability</button>
      </form>
    </div>
  );
}