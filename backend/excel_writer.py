from pandas import DataFrame
import pandas as pd
import xlsxwriter as xl


class ExcelDataframeWriter:
    def __init__(self, path) -> None:
        self.writer = pd.ExcelWriter(path, mode="w", engine="xlsxwriter")

    def generate_doc(self, dataframe: DataFrame, sheet_title: str, report_title: str):
        dataframe.to_excel(
            excel_writer=self.writer,
            sheet_name=sheet_title,
            startrow=2,
            header=False,
            index=False,
        )

        column_settings = [{"header": column} for column in dataframe.columns]
        workbook: xl.Workbook = self.writer.book  # type: ignore
        worksheet: xl.Workbook.worksheet_class = self.writer.sheets[sheet_title]
        max_row, max_col = dataframe.shape
        title = report_title.title()
        format = workbook.add_format({"bold": True, "font_size": 14})
        worksheet.merge_range(
            first_row=0,
            first_col=0,
            last_col=max_col - 1,
            last_row=0,
            data=title,
            cell_format=format,
        )
        column_settings = [{"header": column} for column in dataframe.columns]
        worksheet.add_table(
            1, 0, max_row + 1, max_col - 1, {"columns": column_settings}
        )
        worksheet.set_column(0, max_col - 1, 12)
        worksheet.autofit()

    def close(self):
        self.writer.close()

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self.writer.close()
