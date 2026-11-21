 
"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("questionForm");
    const subjectInput = document.getElementById("subjectSelect");
    const questionInput = document.getElementById("questionInput");
    const photoInput = document.getElementById("photoInput");
    const photoPreview = document.getElementById("photoPreview");
    const solveButton = document.getElementById("solveButton");
    const loadingMessage = document.getElementById("loadingMessage");
    const errorMessage = document.getElementById("errorMessage");
    const answerSection = document.getElementById("answerSection");
    const answerContent = document.getElementById("answerContent");

    if (
        !form || !subjectInput || !questionInput || !photoInput ||
        !photoPreview || !solveButton || !loadingMessage ||
        !errorMessage || !answerSection || !answerContent
    ) {
        console.error("MathForStudent: Required page elements are missing.");
        return;
    }

    const MAX_IMAGE_SIZE = 5 * 1024 * 1024;

    const ALLOWED_IMAGE_TYPES = [
        "image/png",
        "image/jpeg",
        "image/webp"
    ];

    let previewUrl = null;

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove("hidden");
    }

    function hideError() {
        errorMessage.textContent = "";
        errorMessage.classList.add("hidden");
    }

    function addResult(title, value) {
        if (value === null || value === undefined || value === "") {
            return;
        }

        const heading = document.createElement("h3");
        heading.textContent = title;

        const content = document.createElement("div");
        content.className = "result-content";

        if (Array.isArray(value)) {
            const list = document.createElement("ol");

            value.forEach((item) => {
                const li = document.createElement("li");
                li.textContent = String(item);
                list.appendChild(li);
            });

            content.appendChild(list);
        } else if (typeof value === "object") {
            content.textContent = JSON.stringify(value, null, 2);
        } else {
            content.textContent = String(value);
        }

        answerContent.appendChild(heading);
        answerContent.appendChild(content);
    }

    function showAnswer(data) {
        answerContent.replaceChildren();

        if (data.recognized_question) {
            addResult(
                "Recognized Question",
                data.recognized_question
            );
        }

        const result = data.calculation || data.engine_result;

        if (result) {
            if (result.answer !== undefined) {
                addResult("Final Answer", result.answer);
            }

            if (result.method) {
                addResult("Method", result.method);
            }

            if (result.steps) {
                addResult("Step-by-Step Solution", result.steps);
            }
        }

        if (data.explanation) {
            addResult("AI Explanation", data.explanation);
        }

        if (data.message) {
            addResult("Message", data.message);
        }

        if (data.status === "needs_information") {
            addResult(
                "More Information Needed",
                data.message || "Please provide more information."
            );
        }

        if (data.ai_status === "needs_ai" && !data.explanation) {
            addResult(
                "AI Explanation",
                "AI explanation is currently unavailable. The calculation result is shown above."
            );
        }

        if (!answerContent.hasChildNodes()) {
            addResult("Response", "No solution was returned.");
        }

        answerSection.classList.remove("hidden");

        answerSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    function clearPreview() {
        photoPreview.replaceChildren();

        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
            previewUrl = null;
        }
    }

    photoInput.addEventListener("change", () => {
        hideError();
        clearPreview();

        const file = photoInput.files && photoInput.files[0];

        if (!file) {
            return;
        }

        if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
            showError(
                "Please select a PNG, JPG, JPEG, or WEBP image."
            );
            photoInput.value = "";
            return;
        }

        if (file.size > MAX_IMAGE_SIZE) {
            showError("Image size must not exceed 5 MB.");
            photoInput.value = "";
            return;
        }

        const image = document.createElement("img");
        image.alt = "Selected question preview";

        previewUrl = URL.createObjectURL(file);
        image.src = previewUrl;

        image.style.maxWidth = "100%";
        image.style.height = "auto";

        photoPreview.appendChild(image);
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        hideError();
        answerSection.classList.add("hidden");
        answerContent.replaceChildren();

        const subject = subjectInput.value.trim().toLowerCase();
        const question = questionInput.value.trim();
        const photo = photoInput.files && photoInput.files[0];

        if (!subject) {
            showError("Please select a subject.");
            return;
        }

        if (!question && !photo) {
            showError(
                "Please type a question or upload a question photo."
            );
            return;
        }

        if (question.length > 15000) {
            showError(
                "Your question is too long. Maximum length is 15,000 characters."
            );
            return;
        }

        if (photo) {
            if (!ALLOWED_IMAGE_TYPES.includes(photo.type)) {
                showError(
                    "Please select a PNG, JPG, JPEG, or WEBP image."
                );
                return;
            }

            if (photo.size > MAX_IMAGE_SIZE) {
                showError("Image size must not exceed 5 MB.");
                return;
            }
        }

        const formData = new FormData();

        formData.append("subject", subject);
        formData.append("question", question);

        if (photo) {
            formData.append("photo", photo);
        }

        solveButton.disabled = true;
        loadingMessage.classList.remove("hidden");

        try {
            const response = await fetch("/api/solve", {
                method: "POST",
                body: formData
            });

            let data;

            try {
                data = await response.json();
            } catch {
                throw new Error(
                    "The server returned an invalid response."
                );
            }

            if (!response.ok || data.status === "error") {
                throw new Error(
                    data.message || "Unable to solve this question."
                );
            }

            showAnswer(data);

        } catch (error) {
            console.error(
                "MathForStudent request failed:",
                error
            );

            showError(
                error.message || "Network error. Please try again."
            );

        } finally {
            solveButton.disabled = false;
            loadingMessage.classList.add("hidden");
        }
    });
});
