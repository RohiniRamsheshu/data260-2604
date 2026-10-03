import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Home from './components/Home';
import Login from './components/Login';
import CreateRecord from './components/CreateRecord';
import UpdateRecord from './components/UpdateRecord';
import DeleteRecord from './components/DeleteRecord';
export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8804/api/me', { method: 'GET', credentials: 'include' })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setUser(data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <Router>
      <nav style={{ padding: '10px', borderBottom: '1px solid #ccc', marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '10px' }}>Home</Link>
        {user ? (
          <>
            <Link to="/create" style={{ marginRight: '10px' }}>Add Vulnerability</Link>
            <Link to="/update" style={{ marginRight: '10px' }}>Update Vulnerability</Link>
            <Link to="/delete" style={{ marginRight: '10px' }}>Delete Vulnerability</Link>
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </nav>

      {!user && (
        <div style={{ color: 'red', margin: '10px 0' }}>
          <strong>Login required:</strong> Please log in to view or edit records.
        </div>
      )}

      <Routes>
        <Route path="/" element={<Home user={user} />} />
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/create" element={user ? <CreateRecord /> : <Navigate to="/login" />} />
        <Route path="/update" element={user ? <UpdateRecord /> : <Navigate to="/login" />} />
        <Route path="/delete" element={user ? <DeleteRecord /> : <Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}