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
const googleSignupBtn = document.getElementById("googleSignupBtn");
if (googleSignupBtn) {
  googleSignupBtn.addEventListener("click", () => {
    window.location.href = googleAuthUrl;
  });
}

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
      const token = sessionStorage.getItem("token");

      if (!token) {
        window.location.href = "index.html";
        return;
      }

      const response = await fetch("https://applyr-12k0.onrender.com/complete-signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ first_name, last_name, phone_number }),
      });

      if (response.ok) {
        sessionStorage.removeItem("token");
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