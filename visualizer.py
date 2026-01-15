import pandas
import json

sort_by = input("what to sort by\n")
with open("data.json") as f:
    data = json.load(f)

df = pandas.DataFrame.from_dict(data["tracks"],orient="index")

df_sorted = df.sort_values(by=sort_by,ascending=False)
data["tracks"] = df_sorted.to_dict(orient="index")

with open("sorted.json",'w') as f:
    json.dump(data,f,indent=4)


