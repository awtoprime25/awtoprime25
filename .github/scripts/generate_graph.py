import json
import os
import urllib.request

TOKEN = os.environ["GH_TOKEN"]
LOGIN = os.environ.get("GH_LOGIN", "awtoprime25")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def level_color(count, max_count):
    if count == 0 or max_count == 0:
        return "#141414"
    ratio = count / max_count
    if ratio <= 0.25:
        return "#333333"
    if ratio <= 0.5:
        return "#5a5a5a"
    if ratio <= 0.75:
        return "#999999"
    return "#ffffff"


def build_svg(weeks, total):
    cell = 14
    gap = 3
    step = cell + gap
    cols = len(weeks)
    grid_w = cols * step - gap
    canvas_w = 1200
    canvas_h = 220
    start_x = (canvas_w - grid_w) / 2
    start_y = 76

    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    max_count = max(counts) if counts else 0

    cells = []
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            x = start_x + wi * step
            y = start_y + di * step
            color = level_color(day["contributionCount"], max_count)
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3" '
                f'fill="{color}" stroke="#1a1a1a" stroke-width="0.5"/>'
            )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">
  <rect width="{canvas_w}" height="{canvas_h}" fill="#0a0a0a"/>
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1a1a1a" stroke-width="0.5"/>
    </pattern>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="{canvas_w}" height="{canvas_h}" fill="url(#grid)"/>

  <text x="{canvas_w / 2:.0f}" y="42" font-family="JetBrains Mono, monospace" font-size="26"
        font-weight="bold" fill="#ffffff" text-anchor="middle" letter-spacing="4"
        filter="url(#glow)">CONTRIBUTION LOG</text>

  {"".join(cells)}

  <text x="{canvas_w / 2:.0f}" y="208" font-family="JetBrains Mono, monospace" font-size="12"
        fill="#666666" text-anchor="middle" letter-spacing="2">{total} CONTRIBUTIONS &#183; LAST 12 MONTHS</text>

  <path d="M20,20 L20,50 M20,20 L50,20" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.3"/>
  <path d="M{canvas_w - 20},20 L{canvas_w - 20},50 M{canvas_w - 20},20 L{canvas_w - 50},20" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.3"/>
  <path d="M20,{canvas_h - 20} L20,{canvas_h - 50} M20,{canvas_h - 20} L50,{canvas_h - 20}" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.3"/>
  <path d="M{canvas_w - 20},{canvas_h - 20} L{canvas_w - 20},{canvas_h - 50} M{canvas_w - 20},{canvas_h - 20} L{canvas_w - 50},{canvas_h - 20}" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.3"/>
</svg>'''


def main():
    data = fetch()
    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = calendar["weeks"]
    total = calendar["totalContributions"]
    svg = build_svg(weeks, total)
    with open("contribution-graph.svg", "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
