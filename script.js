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
  event.preventDefault();

  const description = document.getElementById("description").value;
  const checkbox = document.getElementById("checkBox").checked;

  const isValid = validateForm(description, checkbox);

  if (!isValid) {
    return;
  }

  console.log("Validation passed!");

  const formData = {
    packageName: document.getElementById("packageName").value,
    affectedVersion: document.getElementById("affectedVersion").value,
    emailId: document.getElementById("emailId").value,
    description: description,
    severity: document.getElementById("severity").value
  };

  const jsonString = JSON.stringify(formData);
  console.log("JSON string:", jsonString);

  const parsedObject = JSON.parse(jsonString);
  const { packageName, emailId } = parsedObject;
  console.log("Package Name:", packageName);
  console.log("Email:", emailId);
});