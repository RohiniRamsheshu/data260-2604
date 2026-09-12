async function loadRecords(query = "") {
  const listEl = document.getElementById("entity-list");
  const loadingEl = document.getElementById("loading-state");
  const emptyEl = document.getElementById("empty-state");
  const errorEl = document.getElementById("error-state");

  loadingEl.style.display = "block";
  emptyEl.style.display = "none";
  errorEl.style.display = "none";
  listEl.innerHTML = "";

  try {
    const url = query ? `/api/records?q=${encodeURIComponent(query)}` : "/api/records";
    const response = await fetch(url);
    if (!response.ok) throw new Error("Request failed");
    const records = await response.json();

    loadingEl.style.display = "none";

    if (records.length === 0) {
      emptyEl.style.display = "block";
      return;
    }

    records.forEach((r) => {
      const li = document.createElement("li");
      li.textContent = `#${r.id} — ${r.packageName} (${r.affectedVersion}) — ${r.severity}`;
      listEl.appendChild(li);
    });
  } catch (err) {
    loadingEl.style.display = "none";
    errorEl.style.display = "block";
  }
}

loadRecords();

document.getElementById("updateBtn").addEventListener("click", async () => {
  const newPackageName = prompt("New package name for record #1:");
  const newVersion = prompt("New affected version for record #1:");
  if (!newPackageName || !newVersion) return;

  const formData = new URLSearchParams();
  formData.append("packageName", newPackageName);
  formData.append("affectedVersion", newVersion);

  await fetch("/api/records/1/update", {
    method: "POST",
    body: formData
  });

  loadRecords();
});

document.getElementById("deleteBtn").addEventListener("click", async () => {
  await fetch("/api/records/delete-highest", {
    method: "POST"
  });

  loadRecords();
});

document.getElementById("searchInput").addEventListener("input", (event) => {
  loadRecords(event.target.value);
});

const form = document.getElementById("vulnForm");

const validateForm = (description, checkbox) => {
  if (description.length <= 25) {
    alert("Description must be more than 25 characters.");
    return false;
  }

  if (!checkbox) {
    alert("You must agree to the terms and conditions.");
    return false;
  }

  return true;
};

form.addEventListener("submit", (event) => {
  const description = document.getElementById("description").value;
  const checkbox = document.getElementById("checkBox").checked;

  const isValid = validateForm(description, checkbox);

  if (!isValid) {
    event.preventDefault();
    return;
  }

  form.action = "/api/records";
  form.method = "POST";
});