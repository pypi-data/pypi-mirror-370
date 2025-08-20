# syntaxmatrix/display.py
# import pandas as pd
# from IPython.display import HTML, display  
# from syntaxmatrix.plottings import datatable_box          

# def show(obj, *, name=None):
#     """
#     Smart display for the SyntaxMatrix auto-code kernel.
#     * Scalars / simple tuples → pretty print
#     * pandas Series / DataFrame → display()
#     * matplotlib / seaborn figs → already auto-render
#     * dicts → key-value table
#     * sklearn estimators with .score_ / feature_importances_ → summary
#     """
#     try:
#         import matplotlib.pyplot as plt
#     except Exception:
#         plt = None

#     if isinstance(obj, (float, int)) and (0 <= obj <= 1):
#         print(f"accuracy = {obj:.3f}")
#         return

     # 1️⃣ pandas objects
    #  if isinstance(obj, (pd.Series, pd.DataFrame)):

    #     html = obj.to_html(classes="smx-table", border=0)
    #     wrapped_html = (
    #         "<style>"
    #         ".smx-table{border-collapse:collapse;font-size:0.9em;white-space:nowrap;}"
    #         ".smx-table th{background:#f0f2f5;text-align:left;padding:6px 8px;border:1px solid gray;}"
    #         ".smx-table td{border:1px solid #ddd;padding:6px 8px;}"
    #         ".smx-table tbody tr:nth-child(even){background-color:#f9f9f9;}"
    #         "</style>"
    #         "<div style='overflow-x:auto; max-width:100%; margin-bottom:1rem;'>"
    #         + html +
    #         "</div>"
    #     )
    #     display(HTML(wrapped_html))
    #     return

#     # matplotlib figs (let Jupyter handle them)
#     if plt and isinstance(obj, plt.Figure):
#         return

#     # tuples of stats results (length 2 or 4 are common)
#     if isinstance(obj, tuple):
#         if len(obj) == 2 and all(isinstance(v, (int, float)) for v in obj):
#             mse, r2 = obj
#             if len(obj) == 2: 
#                 stat, p = obj
#                 print(f"statistic = {stat:.4g}   p-value = {p:.4g}")
#                 print("Result: " + ("significant ✅" if p < 0.05 else "not significant ❌"))
#                 return
#             if len(obj) == 4:         # e.g. χ²
#                 chi2, p, dof, _ = obj
#                 print(f"chi² = {chi2:.3g}   dof = {dof}   p-value = {p:.4g}")
#                 print("Result: " + ("significant ✅" if p < 0.05 else "not significant ❌"))
#                 return
#         # Treat as regression metrics if r2 is ≤ 1 and mse ≥ 0
#         if 0 <= r2 <= 1 and mse >= 0:
#             df_ = pd.DataFrame(
#                 {"metric": ["Mean-squared error", "R²"],
#                 "value":  [mse, r2]}
#             )
#             display(HTML(datatable_box(df_)))
#             return

#     # dict → nice key:value printout
#     if isinstance(obj, dict):
#         for k, v in obj.items():
#             print(f"{k:<25} {v}")
#         return

#     # fallback
#     print(obj)

  
# -----------------------------------------------------------------
#  Paste *inside* syntaxmatrix/display.py – only the show() body
# -----------------------------------------------------------------
def show(obj):
    """
    Render common objects so the Dashboard (or chat) always shows output.
    """
    import io, base64, numbers
    from IPython.display import display, HTML
    import pandas as pd
    import matplotlib.figure as mpfig

    # ── matplotlib Figure ─────────────────────────────────────────
    if isinstance(obj, mpfig.Figure):
        display(obj)                  
        return obj
    
    if isinstance(obj, (pd.Series, pd.DataFrame)):

        html = obj.to_html(classes="smx-table", border=0)
        wrapped_html = (
            "<style>"
            ".smx-table{border-collapse:collapse;font-size:0.9em;white-space:nowrap;}"
            ".smx-table th{background:#f0f2f5;text-align:left;padding:6px 8px;border:1px solid gray;}"
            ".smx-table td{border:1px solid #ddd;padding:6px 8px;}"
            ".smx-table tbody tr:nth-child(even){background-color:#f9f9f9;}"
            "</style>"
            "<div style='overflow-x:auto; max-width:100%; margin-bottom:1rem;'>"
            + html +
            "</div>"
        )
        display(HTML(wrapped_html))
        return HTML(wrapped_html)

    # ── dict of scalars → pretty 2-col table ─────────────────────
    if isinstance(obj, dict) and all(isinstance(v, numbers.Number) for v in obj.values()):
        df_ = pd.DataFrame({"metric": list(obj.keys()),
                            "value":  list(obj.values())})
        display(df_)
        return df_

    # ── 2-tuple of numbers (mse, r²) ─────────────────────────────
    if (isinstance(obj, tuple) and len(obj) == 2 and
            all(isinstance(v, numbers.Number) for v in obj)):
        mse, r2 = obj
        df_ = pd.DataFrame({"metric": ["Mean-squared error", "R²"],
                            "value":  [mse, r2]})
        display(df_)
        return df_

    # ── fallback ─────────────────────────────────────────────────
    display(HTML(f"<pre>{obj}</pre>"))

    return obj
