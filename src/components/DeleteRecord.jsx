import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import { deleteVulnerability } from "../store.js";

export default function DeleteRecord() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [id, setId] = useState("");
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async (event) => {
    event.preventDefault();
    setError("");
    setDeleting(true);

    try {
      await dispatch(deleteVulnerability(Number(id))).unwrap();
      navigate("/");
    } catch (errorMessage) {
      setError(errorMessage);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Delete Vulnerability Record</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <form onSubmit={handleDelete}>
        <div style={{ marginBottom: "10px" }}>
          <label>Record ID to Delete: </label>

          <input
            type="number"
            min="1"
            value={id}
            onChange={(event) => setId(event.target.value)}
            required
          />
        </div>

        <button
          type="submit"
          disabled={deleting}
          style={{
            backgroundColor: "red",
            color: "white",
            padding: "8px 12px",
          }}
        >
          {deleting ? "Deleting..." : "Delete Vulnerability"}
        </button>
      </form>
    </div>
  );
}