
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".btn-google").forEach(btn => {
    btn.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:8000/auth/google";
    });
  });

  const primaryBtn = document.querySelector(".btn-primary");
  if (primaryBtn) {
    primaryBtn.addEventListener("click", () => {
      window.location.href = "http://127.0.0.1:8000/auth/google";
    });
  }
});

// ---------- SIGNUP FORM REDIRECT ----------

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
      phoneInput.value = phoneInput.value.replace(digitsOnly, "").slice(0, 10);
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const first_name = firstNameInput?.value.trim() || "";
    const last_name = lastNameInput?.value.trim() || "";
    const phone_number = phoneInput?.value.trim() || "";

    if (!isValidName.test(first_name) || !isValidName.test(last_name)) {
      window.location.href = "error.html";
      return;
    }

    if (!isValidPhone.test(phone_number)) {
      window.location.href = "error.html";
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/complete-signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({
          first_name,
          last_name,
          phone_number
        })
      });

      if (response.ok) {
        window.location.href = "complete.html";
      } else {
        window.location.href = "error.html";
      }
    } catch (error) {
      window.location.href = "error.html";
    }
  });
});