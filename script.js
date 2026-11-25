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

// Current Entrants: load registered team names live from the server.
// Shows the first few, with the rest in a "See all" dropdown.
const entrants = document.getElementById("entrants");
if (entrants) {
  const VISIBLE = 5;
  const makeList = (names) => {
    const ul = document.createElement("ul");
    ul.className = "team-list";
    names.forEach((name) => {
      const li = document.createElement("li");
      li.textContent = name; // textContent: team names are shown as plain text, never HTML
      ul.appendChild(li);
    });
    return ul;
  };

  fetch("api/teams.php", { headers: { Accept: "application/json" }, cache: "no-store" })
    .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
    .then(({ teams }) => {
      if (!Array.isArray(teams) || teams.length === 0) return;
      entrants.replaceChildren(makeList(teams.slice(0, VISIBLE)));
      if (teams.length > VISIBLE) {
        const more = document.createElement("details");
        more.className = "team-more";
        const summary = document.createElement("summary");
        summary.textContent = `See all ${teams.length} teams`;
        more.append(summary, makeList(teams.slice(VISIBLE)));
        more.addEventListener("toggle", () => {
          summary.textContent = more.open ? "Show fewer" : `See all ${teams.length} teams`;
        });
        entrants.appendChild(more);
      }
      const note = document.getElementById("entrants-note");
      if (note) {
        note.innerHTML = "";
        const count = document.createElement("span");
        count.className = "team-count";
        count.textContent = `${teams.length} ${teams.length === 1 ? "team" : "teams"}`;
        note.append(count, " locked in. Many more to follow.");
      }
    })
    .catch(() => { /* keep the list written in the page */ });
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
