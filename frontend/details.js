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
    const OBSERVER_OPTIONS = {
        threshold: 0.06,
        rootMargin: "0px 0px -40px 0px",
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    }, OBSERVER_OPTIONS);

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

    const countryInput = document.getElementById("country");
    const stateInput = document.getElementById("state");
    const cityInput = document.getElementById("city");
    const zipcodeInput = document.getElementById("zip-code");
    const disabilityInput = document.getElementById("disability");
    const veteranInput = document.getElementById("veteran");
    const ethnicityInput = document.getElementById("ethnicity");

    if (!detailsForm) return;

    function clearValidityOnInput(input) {
        if (!input) return;

        input.addEventListener("input", () => {
            input.setCustomValidity("");
        });

        input.addEventListener("change", () => {
            input.setCustomValidity("");
        });
    }

    [
        countryInput,
        stateInput,
        cityInput,
        zipcodeInput,
        disabilityInput,
        veteranInput,
        ethnicityInput
    ].forEach(clearValidityOnInput);

    document.querySelectorAll('input[name="work-authorization"]').forEach((input) => {
        input.addEventListener("change", () => {
            input.setCustomValidity("");
        });
    });

    document.querySelectorAll('input[name="gender"]').forEach((input) => {
        input.addEventListener("change", () => {
            input.setCustomValidity("");
        });
    });

    detailsForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const country = countryInput.value;
        const state = stateInput.value;
        const city = cityInput.value.trim();
        const zipcode = zipcodeInput.value.trim();
        const disability = disabilityInput.value;
        const veteran = veteranInput.value;
        const ethnicityValue = ethnicityInput.value;

        const authorizationInput = document.querySelector(
            'input[name="work-authorization"]:checked'
        );

        const authorizationReporter = document.querySelector(
            'input[name="work-authorization"]'
        );

        const genderInput = document.querySelector(
            'input[name="gender"]:checked'
        );

        const genderReporter = document.querySelector(
            'input[name="gender"]'
        );

        if (!country) {
            countryInput.setCustomValidity("Please select your country.");
            countryInput.reportValidity();
            return;
        }

        if (!state) {
            stateInput.setCustomValidity("Please select your state.");
            stateInput.reportValidity();
            return;
        }

        if (!city) {
            cityInput.setCustomValidity("Please enter your city.");
            cityInput.reportValidity();
            return;
        }

        if (!zipcode) {
            zipcodeInput.setCustomValidity("Please enter your zip code.");
            zipcodeInput.reportValidity();
            return;
        }

        if (!authorizationInput) {
            authorizationReporter.setCustomValidity("Please select yes or no.");
            authorizationReporter.reportValidity();
            return;
        }

        if (!disability) {
            disabilityInput.setCustomValidity("Please select your disability status.");
            disabilityInput.reportValidity();
            return;
        }

        if (!veteran) {
            veteranInput.setCustomValidity("Please select your veteran status.");
            veteranInput.reportValidity();
            return;
        }

        if (!genderInput) {
            genderReporter.setCustomValidity("Please select your gender.");
            genderReporter.reportValidity();
            return;
        }

        if (!ethnicityValue) {
            ethnicityInput.setCustomValidity("Please select your ethnicity.");
            ethnicityInput.reportValidity();
            return;
        }

        const detailsData = {
            country,
            state,
            city,
            zipcode,
            authorization: authorizationInput.value,
            disability,
            veteran,
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

            if (response.ok) {
                window.location.href = "complete.html";
            } else if (response.status === 401) {
                window.location.href = "index.html";
            } else {
                console.error("Details error:", await response.json());
                window.location.href = "error.html";
            }

        } catch (error) {
            console.error("Request failed:", error);
            window.location.href = "error.html";
        }
    });
});