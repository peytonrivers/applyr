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
    if (window.scrollY > 20) {
      header.classList.add("scrolled");
    } else {
      header.classList.remove("scrolled");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("skillForm");

  const resume = document.getElementById("resume");
  const coverLetter = document.getElementById("coverLetter");

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

  const maxFileSize = 5 * 1024 * 1024;
  const allowedExtensions = ["pdf", "doc", "docx"];

  let workExperienceCount = 0;
  const MAX_WORK_EXPERIENCE = 7;

  let educationCount = 0;
  const MAX_EDUCATION = 7;

  if (!form) return;

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

    if (!allowedExtensions.includes(extension)) {
      input.setCustomValidity("Please upload a PDF, DOC, or DOCX file.");
      input.reportValidity();
      return false;
    }

    if (file.size > maxFileSize) {
      input.setCustomValidity("File must be 5MB or smaller.");
      input.reportValidity();
      return false;
    }

    input.setCustomValidity("");
    return true;
  }

  function createWorkExperience() {
    if (workExperienceCount >= MAX_WORK_EXPERIENCE) return;

    const workDiv = document.createElement("div");
    workDiv.className = "work-card";

    workDiv.innerHTML = `
      <div class="field">
        <label>Company</label>
        <input type="text" name="company" class="field-input" placeholder="Company">
      </div>

      <div class="field">
        <label>Position</label>
        <input type="text" name="position" class="field-input" placeholder="Position">
      </div>

      <div class="field">
        <label>Start Date</label>
        <input type="date" name="work_start_date" class="field-input">
      </div>

      <div class="field">
        <label>End Date</label>
        <input type="date" name="work_end_date" class="field-input">
      </div>
    `;

    workExperienceContainer.appendChild(workDiv);
    workExperienceCount++;
  }

  function createEducation() {
    if (educationCount >= MAX_EDUCATION) return;

    const educationDivCard = document.createElement("div");
    educationDivCard.className = "education-card";

    educationDivCard.innerHTML = `
      <div class="field">
        <label>School</label>
        <input type="text" name="school" class="field-input" placeholder="School">
      </div>

      <div class="field">
        <label>Major</label>
        <input type="text" name="major" class="field-input" placeholder="Major">
      </div>

      <div class="field">
        <label>Start Date</label>
        <input type="date" name="school_start_date" class="field-input">
      </div>

      <div class="field">
        <label>End Date</label>
        <input type="date" name="school_end_date" class="field-input">
      </div>
    `;

    educationContainer.appendChild(educationDivCard);
    educationCount++;
  }

  showWorkButton.addEventListener("click", () => {
    workExperienceDiv.classList.remove("hidden");

    if (workExperienceCount === 0) {
      createWorkExperience();
    }

    showWorkButton.classList.add("hidden");
  });

  continueWorkButton.addEventListener("click", () => {
    createWorkExperience();

    if (workExperienceCount >= MAX_WORK_EXPERIENCE) {
      continueWorkButton.disabled = true;
      continueWorkButton.textContent = "Maximum Work Experience Added";
    }
  });

  showEducationButton.addEventListener("click", () => {
    educationDiv.classList.remove("hidden");

    if (educationCount === 0) {
      createEducation();
    }

    showEducationButton.classList.add("hidden");
  });

  continueEducationButton.addEventListener("click", () => {
    createEducation();

    if (educationCount >= MAX_EDUCATION) {
      continueEducationButton.disabled = true;
      continueEducationButton.textContent = "Maximum Education Added";
    }
  });

  resume.addEventListener("change", () => {
    showSelectedFile(resume, resumeFileName, "Upload your resume");
    validateFile(resume, "resume");
  });

  coverLetter.addEventListener("change", () => {
    showSelectedFile(coverLetter, coverLetterFileName, "Upload your cover letter");
    validateFile(coverLetter, "cover letter");
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!validateFile(resume, "resume")) return;
    if (!validateFile(coverLetter, "cover letter")) return;

    const workExperience = [];

    document.querySelectorAll(".work-card").forEach((card) => {
      const company = card.querySelector('input[name="company"]').value.trim();
      const position = card.querySelector('input[name="position"]').value.trim();
      const startDate = card.querySelector('input[name="work_start_date"]').value;
      const endDate = card.querySelector('input[name="work_end_date"]').value;

      if (company || position || startDate || endDate) {
        workExperience.push({
          company,
          position,
          start_date: startDate,
          end_date: endDate,
        });
      }
    });

    const education = [];

    document.querySelectorAll(".education-card").forEach((card) => {
      const school = card.querySelector('input[name="school"]').value.trim();
      const major = card.querySelector('input[name="major"]').value.trim();
      const startDate = card.querySelector('input[name="school_start_date"]').value;
      const endDate = card.querySelector('input[name="school_end_date"]').value;

      if (school || major || startDate || endDate) {
        education.push({
          school,
          major,
          start_date: startDate,
          end_date: endDate,
        });
      }
    });

    const formData = new FormData();

    formData.append("work_experience", JSON.stringify(workExperience));
    formData.append("school", JSON.stringify(education));
    formData.append("resume", resume.files[0]);
    formData.append("cover_letter", coverLetter.files[0]);

    try {
      const response = await apiFetch(`${API_URL}/complete-skill`, {
        method: "POST",
        body: formData,
      });

      if (!response) return;

      if (response.ok) {
        window.location.href = "details.html";
      } else {
        console.error("Skill form error:", await response.text());
        window.location.href = "error.html";
      }
    } catch (error) {
      console.error("Request failed:", error);
      window.location.href = "error.html";
    }
  });
});