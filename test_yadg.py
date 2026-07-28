import yadg
import sys

file_path = r"e:\Github_repositories\EIS_analysis\data\20260722_C23_SMSP20_operando_EIS_C01.mpr"
try:
    data = yadg.extract(filetype="eclab.mpr", file=file_path)
    print("Available arrays:")
    print(list(data.data_vars))
    
    # Try to see if it has 'cycle number' or 'loop number'
    if 'cycle number' in data.data_vars:
        print("\nCycle numbers:", set(data['cycle number'].values))
except Exception as e:
    print(f"Failed to read with yadg: {e}")
