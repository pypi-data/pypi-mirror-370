"""
pip install pandas==1.3.4
pip install openpyxl==3.0.9
pip install XlsxWriter==3.0.2
"""
import pandas as pd


class Excel(object):
    """excel读写"""

    def __init__(self, file_name):
        self.file_name = file_name

    def read_all(self, sheet_name=0):
        df = pd.read_excel(self.file_name, sheet_name=sheet_name)
        res = df.values.tolist()
        return res

    def read_row_index(self, row_index: int, sheet_name=0):
        """
        index：第一行（index=0）需要有标题，默认会忽略，取值从1开始
        """
        df = pd.read_excel(self.file_name, sheet_name=sheet_name)
        res = df.values[row_index-1].tolist()
        return res

    def read_col_index(self, col_index: int, sheet_name=0):
        """
        index：从1开始
        """
        df = pd.read_excel(self.file_name, usecols=[col_index-1], sheet_name=sheet_name)
        res = [r[0] for r in df.values.tolist()]
        return res

    def read_col_name(self, col_name: str, sheet_name=0):
        df = pd.read_excel(self.file_name, sheet_name=sheet_name)
        res = df[col_name].values.tolist()
        return res

    def write(self, data: dict, sheet_name='sheet1', column_width=20):
        """
        数据格式：{
            '标题列1': ['张三', '李四'],
            '标题列2': [80, 90]
        }
        """

        df = pd.DataFrame(data)
        writer = pd.ExcelWriter(self.file_name)
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        sheet = writer.sheets.get(sheet_name)
        for index in range(len(df)):
            # print(index, value)
            for i in range(len(df.columns)):
                sheet.set_column(index+1, i, column_width)
        writer.save()

    def write_sheets(self, sheet_dict: dict, column_width=20):
        """
        sheet_dict: {
            'sheet1_name': {'标题列1': ['张三', '李四'], '标题列2': [80, 90]},
            'sheet2_name': {'标题列3': ['王五', '郑六'], '标题列4': [100, 110]}
        }
        """
        writer = pd.ExcelWriter(self.file_name)
        for sheet_name, sheet_data in sheet_dict.items():
            df = pd.DataFrame(sheet_data)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            sheet = writer.sheets.get(sheet_name)
            for index in range(len(df)):
                for i in range(len(df.columns)):
                    sheet.set_column(index + 1, i, column_width)
        writer.save()

    def get_sheet_names(self):
        return list(pd.read_excel(self.file_name, sheet_name=None))


class CSV(object):
    """csc读写"""

    def __init__(self, file_name):
        self.file_name = file_name

    def read_all(self):
        df = pd.read_csv(self.file_name)
        res = df.values.tolist()
        return res

    def read_row_index(self, row_index: int):
        """
        index: 第一行（index=0）需要有标题，默认会忽略，取值从1开始
        """
        df = pd.read_csv(self.file_name)
        res = df.values[row_index-1].tolist()
        return res

    def read_col_index(self, col_index: int):
        """
        index：从1开始
        """
        df = pd.read_csv(self.file_name, usecols=[col_index-1])
        res = [r[0] for r in df.values.tolist()]
        return res

    def read_col_name(self, col_name: str):
        df = pd.read_csv(self.file_name, usecols=[col_name])
        res = [r[0] for r in df.values.tolist()]
        return res

    def write(self, data: dict):
        """
        数据格式：{
            '标题列1': ['张三', '李四'],
            '标题列2': [80, 90]
        }
        """
        df = pd.DataFrame(data)
        df.to_csv(self.file_name, index=False)


if __name__ == '__main__':
    pass

