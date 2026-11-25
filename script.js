// ===== EDIT THESE to update the site =====
const CONFIG = {
  contactEmail: "hello@example.com",   // registrations are emailed here
  donateUrl: "#",                       // your donation page link
  mealsRaised: 0,
  mealsGoal: 10000,
  stats: {
    teams: 0,
    pounds: 0,
    volunteers: 0,
  },
};
// =========================================

const fmt = (n) => n.toLocaleString("en-US");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function countUp(el, target, duration = 1400) {
  if (reduceMotion || target === 0) { el.textContent = fmt(target); return; }
  const start = performance.now();
  const tick = (now) => {
    const t = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = fmt(Math.round(target * eased));
    if (t < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

// Year, links
document.getElementById("year").textContent = new Date().getFullYear();
const contact = document.getElementById("contact-link");
contact.href = `mailto:${CONFIG.contactEmail}`;
contact.textContent = CONFIG.contactEmail;
document.getElementById("donate-link").href = CONFIG.donateUrl;

// Progress card
const pct = CONFIG.mealsGoal ? Math.min(100, (CONFIG.mealsRaised / CONFIG.mealsGoal) * 100) : 0;
document.getElementById("meals-goal").textContent = fmt(CONFIG.mealsGoal);
countUp(document.getElementById("meals-count"), CONFIG.mealsRaised);
const progress = document.querySelector(".progress");
progress.setAttribute("aria-valuenow", Math.round(pct));
requestAnimationFrame(() => { document.getElementById("progress-bar").style.width = `${pct}%`; });

// Stats: animate when scrolled into view
const statEls = document.querySelectorAll("[data-stat]");
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    const el = entry.target;
    countUp(el, CONFIG.stats[el.dataset.stat] ?? 0);
    observer.unobserve(el);
  });
}, { threshold: 0.4 });
statEls.forEach((el) => observer.observe(el));

// Mobile nav
const toggle = document.querySelector(".nav-toggle");
const links = document.getElementById("nav-links");
toggle.addEventListener("click", () => {
  const open = links.classList.toggle("open");
  toggle.setAttribute("aria-expanded", String(open));
});
links.addEventListener("click", (e) => {
  if (e.target.tagName === "A") {
    links.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
  }
});

// Registration form: validates, then opens a pre-filled email
const form = document.getElementById("register-form");
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
    return;
  }
  const data = new FormData(form);
  const body = [
    `Team: ${data.get("team")}`,
    `Captain: ${data.get("captain")}`,
    `Email: ${data.get("email")}`,
    `Division: ${data.get("division")}`,
    "",
    "Players:",
    data.get("players") || "(not listed)",
  ].join("\n");
  const subject = `Hoops4Hunger registration: ${data.get("team")}`;
  window.location.href = `mailto:${CONFIG.contactEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  status.textContent = "Thanks! Your email app should open so you can send the registration.";
  status.className = "form-status ok";
});
