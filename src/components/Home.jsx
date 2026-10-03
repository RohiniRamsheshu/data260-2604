import React, { useState, useEffect } from 'react';

export default function Home({ user }) {
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) return; // Don't fetch if unauthenticated

    fetch('http://localhost:8804/api/vulnerabilities', {
      method: 'GET',
      credentials: 'include',
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch records');
        return res.json();
      })
      .then((data) => setVulnerabilities(data))
      .catch((err) => setError(err.message));
  }, [user]);

  if (!user) {
    return <h2>Please log in to view vulnerabilities.</h2>;
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h2>Vulnerability Records</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <table border="1" cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Package Name</th>
            <th>CVE ID</th>
          </tr>
        </thead>
        <tbody>
          {vulnerabilities.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.package_name}</td>
              <td>{item.cve_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}