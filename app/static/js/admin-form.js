(function () {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  const slots = document.querySelectorAll(".photo-manager-slot");

  if (!slots.length || !csrfToken) {
    return;
  }

  function setStatus(slotEl, message, type) {
    const status = slotEl.querySelector(".photo-manager-status");
    status.textContent = message || "";
    status.classList.remove("is-error", "is-success");
    if (type) {
      status.classList.add(`is-${type}`);
    }
  }

  function setBusy(slotEl, busy) {
    const fileInput = slotEl.querySelector(".photo-manager-input");
    const hasFile = Boolean(fileInput.files?.length);

    slotEl.classList.toggle("is-busy", busy);
    slotEl.querySelectorAll("button").forEach((button) => {
      if (busy) {
        button.disabled = true;
        return;
      }
      if (button.classList.contains("photo-manager-upload")) {
        button.disabled = !hasFile;
      } else {
        button.disabled = false;
      }
    });
  }

  function showPhoto(slotEl, photoUrl) {
    const preview = slotEl.querySelector(".photo-manager-image");
    const removeBtn = slotEl.querySelector(".photo-manager-remove");

    preview.src = photoUrl;
    removeBtn.hidden = false;
    slotEl.classList.add("has-photo");
  }

  function clearPhoto(slotEl) {
    const preview = slotEl.querySelector(".photo-manager-image");
    const removeBtn = slotEl.querySelector(".photo-manager-remove");
    const fileInput = slotEl.querySelector(".photo-manager-input");
    const filename = slotEl.querySelector(".photo-manager-filename");
    const uploadBtn = slotEl.querySelector(".photo-manager-upload");

    preview.removeAttribute("src");
    removeBtn.hidden = true;
    slotEl.classList.remove("has-photo");
    fileInput.value = "";
    filename.textContent = "";
    uploadBtn.disabled = true;
  }

  async function postJson(url, body) {
    const options = {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
      },
      credentials: "same-origin",
    };

    if (body instanceof FormData) {
      options.body = body;
    }

    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok || !data.ok) {
      throw new Error(data.error || "Request failed.");
    }
    return data;
  }

  slots.forEach((slotEl) => {
    const fileInput = slotEl.querySelector(".photo-manager-input");
    const chooseBtn = slotEl.querySelector(".photo-manager-choose");
    const uploadBtn = slotEl.querySelector(".photo-manager-upload");
    const removeBtn = slotEl.querySelector(".photo-manager-remove");
    const filename = slotEl.querySelector(".photo-manager-filename");

    chooseBtn.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
      const file = fileInput.files?.[0];
      if (!file) {
        filename.textContent = "";
        uploadBtn.disabled = true;
        return;
      }
      filename.textContent = file.name;
      uploadBtn.disabled = false;
      setStatus(slotEl, "");
    });

    uploadBtn.addEventListener("click", async () => {
      const file = fileInput.files?.[0];
      if (!file) {
        setStatus(slotEl, "Choose an image first.", "error");
        return;
      }

      const formData = new FormData();
      formData.append("photo", file);

      setBusy(slotEl, true);
      setStatus(slotEl, "Uploading…");

      try {
        const data = await postJson(slotEl.dataset.uploadUrl, formData);
        showPhoto(slotEl, `${data.photo_url}?t=${Date.now()}`);
        fileInput.value = "";
        filename.textContent = "";
        uploadBtn.disabled = true;
        setStatus(slotEl, "Photo uploaded.", "success");
      } catch (error) {
        setStatus(slotEl, error.message, "error");
      } finally {
        setBusy(slotEl, false);
      }
    });

    removeBtn.addEventListener("click", async () => {
      if (!confirm("Remove this photo?")) {
        return;
      }

      setBusy(slotEl, true);
      setStatus(slotEl, "Removing…");

      try {
        await postJson(slotEl.dataset.removeUrl);
        clearPhoto(slotEl);
        setStatus(slotEl, "Photo removed.", "success");
      } catch (error) {
        setStatus(slotEl, error.message, "error");
      } finally {
        setBusy(slotEl, false);
      }
    });
  });
})();
