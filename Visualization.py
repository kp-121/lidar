from DataExtractor import DataExtractor
from LMOG import LiDARMOG

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import numpy as np


class Visualization:
    def __init__(self, extractor: DataExtractor, mog: LiDARMOG, radius: float = 10.0):
        self.extractor = extractor
        self.mog = mog
        self.radius = radius
        self.app = dash.Dash(__name__)
        self._setup_layout()
        self._register_callbacks()

    def _setup_layout(self):
        self.app.layout = html.Div([
            html.Button('Pause', id='pause-button', n_clicks=0),
            dcc.Store(id='pause-store', data=False),
            dcc.Graph(id='lidar-graph', style={'height': '90vh'}),
            dcc.Interval(id='interval-component', interval=100, disabled=False, n_intervals=0)
        ])

    def _register_callbacks(self):
        @self.app.callback(
            [Output('interval-component', 'disabled'),
             Output('pause-store', 'data'),
             Output('pause-button', 'children')],
            Input('pause-button', 'n_clicks'),
            State('pause-store', 'data')
        )
        def toggle_pause(n_clicks, paused):
            if n_clicks is None:
                raise PreventUpdate
            new_paused = not paused
            btn_text = 'Resume' if new_paused else 'Pause'
            return new_paused, new_paused, btn_text

        @self.app.callback(
            Output('lidar-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_graph(n):
            pts = self.extractor.get_latest_cloud()
            fg_bins = self.mog.update(pts)
            xs, ys, cs = zip(*pts) if pts else ([], [], [])
            zs = [0.0] * len(xs)
            scatter3d = go.Scatter3d(
                x=xs, y=ys, z=zs,
                mode='markers',
                marker=dict(size=4, color=cs, colorscale='Viridis', cmin=0, cmax=255)
            )
            origin = go.Scatter3d(
                x=[0], y=[0], z=[0], mode='markers',
                marker=dict(size=6, color='red', symbol='diamond')
            )
            theta = np.radians(fg_bins)
            ranges = self.mog.last_binned[fg_bins]
            mx = np.cos(theta) * ranges
            my = np.sin(theta) * ranges
            fg_scatter = go.Scatter3d(
                x=mx, y=my, z=[0]*len(mx), mode='markers',
                marker=dict(size=6, color='orange', symbol='circle'),
                name='Motion'
            )
            fig = go.Figure(data=[scatter3d, origin, fg_scatter])
            fig.update_layout(
                title="3D LiDAR MOG Motion Detection",
                scene=dict(
                    xaxis=dict(range=[-self.radius, self.radius], autorange=False),
                    yaxis=dict(range=[-self.radius, self.radius], autorange=False),
                    zaxis=dict(range=[-1, 1], autorange=False),
                    aspectmode='cube'
                ),
                margin=dict(l=0, r=0, b=0, t=30),
                uirevision='constant'
            )
            return fig

    def run(self, debug: bool = True, use_reloader: bool = False):
        try:
            self.app.run(debug=debug, use_reloader=use_reloader)
        finally:
            self.extractor.shutdown()
