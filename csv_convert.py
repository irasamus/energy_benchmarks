import json
import pandas as pd
from datetime import datetime

with open("raw_energy_data.json", "r") as f:
    raw_data = json.load(f)

rows = []
for entry in raw_data:
    # Parse ISO timestamp to Unix seconds
    ts_str = entry['timestamp'].split('+')[0]
    unix_ts = datetime.fromisoformat(ts_str).timestamp()
    rows.append({"timestamp_unix": unix_ts, "watts": entry['value']})

df = pd.DataFrame(rows).sort_values("timestamp_unix")
df.to_csv("verify_energy.csv", index=False)
print("Saved to verify_energy.csv. Open this to see the raw data!")