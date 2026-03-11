/* ============================================================
   style.js  —  Scroll Reveal
   Uses IntersectionObserver to add .visible to [data-reveal]
   elements as they enter the viewport.
   ============================================================ */

(function () {
  const OBSERVER_OPTIONS = {
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px',
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, OBSERVER_OPTIONS);

  function initReveal() {
    document.querySelectorAll('[data-reveal]').forEach((el) => {
      observer.observe(el);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReveal);
  } else {
    initReveal();
  }
})();


// ---------- API CONFIG ----------

const API_URL = "https://api.apply-r.com";

async function apiFetch(url, options = {}) {
  const res = await fetch(url, { credentials: "include", ...options });

  if (res.status === 401) {
    const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });

    if (refreshRes.ok) {
      return fetch(url, { credentials: "include", ...options });
    } else {
      window.location.href = "index.html";
      return;
    }
  }

  return res;
}


// ---------- SIGN UP BUTTONS (index.html only) ----------

const googleAuthUrl = `${API_URL}/auth/google`;

const headerSignUpBtn = document.getElementById("headerSignUpBtn");
if (headerSignUpBtn) {
  headerSignUpBtn.addEventListener("click", () => {
    window.location.href = googleAuthUrl;
  });
}

const heroSignUpBtn = document.getElementById("heroSignUpBtn");
if (heroSignUpBtn) {
  heroSignUpBtn.addEventListener("click", () => {
    window.location.href = googleAuthUrl;
  });
}

document.querySelectorAll('.btn-signup').forEach((btn) => {
  btn.addEventListener('click', () => {
    window.location.href = googleAuthUrl;
  });
});


// ---------- SIGNUP FORM (signup.html) ----------

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("signupForm");
  const firstNameInput = document.getElementById("firstName");
  const lastNameInput = document.getElementById("lastName");
  const phoneInput = document.getElementById("phoneNumber");

  if (!form) return;

  const lettersOnly = /[^A-Za-z]/g;
  const digitsOnly = /\D/g;
  const isValidName = /^[A-Za-z]+$/;
  const isValidPhone = /^\d{10}$/;

  [firstNameInput, lastNameInput].forEach((input) => {
    if (!input) return;
    input.addEventListener("input", () => {
      input.value = input.value.replace(lettersOnly, "");
    });
  });

  if (phoneInput) {
    phoneInput.addEventListener("input", () => {
      phoneInput.setCustomValidity("");
      const digits = phoneInput.value.replace(digitsOnly, "").slice(0, 10);
      let formatted = "";
      if (digits.length <= 3) {
        formatted = digits.length ? `(${digits}` : "";
      } else if (digits.length <= 6) {
        formatted = `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
      } else {
        formatted = `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
      }
      phoneInput.value = formatted;
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const first_name = firstNameInput?.value.trim() || "";
    const last_name = lastNameInput?.value.trim() || "";
    const phone_number = phoneInput?.value.replace(digitsOnly, "") || "";

    if (!isValidName.test(first_name) || !isValidName.test(last_name)) {
      window.location.href = "error.html";
      return;
    }

    if (!isValidPhone.test(phone_number)) {
      phoneInput.setCustomValidity("Please enter a valid 10-digit phone number.");
      phoneInput.reportValidity();
      return;
    }

    try {
      const response = await apiFetch(`${API_URL}/complete-signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ first_name, last_name, phone_number }),
      });

      if (response.ok) {
        window.location.href = "complete.html";
      } else if (response.status === 401) {
        window.location.href = "index.html";
      } else {
        console.error("Signup error:", await response.json());
        window.location.href = "error.html";
      }
    } catch (error) {
      console.error("Request failed:", error);
      window.location.href = "error.html";
    }
  });
});


// ---------- HEADER SCROLL ----------

const header = document.querySelector('.site-header');

window.addEventListener('scroll', () => {
  if (window.scrollY > 20) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});