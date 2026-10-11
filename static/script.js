const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const preview = document.getElementById("preview");
const recognizeBtn = document.getElementById("recognizeBtn");
const result = document.getElementById("result");

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;

  fileName.textContent = file.name;
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
  recognizeBtn.disabled = false;
});

recognizeBtn.addEventListener("click", () => {
  result.value = response.ok ? JSON.stringify(data, null, 2) : "Ошибка: " + data.error;
});