"""Report generators for merged SARIF output (HTML and Markdown)."""

import html
from datetime import datetime
from collections import defaultdict


def _severity_order(level: str) -> int:
    return {"error": 0, "warning": 1, "note": 2}.get((level or "warning").lower(), 1)


def _level_badge_html(level: str) -> str:
    colours = {"error": "#d73a49", "warning": "#e36209", "note": "#0075ca"}
    colour = colours.get(level.lower() if level else "warning", "#e36209")
    label = (level or "warning").upper()
    return (
        f'<span style="background:{colour};color:#fff;padding:2px 7px;'
        f'border-radius:3px;font-size:11px;font-weight:600;">{html.escape(label)}</span>'
    )


def _build_report_data(merged_sarif: dict) -> dict:
    """Extract and group all findings from a merged SARIF document.

    Returns a dict with keys:
      all_findings, sorted_groups, tool_counts,
      total, error_count, warning_count, note_count
    """
    runs = merged_sarif.get("runs", [])
    all_findings = []
    tool_counts: dict = {}

    for run in runs:
        driver = run.get("tool", {}).get("driver", {})
        tool_name = driver.get("name", "Unknown")
        tool_uri = driver.get("informationUri", "")

        rules_index: dict = {}
        for rule in driver.get("rules", []):
            rid = rule.get("id", "")
            desc = (
                rule.get("shortDescription", {}).get("text")
                or rule.get("fullDescription", {}).get("text")
                or rid
            )
            rules_index[rid] = {"desc": desc, "help_uri": rule.get("helpUri", "")}

        counts = tool_counts.setdefault(tool_name, {"error": 0, "warning": 0, "note": 0, "uri": tool_uri})
        for result in run.get("results", []):
            raw_level = (result.get("level") or "").lower()
            # SARIF spec §3.27.10: omitted level defaults to "warning".
            level = raw_level if raw_level in ("error", "warning", "note") else "warning"
            counts[level] += 1

            rule_id = result.get("ruleId", "")
            message = result.get("message", {}).get("text", "")
            loc = (result.get("locations") or [{}])[0]
            phys = loc.get("physicalLocation", {})
            uri = phys.get("artifactLocation", {}).get("uri", "")
            start_line = phys.get("region", {}).get("startLine", "")
            rule_meta = rules_index.get(rule_id, {"desc": rule_id, "help_uri": ""})

            all_findings.append({
                "tool": tool_name,
                "rule_id": rule_id,
                "description": rule_meta["desc"],
                "help_uri": rule_meta["help_uri"],
                "level": level,
                "message": message,
                "uri": uri,
                "start_line": start_line,
            })

    groups: dict = defaultdict(lambda: {"level": "warning", "description": "", "help_uri": "", "locations": [], "_seen": set()})
    for f in all_findings:
        key = (f["tool"], f["rule_id"], f["message"] or f["description"])
        g = groups[key]
        g["level"] = f["level"]
        g["description"] = f["description"]
        if f["help_uri"]:
            g["help_uri"] = f["help_uri"]
        if f["uri"]:
            loc_key = (f["uri"], f["start_line"])
            if loc_key not in g["_seen"]:
                g["_seen"].add(loc_key)
                g["locations"].append(loc_key)

    sorted_groups = sorted(
        groups.items(),
        key=lambda kv: (_severity_order(kv[1]["level"]), kv[0][0], kv[0][1])
    )

    total         = len(all_findings)
    error_count   = sum(1 for f in all_findings if f["level"] == "error")
    warning_count = sum(1 for f in all_findings if f["level"] == "warning")
    note_count    = sum(1 for f in all_findings if f["level"] == "note")

    return {
        "all_findings": all_findings,
        "sorted_groups": sorted_groups,
        "tool_counts": tool_counts,
        "total": total,
        "error_count": error_count,
        "warning_count": warning_count,
        "note_count": note_count,
    }


# ── HTML ─────────────────────────────────────────────────────────────────────

def generate_html_report(merged_sarif: dict, digest: str, languages: list, elapsed: float = 0.0) -> str:
    d = _build_report_data(merged_sarif)
    sorted_groups = d["sorted_groups"]
    tool_counts   = d["tool_counts"]
    total         = d["total"]
    error_count   = d["error_count"]
    warning_count = d["warning_count"]
    note_count    = d["note_count"]

    generated_at  = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    languages_str = html.escape(", ".join(languages) if languages else "—")

    tool_rows = ""
    for name, counts in sorted(tool_counts.items()):
        uri = counts.get("uri", "")
        name_cell = (
            f'<a href="{html.escape(uri)}" target="_blank">{html.escape(name)}</a>'
            if uri else html.escape(name)
        )
        tool_rows += (
            f"<tr>"
            f"<td>{name_cell}</td>"
            f'<td style="color:#d73a49;font-weight:600;">{counts.get("error", 0)}</td>'
            f'<td style="color:#e36209;font-weight:600;">{counts.get("warning", 0)}</td>'
            f'<td style="color:#0075ca;">{counts.get("note", 0)}</td>'
            f"<td>{counts.get('error',0)+counts.get('warning',0)+counts.get('note',0)}</td>"
            f"</tr>"
        )

    finding_rows = ""
    for idx, ((tool_name, rule_id, message), g) in enumerate(sorted_groups):
        locs  = g["locations"]
        count = len(locs)
        group_id = f"grp-{idx}"

        loc_items = ""
        for uri, line in locs:
            text = html.escape(uri) + (f":{line}" if line else "")
            loc_items += (
                f'<span style="display:inline-block;background:#f6f8fa;border:1px solid #e1e4e8;'
                f'border-radius:3px;padding:2px 8px;margin:3px 4px 3px 0;'
                f'font-family:monospace;font-size:11px;white-space:nowrap;">{text}</span>'
            )

        locations_cell = (
            f'<span class="loc-count" onclick="toggleLocs(\'{group_id}\')" '
            f'style="cursor:pointer;color:#0366d6;text-decoration:underline;font-size:12px;">'
            f'{count} location{"s" if count != 1 else ""} &#9660;</span>'
        ) if locs else '<span style="color:#999;font-size:12px;">—</span>'

        detail_row = (
            f'<tr id="{group_id}" style="display:none;background:#fafbfc;">'
            f'<td colspan="5" style="padding:10px 16px;border-bottom:1px solid #e1e4e8;">'
            f'<div style="font-size:11px;font-weight:600;color:#586069;margin-bottom:6px;">LOCATIONS ({count})</div>'
            f'<div style="line-height:1.8;">{loc_items}</div>'
            f'</td></tr>'
        ) if locs else ""

        help_uri  = g["help_uri"]
        rule_cell = (
            f'<a href="{html.escape(help_uri)}" target="_blank" style="font-family:monospace;font-size:12px;">'
            f'{html.escape(rule_id)}</a>'
            if help_uri else
            f'<code style="font-size:12px;">{html.escape(rule_id)}</code>'
        )

        finding_rows += (
            f"<tr>"
            f"<td>{_level_badge_html(g['level'])}</td>"
            f"<td>{html.escape(tool_name)}</td>"
            f"<td>{rule_cell}</td>"
            f"<td>{html.escape(message)}</td>"
            f"<td>{locations_cell}</td>"
            f"</tr>"
            f"{detail_row}"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>mono-sast Report</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
         font-size: 14px; background: #f6f8fa; color: #24292e; }}
  header {{ background: #24292e; color: #fff; padding: 20px 32px; }}
  header h1 {{ margin: 0 0 4px; font-size: 20px; font-weight: 600; }}
  header p  {{ margin: 0; font-size: 12px; opacity: .7; }}
  main {{ padding: 24px 32px; max-width: 1400px; margin: 0 auto; }}
  .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }}
  .card {{ background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 16px 20px; }}
  .card .num {{ font-size: 32px; font-weight: 700; line-height: 1; }}
  .card .lbl {{ font-size: 12px; color: #586069; margin-top: 4px; }}
  .card.error   .num {{ color: #d73a49; }}
  .card.warning .num {{ color: #e36209; }}
  .card.note    .num {{ color: #0075ca; }}
  section {{ background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; margin-bottom: 24px; }}
  section h2 {{ margin: 0; padding: 12px 16px; font-size: 14px; font-weight: 600;
                border-bottom: 1px solid #e1e4e8; background: #f6f8fa;
                border-radius: 6px 6px 0 0; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; padding: 8px 12px; font-size: 12px; font-weight: 600;
        color: #586069; border-bottom: 1px solid #e1e4e8; background: #f6f8fa; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #f0f0f0; vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #f6f8fa; }}
  .meta {{ display: flex; flex-direction: column; gap: 8px; padding: 14px 16px; }}
  .meta div {{ display: flex; align-items: baseline; gap: 10px; font-size: 13px; }}
  .meta-label {{ font-weight: 600; color: #586069; min-width: 220px; flex-shrink: 0; }}
  .meta-value {{ color: #24292e; font-family: monospace; font-size: 12px; word-break: break-all; }}
  .loc-count:hover {{ color: #0075ca; }}
</style>
<script>
  function toggleLocs(id) {{
    var el = document.getElementById(id);
    el.style.display = el.style.display === 'none' ? 'table-row' : 'none';
  }}
</script>
</head>
<body>
<header>
  <h1>mono-sast Security Report</h1>
  <p>Generated {generated_at}</p>
</header>
<main>
  <div class="cards">
    <div class="card">
      <div class="num">{total}</div>
      <div class="lbl">Total Findings</div>
    </div>
    <div class="card error">
      <div class="num">{error_count}</div>
      <div class="lbl">Errors</div>
    </div>
    <div class="card warning">
      <div class="num">{warning_count}</div>
      <div class="lbl">Warnings</div>
    </div>
    <div class="card note">
      <div class="num">{note_count}</div>
      <div class="lbl">Notes</div>
    </div>
  </div>

  <section>
    <h2>Scan Metadata</h2>
    <div class="meta">
      <div><span class="meta-label">Directory digest (SHA-256)</span><span class="meta-value">{html.escape(digest)}</span></div>
      <div><span class="meta-label">Languages</span><span class="meta-value">{languages_str}</span></div>
      <div><span class="meta-label">Tools run</span><span class="meta-value">{len(tool_counts)}</span></div>
      <div><span class="meta-label">Elapsed time</span><span class="meta-value">{elapsed:.2f}s</span></div>
    </div>
  </section>

  <section>
    <h2>Results by Tool</h2>
    <table>
      <thead><tr><th>Tool</th><th>Errors</th><th>Warnings</th><th>Notes</th><th>Total</th></tr></thead>
      <tbody>{tool_rows}</tbody>
    </table>
  </section>

  <section>
    <h2>All Findings ({len(sorted_groups)} unique rule{"s" if len(sorted_groups) != 1 else ""}, {total} total occurrences)</h2>
    <table>
      <thead><tr><th>Severity</th><th>Tool</th><th>Rule</th><th>Message</th><th>Locations</th></tr></thead>
      <tbody>{finding_rows if finding_rows else '<tr><td colspan="5" style="text-align:center;color:#586069;padding:24px;">No findings.</td></tr>'}</tbody>
    </table>
  </section>
</main>
</body>
</html>"""


# ── Markdown ──────────────────────────────────────────────────────────────────

def generate_markdown_report(merged_sarif: dict, digest: str, languages: list, elapsed: float = 0.0) -> str:
    d = _build_report_data(merged_sarif)
    sorted_groups = d["sorted_groups"]
    tool_counts   = d["tool_counts"]
    total         = d["total"]
    error_count   = d["error_count"]
    warning_count = d["warning_count"]
    note_count    = d["note_count"]

    generated_at  = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    languages_str = ", ".join(languages) if languages else "—"

    lines = []

    lines.append("# mono-sast Security Report")
    lines.append(f"\n> Generated {generated_at}")

    lines.append("\n## Summary\n")
    lines.append(f"| Total | Errors | Warnings | Notes |")
    lines.append(f"|-------|--------|----------|-------|")
    lines.append(f"| {total} | {error_count} | {warning_count} | {note_count} |")

    lines.append("\n## Scan Metadata\n")
    lines.append(f"| | |")
    lines.append(f"|---|---|")
    lines.append(f"| **Directory digest (SHA-256)** | `{digest}` |")
    lines.append(f"| **Languages** | {languages_str} |")
    lines.append(f"| **Tools run** | {len(tool_counts)} |")
    lines.append(f"| **Elapsed time** | {elapsed:.2f}s |")

    lines.append("\n## Results by Tool\n")
    lines.append("| Tool | Errors | Warnings | Notes | Total |")
    lines.append("|------|--------|----------|-------|-------|")
    for name, counts in sorted(tool_counts.items()):
        uri = counts.get("uri", "")
        name_cell = f"[{name}]({uri})" if uri else name
        row_total = counts.get("error", 0) + counts.get("warning", 0) + counts.get("note", 0)
        lines.append(f"| {name_cell} | {counts.get('error',0)} | {counts.get('warning',0)} | {counts.get('note',0)} | {row_total} |")

    lines.append(f"\n## All Findings ({len(sorted_groups)} unique rules, {total} total occurrences)\n")

    for (tool_name, rule_id, message), g in sorted_groups:
        locs     = g["locations"]
        level    = g["level"]
        help_uri = g["help_uri"]
        rule_ref = f"[{rule_id}]({help_uri})" if help_uri else f"`{rule_id}`"

        summary_line = f"[{level.upper()}] {tool_name} — {rule_ref} — {message}"
        lines.append(f"<details>")
        lines.append(f"<summary>{summary_line}</summary>")
        lines.append("")
        lines.append(f"**Severity:** {level.upper()}  ")
        lines.append(f"**Tool:** {tool_name}  ")
        lines.append(f"**Rule:** {rule_ref}  ")
        lines.append(f"**Message:** {message}  ")
        if locs:
            lines.append(f"\n**Locations ({len(locs)}):**\n")
            for uri, line in locs:
                loc_str = f"{uri}:{line}" if line else uri
                lines.append(f"- `{loc_str}`")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    return "\n".join(lines)
