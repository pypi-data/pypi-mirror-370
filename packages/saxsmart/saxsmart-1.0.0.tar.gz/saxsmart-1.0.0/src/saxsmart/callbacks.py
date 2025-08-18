import os
import shutil
import glob
import time
import random
import base64

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, State, callback_context, no_update, html, dcc
from dash_molstar.utils import molstar_helper

# Import functions and variables from other modules
from .utils import (
    TEMP_DIR,
    SCRIPT_DIR,
    SAXS_QUOTES,
    COLORS,
    parse_saxs_data,
    auto_guinier_fit,
    calculate_pr,
    create_kratky_plot,
    create_pr_plot,
    create_shannon_plot,
    parse_sequence_file,
    parse_structure_file,
    fetch_structure_from_db,
    extract_sequence_from_pdb,
    create_alignment_view,
    run_pepsi_saxs,
    parse_pepsi_output,
    create_placeholder_figure,
)
from .layout import make_status_panel


def register_callbacks(app):
    @app.callback(
        Output("references-modal", "is_open"),
        [Input("references-link", "n_clicks")],
        [State("references-modal", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_modal(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("saxs-file-path-store", "data", allow_duplicate=True),
        Output("sequence-file-path-store", "data", allow_duplicate=True),
        Output("example-model-data-store", "data"),
        Output("alert-container", "children", allow_duplicate=True),
        Input("load-example-data-link", "n_clicks"),
        prevent_initial_call=True,
    )
    def load_example_data(n_clicks):
        if not n_clicks:
            return no_update, no_update, no_update, no_update

        example_dir = os.path.join(SCRIPT_DIR, "example_data")
        if not os.path.isdir(example_dir):
            alert = dbc.Alert(
                "Error: 'example_data' directory not found.",
                color="danger",
                dismissable=True,
            )
            return no_update, no_update, no_update, alert

        try:
            saxs_file = glob.glob(os.path.join(example_dir, "*.dat"))[0]
            seq_file = glob.glob(os.path.join(example_dir, "*.fasta"))[0]
            model_file = glob.glob(os.path.join(example_dir, "*.pdb"))[0]

            saxs_dest = os.path.join(TEMP_DIR, os.path.basename(saxs_file))
            seq_dest = os.path.join(TEMP_DIR, os.path.basename(seq_file))
            shutil.copy(saxs_file, saxs_dest)
            shutil.copy(seq_file, seq_dest)

            with open(model_file, "r") as f:
                model_content = f.read()

            model_data = {
                "contents": model_content,
                "filename": os.path.basename(model_file),
            }

            return saxs_dest, seq_dest, model_data, None

        except IndexError:
            alert = dbc.Alert(
                "Error: Could not find required .dat, .fasta, and .pdb files in 'example_data' directory.",
                color="danger",
                dismissable=True,
            )
            return no_update, no_update, no_update, alert
        except Exception as e:
            alert = dbc.Alert(
                f"An error occurred while loading example data: {e}",
                color="danger",
                dismissable=True,
            )
            return no_update, no_update, no_update, alert

    @app.callback(
        Output("saxs-file-path-store", "data"),
        Input("upload-saxs-data", "contents"),
        State("upload-saxs-data", "filename"),
        prevent_initial_call=True,
    )
    def store_saxs_data(contents, filename):
        if contents:
            _, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
            saxs_path = os.path.join(TEMP_DIR, filename)
            with open(saxs_path, "wb") as f:
                f.write(decoded)
            return saxs_path
        return None

    @app.callback(
        [
            Output("iq-guinier-plot", "figure"),
            Output("kratky-plot", "figure"),
            Output("pr-plot", "figure"),
            Output("shannon-plot", "figure"),
            Output("guinier-rg-val", "children"),
            Output("pr-rg-val", "children"),
            Output("dmax-val", "children"),
            Output("alert-container", "children"),
        ],
        Input("saxs-file-path-store", "data"),
    )
    def update_saxs_plots(saxs_file_path):
        if not saxs_file_path:
            placeholders = [
                create_placeholder_figure(t)
                for t in ["Log-lin", "Dimensionless Kratky", "IFT", "Shannon Sampled"]
            ]
            return placeholders + ["N/A", "N/A", "N/A", None]

        df = parse_saxs_data(saxs_file_path)
        if df is None:
            alert = dbc.Alert(
                "Error: Could not parse SAXS file.", color="danger", dismissable=True
            )
            return [create_placeholder_figure("I(q) vs q")] * 4 + [
                "N/A",
                "N/A",
                "N/A",
                alert,
            ]

        rg_guinier, i0, fit_data = auto_guinier_fit(df)

        iq_fig = go.Figure(
            data=[
                go.Scatter(
                    x=df["q"],
                    y=df["I"],
                    mode="markers",
                    name="Data",
                    marker=dict(color=COLORS["accent"], size=6),
                )
            ]
        )
        if fit_data is not None:
            iq_fig.add_trace(
                go.Scatter(
                    x=fit_data["q"],
                    y=fit_data["I_fit"],
                    mode="lines",
                    name="Guinier Fit",
                    line=dict(color="red", width=2),
                )
            )
        iq_fig.update_layout(
            title_text="Log-lin",
            title_x=0.5,
            title_font_size=14,
            paper_bgcolor=COLORS["card_background"],
            plot_bgcolor=COLORS["card_background"],
            font_color=COLORS["text"],
            margin=dict(l=40, r=10, t=40, b=40),
            showlegend=False,
            xaxis=dict(
                title="q (Å⁻¹)",
                type="linear",
                showgrid=True,
                gridcolor=COLORS["highlight"],
            ),
            yaxis=dict(
                title="I(q)", type="log", showgrid=True, gridcolor=COLORS["highlight"]
            ),
        )

        pr_df, rg_pr, dmax = calculate_pr(df, rg_guinier)
        kratky_fig = create_kratky_plot(df, rg_guinier, i0)
        pr_fig = create_pr_plot(pr_df, dmax)
        shannon_fig = create_shannon_plot(df, dmax)

        guinier_rg_val = (
            f"{rg_guinier:.2f} Å" if rg_guinier is not None else "Fit Failed"
        )
        pr_rg_val = f"{rg_pr:.2f} Å" if rg_pr is not None else "Calc Failed"
        dmax_val = f"{dmax:.2f} Å" if dmax is not None else "Calc Failed"
        return (
            iq_fig,
            kratky_fig,
            pr_fig,
            shannon_fig,
            guinier_rg_val,
            pr_rg_val,
            dmax_val,
            None,
        )

    @app.callback(
        Output("sequence-file-path-store", "data"),
        Input("upload-sequence-data", "contents"),
        State("upload-sequence-data", "filename"),
        prevent_initial_call=True,
    )
    def store_sequence_data(contents, filename):
        if contents:
            _, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
            seq_path = os.path.join(TEMP_DIR, filename)
            with open(seq_path, "wb") as f:
                f.write(decoded)
            return seq_path
        return None

    @app.callback(
        Output("user-sequence-store", "data"), Input("sequence-file-path-store", "data")
    )
    def update_user_sequence_from_file(sequence_path):
        return parse_sequence_file(sequence_path)

    @app.callback(
        [
            Output("model-file-path-store", "data"),
            Output("upload-pdb-data", "children"),
            Output("starting-molstar-viewer", "data"),
            Output("model-sequence-store", "data"),
            Output("alert-container", "children", allow_duplicate=True),
        ],
        [
            Input("upload-pdb-data", "contents"),
            Input("fetch-pdb-button", "n_clicks"),
            Input("example-model-data-store", "data"),
        ],
        [State("upload-pdb-data", "filename"), State("pdb-id-input", "value")],
        prevent_initial_call=True,
    )
    def update_on_structure_upload(contents, n_clicks, example_data, filename, pdb_id):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        file_content = file_name_for_parser = None
        status_message = "Select a file..."
        alert = None

        if triggered_id == "upload-pdb-data" and contents:
            file_content, file_name_for_parser = contents, filename
        elif triggered_id == "fetch-pdb-button" and pdb_id:
            file_content, file_name_for_parser = fetch_structure_from_db(pdb_id)
        elif triggered_id == "example-model-data-store" and example_data:
            file_content, file_name_for_parser = (
                example_data["contents"],
                example_data["filename"],
            )

        if file_content:
            parsed_content, file_ext, pdb_for_seq = parse_structure_file(
                file_content, file_name_for_parser
            )

            if parsed_content:
                base_name = os.path.splitext(file_name_for_parser)[0]
                model_path = os.path.join(TEMP_DIR, f"{base_name}.pdb")
                with open(model_path, "w") as f:
                    f.write(parsed_content)

                model_data = molstar_helper.parse_molecule(
                    inp=parsed_content, fmt=file_ext
                )
                if model_data:
                    color_hex = int(COLORS["fit_color_initial"].lstrip("#"), 16)
                    model_data["representations"] = [
                        {
                            "type": "cartoon",
                            "color": "uniform",
                            "colorParams": {"value": color_hex},
                        }
                    ]
                    model_seq = extract_sequence_from_pdb(pdb_for_seq)
                    status_message = f"Loaded: {file_name_for_parser}"
                    return model_path, status_message, model_data, model_seq, None

        alert = dbc.Alert(
            f"Error processing model: {file_name_for_parser}",
            color="danger",
            dismissable=True,
        )
        return None, status_message, no_update, no_update, alert

    @app.callback(
        Output("upload-saxs-data", "children"), Input("saxs-file-path-store", "data")
    )
    def update_saxs_upload_status(path):
        return f"Loaded: {os.path.basename(path)}" if path else "Select a file..."

    @app.callback(
        Output("upload-sequence-data", "children"),
        Input("sequence-file-path-store", "data"),
    )
    def update_sequence_upload_status(path):
        return f"Loaded: {os.path.basename(path)}" if path else "Select a file..."

    @app.callback(
        Output("starting-model-alignment", "children"),
        [Input("user-sequence-store", "data"), Input("model-sequence-store", "data")],
    )
    def update_alignment_display(user_seq, model_seq):
        return create_alignment_view(user_seq, model_seq)

    @app.callback(
        Output("saxs-wisdom-text", "children"), Input("quote-interval", "n_intervals")
    )
    def update_quote(n):
        return html.P(random.choice(SAXS_QUOTES), className="fst-italic")

    @app.callback(
        Output("initial-fit-trigger-store", "data"),
        Input("refine-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def trigger_initial_fit(n_clicks):
        return time.time()

    @app.long_callback(
        Output("refinement-results-store", "data"),
        Output("flexible-refinement-trigger-store", "data"),
        Output("alert-container", "children", allow_duplicate=True),
        Output("refinement-status-container", "children"),
        Input("initial-fit-trigger-store", "data"),
        [State("saxs-file-path-store", "data"), State("model-file-path-store", "data")],
        running=[(Output("refine-button", "disabled"), True, False)],
        progress=[Output("refinement-status-container", "children")],
        prevent_initial_call=True,
    )
    def run_initial_fit(set_progress, trigger_time, saxs_path, model_path):
        if not saxs_path or not model_path:
            return (
                no_update,
                no_update,
                None,
                make_status_panel(
                    [("Missing SAXS or Model file.", "fas fa-times-circle", False)]
                ),
            )

        set_progress(
            make_status_panel([("Running initial fit...", "spinner-border", False)])
        )
        log, fit_path, _ = run_pepsi_saxs(saxs_path, model_path, use_opt=False)

        if not fit_path:
            alert = dbc.Alert(
                [
                    html.H5("PEPSI-SAXS Error"),
                    dcc.Textarea(
                        value=log,
                        readOnly=True,
                        style={"width": "100%", "height": "200px"},
                    ),
                ],
                color="danger",
            )
            return (
                no_update,
                no_update,
                alert,
                make_status_panel(
                    [("Initial fit failed.", "fas fa-times-circle", False)]
                ),
            )

        _, chi2 = parse_pepsi_output(fit_path)
        status = make_status_panel(
            [
                ("Initial fit complete.", "fas fa-check-circle", False),
                (f"Initial χ² = {chi2:.2f}", "fas fa-check-circle", False),
            ]
        )

        trigger = {
            "saxs_path": saxs_path,
            "model_path": model_path,
            "chi2_initial": chi2,
            "timestamp": time.time(),
        }
        return {"initial": fit_path}, trigger, None, status

    @app.long_callback(
        Output("refinement-results-store", "data", allow_duplicate=True),
        Output("refined-molstar-viewer", "data"),
        Output("refinement-status-container", "children", allow_duplicate=True),
        Input("flexible-refinement-trigger-store", "data"),
        State("refinement-results-store", "data"),
        running=[(Output("refine-button", "disabled"), True, False)],
        progress=[Output("refinement-status-container", "children")],
        prevent_initial_call=True,
    )
    def run_flexible_refinement(set_progress, trigger_data, current_results):
        if not trigger_data:
            return no_update, no_update, no_update

        chi2_initial = trigger_data["chi2_initial"]
        status_items = [
            ("Initial fit complete.", "fas fa-check-circle", False),
            (f"Initial χ² = {chi2_initial:.2f}", "fas fa-check-circle", False),
        ]

        if chi2_initial > 2.0:
            status_items.append(
                ("High χ², starting flexible refinement...", "spinner-border", False)
            )
            set_progress(make_status_panel(status_items))

            log, fit_path, pdb_path = run_pepsi_saxs(
                trigger_data["saxs_path"], trigger_data["model_path"], use_opt=True
            )
            status_items.pop()

            if fit_path:
                current_results["refined"] = fit_path
                _, chi2_refined = parse_pepsi_output(fit_path)

                model_data = no_update
                if pdb_path and os.path.exists(pdb_path):
                    with open(pdb_path, "r") as f:
                        model_data = molstar_helper.parse_molecule(
                            inp=f.read(), fmt="pdb"
                        )
                    if model_data:
                        color_hex = int(COLORS["fit_color_refined"].lstrip("#"), 16)
                        model_data["representations"] = [
                            {
                                "type": "cartoon",
                                "color": "uniform",
                                "colorParams": {"value": color_hex},
                            }
                        ]

                status_items.append(
                    ("Flexible refinement complete.", "fas fa-check-circle", False)
                )
                if chi2_refined is not None:
                    status_items.append(
                        (
                            f"Refined χ² = {chi2_refined:.2f}",
                            "fas fa-check-circle",
                            False,
                        )
                    )
                    improvement = ((chi2_initial - chi2_refined) / chi2_initial) * 100
                    # FIX: Ensure the icon class is passed correctly
                    status_items.append(
                        (f"Improvement: {improvement:.1f}%", "fas fa-chart-line", False)
                    )

                return current_results, model_data, make_status_panel(status_items)
            else:
                status_items.append(
                    ("Flexible refinement failed.", "fas fa-times-circle", False)
                )
                return current_results, no_update, make_status_panel(status_items)
        else:
            status_items.append(
                ("Initial fit is good (χ² ≤ 2.0).", "fas fa-check-circle", False)
            )
            return no_update, no_update, make_status_panel(status_items)

    @app.callback(
        [
            Output("refinement-iq-plot", "figure"),
            Output("refinement-residuals-plot", "figure"),
        ],
        Input("refinement-results-store", "data"),
        prevent_initial_call=True,
    )
    def update_refinement_plots(results_data):
        if not results_data or "initial" not in results_data:
            return create_placeholder_figure("I(q) fit"), create_placeholder_figure(
                "Residuals"
            )

        df_initial, _ = parse_pepsi_output(results_data["initial"])
        if df_initial is None:
            return create_placeholder_figure("Error"), create_placeholder_figure(
                "Error"
            )

        iq_fig = go.Figure()
        iq_fig.add_trace(
            go.Scatter(
                x=df_initial["q"],
                y=df_initial["I_exp"],
                mode="markers",
                name="Experimental",
                marker=dict(color=COLORS["accent"]),
            )
        )
        iq_fig.add_trace(
            go.Scatter(
                x=df_initial["q"],
                y=df_initial["I_fit"],
                mode="lines",
                name="Initial Fit",
                line=dict(color=COLORS["fit_color_initial"]),
            )
        )

        residuals_initial = (df_initial["I_exp"] - df_initial["I_fit"]) / df_initial[
            "I_err"
        ]
        res_fig = go.Figure()
        res_fig.add_trace(
            go.Scatter(
                x=df_initial["q"],
                y=residuals_initial,
                mode="markers",
                name="Initial Residuals",
                marker=dict(color=COLORS["fit_color_initial"], size=4),
            )
        )
        res_fig.add_hline(y=0, line_dash="dash", line_color="grey")

        if "refined" in results_data:
            df_refined, _ = parse_pepsi_output(results_data["refined"])
            if df_refined is not None:
                iq_fig.add_trace(
                    go.Scatter(
                        x=df_refined["q"],
                        y=df_refined["I_fit"],
                        mode="lines",
                        name="Refined Fit",
                        line=dict(color=COLORS["fit_color_refined"]),
                    )
                )
                residuals_refined = (
                    df_refined["I_exp"] - df_refined["I_fit"]
                ) / df_refined["I_err"]
                res_fig.add_trace(
                    go.Scatter(
                        x=df_refined["q"],
                        y=residuals_refined,
                        mode="markers",
                        name="Refined Residuals",
                        marker=dict(color=COLORS["fit_color_refined"], size=4),
                    )
                )

        # FIX: Restore the logarithmic y-axis and other layout properties
        iq_fig.update_layout(
            title_text="I(q) Fit",
            title_x=0.5,
            title_font_size=14,
            paper_bgcolor=COLORS["card_background"],
            plot_bgcolor=COLORS["card_background"],
            font_color=COLORS["text"],
            margin=dict(l=40, r=10, t=40, b=40),
            xaxis=dict(
                showline=True, showticklabels=True, gridcolor=COLORS["highlight"]
            ),
            yaxis=dict(
                title="I(q)",
                type="log",
                showticklabels=False,
                gridcolor=COLORS["highlight"],
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(0,0,0,0.5)",
            ),
        )

        res_fig.update_layout(
            title_text="",
            paper_bgcolor=COLORS["card_background"],
            plot_bgcolor=COLORS["card_background"],
            font_color=COLORS["text"],
            margin=dict(l=40, r=10, t=40, b=40),
            xaxis=dict(
                title="q (Å⁻¹)",
                type="linear",
                showgrid=True,
                gridcolor=COLORS["highlight"],
            ),
            yaxis=dict(
                title="(Iexp - Ifit) / σ", showgrid=True, gridcolor=COLORS["highlight"]
            ),
            showlegend=False,
        )

        return iq_fig, res_fig
