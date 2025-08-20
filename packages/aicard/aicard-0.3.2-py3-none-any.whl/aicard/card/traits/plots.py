import base64
import pandas as pd
import plotly.io as pio
import plotly.express as px
import matplotlib.pyplot as plt
from io import BytesIO
from typing import List


def mtplot_to_base64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    base64_string = base64.b64encode(buf.read()).decode("utf-8")  # Encode as Base64
    buf.close()
    return "data:image/png;base64," + base64_string


class Plots:
    def bar_plot(
        self,
        pdata: pd.DataFrame,
        title: str,
        x: str,
        y: str,
        ptype: str = "ipython",
        xaxis_title: str = "",
        yaxis_title: str = "",
        width: int = 700,
        height: int = 700,
        color=None,
        barmode="relative",
    ):
        if ptype == "ipython":
            width = len(pdata) * 30 + 200
            fig = px.bar(pdata, x=x, y=y, title=title, color=color, barmode=barmode)
            fig.update_layout(
                xaxis_title=xaxis_title,  # Blank x-axis label
                yaxis_title=yaxis_title,  # You can change this to whatever you like
                width=width,  # Set the width to your desired size
                height=height,  # Set the height to your desired size
                font=dict(size=18),  # Adjust the font size here
            )
            plot_html = pio.to_html(fig, full_html=False)
            fig.write_html(f"{title}.html")
            return plot_html
        elif ptype == "mtplotpng":
            return
        elif ptype == "mtplotbase64":
            return

    def insert_img(self, file_path: str, destination: str, title: str):
        self.json[destination][title] = file_path

    # Bar plots
    def fill_bar_plot(self, plot_title: str, labels: List[str], values: List[float]):
        # data = "acc", "ap", or "f1"
        for label, value in zip(labels, values):
            self.append_bar_to_plot(title=plot_title, label=label, value=value)

    def init_bar_plot(self, title: str, xlabel: str = " ", ylabel: str = " "):
        if title in self.bar_plot_data:
            print(f"Plot with title '{title}' already exists.")
            return
        self.bar_plot_data[title] = {"bars": [], "xlabel": xlabel, "ylabel": ylabel}

    def append_bar_to_plot(self, title: str, label: str, value: float):
        if title not in self.bar_plot_data:
            print(
                f"Plot with title '{title}' does not exist. Create it first using 'init_bar_plot'."
            )
            return
        self.bar_plot_data[title]["bars"].append((label, value))

    def add_plot_to(self, title: str, destination: str):  # TODO: Generaliez this
        if title not in self.bar_plot_data:
            print(f"Plot with title '{title}' does not exist.")
            return
        plot_data = self.bar_plot_data[title]
        bars = plot_data["bars"]
        if not bars:
            print(f"No data to plot for '{title}'.")
            return
        # Unpack bar names and values
        names, values = zip(*bars)
        # Create the bar plot
        plt.figure(figsize=(6, 9))
        plt.bar(names, values)
        plt.title(title)
        plt.xlabel(plot_data["xlabel"])
        plt.xticks(rotation=90)
        plt.ylabel(plot_data["ylabel"])
        plt.tight_layout(pad=3.0)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt64 = mtplot_to_base64(plt)
        self.json[destination][title] = plt64

    def add_interactive_plot_to(
        self,
        title: str,
        destination: str,
        shap_plot=-1,  # -1 if not used None if shap plot is passed
        base64encode: bool = False,
    ):
        if shap_plot != -1:
            fig = plt.gcf()

            def on_close(event):
                print("Window closed. Capturing all changes...")
                if base64encode:
                    src = mtplot_to_base64(fig)
                else:
                    src = (
                        f"{destination.replace(' ', '_')}_{title.replace(' ', '_')}.png"
                    )
                    fig.savefig(src, format="png")
                self.json[destination][title] = src
                plt.close(fig)

            fig.canvas.mpl_connect("close_event", on_close)
            plt.show()
            return
        elif title not in self.bar_plot_data:
            print(
                f"Plot with title '{title}' does not exist, and no SHAP plot was provided."
            )
            return
        else:
            # Handle a traditional Matplotlib plot
            plot_data = self.bar_plot_data[title]
            bars = plot_data["bars"]
            if not bars:
                print(f"No data to plot for '{title}'.")
                return
            # Unpack bar names and values
            names, values = zip(*bars)
            plt.figure(figsize=(6, 9))
            plt.bar(names, values)
            plt.title(title)
            plt.xlabel(plot_data["xlabel"])
            plt.xticks(rotation=90)
            plt.ylabel(plot_data["ylabel"])
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            fig = plt.gcf()

            def on_close(event):
                print("Window closed. Capturing all changes...")
                if base64encode:
                    src = mtplot_to_base64(fig)
                else:
                    src = (
                        f"{destination.replace(' ', '_')}_{title.replace(' ', '_')}.png"
                    )
                    fig.savefig(src, format="png")
                self.json[destination][title] = src
                plt.close(fig)

            fig.canvas.mpl_connect("close_event", on_close)
            plt.show()
            return

    def show_plot(self, title: str):
        if title not in self.bar_plot_data:
            print(f"Plot with title '{title}' does not exist.")
            return
        plot_data = self.bar_plot_data[title]
        bars = plot_data["bars"]
        if not bars:
            print(f"No data to plot for '{title}'.")
            return
        names, values = zip(*bars)
        plt.figure(figsize=(10, 6))
        plt.bar(names, values)
        plt.title(title)
        plt.xlabel(plot_data["xlabel"])
        plt.ylabel(plot_data["ylabel"])
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()
