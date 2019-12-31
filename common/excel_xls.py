import datetime
import os
import xlrd
import xlwt

class XLS():
    def __init__(self):
        self.key_word = ""
        self.file=""
        self.sheet=""

    def generate_excel_file_name(self):
        return os.path.join(os.getcwd(),self.key_word+"_"+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".xls")

def read_excel_xls(excel_path,sheet_name="sheet1"):
    wb = xlrd.open_workbook(excel_path)
    ws = wb.sheet_by_name(sheet_name)
    rows=ws.nrows
    data=[]
    for i in range(rows):
        data.append(ws.row_values(i))
    return data

def get_excel_rows_cols(excel_path,sheet_name="sheet1"):
    wb = xlrd.open_workbook(excel_path)
    ws = wb.sheet_by_name(sheet_name)
    rows = ws.nrows
    cols=ws.ncols
    return rows,cols


def write_excel_xls(excel_path,data,start_row=0,start_col=0,sheet_name="sheet1"):
    wb = xlwt.Workbook()
    ws=wb.add_sheet(sheet_name)
    for i in range(len(data)):
        for j in range(len(data[i])):
            ws.write(i+start_row,j+start_col,data[i][j])
    wb.save(excel_path)

if __name__ == '__main__':
    excel_paths=os.getcwd() + "\\1.xls"
    datas=read_excel_xls(excel_paths)
    out_path="ttt.xls"
    write_excel_xls(out_path,datas)
    print("")