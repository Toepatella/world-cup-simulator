# 2026 FIFA World Cup — Monte Carlo Simulator (group stage → final)

Estimates every team's probability of reaching each stage of the tournament —
from the **Round of 32** all the way to **lifting the trophy** — by simulating
the remaining group-stage fixtures *and the full knockout bracket* many times.
Matches already played (as of the snapshot date) are treated as **fixed**; only
the unplayed group fixtures and the entire knockout are simulated.

---

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
| Group composition, played scores, remaining fixtures | Wikipedia per-group pages ("2026 FIFA World Cup Group A … L"), cross-checked vs [NBC](https://www.nbcsports.com/soccer/news/2026-world-cup-group-stage-table-full-standings-for-all-12-groups) / [ESPN](https://www.espn.com/soccer/story/_/id/48939282/) and live [GitHub openfootball/worldcup.json](https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json) | 2026-06-21 |
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

## 9. Headline results (50,000 simulations)

### Title odds — probability of reaching each knockout round (and winning)
Sorted by championship %. `R32` = reach the knockout stage at all.

| Team | R32 | R16 | QF | SF | Final | **Win** |
|---|--:|--:|--:|--:|--:|--:|
| Argentina | 99.95% | 77.98% | 66.70% | 50.46% | 34.57% | **22.06%** |
| Spain | 99.05% | 75.50% | 58.41% | 48.81% | 34.07% | **21.54%** |
| France | 99.91% | 85.29% | 62.16% | 45.07% | 26.89% | **15.61%** |
| England | 100.00% | 82.19% | 61.14% | 40.35% | 21.21% | **11.55%** |
| Colombia | 99.69% | 77.41% | 52.16% | 25.64% | 13.37% | **6.21%** |
| Brazil | 100.00% | 59.54% | 36.75% | 18.74% | 8.32% | **3.52%** |
| Portugal | 88.09% | 58.64% | 31.19% | 16.91% | 8.07% | **3.21%** |
| Germany | 100.00% | 74.05% | 30.09% | 17.20% | 7.22% | **2.62%** |
| Netherlands | 100.00% | 58.45% | 38.35% | 16.57% | 6.94% | **2.55%** |
| Norway | 99.10% | 69.74% | 37.16% | 16.49% | 6.63% | **2.30%** |
| Japan | 100.00% | 51.46% | 27.86% | 11.11% | 4.24% | **1.41%** |
| Belgium | 93.37% | 57.02% | 30.08% | 9.94% | 3.69% | **1.15%** |
| Croatia | 90.78% | 41.66% | 13.44% | 7.30% | 2.85% | **0.82%** |
| Mexico | 100.00% | 61.52% | 19.65% | 8.46% | 2.70% | **0.80%** |
| Switzerland | 100.00% | 62.80% | 25.78% | 8.29% | 2.81% | **0.75%** |
| Austria | 97.02% | 31.89% | 15.32% | 6.86% | 2.28% | **0.57%** |
| Uruguay | 80.16% | 24.57% | 13.14% | 5.83% | 2.02% | **0.52%** |
| Senegal | 72.56% | 37.87% | 17.13% | 5.04% | 1.54% | **0.43%** |
| Australia | 96.45% | 51.07% | 12.54% | 4.77% | 1.48% | **0.42%** |
| Morocco | 100.00% | 38.83% | 19.27% | 5.86% | 1.75% | **0.42%** |
| Ecuador | 32.60% | 17.11% | 9.20% | 3.17% | 1.17% | **0.38%** |
| United States | 100.00% | 61.93% | 27.48% | 5.83% | 1.55% | **0.29%** |
| South Korea | 98.15% | 44.02% | 14.55% | 3.58% | 0.88% | **0.16%** |
| Canada | 100.00% | 49.18% | 14.03% | 2.99% | 0.74% | **0.15%** |
| Scotland | 88.94% | 28.17% | 8.20% | 2.41% | 0.57% | **0.15%** |
| Paraguay | 82.96% | 28.29% | 6.70% | 2.21% | 0.55% | **0.10%** |
| Sweden | 94.47% | 32.42% | 9.70% | 2.11% | 0.41% | **0.08%** |
| Algeria | 53.00% | 15.69% | 6.17% | 1.47% | 0.34% | **0.06%** |
| Ivory Coast | 97.76% | 25.08% | 6.79% | 1.39% | 0.23% | **0.05%** |
| Egypt | 75.81% | 26.67% | 6.78% | 1.28% | 0.26% | **0.05%** |
| Iran | 63.39% | 26.90% | 7.90% | 1.77% | 0.36% | **0.04%** |
| Czech Republic | 12.94% | 4.11% | 1.47% | 0.28% | 0.05% | **<0.01%** |
| DR Congo | 42.81% | 8.01% | 1.57% | 0.36% | 0.06% | **<0.01%** |
| Uzbekistan | 36.84% | 6.58% | 1.37% | 0.36% | 0.07% | **<0.01%** |
| Jordan | 15.33% | 3.87% | 1.04% | 0.13% | 0.03% | **<0.01%** |
| Bosnia and Herzegovina | 60.58% | 14.17% | 3.21% | 0.30% | 0.03% | **<0.01%** |
| New Zealand | 30.56% | 5.87% | 0.73% | 0.07% | <0.01% | **<0.01%** |
| Cape Verde | 49.34% | 7.00% | 1.59% | 0.20% | 0.02% | **<0.01%** |
| Iraq | 5.93% | 1.07% | 0.26% | 0.03% | <0.01% | **<0.01%** |
| South Africa | 8.81% | 1.23% | 0.11% | <0.01% | <0.01% | **0.00%** |
| Qatar | 17.48% | 1.81% | 0.19% | <0.01% | <0.01% | **0.00%** |
| Saudi Arabia | 39.16% | 4.88% | 1.06% | 0.13% | 0.01% | **0.00%** |
| Ghana | 59.08% | 5.78% | 0.99% | 0.10% | 0.01% | **0.00%** |
| Panama | 12.13% | 2.30% | 0.60% | 0.13% | 0.02% | **0.00%** |

*(All 48 teams, including the long shots, are in the CSV. Remaining sides each sit below ~0.7% to win.)*

### Group-stage advancement
`ADV` = P(1st) + P(2nd) + P(qualify as one of the 8 best thirds). Sorted by ADV.
Full machine-readable table: [`output/group_probabilities.csv`](output/group_probabilities.csv).

### Group A
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Mexico | 1881 | 2 | 6 | +3 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| South Korea | 1786 | 2 | 3 | +0 | 0.00% | 91.48% | 7.53% | 6.67% | **98.15%** |
| Czech Republic | 1712 | 2 | 1 | -1 | 0.00% | 0.93% | 70.20% | 12.01% | **12.94%** |
| South Africa | 1511 | 2 | 1 | -2 | 0.00% | 7.59% | 22.27% | 1.22% | **8.81%** |

### Group B
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Canada | 1767 | 2 | 4 | +6 | 59.18% | 40.75% | 0.07% | 0.07% | **100.00%** |
| Switzerland | 1865 | 2 | 4 | +3 | 40.82% | 59.18% | 0.00% | 0.00% | **100.00%** |
| Bosnia and Herzegovina | 1616 | 2 | 1 | -3 | 0.00% | 0.07% | 82.37% | 60.51% | **60.58%** |
| Qatar | 1447 | 2 | 1 | -6 | 0.00% | 0.00% | 17.56% | 17.48% | **17.48%** |

### Group C
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Brazil | 1978 | 2 | 4 | +3 | 61.41% | 23.88% | 14.71% | 14.71% | **100.00%** |
| Morocco | 1840 | 2 | 4 | +1 | 35.12% | 63.88% | 0.99% | 0.99% | **100.00%** |
| Scotland | 1794 | 2 | 3 | +0 | 3.47% | 12.23% | 84.30% | 73.24% | **88.94%** |
| Haiti | 1536 | 2 | 0 | -4 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group D
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| United States | 1780 | 2 | 6 | +5 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Australia | 1839 | 2 | 3 | +0 | 0.00% | 70.30% | 29.70% | 26.16% | **96.45%** |
| Paraguay | 1780 | 2 | 3 | -2 | 0.00% | 29.70% | 70.30% | 53.26% | **82.96%** |
| Turkey | 1849 | 2 | 0 | -3 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group E
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Germany | 1939 | 2 | 6 | +7 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Ivory Coast | 1743 | 2 | 3 | +0 | 0.00% | 94.15% | 3.99% | 3.61% | **97.76%** |
| Ecuador | 1890 | 2 | 1 | -1 | 0.00% | 1.86% | 87.29% | 30.74% | **32.60%** |
| Curacao | 1427 | 2 | 1 | -6 | 0.00% | 3.99% | 8.72% | 1.85% | **5.84%** |

### Group F
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Netherlands | 1944 | 2 | 4 | +4 | 72.41% | 27.47% | 0.11% | 0.11% | **100.00%** |
| Japan | 1910 | 2 | 4 | +4 | 24.47% | 57.02% | 18.51% | 18.51% | **100.00%** |
| Sweden | 1755 | 2 | 3 | +0 | 3.11% | 15.51% | 81.38% | 75.85% | **94.47%** |
| Tunisia | 1585 | 2 | 0 | -8 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group G
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Belgium | 1879 | 1 | 1 | +0 | 55.59% | 24.74% | 15.02% | 13.03% | **93.37%** |
| Egypt | 1711 | 1 | 1 | +0 | 20.32% | 27.69% | 33.47% | 27.80% | **75.81%** |
| Iran | 1756 | 1 | 1 | +0 | 19.90% | 33.24% | 27.68% | 10.25% | **63.39%** |
| New Zealand | 1578 | 1 | 1 | +0 | 4.19% | 14.33% | 23.83% | 12.05% | **30.56%** |

### Group H
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Spain | 2129 | 1 | 1 | +0 | 80.78% | 15.62% | 3.10% | 2.65% | **99.05%** |
| Uruguay | 1870 | 1 | 1 | +0 | 14.80% | 55.26% | 20.47% | 10.10% | **80.16%** |
| Cape Verde | 1606 | 1 | 1 | +0 | 2.73% | 13.95% | 43.47% | 32.66% | **49.34%** |
| Saudi Arabia | 1598 | 1 | 1 | +0 | 1.69% | 15.17% | 32.96% | 22.29% | **39.16%** |

### Group I
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| France | 2084 | 1 | 3 | +2 | 76.61% | 22.70% | 0.60% | 0.60% | **99.91%** |
| Norway | 1929 | 1 | 3 | +3 | 22.44% | 54.07% | 23.28% | 22.59% | **99.10%** |
| Senegal | 1839 | 1 | 0 | -2 | 0.89% | 22.97% | 65.15% | 48.70% | **72.56%** |
| Iraq | 1592 | 1 | 0 | -3 | 0.06% | 0.26% | 10.97% | 5.61% | **5.93%** |

### Group J
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Argentina | 2128 | 1 | 3 | +3 | 89.39% | 10.36% | 0.20% | 0.19% | **99.95%** |
| Austria | 1857 | 1 | 3 | +2 | 10.17% | 68.22% | 20.87% | 18.64% | **97.02%** |
| Algeria | 1759 | 1 | 0 | -3 | 0.32% | 20.60% | 50.97% | 32.08% | **53.00%** |
| Jordan | 1653 | 1 | 0 | -2 | 0.12% | 0.82% | 27.97% | 14.39% | **15.33%** |

### Group K
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Colombia | 1998 | 1 | 3 | +2 | 70.13% | 25.13% | 4.51% | 4.43% | **99.69%** |
| Portugal | 1967 | 1 | 1 | +0 | 27.21% | 49.77% | 18.09% | 11.11% | **88.09%** |
| DR Congo | 1674 | 1 | 1 | +0 | 2.25% | 14.77% | 42.39% | 25.79% | **42.81%** |
| Uzbekistan | 1698 | 1 | 0 | -2 | 0.41% | 10.33% | 35.01% | 26.09% | **36.84%** |

### Group L
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| England | 2055 | 1 | 3 | +2 | 98.23% | 1.68% | 0.07% | 0.07% | **100.00%** |
| Croatia | 1881 | 1 | 0 | -2 | 0.77% | 81.26% | 12.33% | 8.74% | **90.78%** |
| Ghana | 1557 | 1 | 3 | +1 | 0.61% | 12.62% | 77.18% | 45.85% | **59.08%** |
| Panama | 1683 | 1 | 0 | -1 | 0.39% | 4.43% | 10.42% | 7.31% | **12.13%** |

*Probabilities are Monte Carlo estimates (50,000 sims); Monte Carlo standard error is ≈0.2pp or less. Numbers reflect the model and the 2026-06-21 snapshot, not a claim about real-world certainty.*
