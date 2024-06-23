import json


def load_data(DataPath: str):
    try:
        with open(DataPath, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File {DataPath} not found. Error in LoadInterface() LangInterface.py")


data = load_data("data.json")["Test"]
print(data)