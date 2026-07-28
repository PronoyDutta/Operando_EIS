import eclabfiles as ecf
import traceback

mpr_file = r"e:\Github_repositories\EIS_analysis\data\20260722_C23_SMSP20_operando_EIS_C01.mpr"
try:
    df = ecf.to_df(mpr_file)
    print("Columns available:")
    print(df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head())
except Exception as e:
    print(f"Failed to read with eclabfiles!")
    traceback.print_exc()
