from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "QUANT_ALPHA_RESEARCH_FRAMEWORK.md"
DOCS = ROOT / "docs"
OUTPUT = DOCS / "index.html"


def read_article_markdown() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def render_article(markdown_text: str) -> str:
    return markdown.markdown(
        markdown_text,
        extensions=["extra", "sane_lists", "toc"],
        extension_configs={
            "toc": {
                "permalink": False,
                "toc_depth": "2-3",
            }
        },
        output_format="html5",
    )


def build_page(article_html: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>A Beginner-Friendly Framework for Finding Quantitative Alpha</title>
  <meta name="description" content="A class-friendly guide to quantitative alpha research, feature generation, exogenous data, and realistic backtesting.">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
  <header class="site-hero">
    <div class="hero-inner">
      <div class="hero-copy">
        <p class="eyebrow">QQQ Alpha Research Framework</p>
        <h1>A Beginner-Friendly Framework for Finding Quantitative Alpha</h1>
        <p class="hero-lede">How to move from market hypotheses to clean datasets, testable features, realistic next-open backtests, and out-of-sample evidence.</p>
        <nav class="quick-links" aria-label="Key sections">
          <a href="#why-off-the-shelf-chart-tools-are-not-enough">Chart Tools</a>
          <a href="#how-to-generate-features-from-raw-data">Feature Building</a>
          <a href="#how-backtesting-should-work">Backtesting</a>
          <a href="#practical-checklist">Checklist</a>
        </nav>
      </div>
      <figure class="hero-figure">
        <img src="assets/img/walkforward_equity.png" alt="Walk-forward equity curve from the QQQ combined selector research">
        <figcaption>Example output from the walk-forward testing workflow.</figcaption>
      </figure>
    </div>
  </header>

  <section class="principles" aria-label="Core principles">
    <div class="principles-inner">
      <div>
        <span class="principle-number">01</span>
        <h2>Start With A Question</h2>
        <p>Begin with a market behavior you can test, not an indicator that looks good on a chart.</p>
      </div>
      <div>
        <span class="principle-number">02</span>
        <h2>Build Features</h2>
        <p>Convert raw prices, breadth, positioning, and options data into clean columns known before the trade.</p>
      </div>
      <div>
        <span class="principle-number">03</span>
        <h2>Normalize Context</h2>
        <p>Use momentum, z-scores, percentiles, ratios, and volatility adjustment to compare market states fairly.</p>
      </div>
      <div>
        <span class="principle-number">04</span>
        <h2>Test Honestly</h2>
        <p>Use next-open execution, costs, walk-forward selection, non-overlap rules, and out-of-sample validation.</p>
      </div>
    </div>
  </section>

  <main class="page-shell">
    <aside class="toc-panel" aria-label="Table of contents">
      <p class="toc-title">Contents</p>
      <ol class="toc-list"></ol>
    </aside>
    <article class="article">
      {article_html}
    </article>
  </main>

  <section class="chart-strip" aria-label="Example research chart">
    <div class="chart-strip-inner">
      <div>
        <p class="eyebrow">Why normalization matters</p>
        <h2>Raw values are often less useful than context-aware values.</h2>
        <p>Rolling z-scores and rolling percentiles help ask whether a variable is unusual versus its own recent history.</p>
      </div>
      <figure>
        <img src="assets/img/raw_vs_normalized_robust_score.png" alt="Comparison of raw versus normalized DIX and GEX pullback tests">
      </figure>
    </div>
  </section>

  <footer class="site-footer">
    <p>Educational research guide. Not investment advice. Generated from <code>QUANT_ALPHA_RESEARCH_FRAMEWORK.md</code>.</p>
  </footer>

  <script>
    const tocList = document.querySelector(".toc-list");
    const headings = Array.from(document.querySelectorAll(".article h2"));

    headings.forEach((heading) => {{
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = `#${{heading.id}}`;
      link.textContent = heading.textContent;
      item.appendChild(link);
      tocList.appendChild(item);
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    html = build_page(render_article(read_article_markdown()))
    OUTPUT.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
