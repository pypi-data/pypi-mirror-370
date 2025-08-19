# This is a newer version of error_rates.py
# based on the parameters extracted in batched_sweeps_recipe.py

__all__ = [
    "ErrorContrib",
    "ErrorBudget",
    "basic_budget",
]

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib import rcParams
from chencrafts.toolbox import bar_plot_compare

from typing import Callable, List, Dict, Literal

class ErrorContrib:
    def __init__(
        self, 
        name: str, 
        expression: Callable,
        step: int,
        type: Literal["X", "Y", "Z", "L"]
    ):
        self.name = name
        self.expression = expression
        self.step = step
        self.type = type

    def __call__(self, *args, **kwargs):
        return self.expression(*args, **kwargs)

# ##############################################################################
class ErrorBudget:
    def __init__(
        self, 
    ):
        self.error_contribs: Dict[str, ErrorContrib] = {}
        self.contrib_enable_info: Dict[str, bool] = {}

    def __call__(
        self,
        organize_by: Literal["name", "type", "step", "None"] = "None",
        *args,
        **kwargs,
    ) -> np.ndarray | Dict[str, np.ndarray]:
        """returns the total enabled error rate"""
        error_dict = {}
        if organize_by == "type":
            error_dict = {"X": 0, "Y": 0, "Z": 0, "L": 0}
        elif organize_by == "step":
            max_step = max(error_contrib.step for error_contrib in self.error_contribs.values())
            error_dict = {step+1: 0 for step in range(max_step)}

        for name, error_contrib in self.error_contribs.items():
            if not self.contrib_enable_info[name]:
                continue
            error_rate = error_contrib(*args, **kwargs)
            
            if organize_by in ["name", "None"]:
                error_dict[name] = error_rate
                if organize_by == "None":
                    return sum(error_dict.values())
            elif organize_by == "type":
                err_type = error_contrib.type
                error_dict[err_type] += error_rate
            elif organize_by == "step":
                err_step = error_contrib.step
                error_dict[err_step] += error_rate
                
        return error_dict

    def __getitem__(
        self,
        contrib_name: str | List[str],
    ) -> "ErrorContrib | ErrorBudget":
        """calculate the error rate from a single channel"""
        if isinstance(contrib_name, str):
            return self.error_contribs[contrib_name]
        elif isinstance(contrib_name, list) or isinstance(contrib_name, tuple):
            new_budget = ErrorBudget()
            for name in contrib_name:
                new_budget.add_existed_contrib(self[name])
            return new_budget
    
    @property
    def num(self):
        return len(self.error_contribs)

    @property
    def enable_num(self):
        return int(np.sum(list(self.contrib_enable_info.values())))

    @property
    def error_names(self):
        return list(self.error_contribs.keys())

    def add_contrib(
        self,
        name: str, 
        expression: Callable,
        step: int,
        type: Literal["X", "Y", "Z", "L"]
    ):
        self.error_contribs[name] = ErrorContrib(
            name,
            expression,
            step,
            type,
        )

        # update info
        self.contrib_enable_info[name] = True

    def add_existed_contrib(
        self,
        contrib: ErrorContrib,
    ):  
        name = contrib.name

        self.error_contribs[name] = contrib
        
        # update info
        self.contrib_enable_info[name] = True

    def remove_contrib(
        self,
        name
    ):
        try:
            del self.error_contribs[name]
            del self.contrib_enable_info[name]

        except KeyError:
            print(f"No error named {name}")

    def disable_contrib(
        self,
        name: str
    ):
        if not self.contrib_enable_info[name]:
            print(f"This contribution [{name}] is already disabled")
        else:
            self.contrib_enable_info[name] = False

    def enable_contrib(
        self,
        name: str
    ):
        if self.contrib_enable_info[name]:
            print(f"This contribution [{name}] is already enabled")
        else:
            self.contrib_enable_info[name] = True

    def pie_chart(
        self,
        ax = None,
        figsize = (6, 3),
        dpi = None,
        start_angle = 60,
        **kwargs,
    ):

        # error calculation
        error_dict: Dict = self(**kwargs, return_dict=True)
        error_dict.pop("total")
        error_rate_list = list(error_dict.values())
        total_error_rate = np.sum(error_rate_list)

        # color map
        cm_pie = colormaps["rainbow"]
        cm_pie_norm = plt.Normalize(0, self.enable_num)
        cmap_pie = lambda x: cm_pie(cm_pie_norm(x))

        # figure
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(aspect="equal"), dpi=dpi)
            need_show = True

        wedges, texts = ax.pie(
            error_rate_list, 
            wedgeprops=dict(width=0.5), 
            startangle=start_angle, 
            colors=[cmap_pie(i) for i in range(self.enable_num)]
        )

        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle="-"),
                bbox=bbox_props, zorder=0, va="center")

        for i, p in enumerate(wedges):
            err = error_rate_list[i]
            err_percent = err / total_error_rate * 100
            if err < 3e-8:
                continue
            ang = (p.theta2 - p.theta1)/2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate(
                f"{self.error_names[i]}: {err_percent:.0f}%", 
                xy=(x, y), 
                xytext=(1.35*np.sign(x), 1.4*y),
                horizontalalignment=horizontalalignment, 
                **kw
            )

        if need_show:
            plt.tight_layout()
            plt.show()

    def bar_plot(
        self,
        ax = None,
        para_dicts = None,
        figsize = (6, 3), 
        dpi = None,
        labels = None,
        **kwargs
    ):
        # check instance type
        if isinstance(para_dicts, dict):
            para_dicts = [para_dicts]
            compare_num = 1
        elif isinstance(para_dicts, list):
            if isinstance(para_dicts[0], dict):
                compare_num = len(para_dicts)
            else:
                raise TypeError("Should input a single dictionary or a list of "
                    "dictionaries")
        elif para_dicts == None:
            para_dicts = [kwargs]
            compare_num = 1
        else:
            raise TypeError("Should input a single dictionary or a list of "
                "dictionaries")

        # calculate errors and obtain a label to each set of data
        errors = np.zeros((compare_num, self.enable_num))
        for i in range(compare_num):
            error_dict = self(**para_dicts[i], return_dict=True)
            del error_dict["total"]
            for j, err in enumerate(error_dict.values()):
                errors[i, j] = err

        label_list = []
        for i in range(compare_num):
            if labels is not None:
                total = np.sum(errors[i, :])
                label_list.append(labels[i] + f": {total:.2e}")
            else:
                total = np.sum(errors[i, :])
                label_list.append(f"E{i:d}: {total:.2e}")
        plot_dict = dict(zip(label_list, errors))

        
        # plot 
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
            need_show = True

        bar_plot_compare(
            plot_dict,
            x_ticks = self.error_names,
            ax = ax,
            figsize = figsize, 
            dpi = dpi,
            x_tick_rotation = 45, 
        )
        ax.set_ylabel(r"Error Rate / GHz")

        if need_show:
            plt.tight_layout()
            plt.show()

# ##############################################################################
def qubit_g_to_e_prob(Gamma_up, Gamma_down, time):
    return Gamma_up / (Gamma_up + Gamma_down) * (1 - np.exp(-(Gamma_up + Gamma_down) * time))
def qubit_e_to_g_prob(Gamma_up, Gamma_down, time):
    return Gamma_down / (Gamma_up + Gamma_down) * (1 - np.exp(-(Gamma_up + Gamma_down) * time))

def manual_constr(g_sa, min_detuning, detuning_lower_bound, constr_amp, *args, **kwargs):
    detuning_undersize = 2 * np.pi * (g_sa * detuning_lower_bound - min_detuning)
    return constr_amp * detuning_undersize * np.heaviside(detuning_undersize, 0)

manual_constr = ErrorContrib(
    "manual_constr",
    manual_constr,
    1,
    "L"
)

# ------------------------------------------------------------------------------
# all parameters are extracted in batched_sweeps_recipe.py
basic_budget = ErrorBudget()

# step 1: idling
def multi_photon_loss(jump_a, T_W, disp, **kwargs):
    # 1 photon loss
    pl1_prob = jump_a * disp**2 * T_W
    # 2 photon loss
    # pl2_prob = (pl1_prob)**2 * np.exp(-pl1_prob) / 2
    # 2+ photon loss
    mtpl_prob = (
        1 
        - np.exp(-pl1_prob)
        - np.exp(-pl1_prob) * pl1_prob
    )
    return mtpl_prob
basic_budget.add_contrib(
    "multiple_photon_loss",
    multi_photon_loss,
    step = 1,
    type = "Z",
)

# cat size shrinkage missing

basic_budget.add_contrib(
    "photon_gain", 
    lambda jump_adag, T_W, disp, *args, **kwargs: 
        jump_adag * disp**2 * T_W,
    step = 1,
    type = "L", # approximately Z / L
)

basic_budget.add_contrib(
    "anc_prepare", 
    lambda T_W, jump_ij, *args, **kwargs: 
        jump_ij[1, 0] * T_W,
    step = 1,
    type = "L",
)

# step 2: gate. No error contribution for now

# step 3: parity mapping
# not verified, may have a factor 1/2
basic_budget.add_contrib(
    "anc_relax_map", 
    lambda jump_ij, chi_sa, *args, **kwargs: 
        np.pi * jump_ij[0, 1] / np.abs(chi_sa),
    step = 3,
    type = "L",
)

# not verified, may have a factor 1/4
basic_budget.add_contrib(
    "anc_dephase_map", 
    lambda jump_ij, chi_sa, *args, **kwargs: 
        np.pi * jump_ij[1, 1] / np.abs(chi_sa),
    step = 3,
    type = "L",
)

# not verified
basic_budget.add_contrib(
    "cav_relax_map", 
    lambda jump_a, chi_sa, *args, **kwargs: 
        np.pi * jump_a / np.abs(chi_sa),
    step = 3,
    type = "L",
)

# coherent contribution missing

# step 4: gate. No error contribution for now

# step 5: measurement. 
# not verified, need to add readout induced decay
basic_budget.add_contrib(
    "anc_relax_ro", 
    lambda jump_a, jump_ij, tau_m, tau_FD, T_W, *args, **kwargs: 
        jump_a * T_W * jump_ij[0, 1] * (tau_m + tau_FD),
    step = 5,
    type = "L",
)

basic_budget.add_contrib(
    "anc_excite_ro", 
    lambda jump_a, jump_ij, tau_m, T_W, tau_FD, *args, **kwargs: 
        (1 - jump_a * T_W) * jump_ij[1, 0] * (tau_m + tau_FD),
    step = 5,
    type = "L",
)

basic_budget.add_contrib(
    "ro_infidelity", 
    lambda jump_a, T_W, M_eg, M_ge, *args, **kwargs: 
        jump_a * T_W * M_eg 
        + (1 - jump_a * T_W) * M_ge,
    step = 5,
    type = "L",
)