"""Analiza NBA kariere Luke Dončića za Google Colab.

Podatkovni posnetek: zaključena redna sezona 2025/26, stanje 13. 8. 2026.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

try:
    from IPython.display import HTML, display
except ImportError:  # omogoči tudi navaden Python
    HTML = None
    display = print


RAW_BASE = "https://raw.githubusercontent.com/AndrejKnap/Luka/main/data"
LOCAL_DATA_DIR = os.getenv("LUKA_DATA_DIR")
SHOW_FIGURES = os.getenv("LUKA_NO_SHOW", "0") != "1"

COLORS = {
    "luka": "#fdb927",
    "league": "#8b95a7",
    "blue": "#00b4d8",
    "purple": "#9b5de5",
    "green": "#2dd4bf",
    "red": "#ff5c77",
    "paper": "#0b1020",
    "plot": "#111827",
    "grid": "#29364d",
    "text": "#f3f4f6",
}


def load_csv(filename: str) -> pd.DataFrame:
    """Naloži repozitorijski posnetek; lokalna pot je namenjena testiranju."""
    source = Path(LOCAL_DATA_DIR) / filename if LOCAL_DATA_DIR else f"{RAW_BASE}/{filename}"
    return pd.read_csv(source)


def apply_dark_layout(fig: go.Figure, title: str, subtitle: str = "") -> go.Figure:
    full_title = title if not subtitle else f"{title}<br><sup>{subtitle}</sup>"
    fig.update_layout(
        template="plotly_dark",
        title=dict(text=full_title, x=0.02, xanchor="left"),
        paper_bgcolor=COLORS["paper"],
        plot_bgcolor=COLORS["plot"],
        font=dict(family="Arial, sans-serif", color=COLORS["text"], size=13),
        hoverlabel=dict(bgcolor="#172033", font_color="white"),
        legend=dict(orientation="h", y=1.04, x=1, xanchor="right"),
        margin=dict(l=65, r=35, t=95, b=55),
    )
    fig.update_xaxes(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"])
    fig.update_yaxes(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"])
    return fig


def show_table(df: pd.DataFrame, caption: str, precision: int = 1) -> None:
    try:
        styled = (
            df.style.format(precision=precision)
            .set_caption(caption)
            .set_properties(**{"background-color": "#111827", "color": "#f3f4f6", "border-color": "#334155"})
            .set_table_styles([
                {"selector": "caption", "props": [("font-size", "18px"), ("font-weight", "bold"), ("color", "#fdb927"), ("text-align", "left")]},
                {"selector": "th", "props": [("background-color", "#172033"), ("color", "#fdb927")]},
            ])
        )
        display(styled)
    except ImportError:
        print(f"\n{caption}")
        print(df.round(precision).to_string(index=False))


def prepare_data():
    luka = load_csv("luka_seasons.csv")
    league = load_csv("nba_league_averages.csv")
    elite_latest = load_csv("all_nba_first_team_2025_26.csv")
    elite_previous = load_csv("all_nba_first_team_2024_25.csv")

    # Približek True Shooting: PTS / [2 * (FGA + 0,44 * FTA)].
    luka["ts_pct"] = 100 * luka["ppg"] / (2 * (luka["fga"] + 0.44 * luka["fta"]))

    merged = luka.merge(league, on="season", suffixes=("_luka", "_league"))
    # Liga ima približno 241 igralnih minut na ekipo in tekmo (5 igralcev + podaljški).
    # Zato skupne ekipne vrednosti preračunamo na Lukove minute v posamezni sezoni.
    for metric in ["ppg", "rpg", "apg", "spg", "bpg", "tov"]:
        merged[f"{metric}_benchmark"] = (
            merged[f"{metric}_league"] * merged["mpg"] / merged["team_mpg"]
        )
    luka_previous = luka.loc[luka["season"].eq("2024-25")].iloc[0]
    luka_comparison = pd.DataFrame([{
        "player": "Luka Dončić", "team": luka_previous["team"], "gp": luka_previous["gp"],
        "mpg": luka_previous["mpg"], "ppg": luka_previous["ppg"], "rpg": luka_previous["rpg"],
        "apg": luka_previous["apg"], "spg": luka_previous["spg"], "bpg": luka_previous["bpg"],
        "tov": luka_previous["tov"], "fg_pct": luka_previous["fg_pct"],
        "fg3_pct": luka_previous["fg3_pct"], "ft_pct": luka_previous["ft_pct"],
    }])
    previous_comparison = pd.concat([luka_comparison, elite_previous], ignore_index=True)
    return luka, league, elite_latest, elite_previous, previous_comparison, merged


def chart_career_main(merged: pd.DataFrame) -> go.Figure:
    long_parts = []
    labels = {"ppg": "Točke", "rpg": "Skoki", "apg": "Asistence"}
    for metric, label in labels.items():
        long_parts.append(pd.DataFrame({
            "Sezona": merged["season"], "Metrika": label,
            "Vrednost": merged[f"{metric}_luka"], "Serija": "Luka Dončić"
        }))
        long_parts.append(pd.DataFrame({
            "Sezona": merged["season"], "Metrika": label,
            "Vrednost": merged[f"{metric}_benchmark"], "Serija": "NBA – enake minute"
        }))
    long = pd.concat(long_parts, ignore_index=True)
    fig = px.line(
        long, x="Sezona", y="Vrednost", color="Serija", facet_row="Metrika",
        markers=True, color_discrete_map={"Luka Dončić": COLORS["luka"], "NBA – enake minute": COLORS["league"]},
        height=780,
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], textangle=0))
    fig.update_yaxes(matches=None, title=None)
    fig.update_xaxes(title=None)
    return apply_dark_layout(
        fig, "Luka proti ligi: razvoj glavne statistike",
        "NBA primerjava je preračunana na Lukove minute v vsaki sezoni"
    )


def chart_shooting(luka: pd.DataFrame, league: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    series = [
        ("Luka FG%", luka["fg_pct"], COLORS["luka"], "solid"),
        ("Liga FG%", league["fg_pct"], COLORS["league"], "dot"),
        ("Luka 3P%", luka["fg3_pct"], COLORS["blue"], "solid"),
        ("Liga 3P%", league["fg3_pct"], "#5c718f", "dot"),
        ("Luka FT%", luka["ft_pct"], COLORS["green"], "solid"),
        ("Liga FT%", league["ft_pct"], "#547c78", "dot"),
    ]
    for name, values, color, dash in series:
        fig.add_trace(go.Scatter(
            x=luka["season"], y=values, mode="lines+markers", name=name,
            line=dict(color=color, width=3 if "Luka" in name else 2, dash=dash),
            hovertemplate=f"{name}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_yaxes(title="Uspešnost (%)", range=[28, 91])
    return apply_dark_layout(fig, "Natančnost meta skozi kariero", "Črtkane črte prikazujejo povprečje NBA")


def chart_latest_vs_league(merged: pd.DataFrame) -> go.Figure:
    row = merged.iloc[-1]
    metrics = ["Točke", "Skoki", "Asistence", "Ukradene", "Blokade", "Izgubljene"]
    keys = ["ppg", "rpg", "apg", "spg", "bpg", "tov"]
    values = pd.DataFrame({
        "Metrika": metrics * 2,
        "Vrednost": [row[f"{k}_luka"] for k in keys] + [row[f"{k}_benchmark"] for k in keys],
        "Serija": ["Luka Dončić"] * len(keys) + ["NBA – enake minute"] * len(keys),
    })
    fig = px.bar(
        values, x="Metrika", y="Vrednost", color="Serija", barmode="group", text_auto=".1f",
        color_discrete_map={"Luka Dončić": COLORS["luka"], "NBA – enake minute": COLORS["league"]},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(title="Na tekmo")
    return apply_dark_layout(fig, "Sezona 2025/26: Luka proti ligi", "Obe seriji sta izraženi na 35,8 minute")


def chart_elite_scatter(elite: pd.DataFrame, season: str, includes_luka: bool = True) -> go.Figure:
    fig = px.scatter(
        elite, x="apg", y="ppg", size="rpg", color="player", text="player",
        size_max=45, hover_data={"gp": True, "mpg": True, "spg": True, "bpg": True, "player": False},
        labels={"apg": "Asistence na tekmo", "ppg": "Točke na tekmo", "rpg": "Skoki"},
        color_discrete_sequence=[COLORS["luka"], COLORS["blue"], COLORS["purple"], COLORS["green"], COLORS["red"]],
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(showlegend=False)
    title = f"Napadalni profil All‑NBA First Team {season}"
    if not includes_luka:
        title = f"Luka proti All‑NBA First Team {season}"
    return apply_dark_layout(fig, title, "Velikost kroga = skoki na tekmo")


def chart_elite_heatmap(elite: pd.DataFrame, season: str, includes_luka: bool = True) -> go.Figure:
    metrics = ["ppg", "rpg", "apg", "spg", "bpg", "fg_pct", "fg3_pct", "ft_pct"]
    metric_labels = ["PTS", "REB", "AST", "STL", "BLK", "FG%", "3P%", "FT%"]
    raw = elite.set_index("player")[metrics]
    # 0–100 znotraj peterice omogoča primerjavo statistik z različnimi merskimi lestvicami.
    spread = (raw.max() - raw.min()).replace(0, 1)
    score = 100 * (raw - raw.min()) / spread
    custom = np.stack([raw.values, score.values], axis=-1)
    fig = go.Figure(go.Heatmap(
        z=score.values,
        x=metric_labels,
        y=raw.index,
        customdata=custom,
        colorscale=[[0, "#172033"], [0.5, "#2b5c79"], [1, COLORS["luka"]]],
        colorbar=dict(title="Indeks<br>0–100"),
        text=np.round(raw.values, 1),
        texttemplate="%{text}",
        hovertemplate="%{y}<br>%{x}: %{customdata[0]:.1f}<br>Indeks v peterici: %{customdata[1]:.0f}<extra></extra>",
    ))
    group = "peterice" if includes_luka else "primerjalne skupine"
    return apply_dark_layout(
        fig, f"Statistični profil elitne skupine {season}",
        f"Številke so dejanske vrednosti; barva je indeks znotraj {group}"
    )


def chart_availability(luka: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        luka, x="season", y="gp", text="gp", color="gp",
        color_continuous_scale=[[0, COLORS["red"]], [0.5, COLORS["blue"]], [1, COLORS["green"]]],
        labels={"season": "Sezona", "gp": "Odigrane tekme"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False)
    fig.update_yaxes(range=[0, 82])
    return apply_dark_layout(fig, "Razpoložljivost po sezonah", "Redni del; sezona 2019/20 je bila skrajšana")


def export_dashboard(figures: list[go.Figure], path: str = "luka_dashboard.html") -> None:
    parts = [
        "<!doctype html><html lang='sl'><head><meta charset='utf-8'><title>Luka Dončić – NBA analiza</title>",
        "<style>body{margin:0;background:#0b1020;color:#f3f4f6;font-family:Arial,sans-serif}main{max-width:1250px;margin:auto;padding:24px}h1{color:#fdb927}</style></head><body><main>",
        "<h1>Luka Dončić – analiza NBA kariere</h1><p>Podatki do zaključka sezone 2025/26.</p>",
    ]
    for i, fig in enumerate(figures):
        parts.append(fig.to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False))
    parts.append("</main></body></html>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    pio.templates.default = "plotly_dark"
    luka, league, elite_latest, elite_previous, previous_comparison, merged = prepare_data()

    latest = merged.iloc[-1]
    career = pd.DataFrame({
        "Kazalnik": ["Sezone", "Tekme", "Karierne PTS", "Karierni REB", "Karierni AST", "Najvišji PPG"],
        "Vrednost": [
            len(luka), int(luka["gp"].sum()),
            np.average(luka["ppg"], weights=luka["gp"]),
            np.average(luka["rpg"], weights=luka["gp"]),
            np.average(luka["apg"], weights=luka["gp"]),
            luka["ppg"].max(),
        ],
    })
    show_table(career, "Hiter pregled kariere", precision=1)

    season_table = luka[["season", "team", "gp", "mpg", "ppg", "rpg", "apg", "spg", "bpg", "tov", "fg_pct", "fg3_pct", "ft_pct", "ts_pct"]].copy()
    season_table.columns = ["Sezona", "Ekipa", "GP", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "FG%", "3P%", "FT%", "TS%"]
    show_table(season_table, "Luka Dončić – vse NBA-sezone", precision=1)

    elite_table = elite_latest[["player", "gp", "mpg", "ppg", "rpg", "apg", "spg", "bpg", "tov", "fg_pct", "fg3_pct", "ft_pct"]].copy()
    elite_table.columns = ["Igralec", "GP", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "FG%", "3P%", "FT%"]
    show_table(elite_table, "All‑NBA First Team 2025/26", precision=1)

    previous_table = previous_comparison[["player", "gp", "mpg", "ppg", "rpg", "apg", "spg", "bpg", "tov", "fg_pct", "fg3_pct", "ft_pct"]].copy()
    previous_table.columns = ["Igralec", "GP", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "FG%", "3P%", "FT%"]
    show_table(previous_table, "Luka in All‑NBA First Team 2024/25 (dobesedno lansko leto)", precision=1)

    figures = [
        chart_career_main(merged),
        chart_shooting(luka, league),
        chart_latest_vs_league(merged),
        chart_elite_scatter(elite_latest, "2025/26"),
        chart_elite_heatmap(elite_latest, "2025/26"),
        chart_elite_scatter(previous_comparison, "2024/25", includes_luka=False),
        chart_elite_heatmap(previous_comparison, "2024/25", includes_luka=False),
        chart_availability(luka),
    ]
    if SHOW_FIGURES:
        for fig in figures:
            fig.show()
    export_dashboard(figures)
    print("\nUstvarjeno: luka_dashboard.html (interaktivni Plotly dashboard)")
    print(f"2025/26: {latest['ppg_luka']:.1f} PTS, {latest['rpg_luka']:.1f} REB, {latest['apg_luka']:.1f} AST.")


if __name__ == "__main__":
    main()
