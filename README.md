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
| France | 100.00% | 100.00% | 100.00% | 68.34% | 40.30% | **24.15%** |
| Spain | 100.00% | 100.00% | 100.00% | 73.67% | 38.73% | **22.25%** |
| Argentina | 100.00% | 100.00% | 86.25% | 64.27% | 39.58% | **20.93%** |
| England | 100.00% | 100.00% | 100.00% | 76.26% | 41.05% | **19.35%** |
| Morocco | 100.00% | 100.00% | 100.00% | 31.66% | 13.20% | **5.56%** |
| Belgium | 100.00% | 100.00% | 59.04% | 17.23% | 5.59% | **2.10%** |
| Colombia | 100.00% | 100.00% | 53.65% | 17.63% | 6.62% | **2.10%** |
| Norway | 100.00% | 100.00% | 100.00% | 23.74% | 6.85% | **1.53%** |
| Switzerland | 100.00% | 100.00% | 46.35% | 13.73% | 4.92% | **1.28%** |
| United States | 100.00% | 100.00% | 40.96% | 9.10% | 2.18% | **0.58%** |
| Egypt | 100.00% | 100.00% | 13.75% | 4.37% | 0.98% | **0.18%** |
| Mexico | 100.00% | 100.00% | 0.00% | 0.00% | 0.00% | **0.00%** |
| Canada | 100.00% | 100.00% | 0.00% | 0.00% | 0.00% | **0.00%** |
| Brazil | 100.00% | 100.00% | 0.00% | 0.00% | 0.00% | **0.00%** |
| Paraguay | 100.00% | 100.00% | 0.00% | 0.00% | 0.00% | **0.00%** |
| Portugal | 100.00% | 100.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

*(All 48 teams, including the long shots, are in the CSV. Remaining sides each sit below ~0.7% to win.)*

## Knockout bracket (official results seeded, rest predicted)

`*` = official result already played (21 matches); unmarked matches show the live-rating model's win probabilities, with `>` marking the projected winner.

```text
R32*                                                                                                                                                        
+--------------------------+                                                                                                                                
|  Germany           73.22%|    R16*                                                                                                                        
|> Paraguay          26.78%|    +--------------------------+                                                                                                
+--------------------------+    |  Paraguay           9.43%|                                                                                                
R32*                            |> France            90.57%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|> France            90.60%|                                    QF                                                                                          
|  Sweden             9.40%|                                    +--------------------------+                                                                
+--------------------------+                                    |> France            68.20%|                                                                
R32*                                                            |  Morocco           31.80%|                                                                
+--------------------------+                                    +--------------------------+                                                                
|  South Africa      34.98%|    R16*                                                                                                                        
|> Canada            65.02%|    +--------------------------+                                                                                                
+--------------------------+    |  Canada            19.84%|                                                                                                
R32*                            |> Morocco           80.16%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|  Netherlands       48.05%|                                                                    SF                                                          
|> Morocco           51.95%|                                                                    +--------------------------+                                
+--------------------------+                                                                    |> France            52.86%|                                
R32*                                                                                            |  Spain             47.14%|                                
+--------------------------+                                                                    +--------------------------+                                
|> Portugal          60.96%|    R16*                                                                                                                        
|  Croatia           39.04%|    +--------------------------+                                                                                                
+--------------------------+    |  Portugal          31.05%|                                                                                                
R32*                            |> Spain             68.95%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|> Spain             86.30%|                                    QF                                                                                          
|  Austria           13.70%|                                    +--------------------------+                                                                
+--------------------------+                                    |> Spain             71.06%|                                                                
R32*                                                            |  Belgium           28.94%|                                                                
+--------------------------+                                    +--------------------------+                                                                
|> United States     82.93%|    R16                                                                                                                         
|  Bosnia and Herz.  17.07%|    +--------------------------+                                                                                                
+--------------------------+    |  United States     41.24%|                                                                                                
R32*                            |> Belgium           58.76%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|> Belgium           65.58%|                                                                                                    Final                       
|  Senegal           34.42%|                                                                                                    +--------------------------+
+--------------------------+                                                                                                    |> France            52.23%|
R32*                                                                                                                            |  Argentina         47.77%|
+--------------------------+                                                                                                    +--------------------------+
|> Brazil            64.94%|    R16*                                                                                                                        
|  Japan             35.06%|    +--------------------------+                                                                                                
+--------------------------+    |  Brazil            64.49%|                                                                                                
R32*                            |> Norway            35.51%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|  Ivory Coast       34.07%|                                    QF                                                                                          
|> Norway            65.93%|                                    +--------------------------+                                                                
+--------------------------+                                    |  Norway            23.72%|                                                                
R32*                                                            |> England           76.28%|                                                                
+--------------------------+                                    +--------------------------+                                                                
|> Mexico            71.93%|    R16*                                                                                                                        
|  Ecuador           28.07%|    +--------------------------+                                                                                                
+--------------------------+    |  Mexico            31.49%|                                                                                                
R32*                            |> England           68.51%|                                                                                                
+--------------------------+    +--------------------------+                                                                                                
|> England           88.79%|                                                                    SF                                                          
|  DR Congo          11.21%|                                                                    +--------------------------+                                
+--------------------------+                                                                    |  England           43.84%|                                
R32*                                                                                            |> Argentina         56.16%|                                
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
|> Spain             55.54%|
|  England           44.46%|
+--------------------------+

Champion: France
```

### Group-stage advancement
`FIFA` = live FIFA World Ranking points (2 decimals), updated after every match. `ADV` = P(1st) + P(2nd) + P(qualify as one of the 8 best thirds). Sorted by ADV.
Full machine-readable table: [`output/group_probabilities.csv`](output/group_probabilities.csv).

### Group A
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Mexico | 1730.58 | 3 | 9 | +6 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| South Africa | 1441.36 | 3 | 4 | -1 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| South Korea | 1559.65 | 3 | 3 | -1 | 0.00% | 0.00% | 100.00% | 0.00% | **0.00%** |
| Czech Republic | 1468.72 | 3 | 1 | -4 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group B
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Switzerland | 1705.78 | 3 | 7 | +4 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Canada | 1549.06 | 3 | 4 | +5 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Bosnia and Herzegovina | 1412.20 | 3 | 4 | -1 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Qatar | 1389.31 | 3 | 1 | -8 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group C
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Brazil | 1766.44 | 3 | 7 | +6 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Morocco | 1791.67 | 3 | 7 | +3 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Scotland | 1489.23 | 3 | 3 | -3 | 0.00% | 0.00% | 100.00% | 0.00% | **0.00%** |
| Haiti | 1272.29 | 3 | 0 | -6 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group D
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| United States | 1686.74 | 3 | 6 | +4 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Australia | 1590.74 | 3 | 4 | +0 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Paraguay | 1531.29 | 3 | 4 | -2 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
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
| Spain | 1904.29 | 3 | 7 | +5 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Cape Verde | 1408.36 | 3 | 3 | +0 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Uruguay | 1630.60 | 3 | 2 | -1 | 0.00% | 0.00% | 100.00% | 0.00% | **0.00%** |
| Saudi Arabia | 1429.74 | 3 | 2 | -4 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group I
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| France | 1924.18 | 3 | 9 | +8 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Norway | 1662.77 | 3 | 6 | +1 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
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
| Portugal | 1765.74 | 3 | 5 | +5 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| DR Congo | 1506.13 | 3 | 4 | +1 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Uzbekistan | 1397.09 | 3 | 0 | -9 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

### Group L
| Team | FIFA | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| England | 1865.64 | 3 | 7 | +4 | 100.00% | 0.00% | 0.00% | 0.00% | **100.00%** |
| Croatia | 1688.33 | 3 | 6 | +0 | 0.00% | 100.00% | 0.00% | 0.00% | **100.00%** |
| Ghana | 1392.05 | 3 | 4 | +0 | 0.00% | 0.00% | 100.00% | 100.00% | **100.00%** |
| Panama | 1479.76 | 3 | 0 | -4 | 0.00% | 0.00% | 0.00% | 0.00% | **0.00%** |

*Probabilities are Monte Carlo estimates (50,000 sims); Monte Carlo standard error is ≈0.2pp or less. Numbers reflect the model and the 2026-07-06 snapshot, not a claim about real-world certainty.*
