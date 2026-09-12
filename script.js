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
const createSubmissionCounter = () => {
  let count = 0;
  return () => {
    count = count + 1;
    return count;
  };
};

const trackSubmission = createSubmissionCounter();

form.addEventListener("submit", (event) => {
  const description = document.getElementById("description").value;
  const checkbox = document.getElementById("checkBox").checked;

  const isValid = validateForm(description, checkbox);

  if (!isValid) {
    event.preventDefault();
    return;
  }

  // Valid: let the browser submit normally to FastAPI
  form.action = "/api/records";
  form.method = "POST";
});

  