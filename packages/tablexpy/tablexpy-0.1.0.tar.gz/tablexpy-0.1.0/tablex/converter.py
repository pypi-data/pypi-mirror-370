import csv
import json
import pandas as pd

class TableX:
    # ---------------- CSV <-> JSON ----------------
    @staticmethod
    def csv_to_json(csv_file, json_file, pretty=True, indent=4):
        """Convert CSV → JSON with optional pretty formatting"""
        df = pd.read_csv(csv_file)
        records = df.to_dict(orient="records")
        with open(json_file, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(records, f, indent=indent, ensure_ascii=False)
            else:
                json.dump(records, f, ensure_ascii=False)
        return records

    @staticmethod
    def json_to_csv(json_file, csv_file):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False)

    # ---------------- JSON <-> Excel ----------------
    @staticmethod
    def json_to_excel(json_file, excel_file):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df.to_excel(excel_file, index=False)

    @staticmethod
    def excel_to_json(excel_file, json_file, sheet_name=0, pretty=True, indent=4):
        """Convert Excel → JSON with optional pretty formatting"""
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        records = df.to_dict(orient="records")
        with open(json_file, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(records, f, indent=indent, ensure_ascii=False)
            else:
                json.dump(records, f, ensure_ascii=False)
        return records

    # ---------------- CSV <-> Excel ----------------
    @staticmethod
    def csv_to_excel(csv_file, excel_file):
        df = pd.read_csv(csv_file)
        df.to_excel(excel_file, index=False)

    @staticmethod
    def excel_to_csv(excel_file, csv_file):
        df = pd.read_excel(excel_file)
        df.to_csv(csv_file, index=False)

    # ---------------- Utility functions ----------------
    @staticmethod
    def pretty_print_json(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(json.dumps(data, indent=4))

    @staticmethod
    def flatten_json(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        flat = {}

        def _flatten(obj, prefix=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    _flatten(v, prefix + k + ".")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    _flatten(v, prefix + str(i) + ".")
            else:
                flat[prefix[:-1]] = obj

        _flatten(data)
        return flat

    @staticmethod
    def unflatten_json(flat_dict):
        result = {}

        for k, v in flat_dict.items():
            keys = k.split(".")
            d = result
            for i, part in enumerate(keys[:-1]):
                if part.isdigit():
                    part = int(part)
                    # Ensure d is a list
                    if not isinstance(d, list):
                        d_parent = []
                        # If d was empty dict, replace it with list
                        # (used when switching between object/list)
                        for _ in range(part + 1):
                            d_parent.append({})
                        # Put existing dict inside
                        d_parent[0] = d
                        d = d_parent

                    while len(d) <= part:
                        d.append({})
                    if not isinstance(d[part], dict):
                        d[part] = {}
                    d = d[part]
                else:
                    if part not in d:
                        d[part] = {}
                    d = d[part]

            last_key = keys[-1]
            if last_key.isdigit():
                last_key = int(last_key)
                if not isinstance(d, list):
                    d = []
                while len(d) <= last_key:
                    d.append({})
                d[last_key] = v
            else:
                d[last_key] = v

        return result

