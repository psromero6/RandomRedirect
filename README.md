# Random Redirect

A tiny static site: visiting it sends you to a random link from `links.csv`.

## Edit the links

Open `links.csv` and add one row per link:

```csv
url,label,weight
https://example.com,Example,1
https://example.org,Shows up twice as often,2
```

- `url` (required): must start with `http://` or `https://`.
- `label` (optional): just a note for you; it isn't shown.
- `weight` (optional): higher numbers get picked more often. Leave blank for 1; use 0 to switch a link off.
- Lines starting with `#` are ignored.

Edit the file on GitHub, commit, and the site picks up the change in a minute or so.

## Host it on GitHub Pages

1. Create a new repository on GitHub (e.g. `random-redirect`).
2. Upload `index.html`, `links.csv` and this README to the root of the repo.
3. Go to **Settings → Pages**.
4. Under **Build and deployment**, set **Source** to *Deploy from a branch*, pick `main` and `/ (root)`, then **Save**.
5. After a minute your site is live at `https://<your-username>.github.io/random-redirect/`.

## Testing locally

Opening `index.html` straight from your disk won't work, because browsers block reading `links.csv` from a `file://` page. Run a local server in the folder instead:

```sh
python3 -m http.server
```

then visit http://localhost:8000.
