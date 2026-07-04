# 2026 FIFA World Cup — Monte Carlo Simulator (group stage → final)

Estimates every team's probability of reaching each stage of the tournament —
from the **Round of 32** all the way to **lifting the trophy**. Every match that
has already been played — group stage *and* knockout — is **seeded in as a fixed
official result**; only the matches still to come are simulated, many times over.
Predictions are driven by the **live FIFA World Ranking**, used as an Elo-style
rating that updates after every played match, so form carried into the knockout
rounds is reflected in the odds.

---

## Headline results (50,000 simulations)

Official results (group stage and any completed knockout rounds) are seeded in as fixed; every unplayed match is predicted. Predictions use the **live FIFA World Ranking** as the rating — every team starts at its pre-tournament FIFA points and the rating is updated after every played match (Elo-style: `r += K·(W − We)`), so a team that wins carries the bump into its next tie.

### Title odds — probability of reaching each knockout round (and winning)
Sorted by championship %. `R32` = reach the knockout stage at all.

| Team | R32 | R16 | QF | SF | Final | **Win** |
|---|--:|--:|--:|--:|--:|--:|
| France | 100.00% | 100.00% | 90.28% | 67.20% | 42.98% | **26.21%** |
| Argentina | 100.00% | 100.00% | 86.16% | 64.21% | 41.50% | **23.56%** |
| Spain | 100.00% | 100.00% | 64.28% | 46.21% | 24.79% | **14.28%** |
| England | 100.00% | 100.00% | 63.82% | 39.47% | 20.53% | **9.78%** |
| Brazil | 100.00% | 100.00% | 73.36% | 35.92% | 16.45% | **6.79%** |
| Morocco | 100.00% | 100.00% | 76.00% | 26.37% | 11.62% | **4.92%** |
| Portugal | 100.00% | 100.00% | 35.72% | 20.83% | 8.36% | **3.55%** |
| Belgium | 100.00% | 100.00% | 58.83% | 21.40% | 7.59% | **2.94%** |
| Mexico | 100.00% | 100.00% | 36.18% | 17.51% | 6.65% | **2.39%** |
| Colombia | 100.00% | 100.00% | 53.90% | 17.65% | 7.03% | **2.33%** |
| Switzerland | 100.00% | 100.00% | 46.10% | 13.71% | 5.03% | **1.49%** |
| United States | 100.00% | 100.00% | 41.17% | 11.56% | 3.33% | **0.98%** |
| Norway | 100.00% | 100.00% | 26.64% | 7.10% | 1.75% | **0.36%** |
| Egypt | 100.00% | 100.00% | 13.84% | 4.42% | 1.07% | **0.19%** |
| Canada | 100.00% | 100.00% | 24.00% | 3.89% | 0.86% | **0.16%** |
| Paraguay | 100.00% | 100.00% | 9.72% | 2.53% | 0.47% | **0.07%** |

*(All 48 teams, including the long shots, are in the CSV. Remaining sides each sit below ~0.7% to win.)*

## Knockout bracket (official results seeded, rest predicted)

`*` = official result already played (16 matches); unmarked matches show the live-rating model's win probabilities, with `>` marking the projected winner.

```text
R32*                                                                                                                                                        
+--------------------------+                                                                                                                                
|  Germany           72.66%|    R16                                                                                                                         
|> Paraguay          27.34%|    +--------------------------+                                                                                                
+--------------------------+    |  Paraguay           9.93%|                                                                                                
R32*                            |> France            90.07%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|> France            90.36%|                                    QF                                                                                          
|  Sweden             9.64%|                                    +--------------------------+                                                                
+--------------------------+                                    |> France            70.16%|                                                                
R32*                                                            |  Morocco           29.84%|                                                                
+--------------------------+                                    +--------------------------+                                                                
|  South Africa      32.29%|    R16                                                                                                                         
|> Canada            67.71%|    +--------------------------+                                                                                                
+--------------------------+    |  Canada            23.95%|                                                                                                
R32*                            |> Morocco           76.05%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|  Netherlands       51.06%|                                                                    SF                                                          
|> Morocco           48.94%|                                                                    +--------------------------+                                
+--------------------------+                                                                    |> France            54.70%|                                
R32*                                                                                            |  Spain             45.30%|                                
+--------------------------+                                                                    +--------------------------+                                
|> Portugal          63.37%|    R16                                                                                                                         
|  Croatia           36.63%|    +--------------------------+                                                                                                
+--------------------------+    |  Portugal          35.60%|                                                                                                
R32*                            |> Spain             64.40%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|> Spain             85.04%|                                    QF                                                                                          
|  Austria           14.96%|                                    +--------------------------+                                                                
+--------------------------+                                    |> Spain             68.91%|                                                                
R32*                                                            |  Belgium           31.09%|                                                                
+--------------------------+                                    +--------------------------+                                                                
|> United States     82.93%|    R16                                                                                                                         
|  Bosnia and Herz.  17.07%|    +--------------------------+                                                                                                
+--------------------------+    |  United States     41.24%|                                                                                                
R32*                            |> Belgium           58.76%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|> Belgium           65.58%|                                                                                                    Final                       
|  Senegal           34.42%|                                                                                                    +--------------------------+
+--------------------------+                                                                                                    |> France            51.51%|
R32*                                                                                                                            |  Argentina         48.49%|
+--------------------------+                                                                                                    +--------------------------+
|> Brazil            69.60%|    R16                                                                                                                         
|  Japan             30.40%|    +--------------------------+                                                                                                
+--------------------------+    |> Brazil            73.49%|                                                                                                
R32*                            |  Norway            26.51%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|  Ivory Coast       38.97%|                                    QF                                                                                          
|> Norway            61.03%|                                    +--------------------------+                                                                
+--------------------------+                                    |  Brazil            43.65%|                                                                
R32*                                                            |> England           56.35%|                                                                
+--------------------------+                                    +--------------------------+                                                                
|> Mexico            73.98%|    R16                                                                                                                         
|  Ecuador           26.02%|    +--------------------------+                                                                                                
+--------------------------+    |  Mexico            36.14%|                                                                                                
R32*                            |> England           63.86%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|> England           87.71%|                                                                    SF                                                          
|  DR Congo          12.29%|                                                                    +--------------------------+                                
+--------------------------+                                                                    |  England           41.29%|                                
R32*                                                                                            |> Argentina         58.71%|                                
+--------------------------+                                                                    +--------------------------+                                
|> Argentina         94.69%|    R16                                                                                                                         
|  Cape Verde         5.31%|    +--------------------------+                                                                                                
+--------------------------+    |> Argentina         86.33%|                                                                                                
R32*                            |  Egypt             13.67%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|  Australia         50.31%|                                    QF                                                                                          
|> Egypt             49.69%|                                    +--------------------------+                                                                
+--------------------------+                                    |> Argentina         73.24%|                                                                
R32*                                                            |  Colombia          26.76%|                                                                
+--------------------------+                                    +--------------------------+                                                                
|> Switzerland       71.41%|    R16                                                                                                                         
|  Algeria           28.59%|    +--------------------------+                                                                                                
+--------------------------+    |  Switzerland       45.97%|                                                                                                
R32*                            |> Colombia          54.03%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|> Colombia          87.73%|                                                                                                                                
|  Ghana             12.27%|                                                                                                                                
+--------------------------+                                                                                                                                

Third place
+--------------------------+
|> Spain             55.58%|
|  England           44.42%|
+--------------------------+

Champion: France
```

### Group-stage advancement
`FIFA` = live FIFA World Ranking points (2 decimals), updated after every match. `ADV` = P(1st) + P(2nd) + P(qualify as one of the 8 best thirds). Sorted by ADV.
Full machine-readable table: [`output/group_probabilities.csv`](output/group_probabilities.csv).

### Group A
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Mexico | 1748.65 | 3 | 9 | +6 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| South Africa | 1441.36 | 3 | 4 | -1 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| South Korea | 1559.65 | 3 | 3 | -1 | 0.00% | 0.00% | 100.00% | 0.00% | **0.00%** |
| Czech Republic | 1468.72 | 3 | 1 | -4 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group B
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Switzerland | 1705.78 | 3 | 7 | +4 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Canada | 1570.02 | 3 | 4 | +5 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Bosnia and Herzegovina | 1412.20 | 3 | 4 | -1 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Qatar | 1389.31 | 3 | 1 | -8 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group C
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Brazil | 1803.19 | 3 | 7 | +6 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Morocco | 1770.71 | 3 | 7 | +3 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Scotland | 1489.23 | 3 | 3 | -3 | 0.00% | 0.00% | 100.00% | 0.00% | **0.00%** |
| Haiti | 1272.29 | 3 | 0 | -6 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group D
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| United States | 1686.74 | 3 | 6 | +4 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Australia | 1590.74 | 3 | 4 | +0 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Paraguay | 1536.26 | 3 | 4 | -2 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Turkey | 1575.17 | 3 | 3 | -2 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group E
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Germany | 1706.05 | 3 | 6 | +6 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Ivory Coast | 1548.06 | 3 | 6 | +2 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Ecuador | 1567.14 | 3 | 4 | +0 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Curacao | 1289.58 | 3 | 1 | -8 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group F
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Netherlands | 1778.09 | 3 | 7 | +6 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Japan | 1659.33 | 3 | 5 | +4 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Sweden | 1530.52 | 3 | 4 | +0 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Tunisia | 1406.10 | 3 | 0 | -10 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group G
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Belgium | 1748.22 | 3 | 5 | +4 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Egypt | 1588.58 | 3 | 5 | +2 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Iran | 1607.93 | 3 | 3 | +0 | 0.00% | 0.00% | 100.00% | 0.00% | **0.00%** |
| New Zealand | 1275.10 | 3 | 1 | -6 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group H
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Spain | 1886.49 | 3 | 7 | +5 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Cape Verde | 1408.36 | 3 | 3 | +0 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Uruguay | 1630.60 | 3 | 2 | -1 | 0.00% | 0.00% | 100.00% | 0.00% | **0.00%** |
| Saudi Arabia | 1429.74 | 3 | 2 | -4 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group I
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| France | 1919.22 | 3 | 9 | +8 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Norway | 1626.02 | 3 | 6 | +1 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Senegal | 1636.24 | 3 | 3 | +2 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Iraq | 1389.08 | 3 | 0 | -11 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group J
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Argentina | 1908.69 | 3 | 9 | +7 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Austria | 1584.54 | 3 | 4 | +0 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Algeria | 1546.74 | 3 | 4 | -2 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Jordan | 1354.68 | 3 | 0 | -5 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group K
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Colombia | 1733.82 | 3 | 7 | +3 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Portugal | 1783.54 | 3 | 5 | +5 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| DR Congo | 1506.13 | 3 | 4 | +1 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Uzbekistan | 1397.09 | 3 | 0 | -9 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group L
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| England | 1847.57 | 3 | 7 | +4 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Croatia | 1688.33 | 3 | 6 | +0 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Ghana | 1392.05 | 3 | 4 | +0 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Panama | 1479.76 | 3 | 0 | -4 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

*Probabilities are Monte Carlo estimates (50,000 sims); Monte Carlo standard error is ≈0.2pp or less. Numbers reflect the model and the 2026-07-04 snapshot, not a claim about real-world certainty.*
