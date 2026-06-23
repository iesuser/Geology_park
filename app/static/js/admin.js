(function () {
  const modal = document.getElementById("qr-modal");
  if (!modal) {
    return;
  }

  const image = document.getElementById("qr-modal-image");
  const title = document.getElementById("qr-modal-title");
  const label = document.getElementById("qr-modal-label");
  const download = document.getElementById("qr-modal-download");
  const triggers = document.querySelectorAll(".admin-qr-trigger");

  function openModal(trigger) {
    const qrUrl = trigger.dataset.qrUrl;
    const qrLabel = trigger.dataset.qrLabel || "QR Code";
    const qrFilename = trigger.dataset.qrFilename || "qr-code.png";

    title.textContent = "QR Code";
    label.textContent = qrLabel;
    image.src = qrUrl;
    image.alt = qrLabel;
    download.href = qrUrl;
    download.download = qrFilename;

    modal.hidden = false;
    document.body.classList.add("admin-modal-open");
    modal.querySelector(".admin-modal-close").focus();
  }

  function closeModal() {
    modal.hidden = true;
    document.body.classList.remove("admin-modal-open");
    image.removeAttribute("src");
  }

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", () => openModal(trigger));
  });

  modal.querySelectorAll("[data-qr-modal-close]").forEach((element) => {
    element.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) {
      closeModal();
    }
  });
})();
