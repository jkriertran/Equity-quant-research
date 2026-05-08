# QQQ Alpha Research Framework GitHub Page

This folder contains the static site version of `QUANT_ALPHA_RESEARCH_FRAMEWORK.md`.

## Additional Docs

- [NTSX + Tactical TQQQ Alpaca Handoff](NTSX_TQQQ_ALPACA_HANDOFF.md)

## Local Preview

Open `docs/index.html` in a browser.

## Regenerate The Page

After editing the source markdown, run:

```bash
python tools/build_github_page.py
```

## Publish With GitHub Pages

1. Push this project to a GitHub repository.
2. In GitHub, open the repository settings.
3. Go to **Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Choose the branch you want to publish, then choose the `/docs` folder.
6. Save the setting.

GitHub will publish the page at:

```text
https://<your-github-username>.github.io/<repository-name>/
```

If the repository is named `<your-github-username>.github.io`, the page will publish at:

```text
https://<your-github-username>.github.io/
```
