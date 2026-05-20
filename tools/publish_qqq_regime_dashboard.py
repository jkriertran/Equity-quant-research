from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis_output" / "qqq_macro_regime_study"
DEST = ROOT / "docs" / "qqq-regime-dashboard"
PLOTS_DEST = DEST / "plots"
DATA_DEST = DEST / "data"


def copy_file(source: Path, dest: Path) -> dict[str, object]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return {
        "path": str(dest.relative_to(DEST)),
        "source": str(source.relative_to(ROOT)),
        "bytes": dest.stat().st_size,
    }


def csv_sources() -> list[Path]:
    return sorted(
        path
        for path in SOURCE.glob("*.csv")
        if path.name != "raw_fred_macro.csv" and not path.name.startswith(".")
    )


def plot_sources() -> list[Path]:
    return sorted(path for path in (SOURCE / "plots").glob("*.png") if not path.name.startswith("."))


def data_download_section(csv_files: list[dict[str, object]]) -> str:
    rows = []
    for file_info in csv_files:
        path = file_info["path"]
        name = Path(str(path)).name
        rows.append(
            "<tr>"
            f'<td><a href="{path}">{name}</a></td>'
            f"<td>{int(file_info['bytes']):,}</td>"
            "</tr>"
        )
    return (
        '<section class="section">\n'
        '  <div class="eyebrow">Published data</div>\n'
        "  <h2>CSV Downloads</h2>\n"
        '  <p class="table-note">These are the generated study outputs copied with this static dashboard. '
        "They support inspection and reproducibility; they are not live data feeds.</p>\n"
        '  <table class="dashboard-table">\n'
        "    <thead><tr><th>File</th><th>Bytes</th></tr></thead>\n"
        f"    <tbody>{''.join(rows)}</tbody>\n"
        "  </table>\n"
        "</section>\n"
    )


def write_index(csv_files: list[dict[str, object]]) -> dict[str, object]:
    source_html = SOURCE / "qqq_macro_regime_nowcasting_dashboard.html"
    if not source_html.exists():
        raise FileNotFoundError(f"Missing dashboard HTML: {source_html}")
    html = source_html.read_text(encoding="utf-8")
    section = data_download_section(csv_files)
    if "<footer>" in html:
        html = html.replace("<footer>", section + "<footer>", 1)
    else:
        html += "\n" + section
    index = DEST / "index.html"
    index.write_text(html, encoding="utf-8")
    return {
        "path": str(index.relative_to(DEST)),
        "source": str(source_html.relative_to(ROOT)),
        "bytes": index.stat().st_size,
    }


def write_readme(csv_files: list[dict[str, object]], plot_files: list[dict[str, object]]) -> dict[str, object]:
    text = "\n".join(
        [
            "# QQQ Regime Dashboard",
            "",
            "Static GitHub Pages copy of the QQQ macro-regime nowcasting dashboard.",
            "",
            "## Files",
            "",
            "- `index.html`: publishable dashboard entry point.",
            f"- `plots/`: {len(plot_files)} PNG chart files.",
            f"- `data/`: {len(csv_files)} CSV study output files plus `manifest.json`.",
            "",
            "## Local Preview",
            "",
            "Open `docs/qqq-regime-dashboard/index.html` in a browser.",
            "",
            "## Regenerate",
            "",
            "After rerunning the regime study, refresh this publishable copy with:",
            "",
            "```bash",
            "python3 tools/publish_qqq_regime_dashboard.py",
            "```",
            "",
        ]
    )
    readme = DEST / "README.md"
    readme.write_text(text, encoding="utf-8")
    return {
        "path": str(readme.relative_to(DEST)),
        "source": "tools/publish_qqq_regime_dashboard.py",
        "bytes": readme.stat().st_size,
    }


def write_manifest(index_file: dict[str, object], csv_files: list[dict[str, object]], plot_files: list[dict[str, object]]) -> dict[str, object]:
    manifest = {
        "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_dir": str(SOURCE.relative_to(ROOT)),
        "publish_dir": str(DEST.relative_to(ROOT)),
        "entrypoint": index_file,
        "plots": plot_files,
        "csv_outputs": csv_files,
    }
    manifest_path = DATA_DEST / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {
        "path": str(manifest_path.relative_to(DEST)),
        "source": "tools/publish_qqq_regime_dashboard.py",
        "bytes": manifest_path.stat().st_size,
    }


def publish() -> dict[str, object]:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source output directory: {SOURCE}")
    DEST.mkdir(parents=True, exist_ok=True)
    PLOTS_DEST.mkdir(parents=True, exist_ok=True)
    DATA_DEST.mkdir(parents=True, exist_ok=True)

    plot_files = [copy_file(path, PLOTS_DEST / path.name) for path in plot_sources()]
    csv_files = [copy_file(path, DATA_DEST / path.name) for path in csv_sources()]
    index_file = write_index(csv_files)
    readme_file = write_readme(csv_files, plot_files)
    manifest_file = write_manifest(index_file, csv_files, plot_files)

    return {
        "publish_dir": str(DEST.relative_to(ROOT)),
        "entrypoint": index_file["path"],
        "plot_count": len(plot_files),
        "csv_count": len(csv_files),
        "manifest": manifest_file["path"],
        "readme": readme_file["path"],
    }


def main() -> None:
    result = publish()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
