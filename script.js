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
});