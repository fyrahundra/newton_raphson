import tkinter as tk
from tkinter import ttk

import numpy as np
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

def parse_function(func_str):
    # Ersätt ^ med **
    func_str = func_str.replace("^", "**")
    print(f"Parsing function: {func_str}")

    # Skapa en lambda-funktion
    try:
        func = eval(f"lambda x: {func_str}")
        return func, func_str
    except Exception as e:
        print(f"Fel i funktionsskrivning: {e}")
        return lambda x: 0

def common_derivative(func_str):
    derivative_str = "1"
    if "x**" in func_str:
        power = func_str.split("x**")[1].split()[0]
        if power.isdigit():
            n = int(power)
            derivative_str = f"{n}*x**{n-1}"
    elif "x" in func_str:
        derivative_str = "1"
    return derivative_str
# =========================
# Funktion och derivata
# =========================

def f(x):
    print(f"parse_function(function)(x): {parse_function(function)[1]} with x={x}")
    return parse_function(function)[0](x)

def derivative_fallback(x):
    h = 1e-7
    return (f(x + h) - f(x - h)) / (2 * h)

def df(x):
    return parse_function(common_derivative(function))[0](x)

# =========================
# Newton-Raphson
# =========================

def newton_raphson(x0, iterations):

    points = []

    x = x0

    for i in range(iterations):

        y = f(x)

        points.append((x, y))

        if df(x) == 0:
            break

        x = x - y / df(x)

    return points, x

# =========================
# Uppdatera graf
# =========================

def callback():
    update_plot()

def update_plot():

    global function

    if func_string is not None:
        function = func_string.get().strip()

    print(f"Updating plot with function: {function}")

    x0 = float(start_slider.get())
    iterations = int(iter_slider.get())

    points, root_approx = newton_raphson(
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

    # Resultattext
    result_label.config(
        text=f"Approximation av 0 ≈ {root_approx:.10f}"
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

iter_slider = tk.Scale(
    controls_frame,
    from_=1,
    to=10,
    orient=tk.HORIZONTAL,
    length=350,
    command=lambda e: update_plot()
)

iter_slider.set(5)

iter_slider.grid(
    row=2,
    column=1
)

# Uppdateringsknapp
update_button = ttk.Button(
    controls_frame,
    text="Uppdatera Graf",
    command=update_plot
)

update_button.grid(
    row=3,
    column=0,
    columnspan=2,
    pady=10
)

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

fig, ax = plt.subplots(
    figsize=(10, 6)
)

canvas = FigureCanvasTkAgg(
    fig,
    master=root
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