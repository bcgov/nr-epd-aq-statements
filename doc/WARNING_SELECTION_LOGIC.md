# Warning Selection Logic

This document outlines how warnings are selected for inclusion in the Recent Warnings and Wildfire Smoke Warnings lists by the `construct-lists.py` script.

## Overview

The script processes input files from Quarto's project input files and categorizes them according to two main criteria:

1. **Recent Warnings**: Warnings issued within the past 5 days (configurable via `RECENT_THRESHOLD_DAYS`)
2. **Wildfire Smoke Warnings**: Specifically categorized wildfire smoke advisories with special handling

## Selection Flowchart

```mermaid
flowchart TD
    A[Start Processing File] --> B{Has YAML Header?}
    B -->|No| Z[Skip File]
    B -->|Yes| C[Extract Header Metadata]
    
    C --> F1{Is type 'wildfire_smoke'?}
    F1 -->|Yes| D1{Has 'date' Metadata?}
    F1 -->|No| D2{Has 'date' Metadata?}
    
    D1 -->|No| Z2[Skip Wildfire Processing]
    D1 -->|Yes| E1[Calculate Age in Days]
    
    E1 --> G{Has ICE = 'issue'?}
    
    G -->|Yes| H[Set Threshold = 1 day]
    G -->|No| I[Use Default Threshold: 5 days]
    
    H --> K{Age < Threshold?}
    I --> K
    
    K -->|Yes| L[Add to WILDFIRE_SMOKE_WARNINGS]
    K -->|No| Z3[Skip Wildfire List]
    
    D2 -->|No| Z4[Skip Recent Processing]
    D2 -->|Yes| E2[Calculate Age in Days]
    
    E2 --> J{Age < RECENT_THRESHOLD_DAYS?}
    
    L --> R{Is type 'wildfire_smoke'?}
    Z3 --> R
    
    R -->|Yes| S{Has ICE = 'issue'?}
    R -->|No| J
    
    S -->|Yes| T{Age >= 1 day?}
    S -->|No| J
    
    T -->|Yes| O[Skip Recent List]
    T -->|No| J
    
    J -->|Yes| N[Add to RECENT_WARNINGS]
    J -->|No| O
```

## Selection Logic Details

### For Any Warning

1. File is processed if it has a valid YAML header.
2. Essential metadata is extracted (path, title, type, ice, date, location).
3. Processing branches into two separate evaluation paths:
   - Evaluation for Wildfire Smoke Warnings
   - Evaluation for Recent Warnings

### For Wildfire Smoke Warnings

1. The code first checks if the file has `type: wildfire_smoke` metadata.
2. If it does, the code then checks if the file has a `date` metadata field.
3. If a date exists, age is calculated by comparing the warning's date to today's date (in BC timezone).
4. Different thresholds apply:
   - Default: Include if less than 5 days old (`RECENT_THRESHOLD_DAYS`)
   - Special case: For warnings with `ice: issue`, include only if less than 1 day old
5. If the age is less than the applicable threshold, the warning is added to the Wildfire Smoke Warnings list.

### For Recent Warnings

1. All files with a `date` metadata field are considered for the Recent Warnings list.
2. Special handling for wildfire smoke warnings:
   - If it's a wildfire smoke warning with `ice: issue` and is 1+ days old, it's explicitly excluded
   - This is done to prevent older "issue" wildfire smoke warnings from appearing in the recent list
3. Otherwise, any warning less than 5 days old (`RECENT_THRESHOLD_DAYS`) is included in the Recent Warnings list.

## Technical Implementation

The script:
1. Reads input files from `QUARTO_PROJECT_INPUT_FILES` environment variable
2. Extracts YAML headers using regex
3. Applies the selection logic
4. Outputs two YAML files:
   - `_recent_warnings.yaml` for recent warnings
   - `_wildfire.yaml` for wildfire smoke warnings

These output files are then used in custom listings within the Quarto site.
