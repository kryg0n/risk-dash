
## Comprehensive Project Pipeline: Simplified Portfolio Risk Management System

### Ready-to-Execute Version with All Data Sources


***

## Project Overview

**Title**: Quantitative Portfolio Risk Analysis: Measurement, Understanding, and Communication Framework

**Core Question**: How can risk be measured, understood, and communicated clearly to support better investment decisions?

**Expected Timeline**: 4-6 weeks for complete implementation and validation

**Key Parameters (Fixed)**:

- Portfolio universe: 300 stocks from S\&P 500
- Historical data period: January 1, 2020 - January 18, 2026 (6+ years)
- EWMA decay factor (λ): 0.94[^1][^2]
- Covariance estimation window: 252 trading days (1 year)[^3][^4]
- Risk-free rate: 3-month US Treasury yield[^5][^6]
- Rebalancing frequency: Quarterly[^7]

***

## Stage 0: Data Acquisition and Preparation

### Objectives

- Download clean historical price data for 300 S\&P 500 stocks
- Obtain risk-free rate data from FRED
- Verify data quality and create analysis-ready dataset


### Data Source 1: S\&P 500 Stock Prices via yfinance

**Stock Universe Selection Method**:

Use Wikipedia's S\&P 500 constituents table to get the current list. The table is located at:[^8]

- URL: `https://en.wikipedia.org/wiki/List_of_S%26P_500_companies`
- Parse the first HTML table containing columns: `Symbol`, `Security`, `GICS Sector`, etc.

**Top 300 Stocks by Market Cap (as of Jan 2026)** - Use these tickers directly:

**Tier 1 - Mega Cap (Top 50)**: AAPL, MSFT, GOOGL, AMZN, NVDA, META, BRK.B, TSLA, LLY, V, UNH, XOM, JPM, MA, AVGO, JNJ, WMT, PG, COST, HD, ABBV, CVX, MRK, KO, NFLX, BAC, ORCL, PEP, AMD, ADBE, CRM, TMO, CSCO, MCD, ABT, INTC, ACN, DHR, NKE, TXN, CMCSA, WFC, BMY, HON, NEE, UNP, VZ, RTX, QCOM, LIN, T

**Tier 2 - Large Cap (51-150)**: AMGN, PM, LOW, UPS, COP, INTU, PFE, SPGI, MDT, DE, C, IBM, BLK, GE, AMAT, ADI, AXP, SBUX, PLD, ISRG, CAT, GILD, MMC, TJX, BKNG, SO, CB, CVS, SYK, SCHW, ADP, AMT, CI, ZTS, MS, GS, NOW, VRTX, BA, MO, REGN, DUK, BDX, CL, EQIX, PNC, ITW, APD, ICE, EOG

**Tier 3 - Large Cap (151-250)**: USB, SLB, HUM, CME, MU, NSC, AON, TGT, LRCX, ETN, MCO, WM, PSA, CCI, MMM, BSX, KLAC, SHW, FCX, APH, ORLY, D, ADM, ROP, EW, ECL, AJG, MSI, DG, MSCI, PCAR, F, TRV, NXPI, GM, KMB, SRE, AEP, EL, APO, WELL, PAYX, MNST, FIS, SPG, AIG, AFL, A, CDNS, TEL

**Tier 4 - Large Cap (251-300)**: KDP, CTAS, KMI, GIS, CMG, HLT, STZ, NEM, WMB, BK, CARR, O, PSX, YUM, MCHP, EXC, MAR, CPRT, ADSK, AZO, TDG, DD, HSY, ROST, ALL, ODFL, CTVA, IDXX, DVN, LHX, PRU, AMP, PEG, AME, CTSH, OTIS, DLR, IQV, EA, RSG, RMD, ED, FAST, MLM, HCA, GWW, KHC, BKR, CNC, SNPS

**yfinance Download Parameters**:

```python
import yfinance as yf
tickers = [list above as array]
data = yf.download(
    tickers,
    start='2020-01-01',
    end='2026-01-19',  # Day after current date
    auto_adjust=True,  # Handles splits/dividends automatically
    threads=True       # Parallel download
)['Adj Close']
```


### Data Source 2: Risk-Free Rate via FRED API

**FRED API Setup**:

- **Series Code**: `DGS3MO` (3-Month Treasury Constant Maturity Rate, daily)[^6][^5]
- **API Endpoint**: `https://api.stlouisfed.org/fred/series/observations`
- **Parameters**:
    - `series_id=DGS3MO`
    - `api_key=YOUR_FRED_API_KEY`
    - `file_type=json`
    - `observation_start=2020-01-01`
    - `observation_end=2026-01-18`

**Python Code Structure**:

```python
import requests
import pandas as pd

url = 'https://api.stlouisfed.org/fred/series/observations'
params = {
    'series_id': 'DGS3MO',
    'api_key': 'YOUR_API_KEY_HERE',  # User will insert their key
    'file_type': 'json',
    'observation_start': '2020-01-01',
    'observation_end': '2026-01-18'
}
response = requests.get(url, params=params)
rf_data = pd.DataFrame(response.json()['observations'])
rf_data['value'] = pd.to_numeric(rf_data['value'], errors='coerce')
rf_data['date'] = pd.to_datetime(rf_data['date'])
```

**Note**: As of Jan 15, 2026, the 3-month Treasury rate is 3.68%[^5]

### Data Validation Rules

**Stock Data Quality Checks**:

1. **Missing data threshold**: Remove stocks with >5% missing values (>75 missing days out of 1,500)
2. **Outlier detection**: Flag daily returns >50% or <-50% as potential data errors
3. **Minimum history**: Require at least 1,200 trading days (5 years) of data
4. **Duplicate check**: Verify no duplicate timestamps

**Data Preprocessing Steps**:

**Step 1: Calculate log returns**

```
r_t = ln(P_t / P_{t-1})
```

where P_t is adjusted close price on day t

**Step 2: Handle missing values**

- Forward-fill gaps ≤5 consecutive days
- Remove stocks exceeding 5% total missing data
- Align all series to common trading days (intersection)

**Step 3: Winsorize extreme outliers** (optional robustness enhancement)

- Cap returns at 1st and 99th percentiles per stock
- Only if verification shows legitimate extreme moves (e.g., news events)

**Step 4: Export clean dataset**

- Save to: `data/clean_returns.csv` (date index, stock tickers as columns)
- Save metadata: `data/data_quality_report.txt` (stocks removed, missing data summary)


### Expected Data Dimensions

After cleaning, expect approximately:

- **Stocks**: 280-295 (some may be removed due to data issues or recent IPOs)
- **Trading days**: ~1,500 (6 years × 252 trading days)
- **Return matrix shape**: 1,500 rows × ~290 columns


### Validation Outputs

**Table 0.1: Data Quality Summary**


| Metric | Target | Actual |
| :-- | :-- | :-- |
| Total stocks downloaded | 300 | [Calculate] |
| Stocks passing quality checks | ≥280 | [Calculate] |
| Trading days available | ~1,500 | [Calculate] |
| Overall missing data % | <1% | [Calculate] |
| Average daily return (%) | ~0.05 | [Calculate] |
| Average daily volatility (%) | ~1.5 | [Calculate] |

**Generate diagnostic plots**:

1. Heatmap of missing data (stocks × time)
2. Distribution of daily returns (histogram, all stocks aggregated)
3. Time series of equal-weighted portfolio cumulative returns (baseline)

***

## Stage 1: Minimum Variance Portfolio Optimization

### Objectives

- Construct portfolio weights minimizing total variance
- Benchmark against equal-weighted (1/N) portfolio
- Quantify diversification benefits


### Mathematical Foundation

**Optimization Problem**:[^9][^3]

$$
\min_{w} \quad \sigma_p^2 = w^T \Sigma w
$$

$$
\text{subject to:} \quad \sum_{i=1}^{N} w_i = 1, \quad w_i \geq 0 \quad \forall i
$$

where:

- $w$ = vector of portfolio weights (N × 1)
- $\Sigma$ = covariance matrix of returns (N × N)
- $\sigma_p^2$ = portfolio variance

**Analytical Note**: This has closed-form solution for unconstrained case: $w = \frac{\Sigma^{-1} \mathbf{1}}{\mathbf{1}^T \Sigma^{-1} \mathbf{1}}$, but numerical optimization handles constraints better[^9]

### Implementation Specification

**Step 1: Covariance Matrix Estimation**

**Window**: Last 252 trading days (1 year) of returns[^4][^3]
**Formula**:

$$
\Sigma_{ij} = \frac{1}{T-1} \sum_{t=1}^{T} (r_{i,t} - \bar{r}_i)(r_{j,t} - \bar{r}_j)
$$

where T = 252, r_{i,t} = return of stock i on day t

**Numerical Stability**: Check condition number $\kappa(\Sigma) = \lambda_{max}/\lambda_{min}$. If κ > 100, apply regularization (add small constant to diagonal: $\Sigma' = \Sigma + 0.0001 \times I$)[^3]

**Step 2: Optimization**

**Solver**: SciPy's `minimize` with SLSQP (Sequential Least Squares Programming) method
**Objective function**: `lambda w: w.T @ cov_matrix @ w`
**Constraints**:

- Equality: `{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}`
- Bounds: `[(0, 0.05) for i in range(N)]` (0% to 5% per stock to prevent concentration)

**Initial guess**: Equal weights `w_0 = [1/N, 1/N, ..., 1/N]`
**Tolerance**: `tol=1e-8`
**Maximum iterations**: 1000

**Convergence check**: Verify optimizer returns `success=True` and final constraint violation < 1e-6

**Step 3: Portfolio Metrics Calculation**

**Portfolio volatility** (annualized):

$$
\sigma_p = \sqrt{w^T \Sigma w} \times \sqrt{252}
$$

**Diversification ratio**:[^7]

$$
DR = \frac{\sum_{i=1}^{N} w_i \sigma_i}{\sigma_p}
$$

where $\sigma_i = \sqrt{\Sigma_{ii}} \times \sqrt{252}$ is stock i's annualized volatility

**Effective number of stocks** (inverse Herfindahl index):

$$
N_{eff} = \frac{1}{\sum_{i=1}^{N} w_i^2}
$$

**Step 4: Equal-Weighted Benchmark**

Calculate same metrics for $w_{EW} = [1/N, 1/N, ..., 1/N]$:

- $\sigma_{EW} = \sqrt{w_{EW}^T \Sigma w_{EW}} \times \sqrt{252}$
- Volatility reduction: $\Delta\sigma = (\sigma_{EW} - \sigma_{MV}) / \sigma_{EW} \times 100\%$

**Expected outcome**: 20-40% volatility reduction[^10][^11]

### Outputs and Validation

**Table 1.1: Portfolio Optimization Results**


| Metric | Minimum Variance | Equal-Weighted | Difference | Expected Range |
| :-- | :-- | :-- | :-- | :-- |
| Annualized Volatility (%) | [Calc] | [Calc] | [Calc] | MV: 12-18% |
| Diversification Ratio | [Calc] | [Calc] | [Calc] | MV: 1.3-1.8 |
| Effective N Stocks | [Calc] | 290 | [Calc] | MV: 80-150 |
| Largest Position (%) | [Calc] | 0.34 | [Calc] | MV: <5% |
| Top 10 Weight (%) | [Calc] | 3.4 | [Calc] | MV: 15-30% |
| Volatility Reduction (%) | - | - | [Calc] | 20-40% [^11] |

**Table 1.2: Top 30 Holdings (Minimum Variance Portfolio)**


| Rank | Ticker | Company | Weight (%) | Annual Vol (%) | Sector |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | [Calc] | [Lookup] | [Calc] | [Calc] | [Lookup] |
| 2 | [Calc] | [Lookup] | [Calc] | [Calc] | [Lookup] |
| ... | ... | ... | ... | ... | ... |
| 30 | [Calc] | [Lookup] | [Calc] | [Calc] | [Lookup] |

**Sector lookup table** (from S\&P 500 data ):[^8]

- Information Technology, Health Care, Financials, Consumer Discretionary, Communication Services, Industrials, Consumer Staples, Energy, Utilities, Real Estate, Materials

**Visualization 1.1: Sector Allocation Comparison**

- Pie charts (side-by-side): Minimum Variance vs. Equal-Weighted
- Show % weight in each of 11 GICS sectors

**Visualization 1.2: Weight vs. Volatility Scatter**

- X-axis: Individual stock volatility (annualized %)
- Y-axis: Portfolio weight (%)
- Color: Sector
- Trendline: Should show negative correlation (low-vol stocks get higher weights)


### Quality Assurance Checks

**Validation Checklist**:

1. ✓ Weights sum to 1.000 (tolerance: ±0.0001)
2. ✓ All weights ≥ 0 and ≤ 0.05 (no shorts, position limits respected)
3. ✓ Portfolio volatility < equal-weighted volatility
4. ✓ Correlation between weight and volatility < -0.3 (inverse relationship)
5. ✓ Diversification ratio > 1.0
6. ✓ Condition number of covariance matrix < 1000 (numerical stability)

**Hypothesis Test**:

- **H2**: Minimum variance achieves 20-40% volatility reduction vs. equal-weighted[^11][^10]
- **Test**: Calculate $\Delta\sigma$; should fall in [20%, 40%] range
- **If fails**: Investigate data quality, check if universe already low-correlation

***

## Stage 2: EWMA Volatility Forecasting

### Objectives

- Generate time-varying volatility forecasts for each stock
- Calculate portfolio-level VaR for 1-day and 10-day horizons
- Validate volatility clustering phenomenon


### Mathematical Foundation

**EWMA Recursion Formula**:[^2][^1]

$$
\hat{\sigma}_{t+1}^2 = \lambda \hat{\sigma}_t^2 + (1 - \lambda) r_t^2
$$

**Parameters** (RiskMetrics standard ):[^2]

- $\lambda = 0.94$ for daily returns
- Initialization: $\hat{\sigma}_1^2 = r_1^2$ or sample variance of first 30 days

**Properties**:

- Effective window: $\approx 1/(1-\lambda) = 16.7$ days[^1]
- Weights decay exponentially: $w_k = (1-\lambda)\lambda^k$
- Infinite memory but recent data dominates

**Volatility Clustering**: High volatility tends to persist (autocorrelation in $\sigma_t$)[^12]

### Implementation Specification

**Step 1: Per-Stock EWMA Calculation**

**Pseudocode**:

```
For each stock i:
    Initialize: sigma2[^0] = mean(returns[0:30]**2)
    For t = 1 to T:
        sigma2[t] = lambda * sigma2[t-1] + (1-lambda) * returns[t-1]**2
    sigma[t] = sqrt(sigma2[t])
    Forecast: sigma_forecast = sigma[T]  # 1-day ahead
```

**Annualization**: Multiply by $\sqrt{252}$ for annualized volatility

**Output**: DataFrame with columns = stock tickers, rows = dates, values = daily EWMA volatility

**Step 2: Portfolio Volatility Aggregation**

**Formula**:

$$
\sigma_p^2(t) = w^T \Sigma_{EWMA}(t) w
$$

where $\Sigma_{EWMA}(t)$ is constructed:

- Diagonal: EWMA variances $\hat{\sigma}_{i,t}^2$
- Off-diagonal: $\sigma_{i,t} \times \sigma_{j,t} \times \rho_{ij}$
- $\rho_{ij}$ = correlation from Stage 1 covariance matrix (static assumption )[^1]

**Justification**: Correlations change slower than volatilities; acceptable approximation[^13][^1]

**Step 3: Value-at-Risk Calculation**

**Parametric VaR** (assumes normal distribution):[^14][^13]

$$
VaR_{\alpha, h} = z_{\alpha} \times \sigma_{p,EWMA} \times \sqrt{h}
$$

where:

- $\alpha$ = confidence level (95%, 99%)
- $z_{\alpha}$ = normal quantile: $z_{0.95} = 1.645$, $z_{0.99} = 2.326$[^13]
- $h$ = holding period in days (1 or 10)
- $\sigma_{p,EWMA}$ = portfolio EWMA volatility (daily, not annualized)

**Calculate for current date (Jan 18, 2026)**:

- 1-day 95% VaR
- 1-day 99% VaR
- 10-day 95% VaR (use $\sqrt{10}$ scaling)
- 10-day 99% VaR

**Express as**:

- % of portfolio value
- Dollar amount (assume \$1,000,000 initial portfolio)

**Step 4: Volatility Clustering Validation**

**Autocorrelation Test**:[^12]

- Calculate: $\rho_k = \text{corr}(\sigma_t, \sigma_{t-k})$ for k = 1, 2, ..., 10
- **Expected**: $\rho_1 > 0.3$ indicates strong clustering[^12]
- Use Pandas `autocorr()` function on portfolio EWMA volatility series


### Outputs and Validation

**Table 2.1: Current Volatility Forecast (as of Jan 18, 2026)**


| Metric | 1-Day | 10-Day | Notes |
| :-- | :-- | :-- | :-- |
| Portfolio EWMA Vol (annualized %) | [Calc] | [Calc] | Same vol, different horizon |
| 95% VaR (%) | [Calc] | [Calc] | ~1.645σ vs. ~5.2σ |
| 95% VaR (\$1M portfolio) | [Calc] | [Calc] | Multiply by \$1M |
| 99% VaR (%) | [Calc] | [Calc] | ~2.326σ vs. ~7.36σ |
| 99% VaR (\$1M portfolio) | [Calc] | [Calc] | Multiply by \$1M |

**Table 2.2: Top 10 Stocks by Current EWMA Volatility**


| Rank | Ticker | EWMA Vol (annualized %) | Portfolio Weight (%) | Risk Contribution (%) | Sector |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | [Calc] | [Calc] | [Calc] | [Preview Stage 3] | [Lookup] |
| ... | ... | ... | ... | ... | ... |
| 10 | [Calc] | [Calc] | [Calc] | [Preview Stage 3] | [Lookup] |

**Visualization 2.1: EWMA Volatility Time Series (Last 2 Years)**

- Line 1: Portfolio EWMA volatility (annualized, %)
- Line 2: Realized volatility (20-day rolling std × √252)
- Shaded regions: Annotate major events:
    - Feb-Mar 2022: Ukraine invasion volatility spike
    - Sep-Oct 2022: Peak inflation/rate hike fears
    - Mar 2023: Banking crisis (SVB collapse)
    - Aug 2024: [Any major event]
    - Oct 2025-Jan 2026: Recent period
- **Purpose**: Show EWMA responsiveness vs. realized volatility

**Visualization 2.2: Stock Volatility Distribution (Current)**

- Histogram: Individual stock EWMA volatilities (all 290 stocks)
- Vertical line: Portfolio EWMA volatility
- Annotation: "Diversification benefit: Portfolio vol = X% of average stock vol"

**Visualization 2.3: Autocorrelation Function**

- Bar chart: $\rho_k$ for k = 1 to 10 days
- Horizontal line at $\rho = 0.3$ (clustering threshold)
- Show significance bands (±1.96/√T for 95% CI)


### Quality Assurance Checks

**Validation Checklist**:

1. ✓ All EWMA volatilities > 0 (no numerical errors)
2. ✓ Portfolio EWMA vol < weighted average of individual vols (diversification)
3. ✓ Current portfolio vol within [0.5×, 2.0×] historical average (sensibility)
4. ✓ 10-day VaR ≈ $\sqrt{10}$ × 1-day VaR (scaling property)
5. ✓ $\rho_1 > 0.2$ (volatility clustering present)[^12]
6. ✓ VaR increases with confidence level (99% > 95%)

**Hypothesis Test**:

- **H3**: EWMA volatility exhibits clustering: $\rho_1 > 0.3$[^12]
- **Test**: Calculate autocorrelation of portfolio EWMA series
- **If fails**: Check if current period unusually stable; verify EWMA calculation

**Contextual Interpretation**:
Compare current EWMA volatility to historical percentiles:

```
percentile = (current_vol < historical_vols).mean() * 100
```

- <25th percentile: Low volatility regime
- 25-75th percentile: Normal regime
- >75th percentile: Elevated volatility regime
- >95th percentile: Crisis-like volatility

***

## Stage 3: Risk Decomposition Analysis

### Objectives

- Identify stocks contributing most to total portfolio risk
- Calculate marginal and component contributions
- Quantify concentration and diversification effectiveness


### Mathematical Foundation

**Marginal Contribution to Risk (MCR)**:[^15][^7]

$$
MCR_i = \frac{\partial \sigma_p}{\partial w_i} = \frac{(\Sigma w)_i}{\sigma_p}
$$

This represents: "How much does portfolio volatility change per 1% increase in stock i's weight?"

**Component Contribution to Risk (CCR)**:[^15]

$$
CCR_i = w_i \times MCR_i
$$

**Key Property** (Euler's theorem for homogeneous functions):

$$
\sum_{i=1}^{N} CCR_i = \sigma_p
$$

**Interpretation**:

- $CCR_i$ = portion of total portfolio volatility attributable to stock i
- Express as percentage: $CCR\%_i = (CCR_i / \sigma_p) \times 100\%$


### Implementation Specification

**Step 1: Calculate Marginal Risk**

**Formula implementation**:

```python
# From Stage 1
cov_matrix = ... # 290 × 290
weights = ...    # 290 × 1
sigma_p = np.sqrt(weights.T @ cov_matrix @ weights)

# Marginal contribution
cov_times_w = cov_matrix @ weights  # Matrix-vector product
mcr = cov_times_w / sigma_p

# Component contribution
ccr = weights * mcr  # Element-wise multiplication
ccr_pct = (ccr / sigma_p) * 100

# Validation
assert abs(ccr.sum() - sigma_p) < 1e-6, "CCR must sum to portfolio vol"
```

**Step 2: Diversification Metrics**

**Diversification Ratio**:[^7]

$$
DR = \frac{\sum_{i=1}^{N} w_i \sigma_i}{\sigma_p}
$$

- Numerator: Weighted average of individual volatilities
- Denominator: Portfolio volatility
- Interpretation: DR = 1.5 means portfolio is 50% less volatile than weighted average stock

**Risk Concentration Metrics**:

- **Risk HHI**: $HHI_{risk} = \sum_{i=1}^{N} (CCR\%_i)^2$
    - Range: [1/N, 1] where 1/N = perfect equal risk contribution, 1 = all risk in one stock
- **Cumulative risk**: Sort by CCR%, calculate running sum
    - Report: % risk from top 10, top 20, top 50 stocks

**Step 3: Stock-Level Analysis**

For each stock, compute:

- Weight ($w_i$)
- Individual volatility ($\sigma_i = \sqrt{\Sigma_{ii}} \times \sqrt{252}$)
- MCR ($MCR_i$)
- CCR ($CCR_i$)
- CCR% ($CCR_i / \sigma_p \times 100$)
- Weight/CCR ratio ($w_i / CCR\%_i$) - efficiency metric
    - Ratio < 1: Stock contributes more risk than weight (risk amplifier)
    - Ratio > 1: Stock contributes less risk than weight (diversifier)


### Outputs and Validation

**Table 3.1: Portfolio Risk Decomposition Summary**


| Metric | Value | Interpretation |
| :-- | :-- | :-- |
| Portfolio Volatility (annualized %) | [From Stage 1] | Total risk |
| Weighted Avg Stock Vol (%) | [Calc: Σ w_i σ_i] | Risk without diversification |
| Diversification Ratio | [Calc] | Expected: 1.3-1.8 [^7] |
| Risk HHI | [Calc] | Lower = more diversified |
| Risk from Top 10 Holdings (%) | [Calc] | Expected: 30-50% |
| Risk from Top 50 Holdings (%) | [Calc] | Expected: 70-85% |
| Risk from Top 100 Holdings (%) | [Calc] | Expected: 90-95% |
| Effective N (by risk) | [Calc: 1/HHI_risk] | Compare to weight-based N_eff |

**Table 3.2: Top 30 Risk Contributors**


| Rank | Ticker | Weight (%) | MCR | CCR (%) | Stock Vol (%) | Sector | W/CCR Ratio |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | [Lookup] | [Calc] |
| 2 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | [Lookup] | [Calc] |
| ... | ... | ... | ... | ... | ... | ... | ... |
| 30 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | [Lookup] | [Calc] |
| ... | ... | ... | ... | ... | ... | ... | ... |
| ALL | 100% | - | 100% | [σ_p] | - | - |  |

Include cumulative CCR% column to show concentration

**Table 3.3: Sector-Level Risk Decomposition**


| Sector | Total Weight (%) | Total CCR (%) | Avg Stock Vol (%) | Diversification |
| :-- | :-- | :-- | :-- | :-- |
| Information Technology | [Calc] | [Calc] | [Calc] | [Interpret] |
| Health Care | [Calc] | [Calc] | [Calc] | [Interpret] |
| Financials | [Calc] | [Calc] | [Calc] | [Interpret] |
| ... (all 11 GICS sectors) | ... | ... | ... | ... |
| **Total** | **100%** | **100%** | - | - |

**Visualization 3.1: Risk Contribution Waterfall**

- Horizontal bars: Top 20 stocks by CCR%
- Bar for "Other 270 stocks" aggregated
- Color code by sector
- Cumulative sum line overlay

**Visualization 3.2: Weight vs. Risk Contribution Scatter**

- X-axis: Portfolio weight (%)
- Y-axis: Risk contribution (%)
- Diagonal line: y = x (proportional contribution)
- Points above diagonal: Risk amplifiers (target for reduction)
- Points below diagonal: Diversifiers (valuable holdings)
- Size: Individual stock volatility
- Color: Sector

**Visualization 3.3: Sector Risk Heatmap**

- Rows: 11 GICS sectors
- Columns: Weight (%), CCR (%), Avg Vol (%)
- Color intensity: Magnitude
- Highlight sectors with CCR% > Weight% (concentrated risk)


### Quality Assurance Checks

**Validation Checklist**:

1. ✓ Sum of CCR = portfolio volatility (within 1e-6 tolerance)
2. ✓ Sum of CCR% = 100% (within 0.01% tolerance)
3. ✓ All MCR values positive for long-only portfolio
4. ✓ Diversification ratio > 1.0
5. ✓ Risk HHI < Weight HHI (risk more concentrated than weights, typical)
6. ✓ Top contributor has CCR% < 10% (not overly concentrated)

**Hypothesis Test**:

- **H4**: Top 20% of stocks contribute >50% of total risk[^7]
- **Test**: Sort by CCR%, sum top 58 stocks (20% of 290), check if >50%
- **Expected**: Typically 50-70% due to correlation structure

**Actionable Insights Generation**:

**Risk Efficiency Analysis**:

- Identify stocks with W/CCR ratio < 0.5 (contributing >2× their weight in risk)
- These are candidates for position reduction
- Document top 10 "risk amplifiers" with recommendation to reduce by X%

**Diversification Opportunities**:

- Identify stocks with W/CCR ratio > 1.5 (contributing <67% their weight in risk)
- These are effective diversifiers to maintain or increase
- Document top 10 "diversifiers" with stable characteristics

***

## Stage 4: Historical Simulation Stress Testing

### Objectives

- Assess portfolio resilience under extreme historical scenarios
- Calculate VaR and Expected Shortfall using actual return distributions
- Identify worst-case losses and recovery patterns


### Mathematical Foundation

**Historical Simulation Method**:[^16][^14]

1. Apply current portfolio weights to historical return scenarios
2. Generate empirical P\&L distribution: $P\&L_t = \sum_{i=1}^{N} w_i r_{i,t}$
3. Sort from worst to best
4. Extract percentiles for VaR

**Historical VaR at confidence level α**:[^16]

$$
VaR_{\alpha} = -\text{Percentile}_{1-\alpha}(P\&L)
$$

For 99% VaR with 1,500 days: 15th worst day loss
For 95% VaR with 1,500 days: 75th worst day loss

**Expected Shortfall (ES)** / Conditional VaR:[^14]

$$
ES_{\alpha} = E[P\&L \mid P\&L < -VaR_{\alpha}]
$$

Average of all losses worse than VaR threshold

**Advantages over parametric VaR**:[^16]

- No distributional assumptions (captures fat tails, skewness)
- Reflects actual correlation patterns during crises
- Transparent and interpretable


### Crisis Period Definitions

**Baseline Scenario**: Full historical period

- Period: January 1, 2020 - January 18, 2026 (all available data)
- Days: ~1,500 trading days
- Characteristics: Mix of normal, high volatility, and crisis periods

**Stress Scenario 1: 2008 Financial Crisis Analog (2020 COVID Crash)**

- **Period**: February 19, 2020 - March 23, 2020
- **Trading days**: 24 days
- **Characteristics**:
    - S\&P 500 declined ~34% peak-to-trough (fastest bear market in history)
    - Volatility (VIX) peaked at 82.69 on March 16, 2020
    - Correlations approached 1.0 (diversification breakdown)
- **Relevance**: Most severe crisis in available data[^17]

**Stress Scenario 2: 2022 Inflation/Rate Shock**

- **Period**: January 3, 2022 - October 13, 2022
- **Trading days**: ~195 days
- **Characteristics**:
    - S\&P 500 declined ~25%, Nasdaq ~33%
    - Fed hiked rates from 0% to 3.75% (fastest cycle since 1980s)
    - Growth stocks underperformed dramatically
    - Bond-stock correlation broke down (both declined)
- **Relevance**: Tests sustained drawdown vs. sharp crash[^17]

**Stress Scenario 3: 2023 Banking Crisis**

- **Period**: March 6, 2023 - March 24, 2023
- **Trading days**: 15 days
- **Characteristics**:
    - Silicon Valley Bank, Signature Bank, Credit Suisse failures
    - Regional bank stocks declined 30-50%
    - Flight to quality (Treasuries rallied, large-cap tech outperformed)
- **Relevance**: Tests sector-specific shocks

**Stress Scenario 4: Volatility-Weighted Historical Simulation**

- **Method**: Scale historical returns by current EWMA volatility ratio[^18]
- **Formula**: $r_{i,t}^{scaled} = r_{i,t} \times \frac{\sigma_{i,EWMA,current}}{\sigma_{i,historical}}$
- **Purpose**: Make old data relevant to current volatility regime
- **Academic source**: Basu (2008)[^18]


### Implementation Specification

**Step 1: Full Historical Simulation**

**Procedure**:

```python
# Using clean returns from Stage 0, portfolio weights from Stage 1
portfolio_returns = (returns_matrix @ weights).values  # Daily P&L
portfolio_returns_sorted = np.sort(portfolio_returns)  # Ascending order

# VaR calculations
n_days = len(portfolio_returns)
var_95_index = int(0.05 * n_days)  # 5th percentile
var_99_index = int(0.01 * n_days)  # 1st percentile

var_95 = -portfolio_returns_sorted[var_95_index] * 100  # As %
var_99 = -portfolio_returns_sorted[var_99_index] * 100  # As %

# Expected Shortfall
es_99 = -portfolio_returns_sorted[:var_99_index].mean() * 100

# Maximum drawdown
cumulative_returns = (1 + portfolio_returns).cumprod()
running_max = cumulative_returns.expanding().max()
drawdown = (cumulative_returns - running_max) / running_max
max_drawdown = drawdown.min() * 100  # As %
```

**Step 2: Crisis Period Stress Tests**

**For each crisis scenario**:

1. Filter returns to crisis dates
2. Calculate P\&L distribution using current weights
3. Compute VaR, ES, maximum single-day loss, cumulative loss
4. Rank stocks by contribution to worst day loss

**Crisis-specific metrics**:

- **95% VaR**: 95th percentile worst loss in crisis period
- **99% VaR**: 99th percentile (may be same as max loss for short periods)
- **Expected Shortfall**: Average of worst 5% of days
- **Cumulative loss**: Total return over full crisis period
- **Maximum single-day loss**: Worst single day
- **Recovery time**: Days to recover to pre-crisis level (if applicable)

**Step 3: Volatility-Weighted Simulation**

**Procedure**:[^18]

```python
# Calculate current vs. historical volatility ratios
current_vols = ewma_vols_current  # From Stage 2
historical_vols = returns_matrix.std() * np.sqrt(252)  # Full sample
vol_ratios = current_vols / historical_vols

# Scale historical returns
scaled_returns = returns_matrix * vol_ratios  # Broadcasting
portfolio_returns_scaled = (scaled_returns @ weights).values

# Recalculate VaR/ES on scaled distribution
...
```

**Step 4: Backtesting VaR Accuracy**

**Kupiec Test** (unconditional coverage):[^16]

- Count: How many days did actual loss exceed 99% VaR?
- Expected: ~1% of days (15 out of 1,500)
- Test statistic: $LR = -2 \ln[(1-p)^{T-N} p^N] + 2 \ln[(1-N/T)^{T-N} (N/T)^N]$
    - $p = 0.01$, $N$ = actual breaches, $T$ = total days
    - $LR \sim \chi^2(1)$ under null
    - Reject if $LR > 3.84$ (95% threshold)


### Outputs and Validation

**Table 4.1: Stress Test Results Summary**


| Scenario | Period | Days | 95% VaR (%) | 99% VaR (%) | ES 99% (%) | Max 1-Day (%) | Cumulative (%) | Recovery Days |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Full History | Jan 2020 - Jan 2026 | ~1,500 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | - |
| COVID Crash | Feb-Mar 2020 | 24 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] |
| Inflation Shock | Jan-Oct 2022 | 195 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] |
| Banking Crisis | Mar 2023 | 15 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] |
| Vol-Weighted | Jan 2020 - Jan 2026 | ~1,500 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | - |

**Table 4.2: Dollar Impact on \$1 Million Portfolio**


| Scenario | 95% VaR (\$) | 99% VaR (\$) | ES 99% (\$) | Max Loss (\$) |
| :-- | :-- | :-- | :-- | :-- |
| Full History | [Calc] | [Calc] | [Calc] | [Calc] |
| COVID Crash | [Calc] | [Calc] | [Calc] | [Calc] |
| Inflation Shock | [Calc] | [Calc] | [Calc] | [Calc] |
| Banking Crisis | [Calc] | [Calc] | [Calc] | [Calc] |

**Table 4.3: Top 10 Loss Contributors (Worst Day in COVID Crash)**

Identify worst single day (likely March 12 or 16, 2020), then decompose:


| Rank | Ticker | Weight (%) | Return (%) | Loss Contribution (\$) | Contribution to Total Loss (%) | Sector |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | [Lookup] |
| ... | ... | ... | ... | ... | ... | ... |
| 10 | [Calc] | [Calc] | [Calc] | [Calc] | [Calc] | [Lookup] |

**Table 4.4: VaR Backtest Results**


| Confidence Level | Expected Breaches | Actual Breaches | Breach Rate (%) | Kupiec LR Stat | p-value | Pass/Fail |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 95% | 75 | [Calc] | [Calc] | [Calc] | [Calc] | [✓/✗] |
| 99% | 15 | [Calc] | [Calc] | [Calc] | [Calc] | [✓/✗] |

**Visualization 4.1: P\&L Distribution Comparison**

- 4 overlapping histograms/density plots:
    - Full history (baseline)
    - COVID crash period
    - Inflation shock period
    - Banking crisis period
- Vertical lines marking 99% VaR for each scenario
- X-axis: Daily portfolio return (%)
- Y-axis: Frequency/density
- **Purpose**: Visualize tail thickness differences

**Visualization 4.2: Maximum Drawdown Chart**

- Line plot: Cumulative portfolio returns over full period (Jan 2020 - Jan 2026)
- Filled area: Drawdown from running maximum (underwater chart)
- Annotations:
    - COVID crash: Feb-Mar 2020 (max drawdown likely ~30-35%)
    - Recovery point (likely summer 2020)
    - 2022 inflation shock drawdown (likely ~20-25%)
    - Current position relative to all-time high
- **Purpose**: Show recovery patterns and current risk position

**Visualization 4.3: Crisis Period Returns Heatmap**

- Rows: Crisis periods (COVID, 2022, Banking)
- Columns: Top 30 stocks by weight
- Cell color: Return during crisis (red = negative, green = positive)
- Row summary: Total portfolio return
- **Purpose**: Identify which stocks provided/reduced protection in each crisis


### Quality Assurance Checks

**Validation Checklist**:

1. ✓ ES > VaR at same confidence level (ES should capture tail beyond threshold)
2. ✓ 99% VaR > 95% VaR (higher confidence = higher loss estimate)
3. ✓ Crisis VaR > baseline VaR (stress periods show higher risk)
4. ✓ VaR backtest breaches ≈ expected (within 95% confidence interval)
5. ✓ Maximum drawdown occurred during identifiable crisis (data sensibility)
6. ✓ Cumulative crisis returns match market behavior (e.g., COVID ~-30%)

**Hypothesis Test**:

- **H5**: Crisis-period 99% VaR is 2-3× baseline 99% VaR[^17]
- **Test**: Calculate ratio of COVID crash VaR to full history VaR
- **Expected**: Ratio ∈ [2.0, 3.5] demonstrating tail risk underestimation
- **If fails**: Check if baseline period already includes sufficient crises

**Contextual Insights**:

**Risk Comparison**:
Compare Stage 2 (EWMA parametric VaR) vs. Stage 4 (historical VaR):

- If Historical VaR > EWMA VaR: Fat tails present, normal assumption inadequate
- If Historical VaR < EWMA VaR: Current volatility elevated vs. history

**Decision Support Recommendations**:


| Finding | Threshold | Action |
| :-- | :-- | :-- |
| Baseline 99% VaR > 3% | High risk | Reduce position sizes by 20% |
| Baseline 99% VaR 2-3% | Moderate risk | Monitor closely, maintain current allocation |
| Baseline 99% VaR < 2% | Low risk | Consider tactical additions |
| Crisis VaR > 5% | Fragile portfolio | Increase defensive stocks, add hedges |
| Max drawdown > 30% | Severe tail risk | Rebalance to lower-beta stocks |
| VaR backtest fails | Model inadequate | Revise approach or increase buffer |


***

## Stage 5: Integration, Reporting, and Validation

### Objectives

- Synthesize all analyses into cohesive narrative
- Validate cross-stage consistency
- Generate executive-ready deliverables


### Cross-Stage Integration Checks

**Consistency Matrix**:


| Metric | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Consistency Check |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Portfolio Volatility | [Calc] | [Calc] | [Calc] | [Implied] | All within 15% of each other |
| Top risk contributors | Top 10 by weight×vol | Top 10 by EWMA | Top 10 by CCR | Top 10 in worst crisis | ≥50% overlap expected |
| Diversification | N_eff, DR | - | DR, Risk HHI | Drawdown vs. S\&P | Metrics align |

**Reconciliation Procedures**:

1. Compare portfolio volatilities:
    - Stage 1: From covariance matrix
    - Stage 2: From EWMA aggregation
    - Stage 3: Implied from CCR sum
    - Stage 4: Realized volatility over full period
    - **Expected**: Within 10-20% (different windows, methods)
2. Cross-check top contributors:
    - Identify stocks in top 20 by CCR (Stage 3)
    - Verify they're also high EWMA vol (Stage 2)
    - Check their contribution in worst crisis days (Stage 4)
    - **Expected**: 60-80% overlap in top 20

### Sensitivity Analysis

**Test 1: Covariance Window Length**

Re-run Stage 1 optimization with:

- **126-day window** (6 months) - more recent, reactive
- **504-day window** (2 years) - smoother, stable

**Compare**:

- Portfolio volatility difference
- Weight turnover: $\sum |w_{new,i} - w_{base,i}|$
- Top 20 holdings overlap

**Expected**: <30% weight turnover, <2 percentage point volatility difference[^3]

**Test 2: EWMA Decay Factor**

Re-run Stage 2 forecasting with:

- **λ = 0.90** (more reactive, ~10-day effective window)
- **λ = 0.97** (smoother, ~33-day effective window)

**Compare**:

- Current VaR estimates
- Autocorrelation strength
- Response to recent volatility spikes

**Expected**: λ = 0.90 shows 20-40% higher VaR in volatile periods[^1]

**Test 3: Position Constraints**

Re-run Stage 1 optimization with:

- **2% max position** (tighter concentration limit)
- **10% max position** (looser limit)
- **No constraints** (fully unconstrained)

**Compare**:

- Number of active positions
- Portfolio volatility
- Top holding weight
- Effective N

**Expected**: Tighter limits → more diversification, slightly higher volatility[^3]

**Sensitivity Summary Table**:


| Parameter | Base Case | Alternative 1 | Alternative 2 | Max Deviation |
| :-- | :-- | :-- | :-- | :-- |
| Covariance window | 252 days | 126 days | 504 days | ±[X]% vol |
| EWMA λ | 0.94 | 0.90 | 0.97 | ±[Y]% VaR |
| Max position | 5% | 2% | 10% | ±[Z]% vol |

**Interpretation**: If max deviations <20%, results are robust; if >50%, parameters matter significantly

### Executive Summary Generation

**One-Page Summary Template**:

***

**PORTFOLIO RISK ANALYSIS SUMMARY**
**Analysis Date**: January 18, 2026
**Portfolio**: Minimum Variance S\&P 500 Strategy

**1. PORTFOLIO CONSTRUCTION**

- **Optimization**: Global minimum variance on [N] S\&P 500 stocks
- **Rebalancing**: Quarterly
- **Constraints**: Long-only, 0-5% per stock

**2. CURRENT RISK METRICS** (as of Jan 18, 2026)


| Metric | Value | Benchmark | Interpretation |
| :-- | :-- | :-- | :-- |
| Portfolio Volatility (annual) | [X]% | [Y]% (equal-weight) | [Z]% reduction |
| 1-Day 99% VaR | [A]% (\$[B]K on \$1M) | - | Max likely daily loss |
| 10-Day 99% VaR | [C]% (\$[D]K on \$1M) | - | Max likely 2-week loss |
| Diversification Ratio | [E] | >1.3 target | [Effective/Moderate/Weak] |
| Effective N Stocks | [F] | 290 available | Risk spread across [F] stocks |

**3. KEY FINDINGS**

**Optimization Effectiveness**: Achieved [X]% volatility reduction vs. equal-weighted portfolio through systematic risk minimization. Current portfolio vol at [percentile] of historical range—[low/normal/elevated] regime.

**Risk Concentration**: Top 10 holdings contribute [Y]% of total risk despite only [Z]% of weight. [Sector] sector represents [A]% of risk vs. [B]% of weight—primary concentration.

**Stress Resilience**: In 2020-style crisis, portfolio could lose up to [X]% in single day (99% VaR) vs. [Y]% baseline. Maximum historical drawdown was [Z]% over [M] months during [crisis period].

**4. ACTIONABLE RECOMMENDATIONS**

**Immediate** (within 1 week):

- Monitor [top 3 tickers] which contribute [X]% of total risk
- Current EWMA volatility at [percentile]—[increase vigilance/maintain/reduce hedges]

**Tactical** (monthly):

- If 10-day rolling EWMA exceeds [threshold], reduce position sizes by [X]%
- Rebalance quarterly to maintain equal risk contributions

**Strategic** (ongoing):

- Consider diversifying [sector] exposure to reduce concentration
- Evaluate protective strategies if stressed VaR exceeds [Y]%

**5. MODEL VALIDATION**

- ✓ All optimization constraints satisfied
- ✓ Volatility clustering confirmed (autocorr = [X])
- ✓ VaR backtest: [Y] breaches vs. [Z] expected ([pass/marginal/fail])
- ✓ Crisis scenarios show [2-3]× baseline VaR (expected tail risk)

**Next Review**: April 18, 2026 (quarterly rebalancing date)

***

### Final Validation Checklist

**Mathematical Correctness**:

- ✓ All constraint sums verified (weights = 1.0, CCR sum = σ_p)
- ✓ Covariance matrix positive definite (all eigenvalues > 0)
- ✓ Optimization converged (KKT conditions satisfied within tolerance)
- ✓ VaR/ES hierarchy correct (ES > VaR, 99% > 95%)
- ✓ Scaling relationships hold (10-day VaR ≈ √10 × 1-day VaR within 10%)

**Economic Sensibility**:

- ✓ Low-vol stocks receive higher weights in min-var portfolio
- ✓ Portfolio vol < weighted avg individual vol (diversification benefit)
- ✓ EWMA volatility responsive to recent market events
- ✓ Crisis VaR > baseline VaR (tail risk present)
- ✓ Correlations in normal range [0.3, 0.8] for stock pairs

**Data Quality**:

- ✓ No missing data in final analysis period (or <0.5%)
- ✓ All tickers valid and active
- ✓ Returns distributions lack extreme outliers (checked via winsorization)
- ✓ Trading days aligned across all stocks

**Academic Rigor**:

- ✓ All methods cited to peer-reviewed sources [web:X]
- ✓ Parameters match academic standards (λ=0.94, 252-day window)
- ✓ Hypotheses tested with statistical criteria
- ✓ Limitations acknowledged in documentation

**Reproducibility**:

- ✓ All data sources documented with dates
- ✓ Random seeds set (if any stochastic processes)
- ✓ Package versions recorded
- ✓ Intermediate results saved for verification


### Deliverables Checklist

**Required Outputs**:

1. ✓ Jupyter Notebook (`.ipynb`) with all code, theory, results
2. ✓ HTML export of notebook for web viewing
3. ✓ PDF export for formal presentation
4. ✓ All tables exported to CSV (`outputs/tables/`)
5. ✓ All visualizations exported to PNG 300 DPI (`outputs/figures/`)
6. ✓ Executive summary as standalone PDF
7. ✓ Data quality report (`data/data_quality_report.txt`)
8. ✓ Parameters configuration file (`config/parameters.yaml`)

**Notebook Structure** (section headings):

1. Executive Summary
2. Introduction \& Methodology Overview
3. Stage 0: Data Acquisition
4. Stage 1: Portfolio Optimization
5. Stage 2: Volatility Forecasting
6. Stage 3: Risk Decomposition
7. Stage 4: Stress Testing
8. Stage 5: Integration \& Sensitivity
9. Conclusions \& Recommendations
10. References
11. Appendix: Technical Details

***

## Academic References (For Citations in Notebook)

### Stage 1: Minimum Variance Optimization

1. Markowitz, H. (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77-91.
2. Clarke, R., De Silva, H., \& Thorley, S. (2011). "Minimum-Variance Portfolio Composition." *Journal of Portfolio Management*, 37(2), 31-45.[^9]
3. DeMiguel, V., Garlappi, L., \& Uppal, R. (2009). "Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy?" *Review of Financial Studies*, 22(5), 1915-1953.[^10][^11]
4. Jagannathan, R., \& Ma, T. (2003). "Risk Reduction in Large Portfolios: Why Imposing the Wrong Constraints Helps." *Journal of Finance*, 58(4), 1651-1683.[^3]

### Stage 2: EWMA Volatility Forecasting

5. J.P. Morgan/Reuters (1996). "RiskMetrics—Technical Document." 4th edition. New York.[^2]
6. Brooks, C., \& Persand, G. (2003). "Volatility Forecasting for Risk Management." *Journal of Forecasting*, 22(1), 1-22.[^19]
7. Zumbach, G. (2007). "The RiskMetrics 2006 Methodology." *Risk*, January 2007.[^1]
8. Engle, R. F. (2001). "GARCH 101: The Use of ARCH/GARCH Models in Applied Econometrics." *Journal of Economic Perspectives*, 15(4), 157-168.[^12]

### Stage 3: Risk Decomposition

9. Roncalli, T., \& Weisang, G. (2016). "Risk Parity Portfolios with Risk Factors." *Quantitative Finance*, 16(3), 377-388.[^20][^21][^7]
10. Maillard, S., Roncalli, T., \& Teïletche, J. (2010). "The Properties of Equally Weighted Risk Contribution Portfolios." *Journal of Portfolio Management*, 36(4), 60-70.[^15]
11. Qian, E. (2006). "On the Financial Interpretation of Risk Contribution: Risk Budgets Do Add Up." *Journal of Investment Management*, 4(4), 41-51.[^15]

### Stage 4: Stress Testing

12. Pritsker, M. (2006). "The Hidden Dangers of Historical Simulation." *Journal of Banking \& Finance*, 30(2), 561-582.[^16]
13. Basu, A. K., \& Ebrahim, M. S. (2008). "Stress Testing with Volatility-Weighted Historical Simulation." *Risk*, 21(8), 78-82.[^18]
14. International Monetary Fund (2006). "Stress Testing Trading Desks: Practical Considerations." *IMF Monetary and Capital Markets Department*.[^17]
15. Jorion, P. (2007). *Value at Risk: The New Benchmark for Managing Financial Risk*. 3rd edition. New York: McGraw-Hill.[^14]
16. Acerbi, C., \& Tasche, D. (2002). "On the Coherence of Expected Shortfall." *Journal of Banking \& Finance*, 26(7), 1487-1503.[^1]

### General Risk Management

17. Christoffersen, P. F. (2012). *Elements of Financial Risk Management*. 2nd edition. Academic Press.
18. McNeil, A. J., Frey, R., \& Embrechts, P. (2015). *Quantitative Risk Management: Concepts, Techniques and Tools*. Princeton University Press.

### Code Organization Structure

**Directory Layout**:

```
portfolio_risk_analysis/
├── data/
│   ├── raw_prices.csv
│   ├── clean_returns.csv
│   ├── risk_free_rate.csv
│   └── data_quality_report.txt
├── outputs/
│   ├── tables/
│   │   ├── table_1_1_optimization_results.csv
│   │   ├── table_1_2_top_holdings.csv
│   │   └── ... (all tables)
│   ├── figures/
│   │   ├── fig_1_1_sector_allocation.png
│   │   └── ... (all visualizations)
│   └── executive_summary.pdf
├── config/
│   └── parameters.yaml
├── portfolio_risk_analysis.ipynb
└── README.md
```


### Key Configuration Parameters (parameters.yaml)

```yaml
# Data Parameters
start_date: '2020-01-01'
end_date: '2026-01-18'
num_stocks: 300
min_trading_days: 1200
max_missing_pct: 5.0

# Optimization Parameters
covariance_window: 252
max_position_weight: 0.05
optimization_tolerance: 1.0e-8
max_iterations: 1000

# EWMA Parameters
ewma_lambda: 0.94
ewma_init_window: 30

# VaR Parameters
var_confidence_levels: [0.95, 0.99]
var_horizons: [1, 10]
z_95: 1.645
z_99: 2.326

# Stress Test Periods
crisis_periods:
  covid_crash:
    start: '2020-02-19'
    end: '2020-03-23'
    name: 'COVID-19 Crash'
  inflation_shock:
    start: '2022-01-03'
    end: '2022-10-13'
    name: '2022 Inflation Shock'
  banking_crisis:
    start: '2023-03-06'
    end: '2023-03-24'
    name: '2023 Banking Crisis'

# Portfolio Parameters
initial_portfolio_value: 1000000
rebalance_frequency: 'quarterly'

# FRED API
fred_series_id: 'DGS3MO'

# Random Seed (for reproducibility)
random_seed: 42
```


### Python Package Requirements

**Required Libraries** (create `requirements.txt`):

```
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
yfinance>=0.2.0
requests>=2.31.0
statsmodels>=0.14.0  # For autocorrelation functions
openpyxl>=3.1.0      # For Excel export
PyYAML>=6.0          # For config file
jupyter>=1.0.0
notebook>=6.5.0
```


### Modular Function Design

**Create reusable functions** (not monolithic code blocks):

**Stage 0 Functions**:

```python
def download_sp500_tickers(num_stocks=300):
    """Scrape S&P 500 tickers from Wikipedia, return top N by market cap"""
    
def download_stock_data(tickers, start_date, end_date):
    """Download adjusted close prices using yfinance"""
    
def download_risk_free_rate(api_key, series_id, start_date, end_date):
    """Download Treasury rate from FRED API"""
    
def validate_data_quality(prices_df, max_missing_pct=5.0):
    """Check missing data, outliers; return quality report and clean tickers"""
    
def calculate_returns(prices_df, method='log'):
    """Calculate log or simple returns from prices"""
    
def generate_data_quality_report(prices_df, returns_df, tickers_removed):
    """Create text report summarizing data quality"""
```

**Stage 1 Functions**:

```python
def estimate_covariance_matrix(returns_df, window=252):
    """Calculate sample covariance matrix from last N days"""
    
def optimize_minimum_variance(cov_matrix, max_weight=0.05):
    """Solve min variance optimization with constraints"""
    
def calculate_portfolio_metrics(weights, cov_matrix):
    """Compute vol, diversification ratio, effective N, etc."""
    
def create_equal_weighted_portfolio(num_stocks):
    """Generate 1/N benchmark weights"""
```

**Stage 2 Functions**:

```python
def calculate_ewma_volatility(returns_series, lambda_param=0.94, init_window=30):
    """Compute EWMA variance series for single stock"""
    
def aggregate_portfolio_ewma(stock_ewmas, weights, corr_matrix):
    """Combine stock-level EWMA into portfolio EWMA"""
    
def calculate_parametric_var(portfolio_vol, confidence_level, horizon):
    """Compute VaR using normal distribution assumption"""
    
def test_volatility_clustering(vol_series, max_lag=10):
    """Calculate autocorrelation to test for clustering"""
```

**Stage 3 Functions**:

```python
def calculate_marginal_risk(weights, cov_matrix):
    """Compute MCR vector"""
    
def calculate_component_contributions(weights, mcr, portfolio_vol):
    """Compute CCR vector and percentages"""
    
def aggregate_by_sector(stock_data, weights, ccr_pct, sectors):
    """Roll up metrics to sector level"""
    
def identify_risk_amplifiers(weights, ccr_pct, threshold=0.5):
    """Find stocks with W/CCR ratio < threshold"""
```

**Stage 4 Functions**:

```python
def calculate_historical_var(returns_series, confidence_level):
    """Compute VaR from empirical distribution"""
    
def calculate_expected_shortfall(returns_series, var_threshold):
    """Compute average of losses beyond VaR"""
    
def calculate_maximum_drawdown(cumulative_returns):
    """Find maximum peak-to-trough decline"""
    
def stress_test_crisis_period(returns_df, weights, start_date, end_date):
    """Apply current weights to historical crisis period"""
    
def volatility_weighted_simulation(returns_df, current_vols, historical_vols):
    """Scale returns by volatility ratio"""
    
def kupiec_test(returns_series, var_threshold, confidence_level):
    """Backtest VaR accuracy with Kupiec LR test"""
    
def decompose_crisis_loss(returns_df, weights, crisis_date):
    """Identify top contributors to worst day loss"""
```

**Visualization Functions**:

```python
def plot_sector_allocation(weights, sectors, title):
    """Create pie chart of sector weights"""
    
def plot_weight_vs_volatility(weights, vols, sectors):
    """Scatter plot with trendline"""
    
def plot_ewma_timeseries(portfolio_ewma, realized_vol, events):
    """Time series with event annotations"""
    
def plot_risk_waterfall(ccr_pct, tickers, top_n=20):
    """Horizontal bar chart of risk contributions"""
    
def plot_weight_vs_risk_scatter(weights, ccr_pct, sectors, vols):
    """Scatter with diagonal line"""
    
def plot_pnl_distributions(pnl_dicts, var_lines):
    """Overlapping histograms for multiple scenarios"""
    
def plot_drawdown_chart(cumulative_returns, events):
    """Underwater chart with annotations"""
```

**Reporting Functions**:

```python
def generate_table(data, filename, caption):
    """Create formatted DataFrame and export to CSV"""
    
def save_figure(fig, filename, dpi=300):
    """Save matplotlib figure to PNG"""
    
def create_executive_summary(all_metrics, recommendations):
    """Generate one-page summary as formatted string"""
```


### Critical Implementation Notes

**1. Stock Universe Selection**

Use the **exact ticker list provided in Stage 0** (300 tickers divided into 4 tiers). This eliminates need for web scraping and ensures reproducibility.

**Alternative approach** (if agent wants fresh data):

```python
import pandas as pd

# Scrape Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tables = pd.read_html(url)
sp500_table = tables[^0]  # First table contains constituents

# Get tickers and market caps
tickers = sp500_table['Symbol'].str.replace('.', '-').tolist()  # Fix ticker format
# Note: Wikipedia table may not have market caps; use yfinance to fetch
# Or simply use first 300 tickers alphabetically as proxy
tickers_300 = tickers[:300]
```

**2. FRED API Integration**

```python
import requests
import pandas as pd

def get_fred_data(api_key, series_id='DGS3MO', start_date='2020-01-01', end_date='2026-01-18'):
    """
    Download data from FRED API
    
    Parameters:
    - api_key: User's FRED API key
    - series_id: FRED series code (default: DGS3MO for 3-month Treasury)
    - start_date, end_date: Date range
    
    Returns:
    - DataFrame with date index and rate values
    """
    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json',
        'observation_start': start_date,
        'observation_end': end_date
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"FRED API error: {response.status_code}")
    
    data = response.json()
    
    if 'observations' not in data:
        raise Exception(f"No data returned from FRED for series {series_id}")
    
    df = pd.DataFrame(data['observations'])
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')  # Handle '.' for missing
    df = df[['date', 'value']].set_index('date')
    df.columns = [series_id]
    
    # Forward fill missing values (weekends/holidays)
    df = df.ffill()
    
    return df

# Usage in notebook:
# USER_FRED_API_KEY = 'your_key_here'  # User must insert their key
# rf_rate = get_fred_data(USER_FRED_API_KEY)
```

**3. Sector Classification**

Since S\&P 500 Wikipedia table includes GICS sector, extract during data download:[^2]

```python
# After scraping Wikipedia table
sector_mapping = dict(zip(sp500_table['Symbol'], sp500_table['GICS Sector']))
# Replace ticker formatting: '.' -> '-'
sector_mapping = {k.replace('.', '-'): v for k, v in sector_mapping.items()}
```

**GICS Sectors (11 total)**:[^2]

1. Information Technology
2. Health Care
3. Financials
4. Consumer Discretionary
5. Communication Services
6. Industrials
7. Consumer Staples
8. Energy
9. Utilities
10. Real Estate
11. Materials

**4. Data Validation Edge Cases**

**Handle common issues**:

- **Delisted stocks**: If stock has insufficient data, remove from universe
- **Stock splits/dividends**: Use `auto_adjust=True` in yfinance
- **Ticker changes**: Some tickers may have changed (e.g., FB → META); yfinance handles automatically
- **Missing data**: Forward-fill up to 5 days; remove if >5% total missing
- **IPOs**: Recent IPOs won't have 6 years of data; remove if <1,200 days

**5. Numerical Stability**

**Covariance matrix conditioning**:

```python
# Check condition number
eigenvalues = np.linalg.eigvals(cov_matrix)
condition_number = eigenvalues.max() / eigenvalues.min()

if condition_number > 100:
    print(f"Warning: High condition number {condition_number:.1f}")
    # Apply regularization
    regularization = 1e-4
    cov_matrix_reg = cov_matrix + regularization * np.eye(len(cov_matrix))
else:
    cov_matrix_reg = cov_matrix
```

**Optimization convergence**:

```python
from scipy.optimize import minimize

result = minimize(
    fun=lambda w: w.T @ cov_matrix @ w,
    x0=np.ones(N) / N,
    method='SLSQP',
    bounds=[(0, max_weight)] * N,
    constraints={'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
    options={'ftol': 1e-8, 'maxiter': 1000}
)

if not result.success:
    raise Exception(f"Optimization failed: {result.message}")

weights = result.x
```

**6. Visualization Best Practices**

**Standard formatting**:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['legend.fontsize'] = 9

# Color palette for sectors
sector_colors = sns.color_palette('tab10', n_colors=11)

# Always include:
# - Title
# - Axis labels with units
# - Legend (if multiple series)
# - Grid for readability
# - Source citation in caption
```

**7. Expected Numerical Ranges** (for validation)

Based on historical S\&P 500 data (2020-2026):


| Metric | Expected Range | Out-of-Range Action |
| :-- | :-- | :-- |
| Stock daily volatility | 15-60% annualized | Flag if >80% |
| Portfolio volatility (min-var) | 12-20% annualized | Check if <10% or >25% |
| Diversification ratio | 1.2-1.8 | Check if <1.1 or >2.0 |
| Effective N | 60-180 | Check if <40 or >250 |
| EWMA autocorr(1) | 0.25-0.60 | Check if <0.1 |
| Baseline 99% VaR (1-day) | 1.5-3.5% | Check if <1% or >5% |
| COVID crash 99% VaR | 5-12% | Check if <4% |
| Max drawdown | 25-40% | Check if <20% or >50% |

**8. Performance Optimization**

For 300 stocks with 1,500 days:

- **Vectorize operations**: Use NumPy array operations, not loops
- **Parallel downloads**: yfinance supports `threads=True`
- **Cached calculations**: Save covariance matrix, don't recalculate
- **Sample data**: During development, test with 50 stocks first

**Example optimization**:

```python
# SLOW (loop):
ewma_vols = []
for ticker in tickers:
    vol = calculate_ewma_volatility(returns[ticker])
    ewma_vols.append(vol)

# FAST (vectorized):
ewma_vols = returns.apply(calculate_ewma_volatility, axis=0)
```

**9. Error Handling**

**Graceful failures**:

```python
try:
    data = yf.download(tickers, start=start_date, end=end_date, 
                       auto_adjust=True, threads=True)
except Exception as e:
    print(f"Download error: {e}")
    print("Retrying with smaller batches...")
    # Fallback: Download in batches of 50
    
# Check data quality
if data.isnull().sum().sum() > len(tickers) * len(data) * 0.05:
    raise Exception("Too much missing data (>5%); check tickers")
```

**10. Documentation Standards**

**In-code comments**:

- Explain **why**, not **what** (code shows what)
- Document assumptions (e.g., "Assumes returns are i.i.d. for VaR calculation")
- Note academic sources for formulas

**Markdown cells**:

- **Before each stage**: 1-2 paragraph overview
- **Before each calculation**: Mathematical formula in LaTeX
- **After each output**: 2-3 sentence interpretation

**Example**:

```markdown
### Stage 2.1: EWMA Variance Calculation

We apply the RiskMetrics (1996) EWMA model to estimate time-varying volatility:

$\hat{\sigma}_{t+1}^2 = \lambda \hat{\sigma}_t^2 + (1-\lambda) r_t^2$

Using $\lambda = 0.94$ (industry standard for daily data), this gives approximately 17-day effective window.
```


***

## Testing and Validation Protocol

### Stage-by-Stage Testing

**After Stage 0 (Data)**:

```python
# Run these checks before proceeding
assert len(returns) >= 1200, "Insufficient history"
assert returns.isnull().sum().sum() / returns.size < 0.01, "Too much missing data"
assert returns.std().min() > 0, "Zero variance stock detected"
print("✓ Data quality checks passed")
```

**After Stage 1 (Optimization)**:

```python
assert abs(weights.sum() - 1.0) < 1e-6, "Weights don't sum to 1"
assert (weights >= 0).all(), "Negative weights found"
assert (weights <= max_weight + 1e-6).all(), "Position limits violated"
assert portfolio_vol < equal_weight_vol, "Min-var should have lower vol"
print("✓ Optimization checks passed")
```

**After Stage 2 (EWMA)**:

```python
assert (ewma_vols > 0).all().all(), "Negative volatility detected"
assert var_99 > var_95, "VaR hierarchy violated"
assert var_10d > var_1d, "Horizon scaling violated"
autocorr_1 = portfolio_ewma.autocorr(lag=1)
assert autocorr_1 > 0.1, f"Weak clustering: ρ(1)={autocorr_1:.3f}"
print("✓ EWMA checks passed")
```

**After Stage 3 (Decomposition)**:

```python
assert abs(ccr.sum() - portfolio_vol) < 1e-6, "CCR doesn't sum to portfolio vol"
assert abs(ccr_pct.sum() - 100) < 0.01, "CCR% doesn't sum to 100%"
assert diversification_ratio > 1.0, "No diversification benefit"
print("✓ Decomposition checks passed")
```

**After Stage 4 (Stress Testing)**:

```python
assert es_99 >= var_99, "ES should be >= VaR"
assert var_99 >= var_95, "99% VaR should be >= 95% VaR"
assert crisis_var > baseline_var, "Crisis VaR should exceed baseline"

# Backtest
expected_breaches = int(len(returns) * 0.01)
actual_breaches = (portfolio_returns < -var_99/100).sum()
assert abs(actual_breaches - expected_breaches) < 2 * np.sqrt(expected_breaches), \
    f"VaR backtest failed: {actual_breaches} vs {expected_breaches} expected"
print("✓ Stress testing checks passed")
```


### Hypothesis Testing Results Table

**Generate at end of analysis**:


| ID | Hypothesis | Expected | Actual | Status | Interpretation |
| :-- | :-- | :-- | :-- | :-- | :-- |
| H2 | Volatility reduction 20-40% | [20%, 40%] | [Calc]% | ✓/✗ | [Interpretation] |
| H3 | Volatility clustering ρ(1)>0.3 | >0.30 | [Calc] | ✓/✗ | [Interpretation] |
| H4 | Top 20% contribute >50% risk | >50% | [Calc]% | ✓/✗ | [Interpretation] |
| H5 | Crisis VaR 2-3× baseline | [2.0, 3.0] | [Calc] | ✓/✗ | [Interpretation] |


***

## Final Execution Checklist for Agent

**Before starting**:

- [ ] Install all required packages from requirements.txt
- [ ] Create directory structure (data/, outputs/, config/)
- [ ] User provides FRED API key (insert into notebook cell)
- [ ] Set random seed for reproducibility

**Data stage**:

- [ ] Download 300 S\&P 500 stock prices from yfinance
- [ ] Download DGS3MO from FRED
- [ ] Run data quality validation
- [ ] Export clean returns to CSV
- [ ] Generate data quality report

**Analysis stages**:

- [ ] Run Stage 1 optimization
- [ ] Run Stage 2 EWMA forecasting
- [ ] Run Stage 3 risk decomposition
- [ ] Run Stage 4 stress testing
- [ ] Run Stage 5 integration and sensitivity

**Outputs**:

- [ ] Generate all 15+ tables, export to CSV
- [ ] Generate all 7+ visualizations, export to PNG
- [ ] Create executive summary
- [ ] Run all validation checks (print status)
- [ ] Test all hypotheses (print results table)

**Documentation**:

- [ ] Add markdown explanations before each section
- [ ] Include LaTeX formulas for all methods
- [ ] Cite academic sources [web:X] throughout
- [ ] Document any deviations or issues encountered

**Export**:

- [ ] Export notebook to HTML
- [ ] Export notebook to PDF
- [ ] Verify all outputs exist in correct directories
- [ ] Create README.md with project overview

***

## Expected Timeline (For Project Planning)

**Week 1: Foundation**

- Days 1-2: Data acquisition and validation (Stage 0)
- Days 3-4: Optimization implementation (Stage 1)
- Day 5: Testing and validation
- **Deliverable**: Working minimum variance portfolio with benchmark

**Week 2: Risk Analysis**

- Days 1-2: EWMA implementation (Stage 2)
- Days 3-4: Risk decomposition (Stage 3)
- Day 5: Cross-validation and initial insights
- **Deliverable**: Time-varying risk metrics and attribution

**Week 3: Stress Testing**

- Days 1-3: Historical simulation implementation (Stage 4)
- Day 4: Crisis scenario analysis
- Day 5: Sensitivity testing
- **Deliverable**: Comprehensive stress test results

**Week 4: Integration \& Polish**

- Days 1-2: Pipeline integration and final validation
- Days 3-4: Documentation, visualizations, and narrative
- Day 5: Executive summary and final review
- **Deliverable**: Production-ready analysis notebook

**Total**: 20 working days for complete, documented, validated implementation

***

## Success Criteria

**Minimum viable project** must achieve:

1. ✓ All 5 stages implemented and producing outputs
2. ✓ All validation checks passing
3. ✓ At least 3 of 4 hypotheses confirmed (or deviations explained)
4. ✓ 15+ tables and 7+ visualizations generated
5. ✓ Executive summary clearly communicating risk insights
6. ✓ All academic methods properly cited

**Excellent project** additionally demonstrates:
7. ✓ Sensitivity analysis showing robustness
8. ✓ Cross-stage consistency verified
9. ✓ Professional-quality visualizations
10. ✓ Actionable recommendations with thresholds
11. ✓ Code modularized with reusable functions
12. ✓ Comprehensive documentation for reproducibility

***

This completes the comprehensive project pipeline. The coding agent now has:

- Complete data sources (300 tickers, FRED API details)
- Exact mathematical formulations
- Step-by-step implementation guidance
- Validation criteria at every stage
- Expected outputs and quality standards
- Academic references for all methods

The agent can begin implementation immediately without needing to search for additional information.

<div align="center">⁂</div>

[^1]: https://corporatefinanceinstitute.com/resources/career-map/sell-side/risk-management/value-at-risk-var/

[^2]: https://palomar.home.ece.ust.hk/ELEC5470_lectures/slides_risk_parity_portfolio.pdf


<span style="display:none">[^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39]</span>

<div align="center">⁂</div>

[^1]: https://portfoliooptimizer.io/blog/volatility-forecasting-simple-and-exponentially-weighted-moving-average-models/

[^2]: https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/exponentially-weighted-moving-average-ewma/

[^3]: https://www.sciencedirect.com/science/article/abs/pii/S0377221715000302

[^4]: https://kurser.math.su.se/pluginfile.php/20130/mod_folder/content/0/Kandidat/2021/2021_5_report.pdf?forcedownload=1

[^5]: https://fred.stlouisfed.org/series/DGS3MO

[^6]: https://fred.stlouisfed.org/graph/?id=DGS3MO%2CDGS5%2CDGS10%2CDGS30

[^7]: https://www.sciencedirect.com/science/article/abs/pii/S0264999317315705

[^8]: https://palomar.home.ece.ust.hk/ELEC5470_lectures/slides_risk_parity_portfolio.pdf

[^9]: https://arxiv.org/html/2501.15793v1

[^10]: https://investresolve.com/portfolio-optimization-simple-optimal-methods/

[^11]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3395359

[^12]: http://www.columbia.edu/~amm26/lecture files/volatilityBehaviorForecasting.pdf

[^13]: https://spoudai.unipi.gr/index.php/spoudai/article/viewFile/1207/1286

[^14]: https://corporatefinanceinstitute.com/resources/career-map/sell-side/risk-management/value-at-risk-var/

[^15]: https://bookdown.org/compfinezbook/introcompfinr/understanding-portfolio-volatility-risk-decompositions.html

[^16]: https://www.simtrade.fr/blog_simtrade/historical-method-var-calculation/

[^17]: https://www.imf.org/external/np/seminars/eng/2006/stress/pdf/ms.pdf

[^18]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1140719

[^19]: https://centaur.reading.ac.uk/21316/1/21316.pdf

[^20]: http://thierry-roncalli.com/download/erc.pdf

[^21]: http://www.thierry-roncalli.com/download/erc.pdf

[^22]: https://en.wikipedia.org/wiki/List_of_S\&P_500_companies

[^23]: https://www.nerdwallet.com/investing/learn/sp-500-companies

[^24]: https://www.spglobal.com/spdji/en/indices/equity/sp-500/

[^25]: https://stockanalysis.com/list/sp-500-stocks/

[^26]: https://www.slickcharts.com/sp500

[^27]: https://github.com/hamed-ahangari/The-SP500-data-downloader

[^28]: https://www.frbsf.org/research-and-insights/data-and-indicators/treasury-yield-premiums/

[^29]: https://www.tradingview.com/symbols/SPX/components/

[^30]: https://enlightenmentinvesting.home.blog/2019/12/01/how-to-download-sp-500-data-from-yahoo-finance-using-python/

[^31]: https://fred.stlouisfed.org/docs/api/fred/

[^32]: https://www.tradingview.com/symbols/FRED-DGS3MO/

[^33]: https://www.tradingview.com/symbols/FRED-DGS3MO/chart/

[^34]: https://www.rdocumentation.org/packages/treasuryTR/versions/0.1.6/topics/get_yields

[^35]: https://ba-odegaard.no/teach/empir_finance_2021/lectures/fama_macbeth/lecture_fm.pdf

[^36]: https://rdrr.io/cran/treasuryTR/man/get_yields.html

[^37]: https://fred.stlouisfed.org/series/TB3MS

[^38]: https://www.datasetiq.com/datasets/fred-dgs3mo-1764226848962

[^39]: https://aws.amazon.com/marketplace/pp/prodview-gur4uync4bl2i

