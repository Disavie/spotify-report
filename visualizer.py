import pandas
import json

def parse_that_shit(sortby):
    with open("data.json") as f:
        data = json.load(f)

    df = pandas.DataFrame.from_dict(data["tracks"],orient="index")

    df_sorted = df.sort_values(by=sortby,ascending=False)
    data["tracks"] = df_sorted.to_dict(orient="index")

    with open("sorted.json",'w') as f:
        json.dump(data,f,indent=4)


