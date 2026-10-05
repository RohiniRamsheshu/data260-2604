import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import { updateVulnerability } from "../store.js";

export default function UpdateRecord() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    id: "",
    package_name: "",
    cve_id: "",
    severity: 0,
    researcher_id: 1,
  });

  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previousForm) => ({
      ...previousForm,
      [name]:
        name === "id" ||
        name === "severity" ||
        name === "researcher_id"
          ? Number(value)
          : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSaving(true);

    try {
      await dispatch(
        updateVulnerability({
          id: form.id,
          data: {
            package_name: form.package_name,
            cve_id: form.cve_id,
            severity: form.severity,
            researcher_id: form.researcher_id,
          },
        })
      ).unwrap();

      navigate("/");
    } catch (errorMessage) {
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Update Vulnerability Record</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "10px" }}>
          <label>Record ID: </label>
          <input
            name="id"
            type="number"
            min="1"
            value={form.id}
            onChange={handleChange}
            required
          />
        </div>

        <div style={{ marginBottom: "10px" }}>
          <label>Package Name: </label>
          <input
            name="package_name"
            type="text"
            value={form.package_name}
            onChange={handleChange}
            required
          />
        </div>

        <div style={{ marginBottom: "10px" }}>
          <label>CVE ID: </label>
          <input
            name="cve_id"
            type="text"
            value={form.cve_id}
            onChange={handleChange}
            placeholder="CVE-2026-12345"
            required
          />
        </div>

        <div style={{ marginBottom: "10px" }}>
          <label>Severity: </label>
          <input
            name="severity"
            type="number"
            min="0"
            max="10"
            value={form.severity}
            onChange={handleChange}
            required
          />
        </div>

        <div style={{ marginBottom: "10px" }}>
          <label>Researcher ID: </label>
          <input
            name="researcher_id"
            type="number"
            min="1"
            value={form.researcher_id}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" disabled={saving}>
          {saving ? "Updating..." : "Update Vulnerability"}
        </button>
      </form>
    </div>
  );
}