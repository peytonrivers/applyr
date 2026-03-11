/* ============================================================
   style.js  —  Scroll Reveal
   Uses IntersectionObserver to add .visible to [data-reveal]
   elements as they enter the viewport.
   ============================================================ */

(function () {
  /* --- Observer config ---
     threshold: how much of the element must be visible before it fires
     rootMargin: fires slightly before the element fully enters (feels snappier) */
  const OBSERVER_OPTIONS = {
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px',
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        // Stop watching once revealed — no need to re-animate
        observer.unobserve(entry.target);
      }
    });
  }, OBSERVER_OPTIONS);

  /* Observe every element that has [data-reveal] */
  function initReveal() {
    document.querySelectorAll('[data-reveal]').forEach((el) => {
      observer.observe(el);
    });
  }

  /* Run after DOM is ready */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReveal);
  } else {
    initReveal();
  }
})();


// ---------- SIGN UP BUTTONS (index.html only) ----------
// Target only the specific sign up buttons, not every .btn on every page

const googleAuthUrl = "https://applyr-12k0.onrender.com/auth/google";

// Header "Sign Up" button
const headerSignUpBtn = document.getElementById("headerSignUpBtn");
if (headerSignUpBtn) {
  headerSignUpBtn.addEventListener("click", () => {
    window.location.href = googleAuthUrl;
  });
}

// Hero "Sign Up with Google" button
const heroSignUpBtn = document.getElementById("heroSignUpBtn");
if (heroSignUpBtn) {
  heroSignUpBtn.addEventListener("click", () => {
    window.location.href = googleAuthUrl;
  });
}

// Waitlist "Sign Up with Google" button
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

    if (!isValidName.test(first_name) || !isValidName