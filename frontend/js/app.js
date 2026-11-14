"use strict";

const form = document.getElementById("questionForm");
const subjectInput = document.getElementById("subjectSelect");
const questionInput = document.getElementById("questionInput");
const photoInput = document.getElementById("photoInput");

const solveButton = document.getElementById("solveButton");
const loadingMessage = document.getElementById("loadingMessage");
const errorMessage = document.getElementById("errorMessage");

const photoPreview = document.getElementById("photoPreview");
const answerSection = document.getElementById("answerSection");
const answerContent = document.getElementById("answerContent");

let selectedPhoto = null;

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}

function clearError() {
    errorMessage.textContent = "";
    errorMessage.classList.add("hidden");
}

function showLoading(isLoading) {
    solveButton.disabled = isLoading;
    loadingMessage.classList.toggle("hidden", !isLoading);
}

function addTextBlock(title, content) {
    const block = document.createElement("div");
    block.className = "answer-block";

    const heading = document.createElement("h3");
    heading.textContent = title;

    const paragraph = document.createElement("p");
    paragraph.textContent = content;

    block.append(heading, paragraph);
    answerContent.appendChild(block);
}

function displayAnswer(data) {
    answerContent.replaceChildren();

    if (data.calculation) {
        addTextBlock(
            "Method",
            data.calculation.method || "Specialist calculation"
        );

        const steps = data.calculation.steps || [];

        if (steps.length) {
            const block = document.createElement("div");
            block.className = "answer-block";

            const heading = document.createElement("h3");
            heading.textContent = "Step-by-step solution";

            const list = document.createElement("ol");

            steps.forEach(step => {
                const item = document.createElement("li");
                item.textContent = String(step);
                list.appendChild(item);
            });

            block.append(heading, list);
            answerContent.appendChild(block);
        }

        addTextBlock(
            "Final Answer",
            data.calculation.answer || "No final answer returned."
        );
    }

    if (data.explanation) {
        addTextBlock("AI Explanation", data.explanation);
    }

    if (!data.calculation && data.message) {
        addTextBlock("Information", data.message);
    }

    answerSection.classList.remove("hidden");
}

photoInput.addEventListener("change", () => {
    clearError();

    const file = photoInput.files[0];

    selectedPhoto = file || null;
    photoPreview.replaceChildren();

    if (!file) return;

    const allowedTypes = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ];

    if (!allowedTypes.includes(file.type)) {
        selectedPhoto = null;
        photoInput.value = "";
        showError("Please select a PNG, JPEG or WebP image.");
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        selectedPhoto = null;
        photoInput.value = "";
        showError("Image must be smaller than 10 MB.");
        return;
    }

    const image = document.createElement("img");
    image.alt = "Selected question preview";

    const objectUrl = URL.createObjectURL(file);
    image.src = objectUrl;

    image.onload = () => URL.revokeObjectURL(objectUrl);

    photoPreview.appendChild(image);
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    clearError();

    const subject = subjectInput.value;
    const question = questionInput.value.trim();

    if (!subject) {
        showError("Please select a subject.");
        return;
    }

    if (!question) {
        showError(
            selectedPhoto
                ? "Photo solving is not connected yet. Please type the question."
                : "Please enter your question."
        );
        return;
    }

    const formData = new FormData();

    formData.append("subject", subject);
    formData.append("question", question);

    showLoading(true);
    answerSection.classList.add("hidden");

    try {
        const response = await fetch("/api/solve", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok || data.status === "error") {
            throw new Error(
                data.message || "Unable to solve this question."
            );
        }

        if (
            data.status === "needs_information" ||
            data.status === "needs_ai"
        ) {
            showError(
                data.message ||
                "More information is required to solve this question."
            );
            return;
        }

        displayAnswer(data);

    } catch (error) {
        showError(
            error.message ||
            "Connection failed. Please check your backend."
        );
    } finally {
        showLoading(false);
    }
});

if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/service-worker.js")
            .catch(() => {
                console.warn("Service worker registration failed.");
            });
    });
}