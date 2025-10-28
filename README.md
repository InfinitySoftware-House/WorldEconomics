# World Economics Simulator

A sophisticated macroeconomic simulation tool that models the interactions between multiple countries over time, including trade, fiscal policy, monetary policy, political cycles, and global economic shocks.

## Overview

This simulator models a multi-country world economy with realistic economic dynamics including:

- **Macroeconomic indicators**: GDP growth, inflation, unemployment
- **Fiscal policy**: Government spending, taxation, debt dynamics
- **Monetary policy**: Interest rates following Taylor rule
- **International trade**: Gravity model with commodity advantages
- **Global cycles**: Global business cycles, commodity cycles, financial cycles
- **Political dynamics**: Elections, policy shifts, regime changes
- **Demographics**: Population growth with income-dependent dynamics

## Requirements

Install the required Python packages:

```bash
pip install matplotlib numpy
```

Or use the project's requirements file:

```bash
pip install -r ../../requirements.txt
```

## Usage

### Basic Command

```bash
python world_economics.py --seed <seed_file.json> --years <num_years> --out <output_dir>
```

### Command-Line Arguments

- `--seed` (required): Path to the seed JSON file containing initial country data
- `--years` (optional, default: 30): Number of years to simulate
- `--out` (optional, default: "out2"): Output directory for results
- `--randseed` (optional, default: 123): Random seed for reproducibility
- `--runs` (optional, default: 1): Number of simulation runs to perform

### Examples

**Single simulation run:**
```bash
python world_economics.py --seed world_seed.json --years 50 --out results
```

**Multiple runs with different random seeds:**
```bash
python world_economics.py --seed world_seed.json --years 30 --out multi_run --runs 10
```

**Reproducible simulation:**
```bash
python world_economics.py --seed world_seed.json --years 40 --randseed 42
```

## Input Format

The seed file must be a JSON file with the following structure:

```json
{
  "countries": [
    {
      "name": "CountryA",
      "region": "Europe",
      "is_democracy": true,
      "gdp": 2000.0,
      "population": 60.0,
      "capital": 1800.0,
      "tfp": 1.0,
      "inflation": 0.02,
      "unemployment": 0.055,
      "debt_to_gdp": 0.60,
      "interest_rate": 0.02,
      "tax_rate": 0.25,
      "gov_spend_share": 0.22,
      "stability": 0.85,
    }
  ],
  "distances": {
    "CountryA|CountryB": 5000.0,
    "CountryA|CountryC": 8000.0
  }
}
```

### Country Parameters

- `name`: Country identifier (string)
- `region`: Geographic region - "Europe", "Americas", "Asia", "Africa", or "Oceania"
- `is_democracy`: Boolean indicating if country has democratic elections
- `gdp`: Initial GDP in billions (float)
- `population`: Population in millions (float)
- `capital`: Initial capital stock in billions (float)
- `tfp`: Total Factor Productivity, baseline is 1.0 (float)
- `inflation`: Initial inflation rate as decimal (e.g., 0.02 = 2%)
- `unemployment`: Initial unemployment rate as decimal (e.g., 0.055 = 5.5%)
- `debt_to_gdp`: Government debt as ratio of GDP (e.g., 0.60 = 60%)
- `interest_rate`: Policy interest rate as decimal (e.g., 0.02 = 2%)
- `tax_rate`: Tax revenue as share of GDP (e.g., 0.25 = 25%)
- `gov_spend_share`: Government spending as share of GDP (e.g., 0.22 = 22%)
- `stability`: Political/economic stability index from 0.0 to 1.0

### Distance Data

The `distances` dictionary defines bilateral distances between countries in kilometers. Format: `"Country1|Country2": distance`. If not specified, default regional distances are used.

## Output Files

For each simulation run, three files are generated:

### 1. `world_timeseries.csv`

Comma-separated values file with annual data for all countries:

- `year`: Simulation year
- `country`: Country name
- `gdp`: GDP in billions
- `pop_m`: Population in millions
- `infl`: Inflation rate (decimal)
- `unemp`: Unemployment rate (decimal)
- `debt_gdp`: Debt-to-GDP ratio (decimal)
- `r_policy`: Policy interest rate (decimal)
- `tax`: Tax rate (decimal)
- `g_spend`: Government spending share (decimal)
- `stability`: Stability index (0-1)
- `ca`: Current account balance in billions

### 2. `world_timeseries.json`

JSON format of the same time series data, useful for programmatic analysis.

### 3. `world_overview.png`

Multi-panel visualization showing time series for all countries:

- GDP (billions)
- Inflation (%)
- Unemployment (%)
- Debt/GDP (%)
- Policy Rate (%)
- Stability index
- Current Account (billions)

## Model Features

### Economic Dynamics

- **Potential growth**: Based on TFP, convergence effects, demographics, and debt
- **Business cycles**: Country-specific and global cycles with AR(1) processes
- **Trade**: Gravity model with commodity comparative advantages
- **Inflation**: Phillips curve with commodity pass-through
- **Unemployment**: Okun's law with mean reversion

### Policy Rules

- **Monetary policy**: Inertial Taylor rule responding to inflation and unemployment
- **Fiscal policy**: Counter-cyclical with debt sustainability targets
- **Automatic stabilizers**: Built into fiscal response

### Political Economy

- **Democracies**: Elections every 4 years with upset probability based on economic performance
- **Non-democracies**: Potential regime changes when stability is very low

### Shocks and Cycles

- **Global business cycle**: Affects all countries' demand
- **Commodity cycle**: Impacts inflation through pass-through effects
- **Financial cycle**: Affects credit conditions and investment
- **Country-specific shocks**: Occasional recession triggers

## Calibration

Key parameters (defined at top of script):

- Target inflation: 2%
- Natural unemployment: 5.5%
- Capital share of output: 33%
- Election cycle: 4 years
- Base interest rate: 1%
- Base tax rate: 20%
- Base government spending: 20%

These can be modified in the script for alternative scenarios.

## Tips for Use

1. **Start simple**: Begin with 2-3 countries to understand the dynamics
2. **Multiple runs**: Use `--runs` to explore stochastic variation
3. **Seed variation**: Different `--randseed` values produce different shock sequences
4. **Long horizons**: Run 50+ years to see long-term debt dynamics
5. **Balanced trade**: The model ensures global current accounts sum to zero

## Example Workflow

```bash
# Create a seed file with your countries
cat > my_world.json << EOF
{
  "countries": [
    {
      "name": "Richland",
      "region": "Europe",
      "is_democracy": true,
      "gdp": 3000.0,
      "population": 80.0,
      "capital": 2800.0,
      "tfp": 1.05,
      "inflation": 0.02,
      "unemployment": 0.05,
      "debt_to_gdp": 0.40,
      "interest_rate": 0.02,
      "tax_rate": 0.28,
      "gov_spend_share": 0.26,
      "stability": 0.9,
      "commodity_endowment": {"oil": -0.3, "metal": 0.1, "agri": 0.0}
    },
    {
      "name": "Emerging",
      "region": "Asia",
      "is_democracy": false,
      "gdp": 1500.0,
      "population": 120.0,
      "capital": 1200.0,
      "tfp": 0.95,
      "inflation": 0.04,
      "unemployment": 0.08,
      "debt_to_gdp": 0.55,
      "interest_rate": 0.05,
      "tax_rate": 0.20,
      "gov_spend_share": 0.18,
      "stability": 0.6,
      "commodity_endowment": {"oil": 0.0, "metal": 0.4, "agri": 0.2}
    }
  ],
  "distances": {
    "Richland|Emerging": 8000.0
  }
}
EOF

# Run simulation
python world_economics.py --seed my_world.json --years 40 --out my_results

# View results
open my_results/world_overview.png
```

## Troubleshooting

- **Import errors**: Ensure matplotlib is installed with `pip install matplotlib`
- **File not found**: Check that the seed file path is correct
- **Strange results**: Verify that initial values in seed file are reasonable (see ranges in code)
- **Blank plots**: May indicate data range issues; check CSV output first

## License

Part of the StartUpBusiness project.

