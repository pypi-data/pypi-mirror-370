from .basic_plot import BasicPlot

# import plotly.graph_objects as go, numpy as np


# def plot(config):
#     fig = go.Figure()
#     for key, value in config["traces"].items():
#         x = value.get("x")
#         y = value["y"]
#         if x is not None:
#             xmin = np.min(x)
#             xmax = np.max(x)
#         if isinstance(y, (float, int)):
#             x = [xmin, xmax]
#             y = [y, y]
#         trace = go.Scatter(
#             x=x,
#             y=y,
#             mode=value["mode"],
#             name=key,
#             text=value.get("hover_labels"),
#             hovertemplate="<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>",
#         )
#         fig.add_trace(trace)

#     xmin = config.get("xmin")
#     xmax = config.get("xmax")
#     ymin = config.get("ymin")
#     ymax = config.get("ymax")

#     fig.update_layout(
#         title=dict(text=f"<b>{config['title']}</b>", x=0.5),
#         xaxis_title=f"<b>{config['xlabel']}</b>",
#         yaxis_title=f"<b>{config['ylabel']}</b>",
#         width=650,
#         # height=400,
#         height=None,
#         margin=dict(t=50, b=110),
#         # margin=dict(t=50, b=50),
#         yaxis=dict(
#             range=[ymin, ymax],
#             showline=True,
#             linecolor="black",
#             linewidth=2,
#             mirror=True,
#             nticks=9,
#         ),
#         xaxis=dict(
#             range=[xmin, xmax],
#             showline=True,
#             linecolor="black",
#             linewidth=2,
#             mirror=True,
#         ),
#         annotations=config.get("info_text"),
#         plot_bgcolor="white",
#         paper_bgcolor="white",
#         # colorway=px.colors.qualitative.D3
#         # colorway=px.colors.qualitative.Set1
#         # colorway=px.colors.qualitative.Pastel
#         # colorway=px.colors.qualitative.Dark2
#     )

#     fig.show()
