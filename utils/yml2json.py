import yaml
import json

def yml_to_json(file):
    fileName = file.split(".")[0] + ".json"
    data = ""
    with open(file, encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.Loader)
    with open(fileName, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

yml_to_json("config/devices.yml")