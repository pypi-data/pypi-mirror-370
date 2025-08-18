# AutoEDA - Automated Exploratory Data Analysis

One function call for comprehensive data analysis and visualization.

## Installation

### Local Development Installation

\`\`\`bash
# Clone or download this project
# Navigate to the project directory
cd autoeda-library

# Install in development mode
pip install -e .
\`\`\`

## Quick Start

```python
import pandas as pd
import autoeda

# Load your data
df = pd.read_csv('your_data.csv')

# One function call does everything!
report = autoeda.analyze(df)

# View summary
report.show_summary()

# Generate visualizations
report.plot_missing_data()
report.plot_distributions()
report.plot_correlation_matrix()
