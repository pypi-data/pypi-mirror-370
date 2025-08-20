import io
import base64
import pandas as pd
import plotly.express as px

import matplotlib
matplotlib.use("Agg")  # Use a backend for image-only (no GUI)
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="FigureCanvasAgg is non-interactive"
)

# ── Matplotlib Integration (static PNGs) ────────────────────────────────

def figure(*args, **kwargs):
    """Return a fresh Matplotlib Figure so callers don’t have to import plt."""
    return plt.figure(*args, **kwargs)


def pyplot(fig, dpi: int = 200) -> str:
    """Render *fig* to a base‑64 PNG <img> tag that SyntaxMatrix can embed."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=dpi)
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode("utf-8")
    return f'<img src="data:image/png;base64,{img_data}" style="max-width:100%;">'

# ── Plotly Integration (interactive) ───────────────────────────────────

def plotly():
    """Shorthand to import *plotly.express* lazily."""
    return px

def render_plotly(fig):
    """Return Plotly figure HTML stripped of the outer <html> shell."""
    return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"displaylogo": False})


# ── Data‑table helpers (for pandas DataFrames) ─────────────────────────

def _table_css() -> str:
    """Shared CSS for compact, scrollable tables."""
    return (
        "<style>"
        ".smx-table{border-collapse:collapse;width:max-content;font-size:0.9em;}"
        ".smx-table th{background:#f0f2f5;text-align:left;padding:6px 8px;white-space:nowrap;}"
        ".smx-table td{border:1px solid #ddd;padding:6px 8px;white-space:nowrap;}"
        "</style>"
    )


def datatable_design() -> str:
    """Return the <style> block so callers can inject it once per session."""
    return _table_css()


def datatable_box(df: "pd.DataFrame", max_h: int = 260) -> str:
    """Wrap *df* in a scrollable div with the SMX table styling."""
    html = df.to_html(index=False, classes="smx-table", border=0)
    return (
        _table_css()
        + f"<div style='max-height:{max_h}px; overflow:auto; border:1px solid #ccc; "
        "border-radius:4px; margin-bottom:12px;'>"
        + html
        + "</div>"
    )


# Back‑compat shim so older code that called tableframe() still works.

def tableframe(df: "pd.DataFrame", max_h: int = 260) -> str:  # noqa: N802
    """Alias to *datatable_box* (kept for backward compatibility)."""
    return datatable_box(df, max_h)


def render_ai_cell_output(local_env, stdout_text=None):
    """
    Renders plots, tables, or variable values, but only shows plots if they are NOT blank.
    """

    # 1. Matplotlib (but only if the figure isn't blank)
    try:
        figs = [plt.figure(n) for n in plt.get_fignums()]
        valid_fig = None
        for fig in figs:
            axes = fig.get_axes()
            if axes:
                for ax in axes:
                    if (
                        getattr(ax, "lines", None) and len(ax.lines) > 0 or
                        getattr(ax, "patches", None) and len(ax.patches) > 1 or
                        getattr(ax, "collections", None) and len(ax.collections) > 0 or
                        getattr(ax, "images", None) and len(ax.images) > 0
                    ):
                        valid_fig = fig
                        break
                if valid_fig:
                    break
        if valid_fig:
            buf = io.BytesIO()
            valid_fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            html = f'<img src="data:image/png;base64,{img_base64}" style="max-width:100%;">'
            plt.close("all")
            return html
        else:
            plt.close("all")
    except Exception:
        pass

    # 2. Plotly support (same as before)
    try:
        for v in local_env.values():
            if hasattr(v, "to_plotly_json"):
                html = v.to_html(full_html=False, include_plotlyjs="cdn", config={"displaylogo": False})
                return html
    except Exception:
        pass

    # 3. DataFrames except raw df
    for k, v in local_env.items():
        if k == "df":
            continue
        
        if hasattr(v, "to_html"):
            return datatable_box(v, max_h=320)   # vertical & horizontal scroll

    # 4. Series as table, value as text
    candidates = [
        (k, v) for k, v in local_env.items()
        if k != "df"
           and not k.startswith("__")
           and not hasattr(v, "to_html")
           and not hasattr(v, "to_plotly_json")
           and not callable(v)
           and not isinstance(v, type)
    ]
    if candidates:
        var_name, var_val = candidates[-1]
        if isinstance(var_val, pd.Series):
            rows = "".join(
                f"<tr><td style='font-weight:bold;padding-right:12px;'>{k}</td><td>{v}</td></tr>"
                for k, v in var_val.items()
            )
            html = f"""
            <table class='smx-table' style='width:auto;min-width:320px;'>
              <caption style='caption-side:top;font-weight:bold;font-size:1.1em;padding-bottom:8px;'>{var_name}</caption>
              <tbody>{rows}</tbody>
            </table>
            """
        else:
            html = f"<div style='font-size:1.1em;'><strong>{var_name}</strong>: <code>{repr(var_val)}</code></div>"
        return html

    # --- 5. Print/stdout fallback ---
    if stdout_text:
        return f"<pre>{stdout_text.strip()}</pre>"
    return "<em>No output produced.</em>"


    

