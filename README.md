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
| Argentina | 99.9% | 78.0% | 66.7% | 50.5% | 34.6% | **22.1%** |
| Spain | 99.0% | 75.5% | 58.4% | 48.8% | 34.1% | **21.5%** |
| France | 99.9% | 85.3% | 62.2% | 45.1% | 26.9% | **15.6%** |
| England | 100.0% | 82.2% | 61.1% | 40.3% | 21.2% | **11.6%** |
| Colombia | 99.7% | 77.4% | 52.2% | 25.6% | 13.4% | **6.2%** |
| Brazil | 100.0% | 59.5% | 36.8% | 18.7% | 8.3% | **3.5%** |
| Portugal | 88.1% | 58.6% | 31.2% | 16.9% | 8.1% | **3.2%** |
| Germany | 100.0% | 74.0% | 30.1% | 17.2% | 7.2% | **2.6%** |
| Netherlands | 100.0% | 58.5% | 38.4% | 16.6% | 6.9% | **2.5%** |
| Norway | 99.1% | 69.7% | 37.2% | 16.5% | 6.6% | **2.3%** |
| Japan | 100.0% | 51.5% | 27.9% | 11.1% | 4.2% | **1.4%** |
| Belgium | 93.4% | 57.0% | 30.1% | 9.9% | 3.7% | **1.2%** |
| Croatia | 90.8% | 41.7% | 13.4% | 7.3% | 2.9% | **0.8%** |
| Mexico | 100.0% | 61.5% | 19.7% | 8.5% | 2.7% | **0.8%** |
| Switzerland | 100.0% | 62.8% | 25.8% | 8.3% | 2.8% | **0.7%** |
| Austria | 97.0% | 31.9% | 15.3% | 6.9% | 2.3% | **0.6%** |
| Uruguay | 80.2% | 24.6% | 13.1% | 5.8% | 2.0% | **0.5%** |
| Senegal | 72.6% | 37.9% | 17.1% | 5.0% | 1.5% | **0.4%** |
| Australia | 96.5% | 51.1% | 12.5% | 4.8% | 1.5% | **0.4%** |
| Morocco | 100.0% | 38.8% | 19.3% | 5.9% | 1.7% | **0.4%** |
| Ecuador | 32.6% | 17.1% | 9.2% | 3.2% | 1.2% | **0.4%** |
| United States | 100.0% | 61.9% | 27.5% | 5.8% | 1.5% | **0.3%** |
| South Korea | 98.2% | 44.0% | 14.5% | 3.6% | 0.9% | **0.2%** |
| Canada | 100.0% | 49.2% | 14.0% | 3.0% | 0.7% | **0.2%** |
| Scotland | 88.9% | 28.2% | 8.2% | 2.4% | 0.6% | **0.1%** |
| Paraguay | 83.0% | 28.3% | 6.7% | 2.2% | 0.5% | **0.1%** |
| Sweden | 94.5% | 32.4% | 9.7% | 2.1% | 0.4% | **<0.1%** |
| Algeria | 53.0% | 15.7% | 6.2% | 1.5% | 0.3% | **<0.1%** |
| Ivory Coast | 97.8% | 25.1% | 6.8% | 1.4% | 0.2% | **<0.1%** |
| Egypt | 75.8% | 26.7% | 6.8% | 1.3% | 0.3% | **<0.1%** |
| Iran | 63.4% | 26.9% | 7.9% | 1.8% | 0.4% | **<0.1%** |
| Czech Republic | 12.9% | 4.1% | 1.5% | 0.3% | <0.1% | **<0.1%** |
| DR Congo | 42.8% | 8.0% | 1.6% | 0.4% | <0.1% | **<0.1%** |
| Uzbekistan | 36.8% | 6.6% | 1.4% | 0.4% | <0.1% | **<0.1%** |
| Jordan | 15.3% | 3.9% | 1.0% | 0.1% | <0.1% | **<0.1%** |
| Bosnia and Herzegovina | 60.6% | 14.2% | 3.2% | 0.3% | <0.1% | **<0.1%** |
| New Zealand | 30.6% | 5.9% | 0.7% | <0.1% | <0.1% | **<0.1%** |
| Cape Verde | 49.3% | 7.0% | 1.6% | 0.2% | <0.1% | **<0.1%** |
| Iraq | 5.9% | 1.1% | 0.3% | <0.1% | <0.1% | **<0.1%** |
| South Africa | 8.8% | 1.2% | 0.1% | <0.1% | <0.1% | **0.0%** |
| Qatar | 17.5% | 1.8% | 0.2% | <0.1% | <0.1% | **0.0%** |
| Saudi Arabia | 39.2% | 4.9% | 1.1% | 0.1% | <0.1% | **0.0%** |
| Ghana | 59.1% | 5.8% | 1.0% | <0.1% | <0.1% | **0.0%** |
| Panama | 12.1% | 2.3% | 0.6% | 0.1% | <0.1% | **0.0%** |

*(All 48 teams, including the long shots, are in the CSV. Remaining sides each sit below ~0.7% to win.)*

### Group-stage advancement
`ADV` = P(1st) + P(2nd) + P(qualify as one of the 8 best thirds). Sorted by ADV.
Full machine-readable table: [`output/group_probabilities.csv`](output/group_probabilities.csv).

### Group A
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Mexico | 1881 | 2 | 6 | +3 | 100.0% | 0.0% | 0.0% | 0.0% | **100.0%** |
| South Korea | 1786 | 2 | 3 | +0 | 0.0% | 91.5% | 7.5% | 6.7% | **98.2%** |
| Czech Republic | 1712 | 2 | 1 | -1 | 0.0% | 0.9% | 70.2% | 12.0% | **12.9%** |
| South Africa | 1511 | 2 | 1 | -2 | 0.0% | 7.6% | 22.3% | 1.2% | **8.8%** |

### Group B
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Canada | 1767 | 2 | 4 | +6 | 59.2% | 40.8% | <0.1% | <0.1% | **100.0%** |
| Switzerland | 1865 | 2 | 4 | +3 | 40.8% | 59.2% | 0.0% | 0.0% | **100.0%** |
| Bosnia and Herzegovina | 1616 | 2 | 1 | -3 | 0.0% | <0.1% | 82.4% | 60.5% | **60.6%** |
| Qatar | 1447 | 2 | 1 | -6 | 0.0% | 0.0% | 17.6% | 17.5% | **17.5%** |

### Group C
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Brazil | 1978 | 2 | 4 | +3 | 61.4% | 23.9% | 14.7% | 14.7% | **100.0%** |
| Morocco | 1840 | 2 | 4 | +1 | 35.1% | 63.9% | 1.0% | 1.0% | **100.0%** |
| Scotland | 1794 | 2 | 3 | +0 | 3.5% | 12.2% | 84.3% | 73.2% | **88.9%** |
| Haiti | 1536 | 2 | 0 | -4 | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |

### Group D
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| United States | 1780 | 2 | 6 | +5 | 100.0% | 0.0% | 0.0% | 0.0% | **100.0%** |
| Australia | 1839 | 2 | 3 | +0 | 0.0% | 70.3% | 29.7% | 26.2% | **96.5%** |
| Paraguay | 1780 | 2 | 3 | -2 | 0.0% | 29.7% | 70.3% | 53.3% | **83.0%** |
| Turkey | 1849 | 2 | 0 | -3 | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |

### Group E
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Germany | 1939 | 2 | 6 | +7 | 100.0% | 0.0% | 0.0% | 0.0% | **100.0%** |
| Ivory Coast | 1743 | 2 | 3 | +0 | 0.0% | 94.1% | 4.0% | 3.6% | **97.8%** |
| Ecuador | 1890 | 2 | 1 | -1 | 0.0% | 1.9% | 87.3% | 30.7% | **32.6%** |
| Curacao | 1427 | 2 | 1 | -6 | 0.0% | 4.0% | 8.7% | 1.8% | **5.8%** |

### Group F
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Netherlands | 1944 | 2 | 4 | +4 | 72.4% | 27.5% | 0.1% | 0.1% | **100.0%** |
| Japan | 1910 | 2 | 4 | +4 | 24.5% | 57.0% | 18.5% | 18.5% | **100.0%** |
| Sweden | 1755 | 2 | 3 | +0 | 3.1% | 15.5% | 81.4% | 75.8% | **94.5%** |
| Tunisia | 1585 | 2 | 0 | -8 | 0.0% | 0.0% | 0.0% | 0.0% | **0.0%** |

### Group G
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Belgium | 1879 | 1 | 1 | +0 | 55.6% | 24.7% | 15.0% | 13.0% | **93.4%** |
| Egypt | 1711 | 1 | 1 | +0 | 20.3% | 27.7% | 33.5% | 27.8% | **75.8%** |
| Iran | 1756 | 1 | 1 | +0 | 19.9% | 33.2% | 27.7% | 10.2% | **63.4%** |
| New Zealand | 1578 | 1 | 1 | +0 | 4.2% | 14.3% | 23.8% | 12.0% | **30.6%** |

### Group H
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Spain | 2129 | 1 | 1 | +0 | 80.8% | 15.6% | 3.1% | 2.6% | **99.0%** |
| Uruguay | 1870 | 1 | 1 | +0 | 14.8% | 55.3% | 20.5% | 10.1% | **80.2%** |
| Cape Verde | 1606 | 1 | 1 | +0 | 2.7% | 13.9% | 43.5% | 32.7% | **49.3%** |
| Saudi Arabia | 1598 | 1 | 1 | +0 | 1.7% | 15.2% | 33.0% | 22.3% | **39.2%** |

### Group I
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| France | 2084 | 1 | 3 | +2 | 76.6% | 22.7% | 0.6% | 0.6% | **99.9%** |
| Norway | 1929 | 1 | 3 | +3 | 22.4% | 54.1% | 23.3% | 22.6% | **99.1%** |
| Senegal | 1839 | 1 | 0 | -2 | 0.9% | 23.0% | 65.1% | 48.7% | **72.6%** |
| Iraq | 1592 | 1 | 0 | -3 | <0.1% | 0.3% | 11.0% | 5.6% | **5.9%** |

### Group J
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Argentina | 2128 | 1 | 3 | +3 | 89.4% | 10.4% | 0.2% | 0.2% | **99.9%** |
| Austria | 1857 | 1 | 3 | +2 | 10.2% | 68.2% | 20.9% | 18.6% | **97.0%** |
| Algeria | 1759 | 1 | 0 | -3 | 0.3% | 20.6% | 51.0% | 32.1% | **53.0%** |
| Jordan | 1653 | 1 | 0 | -2 | 0.1% | 0.8% | 28.0% | 14.4% | **15.3%** |

### Group K
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Colombia | 1998 | 1 | 3 | +2 | 70.1% | 25.1% | 4.5% | 4.4% | **99.7%** |
| Portugal | 1967 | 1 | 1 | +0 | 27.2% | 49.8% | 18.1% | 11.1% | **88.1%** |
| DR Congo | 1674 | 1 | 1 | +0 | 2.2% | 14.8% | 42.4% | 25.8% | **42.8%** |
| Uzbekistan | 1698 | 1 | 0 | -2 | 0.4% | 10.3% | 35.0% | 26.1% | **36.8%** |

### Group L
| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| England | 2055 | 1 | 3 | +2 | 98.2% | 1.7% | <0.1% | <0.1% | **100.0%** |
| Croatia | 1881 | 1 | 0 | -2 | 0.8% | 81.3% | 12.3% | 8.7% | **90.8%** |
| Ghana | 1557 | 1 | 3 | +1 | 0.6% | 12.6% | 77.2% | 45.8% | **59.1%** |
| Panama | 1683 | 1 | 0 | -1 | 0.4% | 4.4% | 10.4% | 7.3% | **12.1%** |

*Probabilities are Monte Carlo estimates (50,000 sims); Monte Carlo standard error is ≈0.2pp or less. Numbers reflect the model and the 2026-06-21 snapshot, not a claim about real-world certainty.*
