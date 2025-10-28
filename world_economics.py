#!/usr/bin/env python3
import matplotlib.pyplot as plt
import argparse
import json
import math
import random
import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple
import matplotlib
matplotlib.use("Agg")

# ------------- Calibration -------------
TARGET_INFL = 0.02
NATURAL_UNEMP = 0.055
ALPHA_CAPITAL = 0.33

# Cycles
RHO_GLOBAL = 0.75
RHO_COMMOD = 0.7
RHO_FIN = 0.6
RHO_COUNTRY = 0.6

# Bounds
MIN_UNEMP, MAX_UNEMP = 0.03, 0.22
MIN_INFL,  MAX_INFL = -0.01, 0.10
MAX_GROWTH = 0.06
MIN_GROWTH = -0.05

# Trade
GRAVITY_K = 3e-7
TRADE_ELASTICITY = 0.25
DISTANCE_DECAY = 1.0

# Policy
ELECTION_CYCLE_YEARS = 4
BASE_R = 0.01
DEBT_RISK_SLOPE = 0.012
POLICY_INERTIA = 0.7
TAYLOR_PI = 1.1
TAYLOR_U = 0.35

# Fiscal rule
BASE_TAX = 0.20
BASE_G = 0.20
DEBT_PB_SLOPE = 0.02     # pb target rises 2pp per 10pp debt over 80%
DEFICIT_FLOOR = -0.06


def clamp(x, lo, hi): return max(lo, min(hi, x))


def dist_region(a: str, b: str) -> float:
    if a == b:
        return 1000.0
    pairs = {
        ("Europe", "Americas"): 7000, ("Europe", "Asia"): 6000, ("Europe", "Africa"): 3000, ("Europe", "Oceania"): 16000,
        ("Americas", "Asia"): 10000, ("Americas", "Africa"): 8000, ("Americas", "Oceania"): 12000,
        ("Asia", "Africa"): 6000, ("Asia", "Oceania"): 7000, ("Africa", "Oceania"): 11000
    }
    return pairs.get((a, b), pairs.get((b, a), 9000))


@dataclass
class Country:
    name: str
    region: str
    is_democracy: bool
    gdp: float
    population: float
    capital: float
    tfp: float
    inflation: float
    unemployment: float
    debt_to_gdp: float
    interest_rate: float
    tax_rate: float
    gov_spend_share: float
    stability: float
    party_leaning: float = 0.0
    years_to_election: int = ELECTION_CYCLE_YEARS
    ca: float = 0.0
    last_gdp: float = None
    cyc_state: float = 0.0  # country cycle

    def potential_growth(self, gdp_per_capita: float) -> float:
        # Base 1.3% + TFP mean reversion + demographic slowdown by income + debt drag
        # Beta-convergence: poorer countries grow a bit faster
        # ~0.4% extra when poor
        base = 0.013 + 0.004 * (1.0 / (1.0 + gdp_per_capita/50.0))
        tfp_term = (self.tfp - 1.0) * 0.25
        # richer -> slower pop effect
        demo_drag = -0.003 * (gdp_per_capita / 100.0)
        debt_drag = -0.01 * max(0.0, self.debt_to_gdp - 0.9)
        return clamp(base + tfp_term + demo_drag + debt_drag, -0.01, 0.03)


class World:
    def __init__(self, countries: List[Country], distances: Dict[Tuple[str, str], float], rnd: random.Random):
        self.c = {x.name: x for x in countries}
        self.distances = distances
        self.rnd = rnd
        # Global cycles
        self.g_cycle = 0.0
        self.comm_cycle = 0.0
        self.fin_cycle = 0.0

    def distance(self, a: Country, b: Country) -> float:
        key = (a.name, b.name)
        if key in self.distances:
            return self.distances[key]
        key = (b.name, a.name)
        if key in self.distances:
            return self.distances[key]
        return dist_region(a.region, b.region)

    def step(self, year: int):
        # Update global cycles (AR(1))
        self.g_cycle = RHO_GLOBAL*self.g_cycle + self.rnd.uniform(-0.01, 0.01)
        self.comm_cycle = RHO_COMMOD*self.comm_cycle + \
            self.rnd.uniform(-0.02, 0.02)
        self.fin_cycle = RHO_FIN*self.fin_cycle + \
            self.rnd.uniform(-0.015, 0.015)

        # Policies
        for c in self.c.values():
            self._policy(c)

        # Trade and CA (balanced)
        self._trade_and_balance_CA()

        # Macro
        for c in self.c.values():
            self._macro(c)

        # Fiscal & debt
        for c in self.c.values():
            self._fiscal(c)

        # Domestic politics
        for c in self.c.values():
            self._politics(c)

    # -------- Policies --------
    def _policy(self, c: Country):
        # Monetary policy: inertial Taylor with neutral rate ~ inflation target + 0.5% - risk
        pi_gap = c.inflation - TARGET_INFL
        u_gap = c.unemployment - NATURAL_UNEMP
        neutral = TARGET_INFL + 0.005
        desired = clamp(neutral + TAYLOR_PI*pi_gap - TAYLOR_U *
                        u_gap - 0.5*(1.0-c.stability), 0.0, 0.12)
        c.interest_rate = clamp(
            POLICY_INERTIA*c.interest_rate + (1-POLICY_INERTIA)*desired, 0.0, 0.15)

        # Fiscal: set a primary balance target that reacts to debt>80% GDP
        # e.g., 2% surplus per +10pp of debt
        pb_target = 0.0 + DEBT_PB_SLOPE * max(0.0, (c.debt_to_gdp - 0.8))
        # Convert pb_target into spend share (given a current tax rate), with guardrails
        c.tax_rate = clamp(c.tax_rate, 0.15, 0.35)
        spend = c.tax_rate - pb_target
        c.gov_spend_share = clamp(spend, 0.14, 0.27)

        # TFP mean reversion + occasional positive shock
        reversion = 1.0 + (c.tfp - 1.0)*0.9
        if self.rnd.random() < 0.08 + 0.04*c.stability:
            c.tfp = reversion * (1.0 + self.rnd.uniform(0.0, 0.005))
        else:
            c.tfp = reversion

    # -------- Trade & CA --------
    def _trade_and_balance_CA(self):
        names = list(self.c.keys())
        exports = {n: 0.0 for n in names}
        imports = {n: 0.0 for n in names}
        for i in range(len(names)):
            for j in range(len(names)):
                if i == j:
                    continue
                a, b = self.c[names[i]], self.c[names[j]]
                dist = self.distance(a, b)
                base = GRAVITY_K * (a.gdp * b.gdp) / (dist ** DISTANCE_DECAY)
                flow = base
                exports[a.name] += flow
                imports[b.name] += flow

        # raw CA
        total_CA = 0.0
        for n in names:
            self.c[n].ca = exports[n] - imports[n]
            total_CA += self.c[n].ca

        # Balance to ~0 by scaling surpluses/deficits
        if abs(total_CA) > 1e-6:
            adjust = total_CA / len(names)
            for n in names:
                self.c[n].ca -= adjust  # simple uniform offset to make sum ~ 0

    # -------- Macro --------
    def _macro(self, c: Country):
        # Country cycle AR(1) with rare recession push
        if self.rnd.random() < 0.08:
            c.cyc_state += self.rnd.uniform(-0.03, -0.01)
        c.cyc_state = RHO_COUNTRY*c.cyc_state + self.rnd.uniform(-0.005, 0.005)

        gdp_pc = c.gdp / max(1.0, c.population)
        pot = c.potential_growth(gdp_pc)
        demand = 0.5*(c.gov_spend_share - BASE_G) - 0.2 * \
            (c.interest_rate - TARGET_INFL) + 0.001*(c.ca/max(1.0, c.gdp))
        # Global + country cycles affect demand
        demand += 0.6*self.g_cycle + 0.7*c.cyc_state

        # Credit channel: financial stress hurts growth more for high-debt countries
        spread = DEBT_RISK_SLOPE * \
            max(0.0, c.debt_to_gdp - 0.6) + 0.02*(1.0 - c.stability)
        credit_drag = -0.4*self.fin_cycle * clamp(c.debt_to_gdp, 0, 1.5)

        growth = clamp(pot + demand + credit_drag, MIN_GROWTH, MAX_GROWTH)
        c.last_gdp = c.gdp
        c.gdp *= (1.0 + growth)

        # Capital accumulation with debt/risk sensitivity
        invest = clamp(0.17 - 0.4*max(0.0, c.interest_rate-0.03) -
                       0.05*spread + 0.04*c.stability, 0.06, 0.25)
        c.capital = (1-0.05)*c.capital + invest*c.gdp

        # Inflation
        phil = 0.18*(NATURAL_UNEMP - c.unemployment) + 0.12 * \
            demand + 0.08*self.fin_cycle
        c.inflation = clamp(0.6*c.inflation + 0.4 *
                            (TARGET_INFL + phil), MIN_INFL, MAX_INFL)

        # Unemployment (Okun) with mean reversion
        gap = growth - pot
        c.unemployment = clamp(0.9*c.unemployment - 0.35 *
                               gap + 0.1*NATURAL_UNEMP, MIN_UNEMP, MAX_UNEMP)

        # Stability
        c.stability = clamp(c.stability - 0.2*max(0.0, c.inflation-0.05) - 0.2*max(0.0, c.unemployment -
                            NATURAL_UNEMP) + 0.1*max(0.0, growth) + (0.02 if c.ca > 0 else -0.01), 0.0, 1.0)

        # Demography: slows as income rises; disasters not modeled explicitly but captured by cycles
        pop_g = clamp(0.007 - 0.005*(gdp_pc/80.0) -
                      0.004*self.fin_cycle, -0.005, 0.012)
        c.population = max(1.0, c.population*(1.0 + pop_g))

    # -------- Fiscal & debt --------
    def _fiscal(self, c: Country):
        revenue = c.tax_rate * c.gdp
        spend = c.gov_spend_share * c.gdp
        pb = revenue - spend
        pb_share = pb / max(1.0, c.gdp)

        # Effective interest rate on debt
        spread = DEBT_RISK_SLOPE * \
            max(0.0, c.debt_to_gdp - 0.6) + 0.02*(1.0 - c.stability)
        r_eff = BASE_R + spread

        # Nominal growth
        if c.last_gdp:
            g = (c.gdp - c.last_gdp)/max(1e-6, c.last_gdp)
        else:
            g = c.inflation + 0.01
        c.debt_to_gdp = max(
            0.0, ((1+r_eff)*c.debt_to_gdp - pb_share) / max(1e-3, (1+g)))

    # -------- Politics --------
    def _politics(self, c: Country):
        if c.is_democracy:
            c.years_to_election -= 1
            if c.years_to_election <= 0:
                upset = 0.22 + 1.0 * \
                    max(0.0, c.inflation - TARGET_INFL) + 1.4 * \
                    max(0.0, c.unemployment - NATURAL_UNEMP)
                if self.rnd.random() < min(0.6, upset):
                    c.party_leaning = self.rnd.uniform(-1.0, 1.0)
                c.years_to_election = ELECTION_CYCLE_YEARS
        else:
            if c.stability < 0.25 and self.rnd.random() < 0.12:
                if self.rnd.random() < 0.08:
                    c.is_democracy = True
                    c.years_to_election = ELECTION_CYCLE_YEARS
                c.stability = min(1.0, c.stability + 0.2)


def load_seed(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    countries = [Country(**row) for row in data["countries"]]
    distances = {}
    for k, v in data.get("distances", {}).items():
        a, b = k.split("|")
        distances[(a, b)] = float(v)
    return countries, distances


def write_csv(rows: List[dict], path: str):
    if not rows:
        return
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def plot_multi(timeseries: List[dict], out_png: str):
    # group
    byc = {}
    for r in timeseries:
        d = byc.setdefault(r["country"], {"year": [], "gdp": [], "infl": [], "unemp": [
        ], "debt_gdp": [], "r_policy": [], "stability": [], "ca": []})
        for k in d.keys():
            pass
        d["year"].append(r["year"])
        d["gdp"].append(r["gdp"])
        d["infl"].append(r["infl"]*100.0)
        d["unemp"].append(r["unemp"]*100.0)
        d["debt_gdp"].append(r["debt_gdp"]*100.0)
        d["r_policy"].append(r["r_policy"]*100.0)
        d["stability"].append(r["stability"])
        d["ca"].append(r["ca"])
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 4, figsize=(18, 8))
    axes = axes.flatten()
    metrics = [
        ("gdp", "GDP (bln)", "GDP"),
        ("infl", "Inflation (%)", "Inflation"),
        ("unemp", "Unemployment (%)", "Unemployment"),
        ("debt_gdp", "Debt/GDP (%)", "Debt/GDP"),
        ("r_policy", "Policy Rate (%)", "Policy Rate"),
        ("stability", "Stability", "Stability"),
        ("ca", "Current Account (bln)", "Current Account"),
    ]
    handles, labels = [], []
    for ax, (k, ylabel, title) in zip(axes, metrics):
        for name, series in byc.items():
            line = ax.plot(series["year"], series[k], label=name)
            if len(handles) == 0 or name not in labels:
                handles.append(line[0])
                labels.append(name)
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.2)
    # hide any unused panel
    if len(axes) > len(metrics):
        for ax in axes[len(metrics):]:
            ax.axis("off")
    fig.tight_layout()
    # Add single legend at bottom right
    fig.legend(handles, labels, loc='lower right', fontsize=9, framealpha=0.9)
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def main():
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True)
    ap.add_argument("--years", type=int, default=30)
    ap.add_argument("--out", default="out2")
    ap.add_argument("--randseed", type=int, default=123)
    ap.add_argument("--runs", type=int, default=1,
                    help="Number of simulation runs")
    args = ap.parse_args()

    for run_idx in range(1, args.runs + 1):
        # Use different random seed for each run
        run_seed = args.randseed + (run_idx - 1) * 1000
        rnd = random.Random(run_seed)
        countries, distances = load_seed(args.seed)
        world = World(countries, distances, rnd)

        # Create numbered output directory
        if args.runs > 1:
            run_out = os.path.join(args.out, f"run_{run_idx}")
        else:
            run_out = args.out

        os.makedirs(run_out, exist_ok=True)
        rows = []
        for y in range(1, args.years+1):
            world.step(y)
            for c in world.c.values():
                rows.append({
                    "year": y,
                    "country": c.name,
                    "gdp": round(c.gdp, 2),
                    "pop_m": round(c.population, 2),
                    "infl": round(c.inflation, 4),
                    "unemp": round(c.unemployment, 4),
                    "debt_gdp": round(c.debt_to_gdp, 4),
                    "r_policy": round(c.interest_rate, 4),
                    "tax": round(c.tax_rate, 4),
                    "g_spend": round(c.gov_spend_share, 4),
                    "stability": round(c.stability, 4),
                    "ca": round(c.ca, 2),
                })

        csv_path = os.path.join(run_out, "world_timeseries.csv")
        json_path = os.path.join(run_out, "world_timeseries.json")
        write_csv(rows, csv_path)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

        png_path = os.path.join(run_out, "world_overview.png")
        plot_multi(rows, png_path)

        print(f"Run {run_idx}/{args.runs} - Saved:", csv_path)
        print(f"Run {run_idx}/{args.runs} - Saved:", json_path)
        print(f"Run {run_idx}/{args.runs} - Saved:", png_path)


if __name__ == "__main__":
    main()
