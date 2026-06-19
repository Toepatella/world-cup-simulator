"""
Match-outcome model: World Football Elo -> scoreline via independent Poisson.

Why score a match rather than just W/D/L?  FIFA tiebreakers need goal
difference and goals scored, so the simulation must produce *scorelines*, not
only win/draw/loss. We therefore model each team's goals as an independent
Poisson variable whose mean is set from the Elo difference, then read off
W/D/L from the sampled score.

Construction (one match, team A vs team B with Elo R_A, R_B):

    dr        = (R_A + host_A) - (R_B + host_B)        # Elo gap, incl. host edge
    supremacy = SUP_SCALE * dr                          # expected goal margin
    lambda_A  = max(mu/2 + supremacy/2, MIN_LAMBDA)     # A's expected goals
    lambda_B  = max(mu/2 - supremacy/2, MIN_LAMBDA)     # B's expected goals
    goals_A ~ Poisson(lambda_A),  goals_B ~ Poisson(lambda_B)

`mu` is the expected total goals in an evenly matched game (~2.75, the World
Cup group-stage historical average). `SUP_SCALE` converts an Elo gap into an
expected goal margin and is CALIBRATED (not guessed) so that the model's
implied win expectancy matches the canonical Elo formula
    We = 1 / (1 + 10**(-dr/400))
as closely as possible across realistic Elo gaps. This keeps the model
self-consistent with the published Elo metric while also yielding realistic
scorelines for the tiebreakers.

Host advantage: the three host nations (USA, Mexico, Canada) play every group
match in their own country, so the host team gets +HOST_ADV Elo of venue
advantage. No two hosts share a group, so at most one side is ever boosted.
"""

import math

import numpy as np

MU_DEFAULT = 2.75          # expected total goals, evenly matched game
MIN_LAMBDA = 0.15          # floor so even huge underdogs can score
HOST_ADV_DEFAULT = 70.0    # Elo-point venue advantage for host nations
MAX_GOALS_GRID = 12        # truncation for exact W/D/L probability integration


def elo_expectation(dr):
    """Canonical Elo expected score (win=1, draw=0.5) for an Elo gap `dr`."""
    return 1.0 / (1.0 + 10.0 ** (-dr / 400.0))


def lambdas(elo_a, elo_b, mu, sup_scale, host_a=0.0, host_b=0.0):
    """Expected goals (lambda_A, lambda_B) for A vs B."""
    dr = (elo_a + host_a) - (elo_b + host_b)
    sup = sup_scale * dr
    la = max(mu / 2.0 + sup / 2.0, MIN_LAMBDA)
    lb = max(mu / 2.0 - sup / 2.0, MIN_LAMBDA)
    return la, lb


def _poisson_pmf(lam, max_goals):
    """P(X=k) for k=0..max_goals, X ~ Poisson(lam). No scipy dependency."""
    ks = np.arange(max_goals + 1)
    fact = np.array([math.factorial(int(k)) for k in ks], dtype=float)
    return np.exp(-lam) * lam ** ks / fact


def implied_wdl(la, lb, max_goals=MAX_GOALS_GRID):
    """Exact P(win), P(draw), P(loss) for team A under independent Poisson."""
    pa = _poisson_pmf(la, max_goals)
    pb = _poisson_pmf(lb, max_goals)
    joint = np.outer(pa, pb)            # joint[i, j] = P(A=i, B=j)
    p_draw = np.trace(joint)
    p_win = np.tril(joint, -1).sum()    # i > j
    p_loss = np.triu(joint, 1).sum()    # i < j
    # fold truncation mass (tiny) into the nearest sensible bucket
    total = p_win + p_draw + p_loss
    return p_win / total, p_draw / total, p_loss / total


def implied_score_expectation(la, lb):
    """Model-implied expected score (win=1, draw=0.5) for team A."""
    p_win, p_draw, _ = implied_wdl(la, lb)
    return p_win + 0.5 * p_draw


def calibrate_sup_scale(mu=MU_DEFAULT, dr_grid=None, scan=None):
    """Pick SUP_SCALE so the Poisson model's implied win expectancy best matches
    the Elo formula across a grid of Elo gaps. Returns (best_scale, rmse)."""
    if dr_grid is None:
        # realistic span of Elo gaps seen between national teams
        dr_grid = np.arange(0, 701, 25)
    if scan is None:
        scan = np.arange(0.0030, 0.0091, 0.0001)
    target = np.array([elo_expectation(dr) for dr in dr_grid])
    best_scale, best_err = None, np.inf
    for s in scan:
        implied = []
        for dr in dr_grid:
            la, lb = lambdas(1700 + dr, 1700, mu, s)  # absolute Elo irrelevant; gap matters
            implied.append(implied_score_expectation(la, lb))
        err = float(np.sqrt(np.mean((np.array(implied) - target) ** 2)))
        if err < best_err:
            best_err, best_scale = err, float(s)
    return best_scale, best_err


def calibration_report(mu, sup_scale, drs=(0, 50, 100, 200, 300, 500)):
    """Human-readable check: Elo expectancy vs model-implied W/D/L per Elo gap."""
    rows = []
    for dr in drs:
        la, lb = lambdas(1700 + dr, 1700, mu, sup_scale)
        pw, pd, pl = implied_wdl(la, lb)
        rows.append((dr, elo_expectation(dr), pw, pd, pl, la, lb))
    return rows
