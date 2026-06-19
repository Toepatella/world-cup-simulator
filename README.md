# 2026 FIFA World Cup — Monte Carlo Simulator (group stage → final)

Estimates every team's probability of reaching each stage of the tournament —
from the **Round of 32** all the way to **lifting the trophy** — by simulating
the remaining group-stage fixtures *and the full knockout bracket* many times.
Matches already played (as of the snapshot date) are treated as **fixed**; only
the unplayed group fixtures and the entire knockout are simulated.

**Snapshot date: 2026-06-18.** At that point Groups A and B had played 2 of 3
rounds; Groups C–L had played 1 of 3. 28 of 72 group matches were complete; 44
remained to be simulated.

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
| Group composition, played scores, remaining fixtures | Wikipedia per-group pages ("2026 FIFA World Cup Group A … L"), cross-checked vs [NBC](https://www.nbcsports.com/soccer/news/2026-world-cup-group-stage-table-full-standings-for-all-12-groups) / [ESPN](https://www.espn.com/soccer/story/_/id/48939282/) | 2026-06-18 |
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
| Argentina | 100% | 78.0% | 66.8% | 50.7% | 34.6% | **22.2%** |
| Spain | 99.0% | 75.8% | 58.9% | 48.6% | 33.9% | **21.2%** |
| France | 99.9% | 83.1% | 62.8% | 46.3% | 27.5% | **15.8%** |
| England | 100% | 81.3% | 60.1% | 39.2% | 20.8% | **11.4%** |
| Colombia | 99.6% | 75.3% | 49.7% | 24.4% | 12.9% | **6.0%** |
| Brazil | 98.2% | 60.2% | 36.8% | 18.7% | 8.4% | **3.6%** |
| Portugal | 87.7% | 58.7% | 30.6% | 16.2% | 7.8% | **3.1%** |
| Germany | 99.9% | 65.5% | 29.4% | 15.5% | 6.5% | **2.5%** |
| Netherlands | 96.8% | 56.7% | 34.4% | 15.3% | 6.4% | **2.4%** |
| Norway | 98.0% | 62.8% | 34.6% | 15.8% | 6.1% | **2.1%** |
| Japan | 95.2% | 51.0% | 27.8% | 11.0% | 4.2% | **1.4%** |
| Belgium | 93.1% | 56.0% | 27.9% | 9.3% | 3.6% | **1.1%** |
| Ecuador | 89.4% | 46.7% | 23.0% | 8.4% | 3.1% | **1.0%** |
| Switzerland | 100% | 62.0% | 26.4% | 8.6% | 2.8% | **0.8%** |
| Mexico | 100% | 59.4% | 19.1% | 8.0% | 2.4% | **0.8%** |
| Croatia | 89.5% | 40.7% | 13.2% | 6.8% | 2.6% | **0.8%** |

*(All 48 teams, including the long shots, are in the CSV. Remaining sides each
sit below ~0.7% to win.)*

### Group-stage advancement
`ADV` = P(1st) + P(2nd) + P(qualify as one of the 8 best thirds). Sorted by ADV.
Full machine-readable table: [`output/group_probabilities.csv`](output/group_probabilities.csv).

### Group A
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| Mexico | 1881 | 6 | 100% | 0% | 0% | 0% | **100%** |
| South Korea | 1786 | 3 | 0% | 91.7% | 7.4% | 5.2% | **97.0%** |
| Czech Republic | 1712 | 1 | 0% | 0.9% | 70.9% | 11.2% | **12.0%** |
| South Africa | 1511 | 1 | 0% | 7.4% | 21.8% | 1.0% | **8.4%** |

### Group B
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| Canada | 1767 | 4 | 59.3% | 40.7% | <0.1% | <0.1% | **100%** |
| Switzerland | 1865 | 4 | 40.7% | 59.3% | 0% | 0% | **100%** |
| Bosnia and Herzegovina | 1616 | 1 | 0% | <0.1% | 82.4% | 60.1% | **60.1%** |
| Qatar | 1447 | 1 | 0% | 0% | 17.6% | 17.4% | **17.4%** |

### Group C
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| Brazil | 1978 | 1 | 54.8% | 30.4% | 14.3% | 13.1% | **98.2%** |
| Morocco | 1840 | 1 | 25.4% | 38.7% | 31.9% | 27.6% | **91.7%** |
| Scotland | 1794 | 3 | 19.7% | 30.4% | 49.6% | 39.5% | **89.6%** |
| Haiti | 1536 | 0 | <0.1% | 0.5% | 4.2% | 2.6% | **3.1%** |

### Group D
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| United States | 1780 | 3 | 46.2% | 34.3% | 16.4% | 15.5% | **96.0%** |
| Australia | 1839 | 3 | 44.0% | 38.5% | 13.0% | 11.9% | **94.4%** |
| Turkey | 1849 | 0 | 6.6% | 17.4% | 41.9% | 29.5% | **53.5%** |
| Paraguay | 1780 | 0 | 3.3% | 9.8% | 28.8% | 19.3% | **32.3%** |

### Group E
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| Germany | 1939 | 3 | 64.6% | 22.4% | 13.0% | 12.9% | **99.9%** |
| Ivory Coast | 1743 | 3 | 24.2% | 59.1% | 14.5% | 14.1% | **97.4%** |
| Ecuador | 1890 | 0 | 11.2% | 18.1% | 68.7% | 60.1% | **89.4%** |
| Curacao | 1427 | 0 | <0.1% | 0.4% | 3.7% | 1.0% | **1.5%** |

### Group F
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| Netherlands | 1944 | 1 | 46.7% | 36.0% | 15.8% | 14.1% | **96.8%** |
| Sweden | 1755 | 3 | 15.8% | 23.1% | 60.6% | 57.8% | **96.7%** |
| Japan | 1910 | 1 | 37.3% | 40.1% | 20.2% | 17.7% | **95.2%** |
| Tunisia | 1585 | 0 | 0.1% | 0.8% | 3.4% | 1.6% | **2.5%** |

### Group G
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| Belgium | 1879 | 1 | 56.1% | 24.7% | 14.7% | 12.3% | **93.1%** |
| Egypt | 1711 | 1 | 20.1% | 27.2% | 33.9% | 27.8% | **75.1%** |
| Iran | 1756 | 1 | 19.5% | 33.9% | 27.6% | 9.0% | **62.4%** |
| New Zealand | 1578 | 1 | 4.3% | 14.2% | 23.8% | 11.6% | **30.0%** |

### Group H
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| Spain | 2129 | 1 | 80.4% | 15.7% | 3.4% | 2.8% | **99.0%** |
| Uruguay | 1870 | 1 | 15.1% | 54.5% | 20.8% | 9.5% | **79.1%** |
| Cape Verde | 1606 | 1 | 2.8% | 14.6% | 42.7% | 31.2% | **48.5%** |
| Saudi Arabia | 1598 | 1 | 1.7% | 15.2% | 33.2% | 21.7% | **38.6%** |

### Group I
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| France | 2084 | 3 | 76.6% | 22.7% | 0.6% | 0.6% | **99.9%** |
| Norway | 1929 | 3 | 22.5% | 53.8% | 23.5% | 21.7% | **98.0%** |
| Senegal | 1839 | 0 | 0.9% | 23.3% | 65.3% | 44.7% | **68.8%** |
| Iraq | 1592 | 0 | <0.1% | 0.2% | 10.7% | 4.4% | **4.7%** |

### Group J
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| Argentina | 2128 | 3 | 89.6% | 10.1% | 0.2% | 0.2% | **100%** |
| Austria | 1857 | 3 | 10.0% | 68.3% | 20.9% | 16.6% | **94.9%** |
| Algeria | 1759 | 0 | 0.3% | 20.7% | 50.6% | 27.1% | **48.1%** |
| Jordan | 1653 | 0 | <0.1% | 0.8% | 28.3% | 11.9% | **12.8%** |

### Group K
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| Colombia | 1998 | 3 | 69.6% | 25.3% | 4.9% | 4.6% | **99.6%** |
| Portugal | 1967 | 1 | 27.7% | 49.6% | 17.6% | 10.4% | **87.7%** |
| DR Congo | 1674 | 1 | 2.2% | 14.8% | 42.8% | 25.5% | **42.5%** |
| Uzbekistan | 1698 | 0 | 0.5% | 10.3% | 34.7% | 21.8% | **32.6%** |

### Group L
| Team | Elo | Pts | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|
| England | 2055 | 3 | 98.1% | 1.8% | <0.1% | <0.1% | **100%** |
| Croatia | 1881 | 0 | 0.8% | 80.7% | 12.6% | 8.0% | **89.5%** |
| Ghana | 1557 | 3 | 0.7% | 13.0% | 76.8% | 37.4% | **51.2%** |
| Panama | 1683 | 0 | 0.4% | 4.4% | 10.5% | 6.1% | **10.9%** |

*Probabilities are Monte Carlo estimates (50,000 sims); Monte Carlo standard
error is ≈0.2pp or less. Numbers reflect the model and the 2026-06-18 snapshot,
not a claim about real-world certainty.*
