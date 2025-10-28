# World Bank Data Explorer

A data exploration tool for World Bank datasets using Python, Pandas, and Dash.

## Setup Instructions

This project supports both `venv` (standard Python) and `conda` (Anaconda) environments.

### Option 1: Using venv (Standard Python)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd wb-data-explorer
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install packages:**
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Using Conda (Anaconda/Miniconda)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd wb-data-explorer
   ```

2. **Create and activate conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate wb-data-explorer
   ```

### Updating Dependencies

**For venv users:**
- After installing new packages: `pip freeze > requirements.txt`

**For conda users:**
- After installing new packages: `conda env export --no-builds > environment.yml`
- Or manually update `environment.yml`

## Development

Make sure your environment is activated before running any code:
- **venv**: `source venv/bin/activate`
- **conda**: `conda activate wb-data-explorer`

## Dependencies

- pandas - Data manipulation
- numpy - Numerical operations
- plotly - Interactive visualizations
- dash - Web app framework
- requests - HTTP library
- wbgapi - World Bank API wrapper

