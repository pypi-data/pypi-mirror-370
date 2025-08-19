# T1DEXI Processing Utilities

## Overview

This repository contains a collection of Python scripts designed to process the T1DEXI dataset, which is used for
exercise data analysis in individuals with Type 1 Diabetes. These utilities are essential for researchers and clinicians
interested in understanding insulin dynamics and other metabolic parameters during exercise.

<img src="./Flow_of_functionalities.svg?sanitize=true">

## Getting Started

### Prerequisites

- Python 3.6 or newer
- Required Python packages:
    - pandas 2.2.0 or newer
    - numpy
    - pyreadstat
    - xport xpot.v56

### Installation

Clone the repository to your local machine:

```bash
git clone https://gitlab.com/CeADARIreland_Public/netiob.git
```

## Utility Scripts

Each script in the repository serves a specific function in the processing of the T1DEXI dataset. Below are detailed
descriptions and usage instructions for each utility.

### 1. `base_utils.py`

**Description:** This script is responsible for pre-processing and loading data from the T1DEXI dataset for further
analysis. It includes functions to retrieve exercise, glucose, insulin, meal, demographics, and device data, including
our specially processed insulin data which is chunked into 5-minutes delivery intervals (insulin data chunk). It is a
comprehensive tool for initial data handling.

**Key Functions:**

- `get_exercise_data()`: Retrieves exercise-related data.
- `get_glucose_data()`: Pulls glucose measurements.
- `get_insulin_data()`: Fetches insulin administration details.
- `get_meal_data()`: Fetches data on meal intakes.
- `get_demographics_data()`: Provides demographic information of subjects.
- `get_device_data()`: Extracts device usage details.
- `get_insulin_data_chunk()`: Retrieves insulin administration with delivery timestamps chunked into 5-minutes
  intervals.

**How to Use:**

1. Make sure to enter the correct path to the T1DEXI Dataset folder on your local machine in the main `base_utils.py`
   script
2. Import the utilities:
   ```python
   from base_utils import T1DEXI_Utils
   ```
3. Create an instance of `T1DEXI_Utils` and call the desired function. For instance, to fetch meal data:
   ```python
   utils = T1DEXI_Utils()
   meal_data = utils.get_meal_data() 
   # Note that, either of 'aid' or 'non_aid' can be passed as an argument to the function.
   # For example, utils.get_meal_data('aid'), and it would filter the records based on the 
   # category of device (e.g., AID or NON-AID).  Otherwise, all data is returned without 
   # any filter.
   ```
   Alternatively, you can directly use:
   ```python
   meal_data = T1DEXI_Utils().get_meal_data()
   ```
3. For accessing other data files not covered by predefined functions, use:
   ```python
   custom_data = T1DEXI_Utils()._get_data('DM')[0]
   ```

### 2. `insulin_processing.py`

**Description:** This script processes insulin data from Automated Insulin Delivery (AID) pumps used in the T1DEXI
dataset, specifically chunking the data into 5-minute intervals for each type of AID pump. This precision is critical
for subsequent analysis steps, ensuring that the insulin data is uniformly prepared for time-series analysis or other
statistical methods.

**How to Use:**
This utility can be executed as a command-line interface (CLI) tool or imported and run within a Jupyter notebook.
**As a CLI:**

```bash
  python insulin_processing.py
```

After running the command, you will be prompted to enter your T1DEXI folder path.
**In a notebook:**

```python
  from insulin_processing import *
# Follow prompts or additional necessary steps documented in the script comments
```

**Functionality:**

- The script imports necessary functions from `base_utils.py` and utilizes them to load and preprocess the insulin data.
- It includes functions to:
    - Calculate time differences between data points.
    - Chunk insulin records into smaller intervals based on specified conditions (such as insulin type and device type).
    - Save processed data back into a `.xpt` file format suitable for further analysis.

**Output:**

- The script outputs an XPT file containing the processed insulin data, ready for further analysis.

### 3. `baseline_basal_profile.py`

**Description:** This script is designed to generate individual basal profiles for each user from the T1DEXI dataset,
specifically for use during the computation of net Insulin-On-Board (netIOB). The profiles are created by calculating
the hourly average of basal insulin delivery, which are then saved as JSON files for further processing. These profiles
are crucial for comparing actual basal deliveries to predetermined schedules.

**How to Use:**

- This script is typically imported and used in conjunction with the `netIOB_calc.py` script during netIOB computations.
- The primary function, `avg_basal_rate`, processes a user's basal insulin DataFrame to
  generate `basal_rate_profile.json` and `profile.json`, which are then utilized by a JavaScript subprocess for netIOB
  calculations.

**Functionality:**

- **avg_basal_rate(users_basal_record):**
    - **Input:** A DataFrame containing specific basal insulin records for a user.
    - **Output:** Two JSON files:
        - `basal_rate_profile.json`: Contains the basal rate profile structured as a list of dictionaries for each hour.
        - `profile.json`: Contains the `dia` (Duration of Insulin Action) and the basal profile list.

**Process:**

- The script filters and processes the insulin data to align basal flow rate entries with scheduled insulin events based
  on timestamps.
- It then constructs a 24-hour profile for each user, ensuring coverage for all hours and filling any gaps in data.
- Outputs are formatted as JSON files, which are structured to support subsequent computational steps in netIOB
  calculations.

### 4. `netIOB_calc.py`

**Description:** This script is central to the computation of net Insulin-On-Board (netIOB) using data from AID (
Automated Insulin Delivery) pumps in the T1DEXI dataset. It leverages functions from `base_utils.py`
and `baseline_basal_profile.py` to prepare and utilize individual hourly basal profiles for accurate netIOB
calculations.

**How to Use:**
**Important Note:** Before running this script, ensure that insulin data is properly chunked into 5-minute intervals
using `insulin_processing.py`. Save the processed insulin data as `FACM_CHUNK.xpt` in the same folder as other T1DEXI
files. Also, in the `netIOB_calc.py` script, ensure to specify the path to the T1DEXI folder where the `DATA_PATH`
valriable is declared.
To execute the script:
**CLI:**

```bash
  python netIOB_calc.py
```

**In a notebook:**

  ```python
  from netIOB_calc import T1DEXI_netIOB

T1DEXI_netIOB().netIOB('aid') 
  ```

The argument `'aid'` or `'non_aid'` specifies the device category for which netIOB should be calculated.

**Core Functions:**

- `convert_netiob_csv_to_xpt(device_category)`: Converts CSV files containing netIOB data to `.xpt` format.
- `get_last_x_hr(dataframe, real_time, revert_by)`: Retrieves data records from the last 'x' hours.
- `compute_basal_duration(basal_records)`: Calculates durations between consecutive basal insulin deliveries.
- `datetime_to_zoned_iso(time, timezone)`: Formats timestamps for netIOB computation.

**Dependencies:**

- Requires the `ore0` repository, which should be configured correctly in the local environment. This repository is
  crucial for the script’s execution, specifically for the netIOB calculations which rely on JavaScript computations.

**Note:**

- Ensure all configurations and path settings are correctly set up before execution. The script includes conditional
  operations that may need modifications based on specific requirements, such as uncommenting certain blocks for full
  functionality. Get the oref0 repo here: https://github.com/openaps/oref0/tree/master

### 5. `netiob_exercise_processing.py`

**Description:** This script is designed to process T1DEXI data and its corresponding netIOB data. It generates new data
points crucial for analyzing netIOB in relation to users' exercise activity across various time intervals.

**How to Use:**
**Important Note:** Before running this script, ensure that `netIOB_calc.py` is executed beforehand to generate netIOB
data for the category of users to be analysed. Running the script (could take a while to complete) will automatically
save the data as `NETIOB.xpt`.
To execute the script:
**CLI:**

  ```bash
   python netiob_exercise_processing.py
  ```

**In a notebooks:**

  ```python
  from netiob_exercise_processing import T1DEXI_netIOB_exercise

T1DEXI_netIOB_exercise().exercise_netIOB_rel()
  ```

**Core Functions:**
The script imports and create an instance of the `base_utils.py` `class T1DEXI_Utils()`.
It includes the functions to:

- Converts timedelta str to approximate hours
- Computes delta between two values

**Outputs:**

- Generates a new DataFrame from the analysis
- Saves the newly generated DataFrame as `NETIOBEX.xpt` for further use.

### 6. `glucose_variability_analysis.ipynb`

**Description:** This Jupyter notebook contains Python code and scripts for detailed glucose analysis, including data
extraction for AID and non-AID devices, analysis of glucose levels, categorization by insulin device type, and
statistical comparison of various metrics such as Time in Range (TIR) and Time Above Range (TAR) across different
genders and activities. It also includes advanced statistical functions like Shapiro-Wilk, skewness, z-test, and
Mann-Whitney U tests.

**Features:**

- Detailed function annotations for clarity and ease of use.
- Utilizes advanced Python libraries and techniques for in-depth data analysis.
- Provides visualizations and statistical comparisons for a comprehensive understanding of glucose level variations.

**How to Use:**

1. Open the notebook in a Jupyter environment.
2. Call the functions while passing necessary parameters to reproduce the analysis or customize as needed for specific
   research requirements.

## Contributing

We welcome contributions from the community. If you wish to contribute to the project, please fork the repository and
submit a pull request.

## License

This project is licensed under the Apache License 2.0. For more details, please see the LICENSE file in the repository.

## Contributors

CeADAR Connect Group @ CeADAR - Ireland's Centre for AI

- Ahtsham Zafar <ahtsham.zafar@ucd.ie>
- Dr. Abiodun Solanke <abiodun.solanke@ucd.ie>
- Dana Lewis <dana@openaps.org>
- Dr. Arsalan Shahid

## How to build the python package and publish on PyPI

Always update the version in `pyproject.toml`

```shell
python3 -m pip install --upgrade build
python3 -m build
```

```shell
# 2. Upload to PyPI (requires API token)
python3 -m pip install --upgrade twine
python3 -m twine upload dist/*
```

