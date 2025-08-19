__all__ = [
    'color_palettes',
    'color_cyclers',
    'color_iters',
    'set_color_cycler',
    'set_latex_font',
    'PiecewiseLinearNorm',
    'remove_repeated_legend',
    'filter',
    'bar_plot_compare',
    'plot_dictionary_2d',
    'plot_complex_3d_bar',
]


import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D 
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.axes import Axes
from matplotlib import rcParams
from cycler import cycler
from itertools import cycle

from typing import Dict, List, Tuple

from chencrafts.toolbox.data_processing import nd_interpolation

# color cyclers
color_palettes = dict(
    PGL = [
        "#0c2e6d", "#b63566", "#91adc2", "#e9c2c3", "#AEB358"],
    green_to_red = [
        "#001219", "#005f73", "#0a9396", "#94d2bd", "#e9d8a6", 
        "#ee9b00", "#ca6702", "#bb3e03", "#9b2226"],
    sunset = [
        "#F8B195", "#F67280", "#C06C84", "#6C5B7B", "#355C7D"],
    hotel_70s = [
        "#448a9a", "#fb9ab6", "#e1cdd1", "#e1b10f", "#705b4c"],
    blue_to_red = [
        "#e63946", "#a8dadc", "#457b9d", "#a7bb40", "#3d1645"],
    colorblind_1 = [    # from https://arxiv.org/abs/2107.02270
        "#3f90da", "#ffa90e", "#bd1f01", "#832db6", "#94a4a2", 
        "#a96b59", "#e76300", "#b9ac70", "#717581", "#92dadd",],
    C2QA = [
        '#007A86', '#F9B211', '#A12731', '#78C0E0', '#4A0E4E'
    ],
)
color_cyclers = dict([
    (key, cycler(color = color_palettes[key])) for key in color_palettes
])
color_iters = dict([
    (key, cycle(color_palettes[key])) for key in color_palettes
])
def set_color_cycler(
    cycler_name: str | List[str]
):
    """
    Available cycler names: 
    PGL, green_to_red, sunset, hotel_70s, blue_to_red, colorblind_1, C2QA
    """
    if isinstance(cycler_name, str):
        mpl.rcParams["axes.prop_cycle"] = color_cyclers[cycler_name]
        plt.rcParams["axes.prop_cycle"] = color_cyclers[cycler_name]
    elif isinstance(cycler_name, list):
        mpl.rcParams["axes.prop_cycle"] = cycler(color = cycler_name)
        plt.rcParams["axes.prop_cycle"] = cycler(color = cycler_name)
        
def set_latex_font():
    """
    Sets Matplotlib rcParams to use LaTeX rendering for consistent fonts
    in both math expressions and normal text, matching LaTeX's default
    (Computer Modern).
    
    Note: This requires a LaTeX installation on your system.
    """
    mpl.rcParams.update({
        'text.usetex': True,
        # Optional: Specify font family, but with usetex=True, LaTeX handles it
        'font.family': 'serif',
        'font.serif': ['Computer Modern'],
        # You can add more if needed, e.g., for sans-serif or monospace
        'font.sans-serif': ['Computer Modern Sans Serif'],
        'font.monospace': ['Computer Modern Typewriter'],
    })
    # Optionally, add LaTeX packages to preamble if needed, e.g.:
    mpl.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'
    
def remove_repeated_legend(ax=None):
    """remove repeated legend"""
    if ax is None:
        ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())

def filter(c, filter_name):
    if filter_name in ["translucent", "trans"]:
        r, g, b, a = c
        return [r, g, b, a * 0.2]
    elif filter_name in ["emphsize", "emph"]:
        r, g, b, a = c
        factor = 3
        return [r ** factor, g ** factor, b ** factor, a]

# class Cmap():
#     def __init__(
#         self, 
#         upper: float, 
#         lower: float = 0, 
#         cmap_name="rainbow"
#     ):
#         self.upper = upper
#         self.lower = lower
#         self.cmap_name = cmap_name

#         self.cmap = colormaps[self.cmap_name]
#         self.norm = plt.Normalize(self.lower, self.upper)
#         self.mappable = plt.cm.ScalarMappable(norm=self.norm, cmap=self.cmap)
    
#     def __call__(self, val):
#         # return self.mappable.cmap(val)
#         return self.cmap(self.norm(val))
# useless now, can be simply replaced by plt.cm.get_cmap(cmap_name)


class PiecewiseLinearNorm:
    def __init__(
        self, 
        value_list: List[float] | np.ndarray,
        color_list: List[float] | np.ndarray,
        clip: bool = False, 
    ):
        assert len(value_list) == len(color_list), "value_list and color_list must have the same length."
        
        # Sorting the lists based on the value_list
        sorted_indices = np.argsort(value_list)
        self.value_list = np.array(value_list)[sorted_indices]
        self.color_list = np.array(color_list)[sorted_indices]
        self.clip = clip

    def __call__(self, value: float) -> float:
        if self.clip:
            if value < self.value_list[0]:
                return self.color_list[0]
            elif value > self.value_list[-1]:
                return self.color_list[-1]
        
        return np.interp(value, self.value_list, self.color_list)

    def inverse(self, color: float) -> float:
        return np.interp(color, self.color_list, self.value_list)


def bar_plot_compare(
    var_list_dict: Dict[str, np.ndarray],
    x_ticks: List = None,
    ax = None,
    figsize = None, 
    dpi = None,
    x_tick_rotation = 45, 
):
    """
    The var_list_dict should be {labels: a series of value to compare}. 

    Note: such function can be realized in pandas by DataFrame.plot(kind="bar")
    """
    # plot 
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)

    x_len = len(x_ticks)
    for key, val in var_list_dict.items():
        assert len(x_ticks) == len(val), (f"x_lables should have the same length with"
        f"the data to be plotted, exception occurs for {key}")

    compare_num = len(var_list_dict)
    plot_width = 1 / (compare_num + 1)
    plot_x = np.linspace(0, x_len-1, x_len) + 0.5 * plot_width
    
    for i, (key, val) in enumerate(var_list_dict.items()):
            
        ax.bar(
            x = plot_x + i * plot_width, 
            height = val,
            width = plot_width,
            align = "edge",
            label = key
        )
            
        ax.set_xticks(plot_x + plot_width * compare_num / 2)
        ax.set_xticklabels(
            x_ticks, 
            rotation=x_tick_rotation, 
            rotation_mode="anchor", 
            horizontalalignment="right", 
            verticalalignment="top", 
            fontsize=rcParams["axes.labelsize"]
        )

        ax.legend()

def plot_dictionary_2d(
    dict: Dict[str, np.ndarray], 
    xy_mesh: List[np.ndarray],
    xy_label: List[str] = ["", ""], 
    single_figsize = (3, 2.5), 
    cols = 3, 
    place_a_point: Tuple[float, float] = tuple(),     # plot a point in the figure
    show_value = False,                   # plot the number number near the destination of the trajectory  
    slc = slice(None),                            # slice the value stored in the dictionary before any processing
    slc_2d = slice(None),  # for zooming in the plots
    contour_levels = 0,
    cmap = "viridis",
    vmin = None,
    vmax = None,
    dpi = 150,
    save_filename = None,
):
    """
    this function plot meshes from a dictionary

    place_a_point should be (x, y)

    """

    rows = np.ceil(len(dict) / cols).astype(int)
    fig, axs = plt.subplots(rows, cols, figsize=(cols*single_figsize[0], rows*single_figsize[1]), dpi=dpi)

    X_mesh, Y_mesh = xy_mesh
    X_mesh, Y_mesh = X_mesh[slc][slc_2d], Y_mesh[slc][slc_2d]
    x_name, y_name = xy_label

    ax_row, ax_col = 0, 0
    for key, full_value in dict.items():
        if rows == 1:
            ax: Axes = axs[ax_col]
        else:
            ax: Axes = axs[ax_row, ax_col]
        value = full_value[slc][slc_2d]

        # base value
        try:
            cax = ax.pcolormesh(X_mesh, Y_mesh, value, vmin=vmin, vmax=vmax, cmap=cmap)
        except (ValueError, IndexError):
            print("Error, Value to be plotted has the shape", value.shape, ", key: ", key)
        # except TypeError:
        #     print("TypeError, key: ", key, "value: ", value, "X, Y mesh", X_mesh, Y_mesh)
        fig.colorbar(cax, ax=ax)

        # contour
        if contour_levels > 0 and np.std(value) > 1e-14:
            try:
                CS = ax.contour(X_mesh, Y_mesh, value, cmap="hsv", levels=contour_levels)
                ax.clabel(CS, inline=True, fontsize=7)
                # fig.colorbar(cax_cont, ax=ax)
            except IndexError as err: # usually when no contour is found\
                print(f"In {key}, except IndexError: {err}")
                pass

        # trajectory
        if place_a_point != ():
            px, py = place_a_point
            ax.scatter(px, py, c="white", s=8)
            if show_value:
                interp = nd_interpolation(
                    [X_mesh, Y_mesh],
                    value
                )
                val = interp(px, py)
                if np.abs(val) >= 1e-2 and np.abs(val) < 1e2: 
                    text = f"  {val:.3f}"
                else:
                    text = f"  {val:.1e}"
                ax.text(px, py, text, ha="left", va="center", c="white", fontsize=7)

        # labels 
        ax.set_title(key)
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)
        ax.grid()

        ax_col += 1
        if ax_col % cols == 0:
            ax_col = 0
            ax_row += 1

    plt.tight_layout()

    if save_filename is not None:
        plt.savefig(save_filename)

    plt.show()

def plot_complex_3d_bar(
    complex_data: np.ndarray, 
    max_val: float | None = None, 
    min_val: float | None = None,
    ax: Axes3D | None = None, 
    cmap: str = 'hsv', 
    labels_x: List[str] | None = None, 
    labels_y: List[str] | None = None, 
    alpha: float = 0.8, 
    bar_width: float = 0.7, 
    show_colorbar: bool = True,
    show_gridlines: bool = True, 
    bar_edge_color: str = 'black', 
    bar_edge_width: float = 0.5
):
    """
    Create a 3D bar plot for visualizing a complex 2D array.
    
    Special features:
    - If the value is larger than max_val, the bar will be truncated and 
        the overflow will be indicated by a diagonal hatching.
    
    Parameters:
    -----------
    complex_data : 2D ndarray of complex numbers
        The complex data to visualize
    max_val : float, optional
        The maximum absolute value for scaling. If None, uses the maximum magnitude in the data
    ax : matplotlib.axes.Axes, optional
        The 3D axes on which to draw the plot. If None, creates a new figure with 3D axes
    cmap : str or matplotlib.colors.Colormap, optional
        Colormap to use for phase representation
    labels_x : list or None
        Labels for the x-axis
    labels_y : list or None
        Labels for the y-axis
    title : str or None
        Title for the plot
    alpha : float
        Transparency of the bars
    bar_width : float
        Width of the bars (0 to 1)
    show_colorbar : bool
        Whether to show a colorbar for phase
    show_gridlines : bool
        Whether to show gridlines on the plot
    bar_edge_color : str or None
        Color for bar edges (None for no edges)
    bar_edge_width : float
        Width of the bar edges
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure containing the 3D bar plot
    ax : matplotlib.axes.Axes
        The 3D axes containing the bar plot
    """
    
    # Get magnitude and phase
    magnitude = np.abs(complex_data)  # Ensure we use absolute value
    phase = np.angle(complex_data)
    
    # Set up the figure and axes
    if ax is None:
        fig = plt.figure(figsize=(6, 5))
        ax: Axes3D = fig.add_subplot(111, projection='3d') # type: ignore
    else:
        fig = ax.figure
    
    # Determine maximum value for scaling
    if max_val is None:
        max_val = magnitude.max()
    
    # Create meshgrid for x and y coordinates
    nrows, ncols = complex_data.shape
    _x_pos = np.arange(ncols)
    _y_pos = np.arange(nrows)
    _xx_pos, _yy_pos = np.meshgrid(_x_pos, _y_pos)
    x_pos = _xx_pos.flatten()
    y_pos = _yy_pos.flatten()
    z_pos = np.zeros_like(x_pos)
    
    # Flatten magnitude and phase for plotting
    magnitudes = magnitude.flatten()
    phases = phase.flatten()
    plot_magnitudes = magnitudes.copy()
    if min_val is not None:
        mask = plot_magnitudes >= min_val
        # Filter all arrays based on mask
        x_pos = x_pos[mask]
        y_pos = y_pos[mask]
        z_pos = z_pos[mask]
        plot_magnitudes = plot_magnitudes[mask]
        phases = phases[mask]
        
        if len(x_pos) == 0:
            return fig, ax
        
    if max_val is not None:
        plot_magnitudes[plot_magnitudes > max_val] = max_val
    
    # Create colormap for phase
    norm = Normalize(vmin=-np.pi, vmax=np.pi)
    cmap_obj = mpl.colormaps[cmap]
    colors = cmap_obj(norm(phases))
    
    # Bar dimensions
    dx = dy = bar_width * np.ones_like(z_pos)
    
    # # Sort indices by x, y position to plot from back to front
    # # This helps with occlusion problems
    # indices = list(range(len(x_pos)))
    # indices.sort(key=lambda i: (-x_pos[i], y_pos[i]))  # Sort by distance from viewing point
    
            
    # Create bar with edgecolor parameter for clear outlines
    bar = ax.bar3d(
        x_pos-dx/2, y_pos-dy/2, z_pos,
        dx, dy, plot_magnitudes, 
        color=colors, alpha=alpha, shade=True,
        edgecolor=bar_edge_color, linewidth=bar_edge_width,
        zsort="average",
        # axlim_clip = True,
    )
            
    for idx in np.ndindex(x_pos.shape):
        x, y, z = x_pos[idx], y_pos[idx], z_pos[idx]
        real_mag, plot_mag, phi = magnitudes[idx], plot_magnitudes[idx], phases[idx]
        if real_mag > max_val:
            # Create vertices for the top face
            verts = [
                (x-dx[idx]/2, y-dy[idx]/2, max_val),
                (x+dx[idx]/2, y-dy[idx]/2, max_val),
                (x+dx[idx]/2, y+dy[idx]/2, max_val),
                (x-dx[idx]/2, y+dy[idx]/2, max_val)
            ]

            # Create a polygon collection for the top face
            poly = Poly3DCollection(
                [verts], alpha=1.0, linewidth=bar_edge_width,
            )
            poly.set_facecolor('gray')  # Base color
            poly.set_edgecolor(bar_edge_color)  # Add edge for better visibility
            poly.set_hatch('//////')       # Diagonal hatching
            # Set a high zorder to ensure the hatching appears on top
            poly.set_zorder(100)
            # Set the sort_zpos parameter to ensure it's drawn after other elements
            poly.set_sort_zpos(max_val + 1.0)
            ax.add_collection3d(poly)
            
            
            # Add text marker for exact value
            ax.text(x, y, max_val*1.1, f"{real_mag:.3f}", 
                    ha='center', va='bottom', color=bar_edge_color, 
                    # fontweight='bold', 
                    fontsize=9, zorder=10)
    
    # Set axis labels
    if labels_x is not None:
        ax.set_xticks(np.arange(ncols))
        ax.set_xticklabels(labels_x)
    else:
        ax.set_xticks(np.arange(ncols))
    
    if labels_y is not None:
        ax.set_yticks(np.arange(nrows))
        ax.set_yticklabels(labels_y)
    else:
        ax.set_yticks(np.arange(nrows))
    
    # Set axis limits with extra space for overflow indicators
    ax.set_xlim(-0.5, ncols-0.5)
    ax.set_ylim(-0.5, nrows-0.5)
    ax.set_zlim(0, max_val * 1.1)  # Extra headroom for overflow indicators
    
    # Reverse y-axis to match matrix orientation
    ax.set_ylim(nrows-0.5, -0.5)
    
    # Set view angle to show bars more clearly
    ax.view_init(elev=30, azim=225)
    
    # Show or hide gridlines
    if not show_gridlines:
        ax.grid(False)
    
    # Add colorbar for phase
    if show_colorbar:
        sm = plt.cm.ScalarMappable(cmap=cmap_obj, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, pad=0.1, aspect=30)
        cbar.set_ticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
        cbar.set_ticklabels([r'$-\pi$', r'$-\pi/2$', r'$0$', r'$\pi/2$', r'$\pi$'])
    
    return fig, ax