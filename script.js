// Registration questions go here if the online form can't be reached.
const CONTACT_EMAIL = "hello@hoops4hunger.com";
const CONTACT_PHONE = "(920) 658-3029";

// Footer year
document.querySelectorAll("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });

// Mobile nav
const toggle = document.querySelector(".nav-toggle");
const links = document.getElementById("nav-links");
if (toggle && links) {
  toggle.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  links.addEventListener("click", (e) => {
    if (e.target.closest("a")) {
      links.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
}

// Registration form: posts to api/register.php, which emails the organizers
// and adds the captain to Hostinger Reach.
const form = document.getElementById("register-form");
if (form) {
  const status = document.getElementById("form-status");
  const button = document.getElementById("submit-btn");
  const buttonLabel = button.textContent;

  const show = (text, kind, html = false) => {
    status[html ? "innerHTML" : "textContent"] = text;
    status.className = `form-status ${kind}`;
  };

  // Result of a no-JavaScript submission redirected back here
  const params = new URLSearchParams(location.search);
  if (params.get("status") === "ok") {
    show("Thanks! Your team is registered. Remember to bring one paper bag of nonperishable food to check-in.", "ok");
  } else if (params.get("status") === "error") {
    show(params.get("msg") || "Something went wrong. Please try again.", "error");
  }

  // Build a pre-filled email as a backup if the server can't be reached
  const mailtoBackup = (d) => {
    const body = [
      `Team Name: ${d.get("team")}`,
      `Captain's Name: ${d.get("captain")}`,
      `Email Address: ${d.get("email")}`,
      `Phone Number: ${d.get("phone")}`,
      "",
      "Individual Player Heights:",
      d.get("heights") || "(not provided)",
    ].join("\n");
    return `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(`Team Registration: ${d.get("team")}`)}&body=${encodeURIComponent(body)}`;
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    let valid = true;
    form.querySelectorAll("[required]").forEach((field) => {
      const ok = field.checkValidity();
      field.classList.toggle("invalid", !ok);
      if (!ok) valid = false;
    });
    if (!valid) {
      show("Please fill in the highlighted fields.", "error");
      form.querySelector(".invalid").focus();
      return;
    }

    const data = new FormData(form);
    button.disabled = true;
    button.textContent = "Submitting…";
    show("", "");

    try {
      const res = await fetch(form.action, {
        method: "POST",
        body: data,
        headers: { Accept: "application/json", "X-Requested-With": "fetch" },
      });
      let result = null;
      try { result = await res.json(); } catch { /* not JSON: handler not available */ }

      if (result && result.ok) {
        show(result.message, "ok");
        form.reset();
      } else if (result) {
        show(result.message || "Something went wrong. Please try again.", "error");
      } else {
        throw new Error(`Unexpected response (${res.status})`);
      }
    } catch (err) {
      // Server unreachable: let them send it by email instead
      show(
        `We couldn't submit the form right now. <a href="${mailtoBackup(data)}">Send your registration by email</a> or call ${CONTACT_PHONE}.`,
        "error",
        true,
      );
    } finally {
      button.disabled = false;
      button.textContent = buttonLabel;
    }
  });

  form.querySelectorAll("[required]").forEach((field) => {
    field.addEventListener("input", () => field.classList.remove("invalid"));
  });
}
