
document.addEventListener('DOMContentLoaded', () => {
  const uuid = sessionStorage.getItem('gitbuilding_qaqc_uuid');
  const buildId = sessionStorage.getItem('gitbuilding_qaqc_id');
  const server = sessionStorage.getItem('gitbuilding_qaqc_server');

  if (!uuid) {
    // If no UUID set, hide all elements with class 'qaqc-page-form'
    const forms = document.querySelectorAll('.qaqc-page-form');
    forms.forEach(form => form.style.display = 'none');
  }
  else{
    // Get the first form
    const firstForm = document.querySelector('.qaqc-page-form');
    // Assuming there is a form
    if (firstForm) {
      // Get the build id for this page
      const pageBuildId = firstForm.dataset.buildId
      // if it matches add listeners to the buttons.
      if (pageBuildId === buildId){
        attach_form_listeners(server, uuid, buildId);
      }
      else {
        // Else hide the forms, they are not for the ongoing build.
        const forms = document.querySelectorAll('.qaqc-page-form');
        forms.forEach(form => form.style.display = 'none');
      }
    }
  }
});

function attach_form_listeners(server, uuid, buildId) {
  document.querySelectorAll('.qaqc-page-form').forEach(wrapper => {
    const form = wrapper.querySelector('form');
    if (!form) return;

    const formId = form.id;

    // Submit button
    const submitBtn = wrapper.querySelector('.qaqc-upload-button');
    if (submitBtn) {
      if (!server) submitBtn.style.display = 'none';
      else submitBtn.addEventListener('click', async function (e) {
        e.preventDefault();
        const endpoint = server + "/submit/" + uuid;
        try {
          const result = await submitFormJson(formId, buildId, uuid, endpoint);
        } catch (err) {
          alert(`Failed to upload form: ${err.message}`);
          console.error("Error:", err);
        }
      });
    }

    // Download button
    const downloadBtn = wrapper.querySelector('.qaqc-download-button');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', async function (e) {
        e.preventDefault();
        const filename = formId + ".json"
        try {
          await downloadFormJson(formId, buildId, uuid, filename);
        } catch (err) {
          alert(`Failed to download form: ${err}`);
          console.error("Download error:", err);
        }
      });
    }
  });
}



// A function to convert form data and return JSON string
async function getFormJson(formId, buildId, uuid) {
  //get page title
  const pageContentDiv = document.querySelector(".page-content");
  const h1 = pageContentDiv ? pageContentDiv.querySelector("h1") : null;
  const title = h1 ? h1.textContent.trim() : "";
  // Also get form
  const formEl = document.getElementById(formId);
  const formData = new FormData(formEl);
  const formObject = {};
  const fullObject = {};

  for (const [key, value] of formData.entries()) {
    const inputEl = formEl.querySelector(`[name="${key}"]`)
    if (formObject[key]) {
      if (Array.isArray(formObject[key])) {
        formObject[key].push(value);
      } else {
        formObject[key] = [formObject[key], value];
      }
    } else {
      if (inputEl?.type === "checkbox") {
        formObject[key] = inputEl.checked;
      } else if (value instanceof File && value.size > 0) {
        formObject[key] = await fileToBase64(value);
      } else {
        formObject[key] = value;
      }
    }
  }

  // explicitly handle unchecked checkboxes, as javascript "helpfully" ignores them.
  formEl.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
    if (!(checkbox.name in formObject)) {
      formObject[checkbox.name] = false;
    }
  });

  fullObject["unique-build-id"] = uuid;
  fullObject["instruction-build-id"] = buildId;
  fullObject["form-id"] = formId;
  fullObject["form-data"] = formObject;
  fullObject["page-title"] = title;

  return JSON.stringify(fullObject, null, 2);
}

// Sends QAQC form data to a specified URL
async function submitFormJson(formId, buildId, uuid, endpoint) {
  const jsonData = await getFormJson(formId, buildId, uuid);

  const res = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: jsonData
  });

  if (!res.ok) {
    const errData = await res.json();
    const message = errData.detail || "Unknown error";
    throw new Error(`Server returned code ${res.status} (${message})`);
  }

  const text = await res.text();

  try {
    jsonResponse = JSON.parse(text);
  } catch (err) {
    console.error(`Server returned invalid JSON (code ${res.status}): ${text}`);
    throw new Error(`Server returned invalid JSON (code ${res.status}): ${text}`);
  }
  // Success. Disable form and turn green.
  const formEl = document.getElementById(formId);
  formEl.querySelectorAll("input, select, textarea, button").forEach(el => {
    el.disabled = true;
  });
  const wrapper = formEl.closest("div");
  wrapper.style.backgroundColor = "#dfd";
  const submitBtn = wrapper.querySelector('.qaqc-upload-button');
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitted";
  return jsonResponse
}


// Download form data as a JSON file
async function downloadFormJson(formId, buildId, uuid, filename = "form-data.json") {
  const jsonData = await getFormJson(formId, buildId, uuid);
  const blob = new Blob([jsonData], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Convert file to base64
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result); // this includes the data: URI prefix
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}


// Grab elements by their  IDs
const startForm = document.getElementById('qaqc-start-server-form');
const serverUrl = document.getElementById('qaqc-server-url');
const uploadBtn = document.getElementById('qaqc-start-upload-btn');
const localBtn = document.getElementById('qaqc-start-local-btn');

if (uploadBtn) {
  uploadBtn.addEventListener('click', async () => startBuild('upload'));
}
if (localBtn) {
  localBtn.addEventListener('click', async () => startBuild('local'));
}

async function startBuild(mode) {

  // Generate a UUID for this session
  const buildUUID = crypto.randomUUID();
  const buildId = startForm.dataset.buildId;
  const deviceTitle = startForm.dataset.deviceTitle;
  const nextPage = startForm.dataset.nextPage;
  const jsonUrl = startForm.dataset.jsonUrl;

  if (mode === 'upload') {
    const url = serverUrl.value.trim();
    if (!url) {
      alert("Please enter a server URL first.");
      return;
    }
    try {
      const startData = await buildStartingData(buildUUID, buildId, deviceTitle, jsonUrl);
      const endpoint = url + "/register/" + buildUUID;
      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: startData
      });
      if (!res.ok) throw new Error(`Server returned code ${res.status} (${res.statusText})`);
      responseJson = await res.json();
      deviceID = responseJson["device-id"]
      reportURL = responseJson["report-url"]
    } catch (err) {
      alert(`Failed to register this build: ${err.message}`);
      console.error("Failed to register this build:", err);
      return;
    }
    sessionStorage.setItem('gitbuilding_qaqc_server', url);
    // Store the UUID
    sessionStorage.setItem('gitbuilding_qaqc_uuid', buildUUID);
    // Store the build ID - used to differentiate between different variations
    sessionStorage.setItem('gitbuilding_qaqc_id', buildId);
    showStartPageOverly(nextPage, buildUUID, deviceID, reportURL);
  } else {
    window.location.href = nextPage;
  }
}

// return starting data as a json string
async function buildStartingData(buildUUID, buildId, deviceTitle, jsonUrl) {

  const startData = {};
  startData["unique-build-id"] = buildUUID;
  startData["instruction-build-id"] = buildId;
  startData["device-title"] = deviceTitle;

  // fetch JSON from the provided URL
  const res = await fetch(jsonUrl);
  if (!res.ok) throw new Error("Failed to fetch JSON");
  const formStructure = await res.json();

  // add the external JSON under a key
  startData["full-form-structure"] = formStructure;

  return JSON.stringify(startData);
}

// Show an overlay over the start page box (In reality a replacement).
async function showStartPageOverly(nextPage, buildUUID, deviceID, reportURL) {
  const container = document.querySelector(".qaqc");

  const overlay = document.createElement("div");
  overlay.className = "qaqc-overlay";
  overlay.innerHTML = `
    <div class="qaqc-overlay-content">
    <h4>Build registered</h4>
    <p>Please save the following information to access your build report.</p>
    <p><strong>Build ID (used for upload):</strong> ${buildUUID}</p>
    <p><strong>Device ID:</strong> ${deviceID}</p>
    <p><strong>Report URL:</strong> <a href="${reportURL}">${reportURL}</a></p>
    <button id="overlay-next-button" class="qaqc-complete">Next</button>
    </div>
  `;

  container.replaceWith(overlay);

  document.getElementById("overlay-next-button").addEventListener("click", () => {
    window.location.href = nextPage;
  });
}
