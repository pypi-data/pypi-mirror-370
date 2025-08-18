from dash import html, dcc
import dash_bootstrap_components as dbc

from wiliot_testers.failure_analysis_tester.configs_gui import RELAY_CONFIG

ELEMENT_WIDTH = "300px"
BUTTON_WIDTH = 30
CELL_STYLE = {"width": ELEMENT_WIDTH, "display": "flex", "justifyContent": "center",
              "alignItems": "center", "flexDirection": "column", "gap": "10px"}
BUTTON_STYLE = {"width": "200px", "height": "20px", "fontSize": "14px",
                "display": "flex", "alignItems": "center", "justifyContent": "center"}
TEST_OPTIONS = [
    {'label': 'IV Curve', 'value': 'IV Curve'},
    {'label': 'Voltage Drop', 'value': 'Voltage Drop'},
    {'label': 'External Power Source', 'value': 'External Power Source'}
]


def get_tag_alias():
    return html.Div(
        [html.Label("Tag Alias"),
         dbc.Input(id="tag_alias", type="text")],
        style={"width": ELEMENT_WIDTH})


def get_folder_name():
    return html.Div(
        [html.Label("Folder Run Name"),
         dbc.Input(id="folder_name", type="text")],
        style={"width": ELEMENT_WIDTH})


def get_comment():
    return html.Div(
        [html.Label("Comment (optional)"),
         dbc.Input(id="test_comment", type="text")],
        style={"width": ELEMENT_WIDTH})


def get_test_type():
    return html.Div([
        html.Label("Test Type"),
        dcc.Dropdown(
            id='test_type',
            options=TEST_OPTIONS,
            value='IV Curve'),],
        style={"width": ELEMENT_WIDTH})


def get_run_finish_buttons():
    return html.Div([
        dbc.Button("Run Test", id="run_test", color="success",
                   n_clicks=0, style={"width": "200px"}),
        dbc.Button("Finish Test", id="finish_test",
                   color="danger", n_clicks=0, style={"width": "200px"}),
    ], style=CELL_STYLE)


def get_test_checkbox():
    return html.Div([
        dcc.Checklist(list(RELAY_CONFIG.keys()), list(
                    RELAY_CONFIG.keys()), id="test_fields",),
    ], style={"width": ELEMENT_WIDTH, "gap": "10px", "display": "flex", "alignItems": "center"})


def get_test_result():
    return html.Div([
        html.Label("Results"),
        dbc.Textarea(id="test_result", rows=4, disabled=True)
    ], style={"width": ELEMENT_WIDTH})


def get_config_buttons():
    return html.Div([
        dbc.Button("Open Config Json", id="open_config_json",
                   color="info", className="mb-2", style=BUTTON_STYLE),
        dbc.Button("Load Config Json", id="load_config_json",
                   color="info", className="mb-2", style=BUTTON_STYLE),
        dbc.Button("Open Output Folder", id="open_output_folder",
                   color="info", className="mb-2", style=BUTTON_STYLE),
    ], style={"width": ELEMENT_WIDTH, "display": "flex", "justifyContent": "center",
              "alignItems": "center", "flexDirection": "column", "gap": "3px"})


def get_plot_selection():
    return html.Div([
        html.Label("Plot Selection"),
        dcc.Dropdown(
            id='plot-selection',
            options=['Empty'] + list(RELAY_CONFIG.keys()),
            value='Empty'),
    ], style={"width": ELEMENT_WIDTH})
    # dbc.Row([
    #     # Left buttons (Run / Finish)
    #     dbc.Col(
    #         html.Div(
    #             html.Div([
    #                 dbc.Button("Run Test", id="run_test", color="success", n_clicks=0, style={
    #                            "width": "3px"}),
    #                 dbc.Button("Finish Test", id="finish_test",
    #                            color="danger", n_clicks=0, style={"width": "3px"})
    #             ], className="d-flex flex-column"),
    #             className="d-flex align-items-center justify-content-center h-100",
    #             style={"width": ELEMENT_WIDTH}),
    #         width="auto"
    #     ),
    #     dcc.ConfirmDialog(
    #         id="confirm", message="Are you sure you want to end the test?"),
    #     # Test checkbox
    #     dbc.Col(
    #         html.Div([
    #             dcc.Checklist(list(RELAY_CONFIG.keys()), list(
    #                 RELAY_CONFIG.keys()), id="test_fields",),
    #         ], style={"width": ELEMENT_WIDTH}),
    #         width="auto"
    #     ),
    #     # Test result field
    #     dbc.Col(
    #         html.Div([
    #             html.Label("Results"),
    #             dbc.Textarea(id="test_result", rows=4, disabled=True)
    #         ], style={"width": ELEMENT_WIDTH}),
    #     ),
    #     # Right buttons (Config / Output)
    #     dbc.Col(
    #         html.Div([
    #             dbc.Button("Open Config Json", id="open_config_json",
    #                        color="info", className="mb-2"),
    #             dbc.Button("Load Config Json", id="load_config_json",
    #                        color="info", className="mb-2"),
    #             dbc.Button("Open Output Folder", id="open_output_folder",
    #                        color="info", className="mb-2"),
    #         ], className="d-flex flex-column"),
    #         width="auto"
    #     ),
