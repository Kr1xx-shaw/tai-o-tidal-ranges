# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.9,<4", "PySide6-Essentials>=6.7,<7"]
# ///

"""Open the native tide explorer with: uv run interactive.py."""
import calendar
import json
import math
import sys
from pathlib import Path
from decimal import Decimal

from PySide6 import QtCore, QtGui, QtWidgets
from matplotlib import get_data_path
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Explicit Qt canvas below works independently of plot.py's headless PNG backend.
from plot import DATA, YEAR, PAPER, INK, ORANGE, BLACK, PALETTE, load_months, to_xy


class TideWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        QtGui.QFontDatabase.addApplicationFont(str(Path(get_data_path()) / "fonts/ttf/DejaVuSans.ttf"))
        self.setWindowTitle("A Year of Tide — Tai O | Native explorer")
        self.resize(1220, 870)
        self.setMinimumSize(940, 720)
        self.setStyleSheet(f"""
            QWidget {{ background: {PAPER}; color: {INK}; font: 12px 'DejaVu Sans'; }}
            QPushButton {{ border: 1px solid #cbd1c7; border-radius: 5px; padding: 7px; }}
            QPushButton:hover {{ background: #e9ede5; }}
            QSlider::groove:vertical {{ background: #dce1d7; width: 5px; border-radius: 2px; }}
            QSlider::handle:vertical {{ background: #537d80; height: 18px; margin: 0 -6px; border-radius: 8px; }}
        """)
        months = load_months(DATA)
        raw = json.loads(DATA.read_text(encoding="utf-8"))
        self.heights = {(int(row[0]), int(row[1])): [Decimal(v) for v in row[2:]]
                        for row in raw["data"]}
        self.layers = []
        self.spacing = 65
        self.zoom = 1.0
        container = QtWidgets.QWidget()
        self.setCentralWidget(container)
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(28, 22, 28, 18)
        title = QtWidgets.QLabel("A YEAR OF TIDE")
        title.setStyleSheet("font-size: 30px; letter-spacing: 3px;")
        layout.addWidget(title)
        layout.addWidget(QtWidgets.QLabel("TAI O / 2026 ASTRONOMICAL TIDE PREDICTIONS     ·     12 MONTHS / 365 DAYS"))
        body = QtWidgets.QHBoxLayout()
        layout.addLayout(body, 1)
        self.figure = Figure(figsize=(9, 7), facecolor=PAPER)
        self.canvas = FigureCanvasQTAgg(self.figure)
        body.addWidget(self.canvas, 1)
        self.ax = self.figure.add_axes([0, 0, 1, 1], projection="3d", facecolor=PAPER)
        self.ax.set_axis_off()
        self.ax.set_xlim(-3.8, 4.0)
        self.ax.set_ylim(-3.8, 3.8)
        self.ax.set_zlim(-.2, 7.2)
        self.ax.set_box_aspect((7.8, 7.6, 7.4), zoom=1.35)
        self.ax.view_init(elev=45, azim=-60, roll=0)
        self.ax.mouse_init(rotate_btn=1, pan_btn=2, zoom_btn=3)
        self.draw_grid()
        for month, entries in months.items():
            color = PALETTE[month - 1]
            x, y = map(list, zip(*(to_xy(day, value) for day, value in entries)))
            z = (month - 1) * self.spacing * .006
            line, = self.ax.plot(x, y, [z] * len(x), color=color, lw=1.5,
                                 marker="o", markersize=2.7)
            closure, = self.ax.plot([x[-1], x[0]], [y[-1], y[0]], [z, z],
                                    color=color, lw=.8, ls=(0, (2, 4)))
            fill = Poly3DCollection([list(zip(x, y, [z] * len(x)))],
                                    facecolor=color, edgecolor="none", alpha=.035)
            self.ax.add_collection3d(fill)
            markers = []
            for value, marker_color in ((max(v for _, v in entries), ORANGE),
                                         (min(v for _, v in entries), BLACK)):
                indices = [i for i, (_, v) in enumerate(entries) if v == value]
                marker, = self.ax.plot([x[i] for i in indices], [y[i] for i in indices],
                                       [z] * len(indices), linestyle="none", marker="o",
                                       markersize=6.5, color=marker_color,
                                       markeredgecolor=PAPER, markeredgewidth=.8)
                markers.append(marker)
            label = self.ax.text(3.95, 0, z, calendar.month_abbr[month].upper(),
                                 color=color, fontsize=8)
            self.layers.append(dict(month=month, entries=entries, x=x, y=y, z=z,
                                    line=line, closure=closure, fill=fill,
                                    markers=markers, label=label, visible=True))
        panel = QtWidgets.QWidget()
        panel.setFixedWidth(275)
        side = QtWidgets.QVBoxLayout(panel)
        side.setContentsMargins(14, 16, 0, 0)
        body.addWidget(panel)
        self.spacing_label = QtWidgets.QLabel("LAYER SPACING   65%")
        side.addWidget(self.spacing_label)
        row = QtWidgets.QHBoxLayout()
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        self.slider.setRange(0, 100)
        self.slider.setValue(self.spacing)
        self.slider.setFixedHeight(180)
        self.slider.setAccessibleName("Month layer separation")
        self.slider.valueChanged.connect(self.set_spacing)
        row.addWidget(self.slider)
        row.addWidget(QtWidgets.QLabel("EXPANDED\n\nDecember at the top\nJanuary at the base\n\nOVERLAID"))
        side.addLayout(row)
        side.addWidget(QtWidgets.QLabel("MONTHS  /  CLICK TO HIDE OR SHOW"))
        grid = QtWidgets.QGridLayout()
        self.month_buttons = []
        for i, color in enumerate(PALETTE):
            button = QtWidgets.QPushButton(calendar.month_abbr[i + 1])
            button.setCheckable(True)
            button.setChecked(True)
            button.setStyleSheet(f"QPushButton:checked {{ border: 2px solid {color}; }}"
                                 "QPushButton:!checked { color: #aab0aa; background: #e8e9e3; }")
            button.toggled.connect(lambda checked, index=i: self.set_visible(index, checked))
            grid.addWidget(button, i // 3, i % 3)
            self.month_buttons.append(button)
        side.addLayout(grid)
        for text, color in (("●  Monthly maximum range", ORANGE), ("●  Monthly minimum range", BLACK)):
            key = QtWidgets.QLabel(text)
            key.setStyleSheet(f"color: {color};")
            side.addWidget(key)
        actions = QtWidgets.QHBoxLayout()
        self.reset_button = QtWidgets.QPushButton("Reset 45°")
        self.top_button = QtWidgets.QPushButton("Top view")
        self.reset_button.clicked.connect(lambda: self.set_view(False))
        self.top_button.clicked.connect(lambda: self.set_view(True))
        actions.addWidget(self.reset_button)
        actions.addWidget(self.top_button)
        side.addLayout(actions)
        help_text = QtWidgets.QLabel("Drag chart to rotate · Scroll to zoom\nHover a dot to inspect its values.\nTop view: set spacing to 0 to compare\nall months on the same plane.")
        help_text.setStyleSheet("font-size: 11px; color: #717e75;")
        side.addWidget(help_text)
        self.details = QtWidgets.QLabel("POINT DETAILS\n\nHover over a daily point.")
        self.details.setMinimumHeight(112)
        self.details.setWordWrap(True)
        self.details.setStyleSheet("border-top: 1px solid #d7ddd2; padding-top: 9px;")
        side.addWidget(self.details)
        side.addStretch()
        foot = QtWidgets.QLabel(
            "DATE → ANGLE   /   DAILY SAMPLED RANGE → RADIUS (m)   /   MONTH → LAYER\n"
            "Vertical spacing is for display only, not tide height. Orange / black = monthly largest / smallest daily range.\n"
            "HKO predictions · 01:00–24:00 HKT · Fixed 31-day scale · Dashed joins are graphical closures.\n"
            "Hourly samples may miss high and low water between hours; these are predictions, not observations.")
        foot.setWordWrap(True)
        foot.setStyleSheet("font-size: 11px; color: #717e75; border-top: 1px solid #d7ddd2; padding-top: 10px;")
        layout.addWidget(foot)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def draw_grid(self):
        for radius in (1, 2, 3):
            angles = [i * math.tau / 180 for i in range(181)]
            self.ax.plot([radius * math.sin(a) for a in angles],
                         [radius * math.cos(a) for a in angles], [-.1] * len(angles),
                         color="#cfd3cb", lw=.6, ls=(0, (3, 5)))
            self.ax.text(radius * .866, radius * .5, -.1, f"{radius} m",
                         color="#89938c", fontsize=8)
        for day in (1, 5, 10, 15, 20, 25, 30):
            x, y = to_xy(day, 3.2)
            self.ax.plot([0, x], [0, y], [-.1, -.1], color="#e0e3dc", lw=.6)
            x, y = to_xy(day, 3.45)
            self.ax.text(x, y, -.1, f"{day:02d}", fontsize=8, color="#89938c")

    def set_spacing(self, value):
        self.spacing = value
        self.spacing_label.setText(f"LAYER SPACING   {value}%")
        for layer in self.layers:
            z = (layer["month"] - 1) * value * .006
            layer["z"] = z
            for artist in [layer["line"], layer["closure"], *layer["markers"]]:
                x, y, _ = artist.get_data_3d()
                artist.set_data_3d(x, y, [z] * len(x))
            layer["fill"].set_verts([list(zip(layer["x"], layer["y"], [z] * len(layer["x"])))])
            layer["label"].set_position_3d((3.95, 0, z))
            layer["label"].set_visible(layer["visible"] and value > 0)
        self.canvas.draw_idle()

    def set_visible(self, index, visible):
        layer = self.layers[index]
        layer["visible"] = visible
        for artist in [layer["line"], layer["closure"], layer["fill"], *layer["markers"]]:
            artist.set_visible(visible)
        layer["label"].set_visible(visible and self.spacing > 0)
        self.canvas.draw_idle()

    def set_view(self, top):
        self.ax.set_proj_type("ortho" if top else "persp")
        self.ax.view_init(elev=90 if top else 45, azim=-90 if top else -60, roll=0)
        self.zoom = 1.0
        self.ax.set_box_aspect((7.8, 7.6, 7.4), zoom=1.35)
        self.canvas.draw_idle()

    def on_scroll(self, event):
        if event.inaxes != self.ax:
            return
        self.zoom = max(.6, min(1.8, self.zoom * 1.12 ** event.step))
        self.ax.set_box_aspect((7.8, 7.6, 7.4), zoom=1.35 * self.zoom)
        self.canvas.draw_idle()

    def nearest_point(self, px, py):
        """Hit-test visible daily points after the current 3D projection."""
        closest, distance = None, 12 ** 2
        projection = self.ax.get_proj()
        for layer in self.layers:
            if not layer["visible"]:
                continue
            xs, ys, _ = proj3d.proj_transform(layer["x"], layer["y"],
                                             [layer["z"]] * len(layer["x"]), projection)
            for i, (x, y) in enumerate(self.ax.transData.transform(list(zip(xs, ys)))):
                d = (x - px) ** 2 + (y - py) ** 2
                if d < distance:
                    closest, distance = (layer, i), d
        return closest

    def on_hover(self, event):
        if event.inaxes != self.ax or event.buttons:
            return
        nearest = self.nearest_point(event.x, event.y)
        if nearest is None:
            self.details.setText("POINT DETAILS\n\nHover over a daily point.")
            return
        layer, i = nearest
        day, value = layer["entries"][i]
        heights = self.heights[layer["month"], day]
        self.details.setText(
            f"{day:02d} {calendar.month_name[layer['month']]} {YEAR}\n"
            f"Sampled daily range: {value:.2f} m\n"
            f"Highest hourly prediction: {max(heights):.2f} m\n"
            f"Lowest hourly prediction: {min(heights):.2f} m")


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TideWindow()
    window.show()
    print("Opened native tide explorer. Close its window to return to the terminal.", flush=True)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
