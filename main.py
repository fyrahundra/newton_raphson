import tkinter as tk
from tkinter import ttk
from collections.abc import Callable
from typing import Any

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

function = "x"
derivative = "1"

# =========================
# Parser för funktionsskrivning
# =========================

def parse_function(func_str: str) -> tuple[Callable[[Any], Any], str]:
    # Ersätt ^ med **
    func_str = func_str.replace("^", "**")
    print(f"Parsing function: {func_str}")

    # Skapa en lambda-funktion
    try:
        func = eval(f"lambda x: {func_str}")
        return func, func_str
    except Exception as e:
        print(f"Fel i funktionsskrivning: {e}")
        return (lambda x: 0, "0")
    
def symbolic_derivative(func_str: str, x_value: float, func: Callable[[Any], Any]) -> float:
    x_symbol = sp.symbols("x")
    try:
        func_expr = sp.sympify(func_str)
        derivative_expr = sp.diff(func_expr, x_symbol)
        derivative_func = sp.lambdify(x_symbol, derivative_expr, modules=["numpy", "math"])
        return float(derivative_func(x_value)), str(derivative_expr)
    except Exception as e:
        print(f"Fel i derivatberäkning: {e}. Kör numerisk derivata istället.")
        return numerical_derivative(func, x_value)

def numerical_derivative(func: Callable[[Any], Any], x_value: float, h: float = 1e-5) -> float:
    return float((func(x_value + h) - func(x_value - h)) / (2 * h))

# =========================
# Funktion och derivata
# =========================

def f(x: Any) -> Any:
    func, parsed_function = parse_function(function)
    print(f"parse_function(function)(x): {parsed_function} with x={x}")
    return func(x)

def df(x: Any) -> Any:
    derivative_value, derivative_expr = symbolic_derivative(function, x, f)
    print(f"derivative: {derivative_value} ({derivative_expr})")
    return derivative_value

# ========================
# Kontrollera int och float för input
# ========================

def validate_float(value: str) -> bool:
    if value == "" or value == "-":
        return True  # Tillåt tomt eller bara minustecken (under skrivning)
    try:
        float(value)
        return True
    except ValueError:
        return False

def validate_pos_int(value: str) -> bool:
    if value == "":
        return True
    try:
        int(value)
        return int(value) > 0
    except ValueError:
        return False

# =========================
# Newton-Raphson
# =========================

def newton_raphson(x0: float, iterations: int) -> tuple[list[tuple[float, float]], list[tuple[int, float, float, float]], float]:

    points = []
    iteration_rows = []

    x = x0

    for i in range(iterations):

        y = f(x)
        dy = df(x)

        points.append((x, y))
        iteration_rows.append((i + 1, x, y, dy))

        if dy == 0:
            break

        x = x - y / dy

    return points, iteration_rows, x

# =========================
# Uppdatera graf
# =========================

def callback():
    update_plot()

def update_plot() -> None:

    global function

    if func_string is not None:
        function = func_string.get().strip()

    print(f"Updating plot with function: {function}")

    x0 = float(start_slider.get())
    iterations = int(iter_slider.get())

    points, iteration_rows, root_approx = newton_raphson(
        x0,
        iterations
    )

    ax.clear()

    # Rita funktion
    x_vals = np.linspace(-5, 5, 1000)
    y_vals = f(x_vals)

    ax.plot(
        x_vals,
        y_vals,
        label=f"f(x) = {function}",
        linewidth=2
    )

    # x-axel
    ax.axhline(
        0,
        linewidth=1
    )

    # Grid
    ax.grid(True)

    # Rita Newton-punkter och tangentlinjer
    for i, (x, y) in enumerate(points):

        # Punkt
        ax.plot(
            x,
            y,
            'o',
            markersize=8
        )

        ax.text(
            x,
            y,
            f"x{i}",
            fontsize=10
        )

        # Tangentlinje
        slope = df(x)

        tangent_x = np.linspace(
            x - 1.5,
            x + 1.5,
            100
        )

        tangent_y = y + slope * (tangent_x - x)

        ax.plot(
            tangent_x,
            tangent_y,
            linestyle='--',
            alpha=0.7
        )

        # Nästa approximation
        next_x = x - y / slope

        # Projektion mot x-axeln
        ax.plot(
            [x, next_x],
            [0, 0],
            linestyle=':',
            linewidth=2
        )

    # Titel och labels
    ax.set_title(
        "Newton-Raphson Metoden",
        fontsize=16
    )

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    ax.legend()

    for row in iteration_table.get_children():
        iteration_table.delete(row)

    for iteration, x_value, function_value, derivative_value in iteration_rows:
        iteration_table.insert(
            "",
            tk.END,
            values=(
                iteration,
                f"{x_value:.6f}",
                f"{function_value:.6f}",
                f"{derivative_value:.6f}"
            )
        )

    approx = points[-1][0] if points else root_approx
    # Resultattext
    result_label.config(
        text=f"Approximation av {function} ≈ {approx:.10f}"
    )

    # Uppdatera canvas
    canvas.draw()

# =========================
# GUI
# =========================

root = tk.Tk()

root.title("Newton-Raphson Visualisering")

# Starta maximerat
root.state("zoomed")

intrcmd = (root.register(validate_pos_int), "%P")
startcmd = (root.register(validate_float), "%P")

# =========================
# Kontrollpanel
# =========================

controls_frame = tk.Frame(root)

controls_frame.pack(
    pady=10
)

# Funktionskrivning
tk.Label(
    controls_frame,
    text="Fuktion: f(x) = ",
    font=("Arial", 12, "bold")
).grid(
    row=0,
    column=0,
    padx=10
)

func_string = tk.StringVar(value=function)
func_string.trace_add("write", lambda *args: update_plot())

tk.Entry(
    controls_frame,
    textvariable=func_string,
    width=20,
    font=("Arial", 12),
).grid(
    row=0,
    column=1,
    padx=10
)

# Startvärde
tk.Label(
    controls_frame,
    text="Startvärde",
    font=("Arial", 11)
).grid(
    row=1,
    column=0,
    padx=10
)

start_slider = tk.Scale(
    controls_frame,
    from_=-5,
    to=5,
    resolution=0.1,
    orient=tk.HORIZONTAL,
    length=350,
    command=lambda e: update_plot()
)

start_slider.set(1.5)

start_slider.grid(
    row=1,
    column=1
)

# Iterationer
tk.Label(
    controls_frame,
    text="Antal iterationer",
    font=("Arial", 11)
).grid(
    row=2,
    column=0,
    padx=10
)

def on_iter_slider(_=None):
    try:
        v = int(float(iter_slider.get()))
    except Exception:
        v = 1
    if v < 1:
        v = 1
    iter_slider.set(v)
    update_plot()

iter_slider = tk.Scale(
    controls_frame,
    from_=1,
    to=10,
    resolution=1,
    orient=tk.HORIZONTAL,
    length=350,
    command=on_iter_slider
)

iter_slider.set(5)

iter_slider.grid(
    row=2,
    column=1
)

# Slider range controls
def update_slider_ranges() -> None:
    # sanitize numeric input (allow comma decimals)
    smin_str = start_min_var.get().strip().replace(',', '.')
    smax_str = start_max_var.get().strip().replace(',', '.')
    if not smin_str or not smax_str:
        return
    try:
        smin = float(smin_str)
        smax = float(smax_str)
    except Exception:
        return

    imax_str = iter_max_var.get().strip().replace(',', '.')
    if not imax_str:
        return
    try:
        imax = int(float(imax_str))
    except Exception:
        return

    # apply to sliders
    start_slider.config(from_=smin, to=smax)
    # clamp current start value
    try:
        cur = float(start_slider.get())
        if cur < smin:
            start_slider.set(smin)
        elif cur > smax:
            start_slider.set(smax)
    except Exception:
        pass

    iter_slider.config(from_=1, to=imax)
    try:
        curi = int(iter_slider.get())
        if curi > imax:
            iter_slider.set(imax)
    except Exception:
        pass

    update_plot()

# Vars and UI for ranges
start_min_var = tk.StringVar(value=str(start_slider.cget('from')))
start_max_var = tk.StringVar(value=str(start_slider.cget('to')))
iter_max_var = tk.StringVar(value=str(iter_slider.cget('to')))

tk.Label(controls_frame, text="Start min", font=("Arial", 10)).grid(row=4, column=0, padx=5)
tk.Entry(
    controls_frame, 
    textvariable=start_min_var, 
    width=8,
    validatecommand=startcmd
).grid(
    row=4, 
    column=1
)
tk.Label(controls_frame, text="Start max", font=("Arial", 10)).grid(row=4, column=2, padx=5)
tk.Entry(
    controls_frame, 
    textvariable=start_max_var, 
    width=8,
    validatecommand=startcmd
).grid(
    row=4, 
    column=3
)

tk.Label(controls_frame, text="Iter max", font=("Arial", 10)).grid(row=5, column=2, padx=5)
tk.Entry(
    controls_frame, 
    textvariable=iter_max_var, 
    width=8,
    validatecommand=intrcmd
).grid(
    row=5, 
    column=3
)

# trace changes
start_min_var.trace_add("write", lambda *args: update_slider_ranges())
start_max_var.trace_add("write", lambda *args: update_slider_ranges())
iter_max_var.trace_add("write", lambda *args: update_slider_ranges())

# =========================
# Resultatlabel
# =========================

result_label = tk.Label(
    root,
    text="",
    font=("Arial", 14)
)

result_label.pack(
    pady=5
)

# =========================
# Matplotlib figur
# =========================

content_frame = tk.Frame(root)

content_frame.pack(
    fill=tk.BOTH,
    expand=True
)

plot_frame = tk.Frame(content_frame)

plot_frame.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True,
    padx=(10, 5),
    pady=5
)

table_frame = tk.Frame(content_frame)

table_frame.pack(
    side=tk.RIGHT,
    fill=tk.Y,
    padx=(5, 10),
    pady=5
)

table_title = tk.Label(
    table_frame,
    text="Iterationer",
    font=("Arial", 12, "bold")
)

table_title.pack(pady=(0, 8))

table_columns = ("iteration", "x", "f(x)", "f'(x)")

iteration_table = ttk.Treeview(
    table_frame,
    columns=table_columns,
    show="headings",
    height=15
)

iteration_table.heading("iteration", text="Iter")
iteration_table.heading("x", text="x")
iteration_table.heading("f(x)", text="f(x)")
iteration_table.heading("f'(x)", text="f'(x)")

iteration_table.column("iteration", width=60, anchor="center")
iteration_table.column("x", width=110, anchor="e")
iteration_table.column("f(x)", width=110, anchor="e")
iteration_table.column("f'(x)", width=110, anchor="e")

table_scrollbar = ttk.Scrollbar(
    table_frame,
    orient=tk.VERTICAL,
    command=iteration_table.yview
)

iteration_table.configure(yscrollcommand=table_scrollbar.set)

iteration_table.pack(side=tk.LEFT, fill=tk.Y)
table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

fig, ax = plt.subplots(
    figsize=(10, 6)
)

canvas = FigureCanvasTkAgg(
    fig,
    master=plot_frame
)

canvas_widget = canvas.get_tk_widget()

canvas_widget.pack(
    fill=tk.BOTH,
    expand=True
)

# =========================
# Toolbar Frame
# =========================

toolbar_frame = tk.Frame(root)

toolbar_frame.pack(
    fill=tk.X,
    padx=5,
    pady=5
)

# =========================
# Toolbar
# =========================

toolbar = NavigationToolbar2Tk(
    canvas,
    toolbar_frame
)

toolbar.update()

# =========================
# Första rendering
# =========================

update_plot()

# =========================
# Starta app
# =========================

root.mainloop()