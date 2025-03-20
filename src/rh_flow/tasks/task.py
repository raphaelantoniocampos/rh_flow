from pandas import DataFrame


class Task:
    def __init__(self, name: str, df: DataFrame, option: str):
        self.name = name
        self.df = df
        self.option = option

    def is_empty(self):
        try:
            return self.df.empty
        except AttributeError:
            return True

    def __len__(self):
        return len(self.df)

    def get_ignore_dict(self):
        ignore_dict = {}
        if self.name == "new":
            ignore_dict = {
                str(series["id"]): {
                    "id": series["id"],
                    "admission_date": series["admission_date"],
                    "name": series["name"],
                    "binding": series["binding"],
                }
                for _, series in self.df.iterrows()
            }
        if self.name == "dismissed":
            ignore_dict = {
                str(series["id"]): {
                    "id": series["id"],
                    "admission_date": series["admission_date"],
                    "name": series["name"],
                    "binding": series["dismissal_date"],
                }
                for _, series in self.df.iterrows()
            }
        return ignore_dict

    def get_ignore_list(self, ignore_dict: dict):
        return [
            f"{id} - {data['admission_date']} - {data['name']} - {data['binding']}"
            for id, data in ignore_dict.items()
        ]

    def update_df(self, df: DataFrame):
        self.df = df
        self.option = self._get_option()
        return self

    def __str__(self):
        return f"""
-name: {self.name}
-df: {self.df}
-option: {self.option}
-"""
