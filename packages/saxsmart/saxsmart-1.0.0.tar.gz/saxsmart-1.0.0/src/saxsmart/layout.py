import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_molstar

from importlib.metadata import version

try:
    app_version = version("saxsmart")
except Exception:
    app_version = "dev"

from .utils import create_placeholder_figure, SAXS_QUOTES, COLORS

# ==============================================================================
# Reusable Layout Components
# ==============================================================================


def make_card(title, content, extra_class="", header_extra=None):
    """Creates a card with an optional extra component in the header."""
    header_content = [html.H5(title, className="card-title")]
    if header_extra:
        header_content.append(header_extra)

    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(header_content, className="card-header-flex"),
                html.Div(content, className="flex-grow-1 position-relative"),
            ],
            className="d-flex flex-column h-100",
        ),
        className=f"h-100 {extra_class}",
    )


def make_starting_model_viewer_card(viewer_id, alignment_id):
    """Creates the content for the starting model viewer card."""
    viewer_layout = {"backgroundColor": "#0F192E", "showControls": False}
    return html.Div(
        [
            html.Div(
                dash_molstar.MolstarViewer(
                    id=viewer_id,
                    style={"width": "100%", "height": "100%", "position": "relative"},
                    layout=viewer_layout,
                ),
                style={"height": "66%"},
            ),
            html.Div(
                id=alignment_id,
                style={
                    "height": "34%",
                    "overflowY": "auto",
                    "backgroundColor": COLORS["highlight"],
                    "padding": "10px",
                },
            ),
        ],
        className="d-flex flex-column h-100",
    )


def make_refined_model_viewer_card(viewer_id):
    """Creates the content for the refined model viewer card."""
    viewer_layout = {"backgroundColor": "#0F192E", "showControls": False}
    return dash_molstar.MolstarViewer(
        id=viewer_id,
        style={"width": "100%", "height": "100%", "position": "relative"},
        layout=viewer_layout,
    )


def make_status_panel(items):
    """Generates the HTML for the refinement status panel."""
    children = [html.H6("Refinement Status", className="card-title")]
    for text, icon_class, is_muted in items:
        item_class = "status-item"
        if is_muted:
            item_class += " status-item-muted"

        icon = (
            html.Div(className="spinner-border status-spinner", role="status")
            if "spinner-border" in icon_class
            else html.I(className=f"{icon_class} status-icon")
        )
        children.append(html.Div([icon, html.Span(text)], className=item_class))
    return html.Div(children)


def info_icon(target_id, text):
    """Creates a small info icon with a tooltip."""
    return html.Span(
        [
            html.I(
                className="fas fa-info-circle ms-2",
                id=target_id,
                style={"cursor": "pointer", "color": "#aaa"},
            ),
            dbc.Tooltip(text, target=target_id, placement="right"),
        ]
    )


# ==============================================================================
# Main App Layout
# ==============================================================================

upload_style = {
    "backgroundColor": "#14213D",
    "borderRadius": "5px",
    "padding": "1rem",
    "textAlign": "left",
    "cursor": "pointer",
    "color": "#E5E5E5",
    "border": "none",
}

controls_panel = dbc.Col(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.Img(
                                src="./assets/esrf_logo.png",
                                className="me-2",
                                style={"height": "120px"},
                            ),
                            html.Img(
                                src="./assets/bm29_logo.png", style={"height": "120px"}
                            ),
                        ],
                        className="mb-4 d-flex justify-content-center",
                    ),
                    html.Hr(style={"borderColor": COLORS["text"]}),
                    html.H2("SAXSMART", className="display-6 text-center"),
                    html.P(
                        "SAXS Modelling and Refinement Toolkit",
                        className="lead text-center mb-4",
                    ),
                    html.Hr(style={"borderColor": COLORS["text"]}),
                    dbc.Label(
                        [
                            "1. Select SAXS curve:",
                            info_icon(
                                "info-saxs",
                                "Upload a .dat file with 3 columns: q, I, err.",
                            ),
                        ]
                    ),
                    dcc.Upload(
                        id="upload-saxs-data",
                        children="Select a file...",
                        className="mb-3",
                        style=upload_style,
                    ),
                    dbc.Label(
                        [
                            "2. Select sequence file:",
                            info_icon(
                                "info-seq",
                                "Upload a .fasta file with the protein sequence.",
                            ),
                        ]
                    ),
                    dcc.Upload(
                        id="upload-sequence-data",
                        children="Select a file...",
                        className="mb-3",
                        style=upload_style,
                    ),
                    dbc.Label(
                        [
                            "3. Upload or Fetch Model:",
                            info_icon(
                                "info-model",
                                "Upload a .pdb or .cif file, or fetch by PDB/AlphaFold DB ID.",
                            ),
                        ]
                    ),
                    dcc.Upload(
                        id="upload-pdb-data",
                        children="Select a file...",
                        className="mb-3",
                        style=upload_style,
                    ),
                    dbc.InputGroup(
                        [
                            dbc.Input(
                                id="pdb-id-input",
                                placeholder="or PDB or AFDB ID",
                                type="text",
                                className="control-text-input",
                            ),
                            dbc.Button(
                                "Fetch", id="fetch-pdb-button", color="secondary"
                            ),
                        ],
                        className="mb-3",
                    ),
                    html.Hr(style={"borderColor": COLORS["text"]}),
                    dbc.Label("Select forward model:"),
                    dbc.RadioItems(
                        options=[
                            {"label": "PEPSI-SAXS", "value": "pepsi"},
                            {"label": "Crysol", "value": "crysol", "disabled": True},
                            {"label": "FoXS", "value": "foxs", "disabled": True},
                        ],
                        value="pepsi",
                        id="forward-model-selector",
                        className="mb-4",
                    ),
                    dbc.Button(
                        "Refine",
                        id="refine-button",
                        color="primary",
                        size="lg",
                        className="w-100",
                    ),
                ]
            ),
            className="h-100",
        ),
        html.Div(style={"minHeight": "1rem"}),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Words of SAXS Wisdom", className="card-title"),
                    html.Div(
                        id="saxs-wisdom-text",
                        children=[html.P(SAXS_QUOTES[0], className="fst-italic")],
                    ),
                ]
            )
        ),
    ],
    md=3,
    className="p-3 d-flex flex-column",
)

parameters_content = html.Div(
    dbc.Row(
        [
            dbc.Col(
                html.Span(["Guinier Rg: ", html.B(id="guinier-rg-val", children="N/A")])
            ),
            dbc.Col(html.Span([" P(r) Rg: ", html.B(id="pr-rg-val", children="N/A")])),
            dbc.Col(html.Span([" Dmax: ", html.B(id="dmax-val", children="N/A")])),
        ],
        className="g-0",
    ),
    className="param-row-top",
)

plot_grid_content = html.Div(
    [
        dcc.Graph(
            id="iq-guinier-plot",
            figure=create_placeholder_figure(),
            config={"displayModeBar": False},
        ),
        dcc.Graph(
            id="kratky-plot",
            figure=create_placeholder_figure(),
            config={"displayModeBar": False},
        ),
        dcc.Graph(
            id="pr-plot",
            figure=create_placeholder_figure(),
            config={"displayModeBar": False},
        ),
        dcc.Graph(
            id="shannon-plot",
            figure=create_placeholder_figure(),
            config={"displayModeBar": False},
        ),
    ],
    className="plot-grid-container-expanded",
)

refinement_curves_content = dbc.Row(
    [
        dbc.Col(
            [
                html.Div(
                    dcc.Graph(
                        id="refinement-iq-plot",
                        figure=create_placeholder_figure("I(q) fit"),
                        config={"displayModeBar": False},
                        style={"height": "100%"},
                    ),
                    style={"height": "66%"},
                ),
                html.Div(
                    dcc.Graph(
                        id="refinement-residuals-plot",
                        figure=create_placeholder_figure("Residuals"),
                        config={"displayModeBar": False},
                        style={"height": "100%"},
                    ),
                    style={"height": "34%"},
                ),
            ],
            md=6,
            className="d-flex flex-column h-100 p-1",
        ),
        dbc.Col(
            html.Div(
                id="refinement-status-container",
                children=make_status_panel(
                    [("Awaiting refinement start", "far fa-circle", True)]
                ),
            ),
            md=6,
            className="d-flex flex-column h-100 p-2",
        ),
    ],
    className="g-0 h-100",
)

top_bar = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            [
                dbc.Col(
                    html.A(
                        "Load Example Data",
                        href="#",
                        id="load-example-data-link",
                        className="top-bar-link",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.A(
                        "Generate Report", href="#", className="top-bar-link-disabled"
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.A(
                        "References",
                        href="#",
                        id="references-link",
                        className="top-bar-link",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Span(f"Version {app_version}", className="top-bar-text"),
                    width="auto",
                ),
            ],
            justify="between",
            align="center",
        ),
        className="p-2",
    )
)

references_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("References")),
        dbc.ModalBody(
            [
                html.H5("PEPSI-SAXS"),
                html.P(
                    "Grudinin, S., Garkavenko, M., & Kazennov, A. (2017). Pepsi-SAXS: an adaptive method for rapid and accurate computation of small-angle X-ray scattering profiles. Acta Crystallographica Section D Structural Biology, 73(5), 449–464. https://doi.org/10.1107/s2059798317005745"
                ),
                html.Hr(),
                html.H5("NOLB"),
                html.P(
                    "Hoffmann, A., & Grudinin, S. (2017). NOLB: Nonlinear Rigid Block Normal-Mode Analysis Method. Journal of Chemical Theory and Computation, 13(5), 2123–2134. https://doi.org/10.1021/acs.jctc.7b00197"
                ),
            ]
        ),
    ],
    id="references-modal",
    is_open=False,
    size="lg",
)

content_panel = dbc.Col(
    [
        dbc.Row([dbc.Col(top_bar)], className="g-0 px-2 pt-2"),
        dbc.Row(
            [
                dbc.Col(
                    make_card(
                        "Experimental Data",
                        plot_grid_content,
                        header_extra=parameters_content,
                    ),
                    md=6,
                    className="h-100 p-2",
                ),
                dbc.Col(
                    make_card(
                        "Starting Model & Sequence Alignment",
                        make_starting_model_viewer_card(
                            "starting-molstar-viewer", "starting-model-alignment"
                        ),
                    ),
                    md=6,
                    className="h-100 p-2",
                ),
            ],
            className="g-0 h-50",
        ),
        dbc.Row(
            [
                dbc.Col(
                    make_card("Refinement", refinement_curves_content),
                    md=6,
                    className="h-100 p-2",
                ),
                dbc.Col(
                    make_card(
                        "Refined Model",
                        make_refined_model_viewer_card("refined-molstar-viewer"),
                    ),
                    md=6,
                    className="h-100 p-2",
                ),
            ],
            className="g-0 h-50",
        ),
    ],
    md=9,
    className="h-100 p-0 d-flex flex-column",
)

layout = dbc.Container(
    [
        dcc.Interval(id="quote-interval", interval=30 * 1000, n_intervals=0),
        dcc.Store(id="saxs-file-path-store"),
        dcc.Store(id="sequence-file-path-store"),
        dcc.Store(id="model-file-path-store"),
        dcc.Store(id="refinement-results-store"),
        dcc.Store(id="user-sequence-store"),
        dcc.Store(id="model-sequence-store"),
        dcc.Store(id="example-model-data-store"),
        dcc.Store(id="initial-fit-trigger-store"),
        dcc.Store(id="flexible-refinement-trigger-store"),
        html.Div(id="alert-container"),
        references_modal,
        dbc.Row([controls_panel, content_panel], className="h-100 g-0"),
    ],
    fluid=True,
    className="vh-100",
)
