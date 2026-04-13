import pandas as pd

input_file = "../output/sightengine-raw.json"
output_file = "../output/sightengine-summary.csv"

# Load JSON
df = pd.read_json(input_file)

# Flatten nested structure
df_flat = pd.json_normalize(df.to_dict(orient="records"))
#print(df_flat.columns)

# Fields to extract (use dot notation)
fields = ["media.uri", "type.ai_generated"]

df_filtered = df_flat[fields]

# Optional: rename columns for cleaner CSV
df_filtered.columns = ["file", "ai_score"]

df_filtered.to_csv(output_file, index=False)

print(f"CSV file saved to {output_file}")
