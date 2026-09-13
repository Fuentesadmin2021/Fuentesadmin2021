"""
NYLANDER ROSE — Rosa matemática 3D animada

La superficie utiliza la formulación original de la
"Nylander Rose" de Paul Nylander.

Instalar:
    pip install numpy matplotlib pillow

Ejecutar:
    python nylander_rose.py

Salida:
    nylander_rose.gif
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


NX =  120
NTHETA = 300
NFRAMES = 120

ROSE_COLORS = LinearSegmentedColormap.from_list(
    "rose_fire",
    ["#ed6b27", "#c92c25", "#a91522", "#760d1c", "#4d0916"],
)

x = np.linspace(0, 1, NX)
theta_full = np.linspace(-2*np.pi, 15*np.pi, NTHETA)

Xpar, T = np.meshgrid(x, theta_full, indexing="ij")

# 1. Ángulo de apertura
phi = (np.pi / 2) * np.exp(-T / (8*np.pi))

# 2. Perfil de los pétalos
u = 1 - 0.5 * (
    1.25 * (1 - np.mod(3.6*T, 2*np.pi) / np.pi)**2 - 0.25
)**2

# 3. Curvatura auxiliar
Yaux = (
    1.95653
    * Xpar**2
    * (1.27689*Xpar - 1)**2
    * np.sin(phi)
)

# 4. Radio
r = u * (
    Xpar*np.sin(phi)
    + Yaux*np.cos(phi)
)

# 5. Conversión a coordenadas 3D
Xp = r*np.sin(T)
Yp = r*np.cos(T)
Zp = u * (
    Xpar*np.cos(phi)
    - Yaux*np.sin(phi)
)


fig = plt.figure(figsize=(6, 6), dpi=80, facecolor="black")
ax = fig.add_subplot(111, projection="3d")

star_rng = np.random.default_rng(12)
stars = star_rng.uniform([-1.9, -1.9, -1.35], [1.9, 1.9, 1.45], (70, 3))


def configure():
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.set_zlim(-1.05, 1.05)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.set_facecolor("black")
    ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
    ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
    ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))


def draw_bee(frame):
    angle = frame * 0.13
    bee_center = np.array([
        0.92 * np.cos(angle),
        0.92 * np.sin(angle),
        0.48 + 0.12 * np.sin(angle * 1.7),
    ])
    direction = np.array([-np.sin(angle), np.cos(angle), 0.0])
    side_axis = np.array([np.cos(angle), np.sin(angle), 0.0])
    up = np.array([0.0, 0.0, 1.0])

    body = bee_center + up * 0.02
    abdomen_offsets = (-0.10, -0.035, 0.035, 0.10)
    abdomen_colors = ("#f2a623", "#23171a", "#e8a020", "#24171a")
    for offset, color in zip(abdomen_offsets, abdomen_colors):
        abdomen_part = body + direction * offset
        ax.scatter(*abdomen_part, s=62, c=color, edgecolors="#160f12",
                   linewidths=0.55, depthshade=True, zorder=9)

    head = body + direction * 0.17
    ax.scatter(*head, s=52, c="#171318", edgecolors="#050509",
               linewidths=0.7, depthshade=True, zorder=10)
    for eye_side in (-1, 1):
        eye = head + side_axis * eye_side * 0.027 + up * 0.018
        ax.scatter(*eye, s=7, c="#fff1b0", depthshade=False, zorder=11)

    wing_origin = body + up * 0.055
    wing_flap = 0.10 + 0.015 * np.sin(frame * 1.8)
    for side in (-1, 1):
        wing_points = [
            wing_origin + side * side_axis * 0.015 + up * 0.02,
            wing_origin + side * side_axis * 0.06 + up * (0.09 + wing_flap),
            wing_origin + side * side_axis * 0.13 + up * (0.12 + wing_flap),
            wing_origin + side * side_axis * 0.18 + up * (0.08 + wing_flap),
            wing_origin + side * side_axis * 0.17 + up * 0.02,
            wing_origin + side * side_axis * 0.10 - up * 0.018,
            wing_origin + side * side_axis * 0.04 - up * 0.005,
        ]
        ax.add_collection3d(Poly3DCollection(
            [wing_points], facecolors="#d9f4ef", edgecolors="#e8ffff",
            linewidths=0.35, alpha=0.24, zorder=7,
        ))

    for antenna_side in (-1, 1):
        antenna_base = head + side_axis * antenna_side * 0.018 + up * 0.025
        antenna_tip = antenna_base + direction * 0.07 + side_axis * antenna_side * 0.055 + up * 0.055
        ax.plot(
            [antenna_base[0], antenna_tip[0]],
            [antenna_base[1], antenna_tip[1]],
            [antenna_base[2], antenna_tip[2]],
            color="#181216", linewidth=0.9, alpha=0.9, zorder=10,
        )


def update(frame):
    ax.clear()
    configure()
    ax.scatter(
        stars[:, 0], stars[:, 1], stars[:, 2],
        s=28, c="#f0a34a", alpha=0.055, depthshade=False,
    )
    ax.scatter(
        stars[:, 0], stars[:, 1], stars[:, 2],
        s=2.5, c="#ffe1a1", alpha=0.68, depthshade=False,
    )

    # Construcción progresiva:
    # cada frame añade una nueva sección de theta.
    end = max(4, int((frame + 1) / NFRAMES * NTHETA))

    xs = Xp[:, :end]
    ys = Yp[:, :end]
    zs = Zp[:, :end]

    ax.plot_surface(
        xs, ys, zs,
        rstride=1,
        cstride=2,
        facecolors=ROSE_COLORS(0.18 + 0.82 * np.clip(xs, 0, 1)),
        linewidth=0,
        antialiased=True,
        shade=True
    )

    # Malla matemática sutil.
    ax.plot_wireframe(
        xs[::3, ::5],
        ys[::3, ::5],
        zs[::3, ::5],
        color="#ed6b27",
        linewidth=0.22,
        alpha=0.22
    )

    draw_bee(frame)

    # Movimiento suave de cámara.
    ax.view_init(elev=38 + 5*np.sin(frame/12), azim=-42 + frame*0.9)


ani = FuncAnimation(
    fig,
    update,
    frames=NFRAMES,
    interval=70,
    blit=False
)

ani.save(
    "nylander_rose.gif",
    writer=PillowWriter(fps=14),
    dpi=80,
    savefig_kwargs={"facecolor": "black"}
)

plt.close(fig)
print("Generado: nylander_rose.gif")

