import os
import pandas as pd
import tempfile
import zipfile
from lxml import etree
import json, io
from pyarrow import feather

import warnings
warnings.filterwarnings("ignore")

JSON_FILE = "Health_Data/config.json"
Date_Format = "%Y-%m-%d %H:%M:%S %z"        
DATETIME_KEYS = ["startDate", "endDate"]
NUMERIC_KEYS = ["value"]
OTHER_KEYS = ["type", "sourceName","device", "unit", "MetadataEntry", "HeartRateVariabilityMetadataList"]
ALL_KEYS = OTHER_KEYS + DATETIME_KEYS + NUMERIC_KEYS

def Write_JSON(Watch, First_Instance, Last_Instance):
    try:
        Data = {"Apple Watch Name" : Watch, "Data Upload Date" : "Timestamp", "First Date Instance" : First_Instance, "Last Date Instance" : Last_Instance}
        obj = json.dumps(Data, indent = 4)
        with open(JSON_FILE, "w") as f:
            f.write(obj)
    except Exception as e:
        print(f"{e} error with json")


def health_xml_to_feather(zip_str, output_file, remove_zip=False):
    with tempfile.TemporaryDirectory() as tmpdirname:
        f = zipfile.ZipFile(zip_str, "r")
        f.extractall(tmpdirname)
        xml_path = os.path.join(tmpdirname, "apple_health_export/export.xml")
        tree = etree.parse(xml_path)
        records = tree.xpath("//Record")
        df = pd.DataFrame([{key: r.get(key) for key in ALL_KEYS}
                           for r in records])

        # Clean up key types
        for k in DATETIME_KEYS:
            df[k] = pd.to_datetime(df[k])
        for k in NUMERIC_KEYS:
            # some rows have non-numeric values, so coerce and drop NaNs
            df[k] = pd.to_numeric(df[k], errors="coerce")
            df = df[df["value"].notnull()]
            df = df.reset_index()
            del df["index"]
            df['startDate'] = pd.to_datetime(df['startDate'],format=Date_Format)
            df['endDate'] = pd.to_datetime(df['endDate'],format=Date_Format)
            df['year'] = df['startDate'].dt.year
            df['month'] = df['startDate'].dt.to_period('M')

            df["month"] = df["month"].map(str)

            df['day'] = df['startDate'].dt.day
            df['hour'] = df['startDate'].dt.hour
            df['DayofWeek'] = df['startDate'].dt.day_name()
            df = df[["type", "sourceName", 'month',"day", "year", "hour", "DayofWeek", "startDate", "endDate", "value", "unit", "device", "MetadataEntry", "HeartRateVariabilityMetadataList"]]
            Source_List = df["sourceName"].unique().tolist()
            Location = [i for i, string in enumerate(Source_List) if 'Watch' in string]
            Watch = Source_List[int(Location[0])]
            df = df[df["sourceName"] == Watch]
            df.reset_index(0, inplace=True)
            del df["index"]

            df.to_feather(f"Data/{output_file}")

        return df

