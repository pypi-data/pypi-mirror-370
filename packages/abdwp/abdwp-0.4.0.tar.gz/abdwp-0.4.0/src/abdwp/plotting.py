import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import importlib.resources


def use_abdwp_style():
    with importlib.resources.path("abdwp.style", "abdwp.mplstyle") as style_path:
        plt.style.use(str(style_path))


def draw_field(ax, show_mound=False, zorder=-1, set_aspect=True):

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
    ax.plot([home[0], first[0]], [home[1], first[1]], "k", zorder=zorder)
    ax.plot([first[0], second[0]], [first[1], second[1]], "k", zorder=zorder)
    ax.plot([second[0], third[0]], [second[1], third[1]], "k", zorder=zorder)
    ax.plot([third[0], home[0]], [third[1], home[1]], "k", zorder=zorder)

    # draw bases
    ax.scatter(*first, color="black", marker="D", s=20, zorder=zorder)
    ax.scatter(*second, color="black", marker="D", s=20, zorder=zorder)
    ax.scatter(*third, color="black", marker="D", s=20, zorder=zorder)

    # draw home plate
    ax.scatter(0, 0, color="black", marker="D", s=20, zorder=zorder)

    # draw mound
    if show_mound:
        ax.scatter(*mound, color="black", marker="_", zorder=zorder)

    # draw outfield arc
    ax.plot(outfield[0], outfield[1], c="k", zorder=zorder)

    # draw infield arc
    ax.plot(infield[0], infield[1], c="k", zorder=zorder)

    # foul lines
    ax.plot([home[0], outfield[0, 0]], [home[1], outfield[1, 0]], "k", zorder=zorder)
    ax.plot([home[0], outfield[0, -1]], [home[1], outfield[1, -1]], "k", zorder=zorder)

    # set equal aspect ratio for proper field proportions
    if set_aspect:
        ax.set_aspect("equal")


def draw_strikezone(
    ax,
    sz_bot=1.5,
    sz_top=3.5,
    sz_left=None,
    sz_right=None,
    zorder=-1,
    fill=True,
    alpha=0.2,
    set_aspect: bool = True,
    **kwargs,
):
    face_color = "none"
    if fill:
        face_color = "tab:gray"
    height = sz_top - sz_bot
    if (sz_left is not None) != (sz_right is not None):
        raise ValueError("Both sz_left and sz_right must be supplied together.")
    if sz_left is not None and sz_right is not None:
        width = sz_right - sz_left
    else:
        width = 20 / 12
        sz_left = -10 / 12
    zone = patches.Rectangle(
        xy=(sz_left, sz_bot),
        width=width,
        height=height,
        facecolor=face_color,
        edgecolor="black",
        linewidth=1,
        alpha=alpha,
        zorder=zorder,
        **kwargs,
    )
    ax.add_patch(zone)
    if set_aspect:
        ax.set_aspect("equal")
    return zone
