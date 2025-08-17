def colnum_to_excel_col(n):
    """1-based column number to Excel column letter"""
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string
