import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import plotly.graph_objs as go
import datetime

app = dash.Dash(__name__)
server = app.server  

app.layout = html.Div([
    html.H1("System Metrics Dashboard", style={"textAlign": "center"}),
    dcc.Interval(id='interval-component', interval=5000, n_intervals=0),
    dcc.Graph(id='cpu-graph'),
    dcc.Graph(id='memory-graph'),
    dcc.Graph(id='disk-graph')
])

def fetch_metrics():
    try:
        res = requests.get("http://localhost:8000/history")
        return res.json()
    except:
        return []

@app.callback(
    [Output('cpu-graph', 'figure'),
     Output('memory-graph', 'figure'),
     Output('disk-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    data = fetch_metrics()
    timestamps = [datetime.datetime.fromtimestamp(item["timestamp"]) for item in data]
    
    cpu = [item["cpu"]["average"] for item in data]
    mem = [item["memory"]["percent"] for item in data]
    disk = [item["disk"]["percent"] for item in data]

    fig_cpu = go.Figure(go.Scatter(x=timestamps, y=cpu, mode='lines+markers'))
    fig_cpu.update_layout(title='CPU Usage (%)')

    fig_mem = go.Figure(go.Scatter(x=timestamps, y=mem, mode='lines+markers'))
    fig_mem.update_layout(title='Memory Usage (%)')

    fig_disk = go.Figure(go.Scatter(x=timestamps, y=disk, mode='lines+markers'))
    fig_disk.update_layout(title='Disk Usage (%)')

    return fig_cpu, fig_mem, fig_disk

if __name__ == '__main__':
    app.run(debug=True)
