import pandas as pd

df = pd.read_excel('UV-Sheets_protocol.xlsx')
print("=" * 80)
print("EXCEL FILE ANALYSIS")
print("=" * 80)
print(f"\nTotal rows: {len(df)}\n")
print("Uploaded column - unique values and counts:")
uploaded_counts = df['Uploaded'].value_counts(dropna=False)
print(uploaded_counts)

print("\n\nFirst 10 rows - Code and Uploaded columns:")
print(df[['Code', 'Uploaded']].head(10).to_string())

print("\n\nRows with Number of Sheets:")
print(df[['Code', 'Number of Sheets', 'Uploaded']].to_string())

print("\n\nPending rows (where Uploaded != 'Yes'):")
pending_mask = df['Uploaded'].astype(str).str.strip().str.lower() != 'yes'
pending_count = pending_mask.sum()
print(f"Pending rows: {pending_count}")
if pending_count > 0:
    print(df[pending_mask][['Code', 'Uploaded', 'Number of Sheets']].to_string())
