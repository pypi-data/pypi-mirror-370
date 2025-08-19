# Auto-GARCH

**Regime-aware volatility modeling with automatic GARCH fitting.**

## Usage

from auto_garch import AutoGarch, Config

csv_path = "SPY.csv"
value_col = "Close"
date_col = "Date"

pipeline = AutoGarch(Config())
result = pipeline.run(csv_path, value_col, date_col)
