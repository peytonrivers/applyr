const API_URL = "https://applyr-12k0.onrender.com";

export async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",  // sends the HttpOnly cookie automatically
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (res.status === 401) {
    // Token expired or missing — send back to login
    window.location.href = "/index.html";
    return;
  }

  return res;
}

// Example usage in complete-signup.html:
//
// import { apiFetch } from "./api.js";
//
// const res = await apiFetch("/complete-signup", {
//   method: "POST",
//   body: JSON.stringify({ first_name, last_name, phone_number }),
// });
