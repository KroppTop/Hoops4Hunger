// Registrations from the form are emailed to this address.
const CONTACT_EMAIL = "hello@hoops4hunger.com";

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

// Registration form: validate, then open a pre-filled email to the organizers
const form = document.getElementById("register-form");
if (form) {
  const status = document.getElementById("form-status");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    let valid = true;
    form.querySelectorAll("[required]").forEach((field) => {
      const ok = field.checkValidity();
      field.classList.toggle("invalid", !ok);
      if (!ok) valid = false;
    });
    if (!valid) {
      status.textContent = "Please fill in the highlighted fields.";
      status.className = "form-status error";
      form.querySelector(".invalid").focus();
      return;
    }
    const d = new FormData(form);
    const body = [
      `Team Name: ${d.get("team")}`,
      `Captain's Name: ${d.get("captain")}`,
      `Email Address: ${d.get("email")}`,
      `Phone Number: ${d.get("phone")}`,
      "",
      "Individual Player Heights:",
      d.get("heights") || "(not provided)",
    ].join("\n");
    const subject = `Hoops for Hunger Registration: ${d.get("team")}`;
    window.location.href = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    status.textContent = "Thanks! Your email app should open with your registration ready to send.";
    status.className = "form-status ok";
  });
}
