# Hoops4Hunger

A one-page website for the Hoops4Hunger community 3-on-3 basketball tournament, which raises food and money for local food banks.

Plain HTML, CSS and JavaScript with no build step.

## Preview locally

Open `index.html` in a browser, or run:

```sh
python3 -m http.server 8000
```

then visit http://localhost:8000.

## Updating content

- **Email, donation link, meal goal and stats:** edit the `CONFIG` block at the top of `script.js`.
- **Date, venue, divisions, FAQ:** edit `index.html` (look for `EDIT:` comments).
- **Colors and fonts:** the variables at the top of `styles.css`.

## Publishing with GitHub Pages

In the repository on GitHub, go to **Settings → Pages**, choose **Deploy from a branch**, pick the branch and `/ (root)`, and save.
