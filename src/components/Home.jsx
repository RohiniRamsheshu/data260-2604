import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { fetchVulnerabilities } from "../store.js";

export default function Home({ user }) {
  const dispatch = useDispatch();

  const {
    records: vulnerabilities,
    status,
    error,
  } = useSelector((state) => state.vulnerabilities);

  useEffect(() => {
    if (user) {
      dispatch(fetchVulnerabilities());
    }
  }, [user, dispatch]);

  if (!user) {
    return <h2>Please log in to view vulnerabilities.</h2>;
  }

  if (status === "loading") {
    return <p>Loading vulnerability records...</p>;
  }

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto" }}>
      <h2>Vulnerability Records</h2>

      {error && (
        <p style={{ color: "red" }}>
          {error}
        </p>
      )}

      <table
        border="1"
        cellPadding="8"
        style={{
          width: "100%",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr>
            <th>ID</th>
            <th>Package Name</th>
            <th>CVE ID</th>
            <th>Severity</th>
            <th>Researcher ID</th>
          </tr>
        </thead>

        <tbody>
          {vulnerabilities.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.package_name}</td>
              <td>{item.cve_id}</td>
              <td>{item.severity}</td>
              <td>{item.researcher_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}