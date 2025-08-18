import os
import shutil
import atexit
import base64
import io
import re
import subprocess
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import plotly.graph_objects as go
from Bio.PDB import MMCIFParser, PDBIO
from difflib import SequenceMatcher
from scipy.stats import linregress
from scipy.optimize import lsq_linear
from dash import html

# ==============================================================================
# Constants & Global Setup
# ==============================================================================

# Get the directory where the script is running
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Create a temporary directory within the script's directory
TEMP_DIR = Path(os.environ.get("SAXSMART_TEMP", Path.home() / ".cache" / "saxsmart"))
TEMP_DIR.mkdir(parents=True, exist_ok=True)

COLORS = {
    "background": "#0A111F",
    "card_background": "#0F192E",
    "highlight": "#14213D",
    "text": "#E5E5E5",
    "accent": "#FCA311",
    "fit_color_initial": "#E83F6F",
    "fit_color_refined": "#09814A",
}

SAXS_QUOTES = [
    "A good Guinier fit is the beginning of a good story, not the end.",
    "In SAXS, every particle tells a tale in reciprocal space.",
    "Your P(r) function is the particle's autobiography.",
    "Beware the siren song of a perfect chi-squared; inspect the residuals.",
    "The Kratky plot: a window into the flexibility of your molecule.",
    "Dmax is not a wish, it's a measurement.",
    "Radiation damage: the silent saboteur of SAXS experiments.",
    "Remember to subtract the buffer, for it too scatters.",
    "Aggregation is the enemy of a clean scattering curve.",
    "Low-q data is precious; guard it with your life (and a good beamstop).",
    "A monodisperse sample is a happy sample.",
    "The Porod invariant speaks volumes about your volume.",
    "From I(q) to P(r), the Fourier transform is your trusted guide.",
    "Don't mistake inter-particle interference for internal structure.",
    "Shannon's theorem tells you how many stories your data can tell.",
    "Every bump and wiggle in your curve has a structural meaning.",
    "The difference between a globule and a coil is plain to see in the Kratky.",
    "Always check the log-log plot for signs of aggregation or repulsion.",
    "Your model is only as good as the data you fit it to.",
    "SAXS provides low-resolution shape, but high-resolution insight.",
    "Always listen to Petra!",
]

# ==============================================================================
# Helper & Backend Data Processing Functions
# ==============================================================================


def cleanup_temp_dir():
    """Best-effort cleanup of our temp directory only."""
    try:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    except Exception:
        pass


atexit.register(cleanup_temp_dir)


def create_placeholder_figure(title="Upload Data to Begin"):
    """Generates a blank Plotly figure with a title."""
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor=COLORS["card_background"],
        plot_bgcolor=COLORS["card_background"],
        font_color=COLORS["text"],
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        annotations=[
            dict(
                text=title,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=16),
            )
        ],
    )
    return fig


def parse_saxs_data(saxs_file_path):
    """Parses SAXS data (q, I, err) from a file path."""
    if saxs_file_path is None or not os.path.exists(saxs_file_path):
        return None
    try:
        df = pd.read_csv(
            saxs_file_path,
            comment="#",
            header=None,
            delim_whitespace=True,
            names=["q", "I", "err"],
        )
        df.dropna(subset=["q", "I"], inplace=True)
        df = df[df["q"] > 0].copy()
        return df
    except Exception:
        print("--- ERROR IN: parse_saxs_data ---")
        print(traceback.format_exc())
        return None


def parse_structure_file(contents, filename):
    """Parses a .pdb or .cif file. If CIF, converts to PDB format."""
    try:
        if contents is None:
            return None, None, None

        is_cif = ".cif" in filename.lower()
        is_pdb = ".pdb" in filename.lower()

        if not is_cif and not is_pdb:
            return None, None, None

        if "base64," in contents:
            _, content_string = contents.split(",")
            decoded = base64.b64decode(content_string).decode("utf-8")
        else:
            decoded = contents

        if is_cif:
            parser = MMCIFParser(QUIET=True)
            structure = parser.get_structure("model", io.StringIO(decoded))
            io_pdb = PDBIO()
            io_pdb.set_structure(structure)
            pdb_string_io = io.StringIO()
            io_pdb.save(pdb_string_io)
            pdb_formatted_content = pdb_string_io.getvalue()
            return pdb_formatted_content, "pdb", pdb_formatted_content
        else:
            return decoded, "pdb", decoded

    except Exception:
        print("--- ERROR IN: parse_structure_file ---")
        print(traceback.format_exc())
        return None, None, None


def fetch_structure_from_db(model_id):
    """Fetches a structure from RCSB PDB or AlphaFold DB."""
    try:
        if not model_id:
            return None, None
        model_id = model_id.strip().upper()
        if len(model_id) == 4 and model_id.isalnum():
            url = f"https://files.rcsb.org/download/{model_id}.pdb"
            filename = f"{model_id}.pdb"
        else:
            url = f"https://alphafold.ebi.ac.uk/files/AF-{model_id}-F1-model_v4.cif"
            filename = f"AF-{model_id}.cif"

        response = requests.get(url)
        response.raise_for_status()
        return response.text, filename
    except Exception:
        print("--- ERROR IN: fetch_structure_from_db ---")
        print(traceback.format_exc())
        return None, None


def parse_sequence_file(sequence_path):
    """Reads a protein sequence from a file path."""
    if not sequence_path or not os.path.exists(sequence_path):
        return None
    try:
        with open(sequence_path, "r") as f:
            lines = [line.strip() for line in f if not line.startswith(">")]
        seq = "".join(lines).upper()
        return seq if seq.isalpha() else None
    except Exception:
        print("--- ERROR IN: parse_sequence_file ---")
        print(traceback.format_exc())
        return None


def extract_sequence_from_pdb(pdb_content):
    """Extracts the amino acid sequence from a PDB file string."""
    try:
        three_to_one = {
            "ALA": "A",
            "ARG": "R",
            "ASN": "N",
            "ASP": "D",
            "CYS": "C",
            "GLU": "E",
            "GLN": "Q",
            "GLY": "G",
            "HIS": "H",
            "ILE": "I",
            "LEU": "L",
            "LYS": "K",
            "MET": "M",
            "PHE": "F",
            "PRO": "P",
            "SER": "S",
            "THR": "T",
            "TRP": "W",
            "TYR": "Y",
            "VAL": "V",
        }
        pdb_seq = []
        seen = set()
        for line in pdb_content.splitlines():
            if line.startswith("ATOM") and line[13:15].strip() == "CA":
                resname = line[17:20].strip()
                resnum = int(line[22:26])
                chain = line[21].strip()
                key = (resnum, chain)
                if key not in seen:
                    seen.add(key)
                    pdb_seq.append(three_to_one.get(resname, "X"))

        sequence = "".join(pdb_seq)
        return sequence if sequence else None
    except Exception:
        print("--- ERROR IN: extract_sequence_from_pdb ---")
        print(traceback.format_exc())
        return None


def create_alignment_view(user_seq, model_seq):
    """Creates a minimalist HTML component to display sequence alignment."""
    if not user_seq or not model_seq:
        return html.P(
            "Upload sequence and model to see alignment.", className="small text-muted"
        )

    matcher = SequenceMatcher(None, user_seq, model_seq)

    user_spans = [html.Span("User:  ", style={"fontWeight": "bold"})]
    model_spans = [html.Span("Model: ", style={"fontWeight": "bold"})]

    matches = mismatches = gaps = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        user_chunk = user_seq[i1:i2]
        model_chunk = model_seq[j1:j2]

        if tag == "equal":
            user_spans.append(html.Span(user_chunk))
            model_spans.append(html.Span(model_chunk))
            matches += len(user_chunk)
        elif tag == "replace":
            user_spans.append(html.Span(user_chunk, className="mismatch"))
            model_spans.append(html.Span(model_chunk, className="mismatch"))
            mismatches += len(user_chunk)
        elif tag == "delete":
            user_spans.append(html.Span(user_chunk, className="mismatch"))
            model_spans.append(html.Span("-" * len(user_chunk), className="mismatch"))
            gaps += len(user_chunk)
        elif tag == "insert":
            user_spans.append(html.Span("-" * len(model_chunk), className="mismatch"))
            model_spans.append(html.Span(model_chunk, className="mismatch"))
            gaps += len(model_chunk)

    total_len = max(len(user_seq), len(model_seq))
    identity = (matches / total_len) * 100 if total_len > 0 else 0

    summary_text = f"Identity: {identity:.1f}% ({mismatches} mismatch, {gaps} gaps)"

    summary_div = html.Div(
        html.P(
            summary_text,
            style={"fontSize": "0.8rem", "fontWeight": "bold", "color": COLORS["text"]},
        ),
        style={
            "marginBottom": "0.5rem",
            "paddingBottom": "0.5rem",
            "borderBottom": "1px solid #444",
        },
    )

    sequence_div = html.Div(
        [
            html.P(
                user_spans, className="sequence-text", style={"color": COLORS["text"]}
            ),
            html.P(
                model_spans, className="sequence-text", style={"color": COLORS["text"]}
            ),
        ],
        style={"overflow": "auto", "maxHeight": "100px"},
    )

    return html.Div([summary_div, sequence_div])


def auto_guinier_fit(df, min_points=5):
    """Performs an automatic Guinier fit."""
    if df is None or len(df) < min_points:
        return None, None, None
    df_sorted = df.sort_values(by="q").copy()
    df_sorted["lnI"] = np.log(df_sorted["I"])
    df_sorted["q2"] = df_sorted["q"] ** 2
    best_i = 0
    for i in range(min_points, len(df_sorted)):
        q2_subset = df_sorted["q2"].iloc[:i]
        lnI_subset = df_sorted["lnI"].iloc[:i]
        if len(np.unique(q2_subset)) < 2:
            continue
        slope, intercept, _, _, _ = linregress(q2_subset, lnI_subset)
        if slope >= 0:
            break
        Rg_est = np.sqrt(-3 * slope)
        q_max = df_sorted["q"].iloc[i - 1]
        if q_max * Rg_est > 1.3:
            break
        best_i = i
    if best_i < min_points:
        return None, None, None
    q2_final = df_sorted["q2"].iloc[:best_i]
    lnI_final = df_sorted["lnI"].iloc[:best_i]
    slope, intercept, _, _, _ = linregress(q2_final, lnI_final)
    Rg = np.sqrt(-3 * slope)
    I0 = np.exp(intercept)
    fit_q = df_sorted["q"].iloc[:best_i]
    fit_I = np.exp(intercept + slope * (fit_q**2))
    fit_data = pd.DataFrame({"q": fit_q, "I_fit": fit_I})
    return Rg, I0, fit_data


def calculate_pr(df, rg_guinier, n_points=100, regularization=1e-2):
    """Estimates the P(r) distribution."""
    dmax_guess = rg_guinier * 6 if rg_guinier is not None else 150.0
    q = df["q"].values
    I = df["I"].values
    r = np.linspace(0, dmax_guess, n_points)
    K = np.zeros((len(q), len(r)))
    for i in range(len(q)):
        qr = q[i] * r
        with np.errstate(divide="ignore", invalid="ignore"):
            K[i, :] = np.where(qr != 0, np.sin(qr) / qr, 1.0)
    reg_matrix = regularization * np.identity(n_points)
    A = np.vstack([K, reg_matrix])
    b = np.concatenate([I, np.zeros(n_points)])
    result = lsq_linear(A, b, bounds=(0, np.inf))
    pr = result.x
    try:
        norm = np.trapz(pr, r)
        if norm == 0:
            return None, None, None
        rg2 = np.trapz(pr * r**2, r) / norm
        rg_pr = np.sqrt(rg2)
        positive_pr_indices = np.where(pr > 0.01 * pr.max())[0]
        dmax_idx = positive_pr_indices[-1] if len(positive_pr_indices) > 0 else -1
        dmax = r[dmax_idx] if dmax_idx != -1 else dmax_guess
    except Exception as e:
        print(f"Error calculating Rg/Dmax from P(r): {e}")
        return None, None, None
    pr_df = pd.DataFrame({"r": r, "P(r)": pr})
    pr_df["P(r)"] /= pr_df["P(r)"].max()
    return pr_df, rg_pr, dmax


# FIX: Added the missing plot functions
def create_kratky_plot(df, rg, i0):
    """Generates a Dimensionless Kratky plot."""
    if rg is None or i0 is None:
        return create_placeholder_figure("Dimensionless Kratky")
    fig = go.Figure()
    x = df["q"] * rg
    y = (df["q"] * rg) ** 2 * (df["I"] / i0)
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", marker_color=COLORS["accent"]))
    fig.add_hline(y=1.1, line_dash="dash", line_color="grey")
    fig.add_vline(x=np.sqrt(3), line_dash="dash", line_color="grey")
    fig.update_layout(
        title_text="Dimensionless Kratky",
        title_x=0.5,
        title_font_size=14,
        paper_bgcolor=COLORS["card_background"],
        plot_bgcolor=COLORS["card_background"],
        font_color=COLORS["text"],
        margin=dict(l=40, r=10, t=40, b=40),
        xaxis=dict(
            title="q·Rg", showgrid=True, gridcolor=COLORS["highlight"], range=[0, 6]
        ),
        yaxis=dict(
            title="(q·Rg)²·I(q)/I(0)",
            showgrid=True,
            gridcolor=COLORS["highlight"],
            range=[0, 3],
        ),
    )
    return fig


def create_pr_plot(pr_df, dmax):
    """Generates the P(r) vs r plot."""
    if pr_df is None:
        return create_placeholder_figure("IFT")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=pr_df["r"], y=pr_df["P(r)"], mode="lines", marker_color=COLORS["accent"]
        )
    )

    x_range = [0, dmax * 1.05] if dmax is not None else None

    fig.update_layout(
        title_text="IFT",
        title_x=0.5,
        title_font_size=14,
        paper_bgcolor=COLORS["card_background"],
        plot_bgcolor=COLORS["card_background"],
        font_color=COLORS["text"],
        margin=dict(l=40, r=10, t=40, b=40),
        xaxis=dict(
            title="r (Å)", showgrid=True, gridcolor=COLORS["highlight"], range=x_range
        ),
        yaxis=dict(title="P(r)", showgrid=True, gridcolor=COLORS["highlight"]),
    )
    return fig


def create_shannon_plot(df, dmax):
    """Generates the Shannon sampled plot."""
    if dmax is None:
        return create_placeholder_figure("Shannon Sampled")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["q"],
            y=df["I"],
            mode="lines",
            name="Data",
            line=dict(color=COLORS["accent"], width=1),
        )
    )
    n_shannon = int(np.floor(df["q"].max() * dmax / np.pi))
    shannon_q = np.array([n * np.pi / dmax for n in range(1, n_shannon + 1)])
    shannon_i = np.interp(shannon_q, df["q"], df["I"])
    fig.add_trace(
        go.Scatter(
            x=shannon_q,
            y=shannon_i,
            mode="markers",
            name="Shannon Points",
            marker=dict(color="red", size=10, symbol="x"),
        )
    )
    fig.update_layout(
        title_text=f"{n_shannon} Shannon Channels",
        title_x=0.5,
        title_font_size=14,
        paper_bgcolor=COLORS["card_background"],
        plot_bgcolor=COLORS["card_background"],
        font_color=COLORS["text"],
        margin=dict(l=40, r=10, t=40, b=40),
        showlegend=False,
        xaxis=dict(
            title="q (Å⁻¹)", type="linear", showgrid=True, gridcolor=COLORS["highlight"]
        ),
        yaxis=dict(
            title="I(q)", type="log", showgrid=True, gridcolor=COLORS["highlight"]
        ),
    )
    return fig


def run_pepsi_saxs(saxs_path, model_path, use_opt=False):
    """Runs the PEPSI-SAXS executable."""
    if not saxs_path or not model_path:
        return "Error: SAXS data or model file not provided.", None, None

    pepsi_executable = os.path.join(
        SCRIPT_DIR, "pepsi-SAXS-linux64"
    )  # TODO: Change to not hardcoded path
    if not os.path.exists(pepsi_executable):
        return (
            f"Error: PEPSI-SAXS executable not found at {pepsi_executable}",
            None,
            None,
        )

    model_base_name = os.path.splitext(os.path.basename(model_path))[0]
    output_suffix = "_opt" if use_opt else "_initial"

    output_fit_name = f"{model_base_name}{output_suffix}.fit"
    output_fit_path = os.path.join(TEMP_DIR, output_fit_name)

    refined_pdb_name = f"{output_fit_name}.pdb"
    refined_pdb_path = os.path.join(TEMP_DIR, refined_pdb_name)

    command = [pepsi_executable, model_path, saxs_path, "-o", output_fit_path]
    if use_opt:
        command.append("--opt")

    try:
        process = subprocess.run(
            command, cwd=TEMP_DIR, capture_output=True, text=True, check=True
        )
        log_output = process.stdout + process.stderr

        final_pdb_path = (
            refined_pdb_path if use_opt and os.path.exists(refined_pdb_path) else None
        )

        if os.path.exists(output_fit_path):
            return log_output, output_fit_path, final_pdb_path
        else:
            return log_output, None, None

    except subprocess.CalledProcessError as e:
        log_output = f"PEPSI-SAXS failed with exit code {e.returncode}.\n"
        log_output += "--- STDOUT ---\n" + e.stdout + "\n"
        log_output += "--- STDERR ---\n" + e.stderr
        return log_output, None, None
    except Exception as e:
        return (
            f"An unexpected error occurred: {e}\n{traceback.format_exc()}",
            None,
            None,
        )


def parse_pepsi_output(fit_file_path):
    """Parses the .fit file from PEPSI-SAXS."""
    try:
        chi2 = None
        with open(fit_file_path, "r") as f:
            for line in f:
                if line.startswith("#"):
                    match = re.search(r"Chi2:\s*([0-9.]+)", line)
                    if match:
                        chi2 = float(match.group(1))
                        break
                else:
                    break

        df = pd.read_csv(
            fit_file_path,
            delim_whitespace=True,
            comment="#",
            names=["q", "I_exp", "I_err", "I_fit"],
        )

        if chi2 is None and not df.empty:
            residuals = (df["I_exp"] - df["I_fit"]) / df["I_err"]
            chi2 = np.sum(residuals**2) / len(df)

        return df, chi2
    except Exception as e:
        print(f"Error parsing PEPSI-SAXS output file: {e}")
        return None, None
