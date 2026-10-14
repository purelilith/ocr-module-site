const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const preview = document.getElementById("preview");
const recognizeBtn = document.getElementById("recognizeBtn");
const resultTextarea = document.getElementById("result");
const questionInput = document.getElementById("questionInput"); // Новое поле ввода вопроса

let selectedFile = null;

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;

  selectedFile = file;
  fileName.textContent = file.name;
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
  recognizeBtn.disabled = false;
  resultTextarea.value = "";
});

recognizeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  recognizeBtn.disabled = true;
  recognizeBtn.textContent = "Обработка модулями OCR и RAG...";
  resultTextarea.value = "";

  const formData = new FormData();
  formData.append("photo", selectedFile);
  
  // Передаем вопрос, если он введен пользователем
  if (questionInput && questionInput.value.trim()) {
    formData.append("question", questionInput.value.trim());
  }

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      // Выводим итоговый JSON, включающий результаты OCR и ответы Модуля 3
      resultTextarea.value = JSON.stringify(data, null, 2);
    } else {
      resultTextarea.value = "Ошибка: " + (data.error || "Не удалось обработать документ");
    }
  } catch (error) {
    resultTextarea.value = "Ошибка соединения с сервером";
  } finally {
    recognizeBtn.disabled = false;
    recognizeBtn.textContent = "Распознать и проверить";
  }
});