from openpyxl import worksheet
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

border = Border(
    left=Side(style="thick"),
    right=Side(style="thick"),
    top=Side(style="thick"),
    bottom=Side(style="thick")
)

def add_border( sheet: worksheet,
                min_row: int,
                max_row: int,
                min_col: int,
               max_col: int ):
    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            cell = sheet.cell(row=row, column=col)
            if row == min_row:  # Top border
                cell.border = Border(top=border.top, left=cell.border.left,
                                     right=cell.border.right, bottom=cell.border.bottom)
            if row == max_row:  # Bottom border
                cell.border = Border(bottom=border.bottom, left=cell.border.left,
                                     right=cell.border.right, top=cell.border.top)
            if col == min_col:  # Left border
                cell.border = Border(left=border.left, top=cell.border.top,
                                     bottom=cell.border.bottom, right=cell.border.right)
            if col == max_col:  # Right border
                cell.border = Border(right=border.right, top=cell.border.top,
                                     bottom=cell.border.bottom, left=cell.border.left)
