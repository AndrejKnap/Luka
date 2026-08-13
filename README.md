# Luka Dončić — analiza NBA-kariere

[![Odpri v Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AndrejKnap/Luka/blob/main/Luka_Doncic_NBA_analiza.ipynb)

Interaktivna analiza vseh osmih NBA-sezon Luke Dončića, od 2018/19 do 2025/26.

## Kaj vsebuje

- celotno sezonsko statistiko Luke Dončića;
- primerjavo s povprečjem lige, preračunanim na enako število minut;
- primerjavo z uradnima petericama All‑NBA First Team 2024/25 in 2025/26;
- osem interaktivnih grafov Plotly v temnem načinu;
- samodejni izvoz v `luka_dashboard.html` po zagonu zvezka.

## Zagon

Kliknite značko **Odpri v Google Colab** in nato izberite **Runtime → Run all**. Namestitev ni potrebna.

## Podatki in metodologija

Podatkovni posnetek je pripravljen po zaključku redne sezone 2025/26 (stanje 13. avgusta 2026). Osnovni viri so [NBA.com](https://www.nba.com/player/1629029/luka-doncic), [uradni izbor All‑NBA](https://www.nba.com/news/2025-26-all-nba-teams-announced), [ESPN](https://www.espn.com/nba/player/stats/_/id/3945274/luka-doncic) in [Basketball Reference](https://www.basketball-reference.com/players/d/doncilu01.html).

»Pet najboljših lanskega leta« je opredeljeno kot uradna peterica **All‑NBA First Team 2024/25**; dodana je tudi najnovejša peterica 2025/26. Povprečje lige je skupna produkcija povprečne NBA-ekipe, preračunana na Lukove minute; s tem je primerjava časovno poštena.

## Datoteke

- `Luka_Doncic_NBA_analiza.ipynb` — Colab zvezek;
- `luka_analysis.py` — celoten analizni program;
- `data/luka_seasons.csv` — Luka po sezonah;
- `data/nba_league_averages.csv` — sezonska povprečja lige;
- `data/all_nba_first_team_2025_26.csv` — elitna primerjalna peterica.
- `data/all_nba_first_team_2024_25.csv` — peterica za dobesedno lansko leto.
