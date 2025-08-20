import plotly.graph_objects as go, numpy as np
from catrxneng.utils import plot_info_box


class BasicPlot:

    def __init__(self, title=None):
        self.fig = go.Figure()
        self.title = title

    def add_trace(self, x, y, name=None, mode="lines", hover_label=None):
        if isinstance(y, (float, int)):
            if x is not None:
                xmin = np.min(x)
                xmax = np.max(x)
            x = [xmin, xmax]
            y = [y, y]
        trace = go.Scatter(
            x=x,
            y=y,
            mode=mode,
            name=name,
            text=hover_label,
            hovertemplate="<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>",
        )
        self.fig.add_trace(trace)

    def render(self, xlabel, ylabel, xrange=None, yrange=None, info_text=None):
        if xrange is None:
            xrange = [None, None]
        if yrange is None:
            yrange = [None, None]

        top = 50
        width = 650
        if info_text is None:
            bottom = 50
            height = 400
        else:
            bottom = 110
            height = None

        self.fig.update_layout(
            title=dict(text=f"<b>{self.title}</b>", x=0.5),
            xaxis_title=f"<b>{xlabel}</b>",
            yaxis_title=f"<b>{ylabel}</b>",
            width=width,
            height=height,
            margin=dict(t=top, b=bottom),
            yaxis=dict(
                range=yrange,
                showline=True,
                linecolor="black",
                linewidth=2,
                mirror=True,
                nticks=9,
            ),
            xaxis=dict(
                range=xrange,
                showline=True,
                linecolor="black",
                linewidth=2,
                mirror=True,
            ),
            annotations=plot_info_box(info_text),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        self.fig.show()
