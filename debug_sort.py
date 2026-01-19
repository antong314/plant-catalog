import pandas as pd
import re

def parse_lifespan(val: str):
    if not val:
        return float('inf')
    
    s = val.lower()
    
    if 'annual' in s:
        return 0.1
    if 'biennial' in s:
        return 0.2
        
    nums = re.findall(r'\d+', s)
    if not nums:
        return 9999.0
    
    primary_num = float(nums[0])
    
    if 'month' in s and 'year' not in s:
        return primary_num / 12.0
        
    return primary_num

df = pd.read_csv("tropical-plants.csv").fillna("")
unique_lifespans = df["Lifespan"].unique().tolist()
sorted_lifespans = sorted(unique_lifespans, key=parse_lifespan)

print("Sorted lifespans:")
for l in sorted_lifespans:
    print(f"'{l}' -> {parse_lifespan(l)}")
