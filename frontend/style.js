// ---------- SIGNUP FORM REDIRECT ----------

document.querySelectorAll(".btn").forEach(btn => {
  btn.addEventListener("click", () => {
    window.location.href = "https://applyr-12k0.onrender.com/auth/google";
  });
});

// Handle OAuth callback
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
      const token = localStorage.getItem('token');
      
      if (!token) {
        window.location.href = "index.html";
        return;
      }

      const response = await fetch("https://applyr-12k0.onrender.com/complete-signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          first_name,
          last_name,
          phone_number
        })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.removeItem('token');
        window.location.href = "complete.html";
      } else {
        const error = await response.json();
        console.error("Signup error:", error);
        window.location.href = "error.html";
      }
    } catch (error) {
      console.error("Request failed:", error);
      window.location.href = "error.html";
    }
  });
});
