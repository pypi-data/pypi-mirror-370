import os
import numpy as np


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


def draw_field(ax, show_mound=False):

    # setup
    base_distance = 90
    mound_distance = 60.5
    outfield_radius = 400
    infield_radius = 200

    # coordinates of bases and mound
    home = np.array([0, 0])
    first = np.array([base_distance / np.sqrt(2), base_distance / np.sqrt(2)])
    second = np.array([0, base_distance * np.sqrt(2)])
    third = np.array([-base_distance / np.sqrt(2), base_distance / np.sqrt(2)])
    mound = np.array([0, mound_distance])

    # outfield arc
    theta = np.linspace(np.pi / 4, 3 * np.pi / 4, 200)
    outfield_x = outfield_radius * np.cos(theta)
    outfield_y = outfield_radius * np.sin(theta)
    outfield = np.vstack([outfield_x, outfield_y])

    # infield arc
    infield_x = infield_radius * np.cos(theta)
    infield_y = infield_radius * np.sin(theta)
    infield = np.vstack([infield_x, infield_y])

    # draw base paths
    ax.plot([home[0], first[0]], [home[1], first[1]], "k")
    ax.plot([first[0], second[0]], [first[1], second[1]], "k")
    ax.plot([second[0], third[0]], [second[1], third[1]], "k")
    ax.plot([third[0], home[0]], [third[1], home[1]], "k")

    # draw bases
    ax.scatter(*first, color="black", marker="D", s=20)
    ax.scatter(*second, color="black", marker="D", s=20)
    ax.scatter(*third, color="black", marker="D", s=20)

    # draw home plate
    ax.scatter(0, 0, color="black", marker="D", s=20)

    # draw mound
    if show_mound:
        ax.scatter(*mound, color="black", marker="_")

    # draw outfield arc
    ax.plot(outfield[0], outfield[1], c="k")

    # draw infield arc
    ax.plot(infield[0], infield[1], c="k")

    # foul lines
    ax.plot([home[0], outfield[0, 0]], [home[1], outfield[1, 0]], "k")
    ax.plot([home[0], outfield[0, -1]], [home[1], outfield[1, -1]], "k")

    # set equal aspect ratio for proper field proportions
    ax.set_aspect("equal")
