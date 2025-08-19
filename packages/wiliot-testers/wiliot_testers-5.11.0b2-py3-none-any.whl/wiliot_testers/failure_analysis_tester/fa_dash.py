from dash import Dash, html, dcc, Input, Output, State, clientside_callback, callback_context
import dash_bootstrap_components as dbc
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from wiliot_core.utils.utils import open_directory
from wiliot_testers.failure_analysis_tester.fa_dash_components import *
from wiliot_testers.failure_analysis_tester.configs_gui import CONFIG_FILE, CONFIGS_DIR
from wiliot_testers.failure_analysis_tester.failure_analysis_tester import FailureAnalysisTester

ELEMENT_WIDTH = "300px"
BUTTON_WIDTH = 30
TEST_OPTIONS = [
    {'label': 'IV Curve', 'value': 'IV Curve'},
    {'label': 'Voltage Drop', 'value': 'Voltage Drop'},
    {'label': 'External Power Source', 'value': 'External Power Source'}
]

FAT = FailureAnalysisTester()

app = Dash(__name__, external_stylesheets=[
           dbc.themes.MINTY, dbc.icons.FONT_AWESOME])

color_mode_switch = html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="color-mode-switch"),
        dbc.Switch(id="color-mode-switch", value=False,
                   className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="color-mode-switch"),
    ]
)

clientside_callback(
    """
    (switchOn) => {
       document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');
       return window.dash_clientside.no_update
    }
    """,
    Output("color-mode-switch", "id"),
    Input("color-mode-switch", "value"),
)

app.layout = dbc.Container(
    [
        dcc.ConfirmDialog(
            id="confirm", message="Are you sure you want to end the test?"),
        color_mode_switch,
        html.H3(["Failure Analysis Tester"],
                className="bg-info p-3 text-center"),
        html.Br(),
        html.Div([
            get_tag_alias(),
            get_folder_name(),
            get_comment(),
            get_test_type(),
            get_run_finish_buttons(),
            get_test_checkbox(),
            get_test_result(),
            get_config_buttons(),
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '10px', }),
        html.Br(),
        dcc.Loading(id="loading-output", type="default",
                    children=[html.Div(id="output")]),
        html.Br(),
        get_plot_selection(),
        html.Br(),
        dcc.Graph(id='graph-content', style={"display": "none"}),
    ],
)


@app.callback(
    Output('graph-content', 'figure'),
    Output('graph-content', 'style'),
    Input('plot-selection', 'value'),
    prevent_initial_call=True
)
def update_graph(value):
    fig = go.Figure()
    if value == 'Empty' or value + '_current_uA' not in FAT.df.columns or value + '_voltage_V' not in FAT.df.columns:
        return fig, {"display": "none"}
    
    fig.add_trace(go.Scatter(x=FAT.df[value + '_current_uA'].values, y=FAT.df[value + '_voltage_V'].values, mode='markers', name="Set 1"))
    
    # plot reference if exist
    csv_files = list(CONFIGS_DIR.glob("*.csv"))
    if len(csv_files) == 1:
        reference_df = pd.read_csv(csv_files[0])
        if value + '_current_uA' in reference_df.columns:
            x_ref = reference_df[value + '_current_uA'].values
            lower_limit = reference_df[value + '_min_voltage'].values
            upper_limit = reference_df[value + '_max_voltage'].values
            fig.add_trace(go.Scatter(x=x_ref, y=lower_limit, mode='lines+markers'))
            fig.add_trace(go.Scatter(x=x_ref, y=upper_limit, mode='lines+markers'))

    fig.update_layout(showlegend=False, xaxis_title="Current [uA]", yaxis_title="Voltage [V]")
    return fig, {"display": "block", "height":"700px"}


@app.callback(
    Output("open_config_json", "n_clicks"),
    Input("open_config_json", "n_clicks"),
    prevent_initial_call=True
)
def open_config_json(n_clicks):
    if n_clicks:
        open_directory(CONFIG_FILE.parent)
    return 0


@app.callback(
    Output("load_config_json", "n_clicks"),
    Input("load_config_json", "n_clicks"),
    prevent_initial_call=True
)
def load_config_json(n_clicks):
    if n_clicks:
        FAT.load_config()
    return 0


@app.callback(
    Output("open_output_folder", "n_clicks"),
    Input("open_output_folder", "n_clicks"),
    prevent_initial_call=True
)
def open_output_folder(n_clicks):
    if n_clicks:
        if FAT.output_dir:
            open_directory(FAT.output_dir)
    return 0


@app.callback(
    Output("confirm", "displayed", allow_duplicate=True),
    Input("confirm", "submit_n_clicks"),
    prevent_initial_call=True
)
def close_app(n_clicks):
    if n_clicks:
        FAT.end_test()
        print('done2')
        os._exit(0)
    return False  # Close the ConfirmDialog


@app.callback(
    Output("confirm", "displayed"),
    Input("finish_test", "n_clicks"),
    prevent_initial_call=True
)
def show_confirm(n_clicks):
    return True  # Triggers the pop-up


@app.callback(
    Output("test_result", "style"),
    Input("test_result", "value"),
    prevent_initial_call=True
)
def update_input_style(value):
    color_map = {
        "Fail": "#ffcccc",
        "Pass": "#28a745"
    }
    return {"backgroundColor": color_map.get(value, "")}


@app.callback(
    Output("run_test", "disabled", allow_duplicate=True),
    Output("test_comment", "disabled", allow_duplicate=True),
    Output("test_type", "disabled", allow_duplicate=True),
    Output("tag_alias", "disabled", allow_duplicate=True),
    Output("finish_test", "disabled", allow_duplicate=True),
    Output("test_result", "value"),
    Output("loading-output", "children"),
    Input("run_test", "disabled"),
    State("test_type", "value"),
    State("folder_name", "value"),
    State("tag_alias", "value"),
    State("test_comment", "value"),
    State("test_fields", "value"),
    prevent_initial_call=True
)
def run_test(disabled, test_type, folder_name, tag_alias, comment, test_fields):
    if disabled:
        FAT.run_test(test_type=test_type, folder_name=folder_name,
                     tag_alias=tag_alias, comment=comment, keys=test_fields)
        test_result = FAT.check_test()
        return False, False, False, False, False, test_result, None
    else:
        return True, True, True, True, True, '', None


@app.callback(
    Output("folder_name", "disabled"),
    Output("test_comment", "disabled"),
    Output("test_type", "disabled"),
    Output("tag_alias", "disabled"),
    Output("run_test", "disabled"),
    Output("finish_test", "disabled"),
    Input("run_test", "n_clicks"),
    prevent_initial_call=True
)
def run_test_button(n_clicks):
    return True, True, True, True, True, True


if __name__ == "__main__":
    import webbrowser
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server()
