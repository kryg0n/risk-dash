# Risk Dash

Quantitative Portfolio Risk Analysis: Measurement, Understanding, and Communication Framework

## Project Overview

Risk Dash is a comprehensive portfolio risk management system designed to analyze and compare equity strategies using **Modern Portfolio Theory (MPT)** and **Statistical Risk Modeling**. 

The project has evolved into two versions:
*   **v1 (Prototype)**: A detailed single-portfolio analysis of the S&P 500 (300 stocks).
*   **v2 (Multi-Portfolio Framework)**: A scalable pipeline comparing **10 distinct investment strategies** (Market, Sector, Global) to test diversification hypotheses and crisis robustness.

## v2: Multi-Portfolio Comparison (Current)

The **v2 architecture** allows for the simultaneous analysis of multiple portfolios to answer critical questions about concentration risk and optimization efficiency.

### Key Features
- **Unified Pipeline**: A single notebook (`v2/multi_portfolio_risk_v2.ipynb`) handles Data Acquisition → Optimization → Stress Testing → Reporting.
- **10 Distinct Portfolios**: Analyzes S&P 500, NASDAQ-100, Sector Specific (Tech/Defensive), and International strategies.
- **Advanced Metrics**:
    - **Optimization Efficiency**: Measures volatility reduction vs. Equal-Weight benchmark.
    - **EWMA Volatility**: Time-varying risk forecasting (RiskMetrics $\lambda=0.94$).
    - **Stress Testing**: Simulates performance during the **COVID-19 Market Crash (2020)**.

### Results & Reporting
The v2 pipeline automatically generates comprehensive reports:
*   **[Academic Analysis Report](v2/REPORT.md)**: A semi-academic paper synthesizing the findings, aimed at sophisticated investors.
*   **Master Data**: `v2/data/comparison_final.csv` contains the raw metrics for all portfolios.

### How to Run v2
1.  Open **`v2/multi_portfolio_risk_v2.ipynb`** in VS Code.
2.  Click **"Run All"**.
3.  The system will:
    - Download historical data for ~360 tickers (cached to `v2/data/raw_prices_master.csv`).
    - Optimize and analyze all 10 portfolios.
    - Generate the reports and visualizations in `v2/data/`.

---

## v1: Single Portfolio Deep Dive (Archive)

The v1 prototype provides a granular look at a single S&P 500 portfolio. It is located in the `v1/` folder.

- **[LAYMAN_GUIDE.md](v1/LAYMAN_GUIDE.md)**: Simple explanation for non-technical users.
- **[portfolio_risk_analysis.ipynb](v1/portfolio_risk_analysis.ipynb)**: The original detailed analysis notebook.

## Setup

### Requirements
- Python 3.14.2
- Virtual environment (`.venv/`)
- Libraries: `pandas`, `numpy`, `yfinance`, `scipy`, `matplotlib`, `seaborn`

### Quick Start
```bash
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies (if needed)
pip install -r v2/requirements.txt
```

## Project Structure

```
risk-dash/
├── v2/                                  # VERSION 2 (Active)
│   ├── multi_portfolio_risk_v2.ipynb    # Main Unified Notebook
│   ├── Multi-Portfolio_Analysis_Report_Academic.md # Final Analysis
│   ├── requirements.txt
│   └── data/                            # v2 Data & Outputs
│       ├── comparison_final.csv         # Master Metrics
│       ├── comparison_charts.png        # Visualization
│       ├── REPORT.md                    # Generated Dashboard
│       └── P1/ ... P10/                 # Per-portfolio clean data
├── v1/                                  # VERSION 1 (Archive)
│   ├── portfolio_risk_analysis.ipynb
│   ├── LAYMAN_GUIDE.md
│   └── data/
├── config.py                            # Shared Configuration
├── README.md                            # This file
├── development_log.md                   # Chronological Progress
└── pipeline.md                          # Original Spec
```
