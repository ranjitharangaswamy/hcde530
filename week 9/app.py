#!/usr/bin/env python3
"""
Litigation Legal Tech Discourse — Simple Web UI
Flask app that displays themed insights from the pipeline output.
Run: python3 app.py
"""

import os
import pandas as pd
from flask import Flask, render_template_string, request

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Legal AI Discourse — Litigation Tech Insights</title>
<style>
  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #232734;
    --border: #2d3245;
    --text: #e4e6ed;
    --text2: #9ca0b0;
    --accent: #6c8aff;
    --accent2: #4a6cf7;
    --green: #34d399;
    --red: #f87171;
    --yellow: #fbbf24;
    --orange: #fb923c;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg); color: var(--text);
    line-height: 1.6; padding: 0;
  }

  /* Header */
  .header {
    background: linear-gradient(135deg, #1e2235 0%, #141726 100%);
    border-bottom: 1px solid var(--border);
    padding: 2rem 2rem 1.5rem;
  }
  .header h1 { font-size: 1.6rem; font-weight: 700; margin-bottom: 0.3rem; }
  .header p { color: var(--text2); font-size: 0.9rem; }
  .stats-bar {
    display: flex; gap: 2rem; margin-top: 1rem; flex-wrap: wrap;
  }
  .stat { text-align: center; }
  .stat-num { font-size: 1.8rem; font-weight: 700; color: var(--accent); }
  .stat-label { font-size: 0.75rem; color: var(--text2); text-transform: uppercase; letter-spacing: 0.05em; }

  /* Nav */
  .nav {
    display: flex; gap: 0.5rem; padding: 1rem 2rem;
    border-bottom: 1px solid var(--border); flex-wrap: wrap;
    background: var(--surface);
  }
  .nav a {
    padding: 0.4rem 1rem; border-radius: 6px; text-decoration: none;
    color: var(--text2); font-size: 0.85rem; transition: all 0.15s;
    border: 1px solid transparent;
  }
  .nav a:hover { color: var(--text); background: var(--surface2); }
  .nav a.active { background: var(--accent2); color: white; border-color: var(--accent); }

  /* Main */
  .main { max-width: 1100px; margin: 0 auto; padding: 1.5rem 2rem 4rem; }

  /* Theme card */
  .theme-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; margin-bottom: 1.5rem; overflow: hidden;
    transition: border-color 0.15s;
  }
  .theme-card:hover { border-color: var(--accent); }
  .theme-header {
    padding: 1.2rem 1.5rem; display: flex; justify-content: space-between;
    align-items: center; flex-wrap: wrap; gap: 0.5rem;
    border-bottom: 1px solid var(--border);
  }
  .theme-name { font-size: 1.1rem; font-weight: 600; text-transform: capitalize; }
  .theme-name span { color: var(--accent); }
  .theme-meta { display: flex; gap: 1rem; align-items: center; }
  .badge {
    padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem;
    font-weight: 600; text-transform: uppercase;
  }
  .badge-count { background: var(--accent2); color: white; }
  .badge-pct { background: var(--surface2); color: var(--text2); }
  .theme-body { padding: 1.2rem 1.5rem; }

  /* Qualitative bar */
  .qual-row {
    display: flex; gap: 1.5rem; margin-bottom: 1rem; flex-wrap: wrap;
  }
  .qual-item {
    display: flex; align-items: center; gap: 0.4rem;
    font-size: 0.8rem; color: var(--text2);
  }
  .qual-dot {
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
  }
  .dot-pos { background: var(--green); }
  .dot-neg { background: var(--red); }
  .dot-neu { background: var(--yellow); }
  .dot-emo { background: var(--orange); }
  .dot-frame { background: var(--accent); }

  /* Sentiment bar */
  .sent-bar {
    height: 6px; border-radius: 3px; display: flex; overflow: hidden;
    margin: 0.5rem 0; width: 200px; max-width: 100%;
  }
  .sent-pos { background: var(--green); }
  .sent-neg { background: var(--red); }
  .sent-neu { background: #555; }

  /* Excerpt */
  .excerpt {
    background: var(--surface2); border-left: 3px solid var(--accent);
    padding: 0.8rem 1rem; margin: 0.8rem 0; border-radius: 0 6px 6px 0;
    font-size: 0.88rem; color: var(--text);
  }
  .excerpt-text { line-height: 1.5; }
  .excerpt-source {
    margin-top: 0.5rem; font-size: 0.78rem;
  }
  .excerpt-source a {
    color: var(--accent); text-decoration: none;
  }
  .excerpt-source a:hover { text-decoration: underline; }

  /* All items table */
  .items-table {
    width: 100%; border-collapse: collapse; font-size: 0.85rem;
  }
  .items-table th {
    text-align: left; padding: 0.6rem 0.8rem;
    border-bottom: 2px solid var(--border); color: var(--text2);
    font-weight: 600; font-size: 0.75rem; text-transform: uppercase;
  }
  .items-table td {
    padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--border);
    vertical-align: top;
  }
  .items-table tr:hover td { background: var(--surface2); }
  .items-table a { color: var(--accent); text-decoration: none; }
  .items-table a:hover { text-decoration: underline; }
  .pill {
    display: inline-block; padding: 0.15rem 0.5rem; border-radius: 3px;
    font-size: 0.72rem; font-weight: 600;
  }
  .pill-pos { background: rgba(52,211,153,0.15); color: var(--green); }
  .pill-neg { background: rgba(248,113,113,0.15); color: var(--red); }
  .pill-neu { background: rgba(251,191,36,0.15); color: var(--yellow); }

  /* Footer */
  .footer {
    text-align: center; padding: 2rem; color: var(--text2);
    font-size: 0.78rem; border-top: 1px solid var(--border);
  }
  .footer a { color: var(--accent); text-decoration: none; }
</style>
</head>
<body>

<div class="header">
  <h1>Legal AI Discourse Explorer</h1>
  <p>Litigation legal tech insights from public web sources — themes, sentiment, and cited evidence</p>
  <div class="stats-bar">
    <div class="stat"><div class="stat-num">{{ total_items }}</div><div class="stat-label">Items Analyzed</div></div>
    <div class="stat"><div class="stat-num">{{ total_themes }}</div><div class="stat-label">Themes Found</div></div>
    <div class="stat"><div class="stat-num">{{ total_sources }}</div><div class="stat-label">Unique Sources</div></div>
    <div class="stat"><div class="stat-num">{{ sentiment_positive }}%</div><div class="stat-label">Positive Sentiment</div></div>
  </div>
</div>

<div class="nav">
  <a href="/" class="{{ 'active' if view == 'themes' else '' }}">Themes</a>
  <a href="/?view=items" class="{{ 'active' if view == 'items' else '' }}">All Items</a>
  <a href="/?view=narratives" class="{{ 'active' if view == 'narratives' else '' }}">Narratives</a>
</div>

<div class="main">

{% if view == 'themes' %}
  {% for theme in themes %}
  <div class="theme-card">
    <div class="theme-header">
      <div class="theme-name"><span>#</span> {{ theme.theme }}</div>
      <div class="theme-meta">
        <span class="badge badge-count">{{ theme.count }} items</span>
        <span class="badge badge-pct">{{ theme.percentage }}%</span>
      </div>
    </div>
    <div class="theme-body">
      <div class="qual-row">
        <div class="qual-item">
          <div class="qual-dot dot-pos"></div>
          {{ theme.sentiment_positive_pct }}% positive
        </div>
        <div class="qual-item">
          <div class="qual-dot dot-neg"></div>
          {{ theme.sentiment_negative_pct }}% negative
        </div>
        <div class="qual-item">
          <div class="qual-dot dot-emo"></div>
          Emotion: {{ theme.top_emotion }}
        </div>
        <div class="qual-item">
          <div class="qual-dot dot-frame"></div>
          Frame: {{ theme.top_frame }}
        </div>
      </div>
      <div class="sent-bar">
        <div class="sent-pos" style="width:{{ theme.sentiment_positive_pct }}%"></div>
        <div class="sent-neg" style="width:{{ theme.sentiment_negative_pct }}%"></div>
        <div class="sent-neu" style="width:{{ 100 - theme.sentiment_positive_pct - theme.sentiment_negative_pct }}%"></div>
      </div>

      {% for i in range(1, 4) %}
        {% set ex = theme['excerpt_' ~ i] %}
        {% set url = theme['excerpt_' ~ i ~ '_url'] %}
        {% set title = theme['excerpt_' ~ i ~ '_title'] %}
        {% if ex %}
        <div class="excerpt">
          <div class="excerpt-text">{{ ex[:250] }}{% if ex|length > 250 %}...{% endif %}</div>
          {% if url %}
          <div class="excerpt-source">
            Source: <a href="{{ url }}" target="_blank" rel="noopener">{{ title or url[:60] }}</a>
          </div>
          {% endif %}
        </div>
        {% endif %}
      {% endfor %}
    </div>
  </div>
  {% endfor %}

{% elif view == 'items' %}
  <table class="items-table">
    <thead>
      <tr>
        <th>Title</th>
        <th>Theme</th>
        <th>Sentiment</th>
        <th>Emotion</th>
        <th>Frame</th>
        <th>Source</th>
      </tr>
    </thead>
    <tbody>
    {% for item in items %}
      <tr>
        <td>{{ item.title[:60] }}{% if item.title|length > 60 %}...{% endif %}</td>
        <td style="text-transform:capitalize">{{ item.primary_theme }}</td>
        <td>
          <span class="pill pill-{{ 'pos' if item.sentiment_label == 'positive' else ('neg' if item.sentiment_label == 'negative' else 'neu') }}">
            {{ item.sentiment_label }}
          </span>
        </td>
        <td style="text-transform:capitalize">{{ item.dominant_emotion }}</td>
        <td style="text-transform:capitalize">{{ item.rhetorical_frame }}</td>
        <td><a href="{{ item.source_url }}" target="_blank" rel="noopener">View</a></td>
      </tr>
    {% endfor %}
    </tbody>
  </table>

{% elif view == 'narratives' %}
  <h2 style="margin-bottom:1rem; font-size:1.2rem;">First-Person Narratives & Experience Stories</h2>
  {% if narratives|length == 0 %}
    <p style="color:var(--text2)">No first-person narratives detected in current corpus.</p>
  {% endif %}
  {% for n in narratives %}
  <div class="theme-card">
    <div class="theme-header">
      <div class="theme-name"><span>#</span> {{ n.theme }}</div>
      <div class="theme-meta">
        <span class="badge badge-pct">{{ n.speaker_role }}</span>
        <span class="pill pill-{{ 'pos' if n.sentiment == 'positive' else ('neg' if n.sentiment == 'negative' else 'neu') }}">
          {{ n.sentiment }}
        </span>
      </div>
    </div>
    <div class="theme-body">
      <div class="excerpt">
        <div class="excerpt-text">{{ n.excerpt[:350] }}{% if n.excerpt|length > 350 %}...{% endif %}</div>
        {% if n.source_url %}
        <div class="excerpt-source">
          Source: <a href="{{ n.source_url }}" target="_blank" rel="noopener">{{ n.title or n.source_url[:60] }}</a>
        </div>
        {% endif %}
      </div>
    </div>
  </div>
  {% endfor %}
{% endif %}

</div>

<div class="footer">
  HCDE 530 MP2a — Legal AI Discourse Pipeline<br>
  Data from public web sources. All items include <a href="/?view=items">cited sources</a>.
</div>

</body>
</html>
"""


@app.route("/")
def index():
    view = request.args.get("view", "themes")

    # Load data
    qual_path = os.path.join(DATA_DIR, "qualitative_coded.csv")
    summary_path = os.path.join(DATA_DIR, "themes_summary.csv")
    narr_path = os.path.join(DATA_DIR, "narratives.csv")

    def safe_read(path):
        if not os.path.exists(path):
            return pd.DataFrame()
        try:
            d = pd.read_csv(path)
            return d if len(d) > 0 else pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    df = safe_read(qual_path)
    df_sum = safe_read(summary_path)
    df_narr = safe_read(narr_path)

    # Fill NaN
    for d in [df, df_sum, df_narr]:
        for col in d.columns:
            d[col] = d[col].fillna("")

    total_items = len(df)
    total_themes = df["primary_theme"].nunique() if "primary_theme" in df.columns else 0
    total_sources = df["source_url"].nunique() if "source_url" in df.columns else 0
    sent_pos = round((df["sentiment_label"] == "positive").mean() * 100) if "sentiment_label" in df.columns and len(df) > 0 else 0

    themes = df_sum.to_dict("records") if len(df_sum) > 0 else []
    items = df.to_dict("records") if len(df) > 0 else []
    narratives = df_narr.to_dict("records") if len(df_narr) > 0 else []

    return render_template_string(
        HTML_TEMPLATE,
        view=view,
        total_items=total_items,
        total_themes=total_themes,
        total_sources=total_sources,
        sentiment_positive=sent_pos,
        themes=themes,
        items=items,
        narratives=narratives,
    )


if __name__ == "__main__":
    print("\n  Legal AI Discourse Explorer")
    print("  http://localhost:5050\n")
    app.run(host="0.0.0.0", port=5050, debug=False)
