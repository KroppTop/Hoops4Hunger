# St. John Hoops for Hunger

Website for the St. John Hoops for Hunger 3v3 Challenge in Berlin, WI. All proceeds and food donations go to the Berlin Food Pantry.

Plain HTML, CSS and JavaScript with no build step. The content mirrors the current site at hoops4hunger.com.

## Pages

| File | Page |
| --- | --- |
| `index.html` | Home: cash purse, tournament structure, registered squads |
| `schedule-rules.html` | Eligibility, uniforms, fouls, Day 1 / Day 2 details, Championship Saturday timeline |
| `register.html` | Team registration form |
| `sponsors.html` | Sponsor tiers and sponsorship contact |

Shared files: `styles.css` (colors and fonts are the variables at the top), `script.js` (mobile menu and registration form), `images/`, `fonts/`.

## Fonts

- **Headings:** Deutsch Gothic by J. Fordyce (1994), self-hosted in `fonts/`. Its license allows free distribution as long as the font file is unaltered and `DEUTSCH.TXT` stays with it, so keep both files as they are.
- **Body text:** Barlow, with Barlow Condensed for labels, buttons and numbers (Google Fonts).

Fonts do not load when a page is opened directly from disk; use the local server below to preview.

## Common updates

- **Registered teams:** edit the `team-list` in `index.html`.
- **Sponsors:** copy a `sponsor` card in `sponsors.html` and add the logo to `images/`.
- **Dates / deadline:** the "Sign up before April 7!" banner and the dates appear on every page; search for `April` to find them.
- **Header and footer:** repeated in all four pages, so change them in each file.

## How registration works

The site has no server, so **Submit Registration** opens the visitor's email app with a message to hello@hoops4hunger.com containing the team name, captain, email, phone and player heights. To collect submissions without email, point the form at a form service such as Formspree, Netlify Forms or a Google Form.

## Preview locally

```sh
python3 -m http.server 8000
```

then visit http://localhost:8000.

## Publishing with GitHub Pages

In the repository on GitHub, go to **Settings → Pages**, choose **Deploy from a branch**, pick the branch and `/ (root)`, and save. To use hoops4hunger.com, add the domain under **Custom domain** and point the domain's DNS at GitHub Pages.
