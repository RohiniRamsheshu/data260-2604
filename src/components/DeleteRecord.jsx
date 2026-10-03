import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function DeleteRecord() {
  const [id, setId] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleDelete = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch(`http://localhost:8804/api/vulnerabilities/${id}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (res.ok) {
        navigate('/');
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to delete record');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto' }}>
      <h2>Delete Vulnerability Record</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleDelete}>
        <div style={{ marginBottom: '10px' }}>
          <label>Record ID to Delete: </label>
          <input
            type="number"
            value={id}
            onChange={(e) => setId(e.target.value)}
            required
          />
        </div>
        <button type="submit" style={{ backgroundColor: 'red', color: 'white' }}>
          Delete Vulnerability
        </button>
      </form>
    </div>
  );
}