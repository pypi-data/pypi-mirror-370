// Copyright (C) 2025 TU Wien.
//
// Invenio Theme TUW is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".code-block").forEach((block) => {
    const button = block.querySelector(".copy-btn");
    const codeText = block.innerText.trim();

    // Skip this block if the required elements are missing
    if (!button) return;

    const resetTooltip = (btn) => {
      btn.setAttribute("data-tooltip", "Copy to clipboard");
      btn.querySelector("i").classList.replace("check", "copy");
    };

    const handleCopy = () => {
      navigator.clipboard
        .writeText(codeText)
        .then(() => onCopySuccess(button))
        .catch((error) => console.error("Failed to copy: ", error));
    };

    const onCopySuccess = (btn) => {
      btn.setAttribute("data-tooltip", "Copied!");
      btn.querySelector("i").classList.replace("copy", "check");

      setTimeout(resetTooltip, 2000, btn);
    };

    button.addEventListener("click", handleCopy);
  });
});
