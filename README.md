# 2026 FIFA World Cup — Monte Carlo Simulator (group stage → final)

Estimates every team's probability of reaching each stage of the tournament —
from the **Round of 32** all the way to **lifting the trophy** — by simulating
the remaining group-stage fixtures *and the full knockout bracket* many times.
Matches already played (as of the snapshot date) are treated as **fixed**; only
the unplayed group fixtures and the entire knockout are simulated.

---


## Headline results (50,000 simulations)

### Title odds — probability of reaching each knockout round (and winning)
Sorted by championship %. `R32` = reach the knockout stage at all.

| Team | R32 | R16 | QF | SF | Final | **Win** |
|---|--:|--:|--:|--:|--:|--:|
| Argentina | 100.00% | 88.02% | 73.93% | 56.05% | 38.40% | **24.15%** |
| Spain | 100.00% | 79.29% | 60.92% | 51.86% | 36.50% | **22.55%** |
| France | 99.92% | 84.33% | 61.80% | 44.63% | 25.75% | **14.59%** |
| England | 100.00% | 81.37% | 60.26% | 39.83% | 20.83% | **10.93%** |
| Colombia | 99.70% | 78.05% | 52.22% | 24.85% | 12.97% | **6.09%** |
| Brazil | 100.00% | 59.56% | 36.43% | 18.06% | 7.81% | **3.25%** |
| Portugal | 88.35% | 59.64% | 30.90% | 16.35% | 7.89% | **3.19%** |
| Germany | 100.00% | 73.49% | 29.75% | 17.46% | 7.16% | **2.53%** |
| Netherlands | 100.00% | 58.34% | 37.96% | 16.53% | 6.75% | **2.45%** |
| Norway | 99.33% | 69.69% | 37.61% | 17.11% | 6.49% | **2.30%** |
| Japan | 100.00% | 51.06% | 27.45% | 10.78% | 3.83% | **1.36%** |
| Switzerland | 100.00% | 63.02% | 26.17% | 8.35% | 2.74% | **0.80%** |
| Belgium | 93.41% | 53.62% | 20.81% | 7.27% | 2.69% | **0.79%** |
| Mexico | 100.00% | 58.72% | 19.08% | 8.12% | 2.43% | **0.75%** |
| Croatia | 90.55% | 41.04% | 12.33% | 6.93% | 2.57% | **0.74%** |
| Austria | 97.41% | 31.63% | 15.42% | 6.35% | 2.14% | **0.59%** |
| Senegal | 74.07% | 40.10% | 18.50% | 5.20% | 1.57% | **0.44%** |
| Morocco | 100.00% | 39.25% | 19.38% | 6.00% | 1.65% | **0.41%** |
| Australia | 97.39% | 46.07% | 11.72% | 4.61% | 1.39% | **0.39%** |
| Ecuador | 32.82% | 17.78% | 10.00% | 3.25% | 1.18% | **0.35%** |
| United States | 100.00% | 62.57% | 28.88% | 5.67% | 1.50% | **0.27%** |
| Uruguay | 33.63% | 15.01% | 7.67% | 2.84% | 0.98% | **0.25%** |
| South Korea | 98.46% | 43.90% | 14.60% | 3.64% | 0.92% | **0.19%** |
| Canada | 100.00% | 49.41% | 14.31% | 3.12% | 0.77% | **0.12%** |
| Scotland | 91.43% | 29.36% | 8.53% | 2.59% | 0.62% | **0.12%** |
| Paraguay | 86.13% | 26.85% | 6.63% | 2.12% | 0.49% | **0.09%** |
| Iran | 73.25% | 29.14% | 9.18% | 1.79% | 0.42% | **0.09%** |
| Sweden | 95.83% | 32.31% | 9.41% | 2.06% | 0.43% | **0.08%** |
| Algeria | 54.61% | 16.49% | 6.69% | 1.51% | 0.35% | **0.06%** |
| Ivory Coast | 97.87% | 24.97% | 6.91% | 1.40% | 0.20% | **0.03%** |
| Egypt | 100.00% | 34.55% | 10.94% | 1.62% | 0.32% | **0.03%** |
| DR Congo | 43.18% | 8.32% | 1.72% | 0.41% | 0.06% | **<0.01%** |
| Uzbekistan | 38.71% | 6.92% | 1.44% | 0.35% | 0.06% | **<0.01%** |
| Bosnia and Herzegovina | 60.47% | 14.41% | 3.49% | 0.35% | 0.04% | **<0.01%** |
| Jordan | 16.52% | 4.56% | 1.31% | 0.14% | 0.03% | **<0.01%** |
| South Africa | 8.51% | 1.25% | 0.10% | <0.01% | 0.00% | **0.00%** |
| Czech Republic | 13.41% | 4.73% | 1.71% | 0.26% | 0.04% | **0.00%** |
| Qatar | 17.45% | 1.88% | 0.20% | 0.01% | 0.00% | **0.00%** |
| New Zealand | 6.85% | 1.27% | 0.10% | 0.01% | 0.00% | **0.00%** |
| Saudi Arabia | 36.12% | 2.54% | 0.51% | 0.08% | <0.01% | **0.00%** |
| Cape Verde | 65.32% | 5.19% | 1.10% | 0.17% | 0.01% | **0.00%** |
| Iraq | 6.22% | 1.36% | 0.30% | 0.03% | 0.00% | **0.00%** |
| Ghana | 64.59% | 6.12% | 1.02% | 0.09% | 0.01% | **0.00%** |
| Panama | 12.62% | 2.44% | 0.61% | 0.13% | 0.02% | **0.00%** |

*(All 48 teams, including the long shots, are in the CSV. Remaining sides each sit below ~0.7% to win.)*

### Group-stage advancement
`ADV` = P(1st) + P(2nd) + P(qualify as one of the 8 best thirds). Sorted by ADV.
Full machine-readable table: [`output/group_probabilities.csv`](output/group_probabilities.csv).

### Group A
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Mexico | 1881 | 2 | 6 | +3 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| South Korea | 1786 | 2 | 3 | +0 | 0.00% | 91.69% | 7.34% | 6.77% | **98.46%** |
| Czech Republic | 1712 | 2 | 1 | -1 | 0.00% | 0.92% | 70.76% | 12.49% | **13.41%** |
| South Africa | 1511 | 2 | 1 | -2 | 0.00% | 7.39% | 21.90% | 1.12% | **8.51%** |

### Group B
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Canada | 1767 | 2 | 4 | +6 | 59.44% | 40.51% | 0.05% | 0.05% | **100.00%** |
| Switzerland | 1865 | 2 | 4 | +3 | 40.56% | 59.44% | <0.01% | <0.01% | **100.00%** |
| Bosnia and Herzegovina | 1616 | 2 | 1 | -3 | 0.00% | 0.05% | 82.49% | 60.42% | **60.47%** |
| Qatar | 1447 | 2 | 1 | -6 | 0.00% | <0.01% | 17.46% | 17.44% | **17.45%** |

### Group C
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Brazil | 1978 | 2 | 4 | +3 | 61.64% | 23.34% | 15.01% | 15.01% | **100.00%** |
| Morocco | 1840 | 2 | 4 | +1 | 34.81% | 64.10% | 1.08% | 1.08% | **100.00%** |
| Scotland | 1794 | 2 | 3 | +0 | 3.54% | 12.56% | 83.90% | 75.33% | **91.43%** |
| Haiti | 1536 | 2 | 0 | -4 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group D
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| United States | 1780 | 2 | 6 | +5 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Australia | 1839 | 2 | 3 | +0 | 0.00% | 70.44% | 29.56% | 26.95% | **97.39%** |
| Paraguay | 1780 | 2 | 3 | -2 | 0.00% | 29.56% | 70.44% | 56.56% | **86.13%** |
| Turkey | 1849 | 2 | 0 | -3 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group E
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Germany | 1939 | 2 | 6 | +7 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Ivory Coast | 1743 | 2 | 3 | +0 | 0.00% | 94.05% | 4.12% | 3.83% | **97.87%** |
| Ecuador | 1890 | 2 | 1 | -1 | 0.00% | 1.84% | 87.46% | 30.98% | **32.82%** |
| Curacao | 1427 | 2 | 1 | -6 | 0.00% | 4.12% | 8.42% | 1.83% | **5.94%** |

### Group F
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Netherlands | 1944 | 2 | 4 | +4 | 72.23% | 27.64% | 0.13% | 0.13% | **100.00%** |
| Japan | 1910 | 2 | 4 | +4 | 24.74% | 57.04% | 18.22% | 18.22% | **100.00%** |
| Sweden | 1755 | 2 | 3 | +0 | 3.03% | 15.32% | 81.65% | 77.48% | **95.83%** |
| Tunisia | 1585 | 2 | 0 | -8 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group G
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Egypt | 1711 | 2 | 4 | +2 | 48.23% | 18.16% | 33.61% | 33.61% | **100.00%** |
| Belgium | 1879 | 2 | 2 | +0 | 26.53% | 56.61% | 11.18% | 10.27% | **93.41%** |
| Iran | 1756 | 2 | 2 | +0 | 25.24% | 21.35% | 50.58% | 26.66% | **73.25%** |
| New Zealand | 1578 | 2 | 1 | -2 | 0.00% | 3.88% | 4.62% | 2.97% | **6.85%** |

### Group H
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Spain | 2129 | 2 | 4 | +4 | 90.28% | 6.18% | 3.54% | 3.54% | **100.00%** |
| Cape Verde | 1606 | 2 | 2 | +0 | 1.90% | 55.46% | 19.81% | 7.96% | **65.32%** |
| Saudi Arabia | 1598 | 2 | 1 | -4 | 0.00% | 32.72% | 4.57% | 3.40% | **36.12%** |
| Uruguay | 1870 | 2 | 2 | +0 | 7.82% | 5.64% | 72.08% | 20.18% | **33.63%** |

### Group I
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| France | 2084 | 1 | 3 | +2 | 76.37% | 22.92% | 0.64% | 0.64% | **99.92%** |
| Norway | 1929 | 1 | 3 | +3 | 22.67% | 54.05% | 23.13% | 22.61% | **99.33%** |
| Senegal | 1839 | 1 | 0 | -2 | 0.93% | 22.81% | 65.80% | 50.34% | **74.07%** |
| Iraq | 1592 | 1 | 0 | -3 | 0.04% | 0.22% | 10.44% | 5.96% | **6.22%** |

### Group J
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Argentina | 2128 | 1 | 3 | +3 | 89.64% | 10.14% | 0.20% | 0.20% | **100.00%** |
| Austria | 1857 | 1 | 3 | +2 | 9.97% | 68.16% | 21.13% | 19.28% | **97.41%** |
| Algeria | 1759 | 1 | 0 | -3 | 0.28% | 20.86% | 50.58% | 33.46% | **54.61%** |
| Jordan | 1653 | 1 | 0 | -2 | 0.11% | 0.84% | 28.09% | 15.56% | **16.52%** |

### Group K
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Colombia | 1998 | 1 | 3 | +2 | 69.74% | 25.42% | 4.60% | 4.54% | **99.70%** |
| Portugal | 1967 | 1 | 1 | +0 | 27.48% | 49.46% | 17.97% | 11.41% | **88.35%** |
| DR Congo | 1674 | 1 | 1 | +0 | 2.37% | 14.50% | 42.20% | 26.31% | **43.18%** |
| Uzbekistan | 1698 | 1 | 0 | -2 | 0.42% | 10.62% | 35.23% | 27.67% | **38.71%** |

### Group L
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| England | 2055 | 1 | 3 | +2 | 98.20% | 1.70% | 0.07% | 0.07% | **100.00%** |
| Croatia | 1881 | 1 | 0 | -2 | 0.83% | 80.86% | 12.44% | 8.86% | **90.55%** |
| Ghana | 1557 | 1 | 3 | +1 | 0.56% | 12.98% | 77.09% | 51.05% | **64.59%** |
| Panama | 1683 | 1 | 0 | -1 | 0.41% | 4.46% | 10.40% | 7.75% | **12.62%** |

*Probabilities are Monte Carlo estimates (50,000 sims); Monte Carlo standard error is ≈0.2pp or less. Numbers reflect the model and the 2026-06-22 snapshot, not a claim about real-world certainty.*

## 1. Tournament format (confirmed)

The requested format was verified against FIFA and multiple outlets:

- **48 teams**, **12 groups (A–L) of 4**, single round-robin → **72 group matches**.
- **Top 2 of each group** (24 teams) advance to the Round of 32 automatically.
- The **8 best of the 12 third-placed teams** also advance → **32 teams total**.
- The Round of 32 is itself new for 2026 (an extra knockout round).

Sources: [FIFA — how the 48-team format works](https://www.fifa.com/en/articles/article-fifa-world-cup-2026-mexico-canada-usa-new-format-tournament-football-soccer),
[Britannica 2026 World Cup guide](https://www.britannica.com/event/2026-FIFA-World-Cup).

## 2. Data sources

| Data | Source | As of |
|---|---|---|
| Group composition, played scores, remaining fixtures | Wikipedia per-group pages ("2026 FIFA World Cup Group A … L"), cross-checked vs [NBC](https://www.nbcsports.com/soccer/news/2026-world-cup-group-stage-table-full-standings-for-all-12-groups) / [ESPN](https://www.espn.com/soccer/story/_/id/48939282/) and live [GitHub openfootball/worldcup.json](https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json) | 2026-06-22 |
| Team strength (primary) | **World Football Elo** (eloratings.net), via the Wikipedia "World Football Elo Ratings" table | 2026-06-17 |
| Tiebreak / final separator & cross-check | **FIFA/Coca-Cola Men's World Ranking** points | 2026-06-11 |
| Tiebreaker rules | Official "Regulations for the FIFA World Cup 26", Art. 13, confirmed on [FIFA.com](https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/groups-how-teams-qualify-tie-breakers) / ESPN / SofaScore / NBC / SI | 2026 |
| Knockout bracket (R32→Final) | [Wikipedia "2026 FIFA World Cup knockout stage"](https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage), cross-checked vs ESPN's published bracket | 2026 |

All 12 groups' four-team compositions and every played scoreline were
**independently re-verified** against ESPN/NBC/Sky/Fox/Al Jazeera by an
adversarial fact-check pass — **zero discrepancies**. This caught the
qualification-altered seeds (e.g. **Bosnia & Herzegovina**, not Italy, in Group B;
Sweden in F; Turkey in D; Curaçao in E; Cape Verde in H; Uzbekistan in K).

The raw, auditable data lives in [`data.py`](data.py) (72 matches) and
[`ratings.py`](ratings.py) (48 Elo + 48 FIFA values).

## 3. Strength model — Elo → calibrated Poisson scorelines

The FIFA tiebreakers need **goal difference and goals scored**, so the model
produces **scorelines**, not just win/draw/loss. Each remaining match A vs B:

```
dr        = (Elo_A + host_A) − (Elo_B + host_B)     # Elo gap incl. host edge
supremacy = SUP_SCALE · dr                          # expected goal margin
λ_A = max(μ/2 + supremacy/2, 0.15)                  # A's expected goals
λ_B = max(μ/2 − supremacy/2, 0.15)                  # B's expected goals
goals_A ~ Poisson(λ_A),  goals_B ~ Poisson(λ_B)     # independent draws
```

- **μ = 2.75** — expected total goals in an evenly-matched game (World Cup
  group-stage historical average).
- **SUP_SCALE is calibrated, not guessed.** It is chosen so the model's implied
  win expectancy best matches the canonical Elo formula
  `We = 1 / (1 + 10^(−dr/400))` across realistic Elo gaps. Calibrated value
  **≈ 0.0058**, fit RMSE **0.0097** (run `--show-calibration` to see the table).
  This keeps the scoreline model self-consistent with the published Elo metric.

Implied win/draw/loss at the calibrated setting (μ=2.75):

| Elo gap | Elo `We` | model P(W) / P(D) / P(L) |
|--:|--:|--|
| 0 | .500 | .37 / .26 / .37 |
| 100 | .640 | .51 / .24 / .25 |
| 200 | .760 | .65 / .21 / .14 |
| 300 | .849 | .77 / .16 / .07 |
| 500 | .947 | .91 / .08 / .01 |

**Host advantage:** the three hosts (USA, Mexico, Canada) play every group match
at home, so the host team gets **+70 Elo** of venue advantage (tunable via
`--host-adv`). No two hosts share a group.

## 4. Tiebreakers — verified 2026 rules (changed from 2022!)

Ranking teams **within a group** (FIFA WC 26 regulations, Article 13):

1. Points
2. **Head-to-head points** (among the tied teams)
3. **Head-to-head goal difference**
4. **Head-to-head goals scored**  *(criteria 2–4 re-applied to any still-tied subset)*
5. Overall goal difference
6. Overall goals scored
7. Fair-play / conduct points  *(not modelled — no card data)*
8. FIFA World Ranking

> ⚠️ **2026 changed the order.** Unlike 2018/2022 (overall GD first), 2026 applies
> **head-to-head first** (UEFA-style), and **drawing of lots was removed** in
> favour of the FIFA World Ranking. This was double-checked against the primary
> regulation because it contradicts the older convention. The
> [`--no-h2h-first`](#6-running-it) flag reproduces the pre-2026 order for
> comparison — it shifts the most tightly-bunched teams (e.g. Group D's
> Paraguay/Australia/USA) by up to ~2 percentage points.

**Best-third ranking** (across the 12 groups — no head-to-head possible):
Points → overall GD → overall goals scored → fair play (skipped) → FIFA ranking.

Because best-third selection couples all 12 groups, **every group is simulated
jointly in each iteration**, the 12 third-placed teams ranked, and the top 8
flagged as qualifying.

## 5. Knockout stage (Round of 32 → Final)

The bracket structure ([`bracket.py`](bracket.py)) is the official 2026 layout,
verified across Wikipedia and ESPN:

- **Round of 32** (matches 73–88): a fixed template of group winners,
  runners-up and the 8 best thirds. The R16 tree is **not** a consecutive
  pairing (e.g. M89 = W74 vs W77, M90 = W73 vs W75) — taken exactly from the
  published bracket, through QF, SF, third-place play-off and final.
- **Third-place allocation.** The 8 best thirds fill 8 specific slots (matches
  74, 77, 79, 80, 81, 82, 85, 87), each restricted to a set of 5 eligible
  groups (so a third never faces a team from its own group). FIFA resolves this
  with a fixed 495-row lookup table that isn't practically reproducible here,
  and **every** group-combination admits more than one valid matching. Rather
  than freeze one arbitrary choice (which would bias specific teams' R32
  opponents), the sim **samples a valid allocation each iteration**, spreading
  each third over its possible opponents. This honours every official
  constraint; it's the only knockout-structure approximation in the model.
- **Knockout match model.** A knockout tie needs a single winner, so each match
  is decided directly by the **Elo win probability**
  `P(A beats B) = 1 / (1 + 10^(−Δ/400))`. This is exactly what the group-stage
  Poisson model is calibrated to, and it cleanly absorbs extra time and the
  penalty shoot-out into the expectancy (a shoot-out is, on average, the
  near-coin-flip the formula already reflects between close sides).
- **Venues.** Knockout venues are fixed by the bracket, not the opponent, so
  hosts get **no** venue boost by default (`--ko-host-adv` to change).

> **Read title odds as model output, not gospel.** An Elo-only knockout with no
> draws compounds favourites' per-round edges, so the model concentrates title
> probability on the top Elo sides a bit more than betting markets do (which
> price in extra uncertainty). The *shape* — Argentina/Spain clear of France/
> England, then a gap — is robust; treat the exact % as the model's view.

## 6. Assumptions & limitations

- **Independent Poisson goals.** Simple and well-calibrated to Elo, but assumes
  team scoring is independent (no explicit correlation / "both teams score"
  effect) and no in-match game-state dynamics.
- **Static ratings.** Elo is frozen at the 2026-06-17 snapshot; ratings do not
  update as simulated results unfold.
- **No squad/context detail.** Injuries, suspensions, motivation (a team already
  qualified), travel, and weather are not modelled.
- **Fair-play tiebreaker omitted** (no card data); the regulation's next
  criterion, the FIFA ranking, is used instead, with a uniform random lot only
  as an absolute last resort (effectively never triggered — FIFA points are
  distinct).
- **Host edge is a flat +70 Elo** approximation, not a team-specific estimate.
- **Knockout** matches use the Elo win-probability (no scorelines); extra time
  and penalties are absorbed into that expectancy; venues are neutral; and the
  third-place→slot assignment is *sampled* rather than taken from FIFA's exact
  lookup table (see §5).
- Lower-ranked teams' Elo values carry "medium" confidence (see `ratings.py`).

These are deliberately transparent, tunable knobs — not hidden constants.

## 7. Running it

```bash
python simulate.py                     # 50,000 sims (default), 2026 rules
python simulate.py --iters 100000      # more iterations
python simulate.py --show-calibration  # print the Elo→goals calibration table
python simulate.py --no-h2h-first      # pre-2026 tiebreaker order (sensitivity)
python simulate.py --host-adv 0        # turn off group-stage host advantage
python simulate.py --ko-host-adv 50    # give hosts a knockout venue boost too
python test_tiebreakers.py             # unit tests for the tiebreaker logic
python bracket.py                      # bracket self-check over all 495 combos
```

Requires Python 3 + NumPy (no other dependencies). A 50,000-sim run (group stage
+ full knockout) takes ~14 s and is reproducible (`--seed`, default 2026).
Outputs print to console and are written to
[`output/group_probabilities.csv`](output/group_probabilities.csv) (now with
knockout columns) and `output/group_probabilities.md`.

### Validation built in
- `test_tiebreakers.py` proves H2H-first vs overall-first produce the expected
  *different* orderings.
- `bracket.py` confirms a valid third-place allocation exists for all 495
  group-combinations.
- Internal consistency on the 50k run: P(1st)/P(2nd)/P(3rd) each sum to 1.000
  per group; ΣP(best-third) = 8.000; ΣP(advance) = 32.000; and for the knockout
  ΣP(champion) = 1, ΣP(reach R16) = 16, ΣP(QF) = 8, ΣP(SF) = 4, ΣP(final) = 2,
  with P(advance) ≥ P(R16) ≥ … ≥ P(win) for every team.

## 8. Files

| File | Purpose |
|---|---|
| `data.py` | Groups, all 72 matches (played + remaining), host list; self-check |
| `ratings.py` | Elo (primary) + FIFA-points (tiebreak) for all 48 teams, with sources |
| `model.py` | Elo→Poisson match model and SUP_SCALE calibration |
| `tiebreakers.py` | Team tables + verified FIFA-2026 ranking / best-third logic |
| `bracket.py` | Knockout bracket template, third-place allocation, bracket play |
| `simulate.py` | Monte Carlo loop, reporting, CSV/Markdown output |
| `test_tiebreakers.py` | Unit tests for the tiebreaker logic |
| `output/` | Generated probability tables (CSV + Markdown) and run logs |

---

