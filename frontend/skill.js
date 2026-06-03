const API_URL = "https://api.apply-r.com";

async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    credentials: "include",
    ...options,
  });

  if (res.status === 401) {
    const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });

    if (refreshRes.ok) {
      return fetch(url, {
        credentials: "include",
        ...options,
      });
    }

    window.location.href = "index.html";
    return null;
  }

  return res;
}

const header = document.querySelector(".site-header");

if (header) {
  window.addEventListener("scroll", () => {
    header.classList.toggle("scrolled", window.scrollY > 20);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("skillForm");
  if (!form) return;

  const resumeInput = document.getElementById("resume");
  const coverLetterInput = document.getElementById("coverLetter");

  const resumeFileName = document.getElementById("resumeFileName");
  const coverLetterFileName = document.getElementById("coverLetterFileName");

  const showWorkButton = document.getElementById("show-work-experience");
  const workExperienceDiv = document.getElementById("work-experience");
  const workExperienceContainer = document.getElementById("work-experience-container");
  const continueWorkButton = document.getElementById("continue-work-experience");

  const showEducationButton = document.getElementById("show-education");
  const educationDiv = document.getElementById("education");
  const educationContainer = document.getElementById("education-container");
  const continueEducationButton = document.getElementById("continue-education");

  const MAX_FILE_SIZE = 5 * 1024 * 1024;
  const ALLOWED_EXTENSIONS = ["pdf", "docx"];

  const MAX_WORK_EXPERIENCE = 7;
  const MAX_EDUCATION = 7;

  let workExperienceCount = 0;
  let educationCount = 0;

  function showSelectedFile(input, label, fallbackText) {
    const file = input.files?.[0];
    label.textContent = file ? file.name : fallbackText;
  }

  function validateFile(input, fileTypeName) {
    const file = input.files?.[0];

    if (!file) {
      input.setCustomValidity(`Please upload your ${fileTypeName}.`);
      input.reportValidity();
      return false;
    }

    const extension = file.name.split(".").pop().toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      input.setCustomValidity("Please upload a PDF or DOCX file.");
      input.reportValidity();
      return false;
    }

    if (file.size > MAX_FILE_SIZE) {
      input.setCustomValidity("File must be 5MB or smaller.");
      input.reportValidity();
      return false;
    }

    input.setCustomValidity("");
    return true;
  }

  function createWorkExperience() {
    if (workExperienceCount >= MAX_WORK_EXPERIENCE) return;

    const card = document.createElement("div");
    card.className = "work-card";

    card.innerHTML = `
      <div class="field">
        <label>Company</label>
        <input type="text" name="company" class="field-input" placeholder="Google" />
      </div>

      <div class="field">
        <label>Position</label>
        <input type="text" name="position" class="field-input" placeholder="Software Engineer" />
      </div>

      <div class="field">
        <label>Start Date</label>
        <input type="date" name="work_start_date" class="field-input" />
      </div>

      <div class="field">
        <label>End Date</label>
        <input type="date" name="work_end_date" class="field-input" />
      </div>
    `;

    workExperienceContainer.appendChild(card);
    workExperienceCount++;

    if (workExperienceCount >= MAX_WORK_EXPERIENCE) {
      continueWorkButton.disabled = true;
      continueWorkButton.textContent = "Maximum Work Experience Added";
    }
  }

  function createEducation() {
    if (educationCount >= MAX_EDUCATION) return;

    const card = document.createElement("div");
    card.className = "education-card";

    card.innerHTML = `
      <div class="field">
        <label>School</label>
        <input type="text" name="school" class="field-input" placeholder="UNC Charlotte" />
      </div>

      <div class="field">
        <label>Major</label>
        <input type="text" name="major" class="field-input" placeholder="Computer Science" />
      </div>

      <div class="field">
        <label>Start Date</label>
        <input type="date" name="school_start_date" class="field-input" />
      </div>

      <div class="field">
        <label>End Date</label>
        <input type="date" name="school_end_date" class="field-input" />
      </div>
    `;

    educationContainer.appendChild(card);
    educationCount++;

    if (educationCount >= MAX_EDUCATION) {
      continueEducationButton.disabled = true;
      continueEducationButton.textContent = "Maximum Education Added";
    }
  }

  function processWorkExperience() {
    const results = [];

    document.querySelectorAll(".work-card").forEach((card) => {
      const company = card.querySelector('[name="company"]')?.value.trim();
      const position = card.querySelector('[name="position"]')?.value.trim();
      const startDate = card.querySelector('[name="work_start_date"]')?.value;
      const endDate = card.querySelector('[name="work_end_date"]')?.value;

      if (company || position || startDate || endDate) {
        results.push({
          company,
          position,
          start_date: startDate,
          end_date: endDate,
        });
      }
    });

    return results;
  }

  function processEducation() {
    const results = [];

    document.querySelectorAll(".education-card").forEach((card) => {
      const school = card.querySelector('[name="school"]')?.value.trim();
      const major = card.querySelector('[name="major"]')?.value.trim();
      const startDate = card.querySelector('[name="school_start_date"]')?.value;
      const endDate = card.querySelector('[name="school_end_date"]')?.value;

      if (school || major || startDate || endDate) {
        results.push({
          school,
          major,
          start_date: startDate,
          end_date: endDate,
        });
      }
    });

    return results;
  }

  if (showWorkButton) {
    showWorkButton.addEventListener("click", () => {
      workExperienceDiv.classList.remove("hidden");
      showWorkButton.classList.add("hidden");

      if (workExperienceCount === 0) {
        createWorkExperience();
      }
    });
  }

  if (continueWorkButton) {
    continueWorkButton.addEventListener("click", () => {
      createWorkExperience();
    });
  }

  if (showEducationButton) {
    showEducationButton.addEventListener("click", () => {
      educationDiv.classList.remove("hidden");
      showEducationButton.classList.add("hidden");

      if (educationCount === 0) {
        createEducation();
      }
    });
  }

  if (continueEducationButton) {
    continueEducationButton.addEventListener("click", () => {
      createEducation();
    });
  }

  if (resumeInput) {
    resumeInput.addEventListener("change", () => {
      showSelectedFile(resumeInput, resumeFileName, "Upload your resume");
      validateFile(resumeInput, "resume");
    });
  }

  if (coverLetterInput) {
    coverLetterInput.addEventListener("change", () => {
      showSelectedFile(
        coverLetterInput,
        coverLetterFileName,
        "Upload your cover letter"
      );
      validateFile(coverLetterInput, "cover letter");
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!validateFile(resumeInput, "resume")) return;
    if (!validateFile(coverLetterInput, "cover letter")) return;

    const workExperience = processWorkExperience();
    const education = processEducation();

    const formData = new FormData();

    formData.append("work_experience", JSON.stringify(workExperience));
    formData.append("school", JSON.stringify(education));
    formData.append("resume", resumeInput.files[0]);
    formData.append("cover_letter", coverLetterInput.files[0]);

    try {
      const response = await apiFetch(`${API_URL}/complete-skill`, {
        method: "POST",
        body: formData,
      });

      if (!response) return;

      if (response.ok) {
        window.location.href = "details.html";
      } else {
        const errorText = await response.text()
        console.error("Skill form error:", errorText);
        alert(errorText)
      }
    } catch (error) {
      console.error("Request failed:", errorText);
      alert(errorText)
    }
  });
});