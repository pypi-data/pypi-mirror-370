import os


# TODO: check in jupyter AND terminal
# TODO: check with datetimes
# TODO: note mostly GPT coded
def glimpse(df, col_width=None, type_width=None, num_examples=5):
    try:
        terminal_width = os.get_terminal_size().columns
    except Exception:
        terminal_width = 120
    if col_width is None:
        col_width = max([len(col) for col in df.columns])
    if type_width is None:
        type_width = max([len(str(df[col].dtype)) for col in df.columns])
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"")
    for col in df.columns:
        if len(col) > col_width:
            col_display = col[: col_width - 1] + "…"
        else:
            col_display = col
        col_display_bold = f"\033[1m{col_display}\033[0m"
        column = f"{col_display_bold:<{col_width + 9}}"
        dtype = f"{str(df[col].dtype):<{type_width}}"
        values = df[col].head(num_examples).tolist()
        values_str = str(values)
        line = f"{column} {dtype} {values_str}"
        if len(line) > terminal_width:
            line = line[: terminal_width - 3] + "..."
        print(line)
