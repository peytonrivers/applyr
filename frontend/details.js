const API_URL = "https://api.apply-r.com";

async function apiFetch(url, options = {}) {
    const res = await fetch(url, {
        credentials: "include",
        ...options
    });

    if (res.status === 401) {
        const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
            method: "POST",
            credentials: "include"
        });

        if (refreshRes.ok) {
            return fetch(url, {
                credentials: "include",
                ...options
            });
        } else {
            window.location.href = "index.html";
            return;
        }
    }

    return res;
}


// ---------- SCROLL REVEAL ----------

(function () {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.06,
        rootMargin: "0px 0px -40px 0px"
    });

    function initReveal() {
        document.querySelectorAll("[data-reveal]").forEach((el) => {
            observer.observe(el);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initReveal);
    } else {
        initReveal();
    }
})();


// ---------- HEADER SCROLL ----------

const header = document.querySelector(".site-header");

window.addEventListener("scroll", () => {
    if (!header) return;

    if (window.scrollY > 20) {
        header.classList.add("scrolled");
    } else {
        header.classList.remove("scrolled");
    }
});


// ---------- DETAILS FORM ----------

document.addEventListener("DOMContentLoaded", () => {
    const detailsForm = document.getElementById("details-form");

    if (!detailsForm) return;

    detailsForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const country = document.getElementById("country").value;
        const state = document.getElementById("state").value;
        const city = document.getElementById("city").value.trim();
        const zipcode = document.getElementById("zip-code").value.trim();

        const authorizationInput = document.querySelector(
            'input[name="work-authorization"]:checked'
        );

        const genderInput = document.querySelector(
            'input[name="gender"]:checked'
        );

        const disability = document.getElementById("disability").value;
        const veteran = document.getElementById("veteran").value;
        const ethnicityValue = document.getElementById("ethnicity").value;

        if (!authorizationInput) {
            alert("Please select your work authorization.");
            return;
        }

        if (!genderInput) {
            alert("Please select your gender.");
            return;
        }

        const detailsData = {
            country: country,
            state: state,
            city: city,
            zipcode: zipcode,
            authorization: authorizationInput.value,
            disability: disability,
            veteran: veteran,
            gender: genderInput.value,
            ethnicity: [ethnicityValue]
        };

        try {
            const response = await apiFetch(`${API_URL}/complete-details`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(detailsData)
            });

            if (!response) return;

            const result = await response.json();

            if (response.ok) {
                console.log("Details saved:", result);
                window.location.href = "skill.html";
            } else {
                console.error("Details error:", result);
                alert(result.detail || "Something went wrong.");
            }

        } catch (error) {
            console.error("Request failed:", error);
            window.location.href = "error.html";
        }
    });
});