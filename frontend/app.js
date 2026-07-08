const API_URL = "http://127.0.0.1:8000/predict";

const imageInput = document.getElementById("imageInput");
const previewFrame = document.getElementById("previewFrame");
const previewImage = document.getElementById("previewImage");
const analyzeButton = document.getElementById("analyzeButton");
const statusMessage = document.getElementById("statusMessage");
const emptyState = document.getElementById("emptyState");
const resultContent = document.getElementById("resultContent");
const predictedClass = document.getElementById("predictedClass");
const confidenceText = document.getElementById("confidenceText");
const interpretationText = document.getElementById("interpretationText");
const probabilitiesContainer = document.getElementById("probabilities");

let selectedFile = null;

const classMessages = {
    "Potato___Early_blight": "La hoja presenta patrones compatibles con tizón temprano.",
    "Potato___Late_blight": "La hoja presenta patrones compatibles con tizón tardío.",
    "Potato___healthy": "La hoja parece estar sana según el modelo.",
};

function setStatus(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.classList.toggle("error", isError);
}

function formatPercent(value) {
    return `${(value * 100).toFixed(2)}%`;
}

function resetResult() {
    emptyState.classList.remove("hidden");
    resultContent.classList.add("hidden");
    probabilitiesContainer.innerHTML = "";
}

function renderResult(data) {
    emptyState.classList.add("hidden");
    resultContent.classList.remove("hidden");

    predictedClass.textContent = data.class;
    confidenceText.textContent = `Confianza: ${formatPercent(data.confidence)}`;
    interpretationText.textContent = classMessages[data.class] || "Predicción generada por el modelo CNN.";

    probabilitiesContainer.innerHTML = "";

    Object.entries(data.probabilities).forEach(([className, probability]) => {
        const row = document.createElement("div");
        row.className = "probability-row";

        const header = document.createElement("div");
        header.className = "probability-header";

        const name = document.createElement("span");
        name.className = "probability-name";
        name.textContent = className;

        const percent = document.createElement("span");
        percent.textContent = formatPercent(probability);

        const bar = document.createElement("div");
        bar.className = "probability-bar";

        const fill = document.createElement("div");
        fill.className = "probability-fill";
        fill.style.width = formatPercent(probability);

        header.append(name, percent);
        bar.appendChild(fill);
        row.append(header, bar);
        probabilitiesContainer.appendChild(row);
    });
}

async function getErrorMessage(response) {
    try {
        const errorData = await response.json();
        return errorData.detail || "El backend no pudo procesar la imagen.";
    } catch {
        return "El backend no pudo procesar la imagen.";
    }
}

imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    selectedFile = file || null;
    resetResult();

    if (!selectedFile) {
        previewFrame.classList.remove("has-image");
        previewImage.removeAttribute("src");
        analyzeButton.disabled = true;
        setStatus("");
        return;
    }

    if (!selectedFile.type.startsWith("image/")) {
        previewFrame.classList.remove("has-image");
        previewImage.removeAttribute("src");
        analyzeButton.disabled = true;
        setStatus("Selecciona un archivo de imagen válido.", true);
        return;
    }

    previewImage.src = URL.createObjectURL(selectedFile);
    previewFrame.classList.add("has-image");
    analyzeButton.disabled = false;
    setStatus("Imagen lista para analizar.");
});

analyzeButton.addEventListener("click", async () => {
    if (!selectedFile) {
        setStatus("Selecciona una imagen antes de analizar.", true);
        return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    analyzeButton.disabled = true;
    setStatus("Analizando imagen...");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const errorMessage = await getErrorMessage(response);
            throw new Error(errorMessage);
        }

        const data = await response.json();
        renderResult(data);
        setStatus("Análisis completado.");
    } catch (error) {
        resetResult();
        setStatus(
            `No se pudo completar el análisis. ${error.message || "Verifica que el backend FastAPI esté levantado."}`,
            true,
        );
    } finally {
        analyzeButton.disabled = false;
    }
});
