import openai
from openai import OpenAI
import re, os, textwrap
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from .model_templates import classification 
import syntaxmatrix as smx


warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

def strip_describe_slice(code: str) -> str:
    """
    Remove any pattern like  df.groupby(...).describe()[[ ... ]]  because
    slicing a SeriesGroupBy.describe() causes AttributeError.
    We leave the plain .describe() in place (harmless) and let our own
    table patcher add the correct .agg() table afterwards.
    """
    pat = re.compile(
        r"(df\.groupby\([^)]+\)\[[^\]]+\]\.describe\()\s*\[[^\]]+\]\)",
        flags=re.DOTALL,
    )
    return pat.sub(r"\1)", code)

def remove_plt_show(code: str) -> str:
    """Removes all plt.show() calls from the generated code string."""
    return "\n".join(line for line in code.splitlines() if "plt.show()" not in line)

def patch_plot_with_table(code: str) -> str:
    """
    ▸ strips every `plt.show()` (avoids warnings)
    ▸ converts the *last* Matplotlib / Seaborn figure to PNG-HTML so it is
      rendered in the dashboard
    ▸ appends a summary-stats table **after** the plot
    """
    # 0. drop plt.show()
    lines = [ln for ln in code.splitlines() if "plt.show()" not in ln]

    # 1. locate the last plotting line
    plot_kw = ['plt.', 'sns.', '.plot(', '.boxplot(', '.hist(']
    last_plot = max((i for i,l in enumerate(lines) if any(k in l for k in plot_kw)), default=-1)
    if last_plot == -1:
        return "\n".join(lines)          # nothing to do

    whole = "\n".join(lines)

    # 2. detect group / feature (if any)
    group, feature = None, None
    xm = re.search(r"x\s*=\s*['\"](\w+)['\"]", whole)
    ym = re.search(r"y\s*=\s*['\"](\w+)['\"]", whole)
    if xm and ym:
        group, feature = xm.group(1), ym.group(1)
    else:
        cm = re.search(r"column\s*=\s*['\"](\w+)['\"].*by\s*=\s*['\"](\w+)['\"]", whole)
        if cm:
            feature, group = cm.group(1), cm.group(2)

    # 3. code that captures current fig → PNG → HTML
    img_block = textwrap.dedent("""
        import io, base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        from IPython.display import display, HTML
        display(HTML(f'<img src="data:image/png;base64,{img_b64}" style="max-width:100%;">'))          
        plt.close()
    """)

    # 4. build summary-table code
    if group and feature:
        tbl_block = (
            f"summary_table = (\n"
            f"    df.groupby('{group}')['{feature}']\n"
            f"      .agg(['count','mean','std','min','median','max'])\n"
            f"      .rename(columns={{'median':'50%'}})\n"
            f")\n"
        )
    elif ym:
        feature = ym.group(1)
        tbl_block = (
            f"summary_table = (\n"
            f"    df['{feature}']\n"
            f"      .agg(['count','mean','std','min','median','max'])\n"
            f"      .rename(columns={{'median':'50%'}})\n"
            f")\n"
        )
    
    # 3️⃣ grid-search results
    elif "GridSearchCV(" in code:
        tbl_block = textwrap.dedent("""
            # build tidy CV-results table
            cv_df = (
                pd.DataFrame(grid_search.cv_results_)
                .loc[:, ['param_n_estimators', 'param_max_depth',
                        'mean_test_score', 'std_test_score']]
                .rename(columns={
                    'param_n_estimators': 'n_estimators',
                    'param_max_depth':    'max_depth',
                    'mean_test_score':    'mean_cv_accuracy',
                    'std_test_score':     'std'
                })
                .sort_values('mean_cv_accuracy', ascending=False)
                .reset_index(drop=True)
            )
            summary_table = cv_df
        """).strip() + "\n"
    else:
        tbl_block = (
            "summary_table = (\n"
            "    df.describe().T[['count','mean','std','min','50%','max']]\n"
            ")\n"
        )

    tbl_block += "from syntaxmatrix.display import show\nshow(summary_table)"

    # 5. inject image-export block, then table block, after the plot
    patched = (
            lines[:last_plot+1]
            + img_block.splitlines()
            + tbl_block.splitlines()
            + lines[last_plot+1:]
    )
    patched_code = "\n".join(patched)
    # ⬇️ strip every accidental left-indent so top-level lines are flush‐left
    return textwrap.dedent(patched_code)


def refine_eda_question(raw_question, df=None, max_points=1000):
    """
    Rewrites user's EDA question to avoid classic mistakes:
    - For line plots and scatter: recommend aggregation or sampling if large.
    - For histograms/bar: clarify which variable to plot and bin count.
    - For correlation: suggest a heatmap.
    - For counts: direct request for df.shape[0].
    df (optional): pass DataFrame for column inspection.
    """

    # --- SPECIFIC PEARSON CORRELATION DETECTION ----------------------
    pc = re.match(
        r".*\bpearson\b.*\bcorrelation\b.*between\s+(\w+)\s+(and|vs)\s+(\w+)",
        raw_question, re.I
    )
    if pc:
        col1, col2 = pc.group(1), pc.group(3)
        # Return an instruction that preserves the exact intent
        return (
            f"Compute the Pearson correlation coefficient (r) and p-value "
            f"between {col1} and {col2}. "
            f"Print a short interpretation."
        )
    # -----------------------------------------------------------------
    # ── Detect "predict <column>" intent ──────────────────────────────    
    c = re.search(r"\bpredict\s+([A-Za-z0-9_]+)", raw_question, re.I)
    if c:
        target = c.group(1)
        raw_question += (
            f" IMPORTANT: do NOT recreate or overwrite the existing target column "
            f"“{target}”.  Use it as-is for y = df['{target}']."
        )

    q = raw_question.strip()
    # REMOVE explicit summary-table instructions 
    # ── strip any “table” request:  “…table of …”,  “…include table…”,  “…with a table…”
    q = re.sub(r"\b(include|with|and)\b[^.]*\btable[s]?\b[^.]*", "", q, flags=re.I).strip()
    q = re.sub(r"\s*,\s*$", "", q)          # drop trailing comma, if any

    ql = q.lower()

     # ── NEW: if the text contains an exact column name, leave it alone ──
    if df is not None:
        for col in df.columns:
            if col.lower() in ql:
                return q   

    modelling_keywords = (
        "random forest", "gradient-boost", "tree-based model",
        "feature importance", "feature importances",
        "overall accuracy", "train a model", "predict "
    )
    if any(k in ql for k in modelling_keywords):
        return q         

    # 1. Line plots: average if plotting raw numeric vs numeric
    if "line plot" in ql and any(word in ql for word in ["over", "by", "vs"]):
        match = re.search(r'line plot of ([\w_]+) (over|by|vs) ([\w_]+)', ql)
        if match:
            y, _, x = match.groups()
            return f"Show me the average {y} by {x} as a line plot."

    # 2. Scatter plots: sample if too large
    if "scatter" in ql or "scatter plot" in ql:
        if df is not None and df.shape[0] > max_points:
            return q + " (use only a random sample of 1000 points to avoid overplotting)"
        else:
            return q

    # 3. Histogram: specify bins and column
    if "histogram" in ql:
        match = re.search(r'histogram of ([\w_]+)', ql)
        if match:
            col = match.group(1)
            return f"Show me a histogram of {col} using 20 bins."

        # Special case: histogram for column with most missing values
        if "most missing" in ql:
            return (
                "Show a histogram for the column with the most missing values. "
                "First, select the column using: "
                "column_with_most_missing = df.isnull().sum().idxmax(); "
                "then plot its histogram with: "
                "df[column_with_most_missing].hist()"
            )

    # 4. Bar plot: show top N
    if "bar plot" in ql or "bar chart" in ql:
        match = re.search(r'bar (plot|chart) of ([\w_]+)', ql)
        if match:
            col = match.group(2)
            return f"Show me a bar plot of the top 10 {col} values."

    # 5. Correlation or heatmap
    if "correlation" in ql:
        return (
            "Show a correlation heatmap for all numeric columns only. "
            "Use: correlation_matrix = df.select_dtypes(include='number').corr()"
        )


    # 6. Counts/size
    if "how many record" in ql or "row count" in ql or "number of rows" in ql:
        return "How many rows are in the dataset?"

    # 7. General best-practices fallback: add axis labels/titles
    if "plot" in ql:
        return q + " (make sure the axes are labeled and the plot is readable)"
    
    # 8. 
    if (("how often" in ql or "count" in ql or "frequency" in ql) and "category" in ql) or ("value_counts" in q):
        match = re.search(r'(?:categories? in |bar plot of |bar chart of )([\w_]+)', ql)
        col = match.group(1) if match else None
        if col:
            return (
                f"Show a bar plot of the counts of {col} using: "
                f"df['{col}'].value_counts().plot(kind='bar'); "
                "add axis labels and a title, then plt.show()."
            )
    
    if ("mean" in ql and "median" in ql and "standard deviation" in ql) or ("summary statistics" in ql):
        return (
            "Show a table of the mean, median, and standard deviation for all numeric columns. "
            "Use: tbl = df.describe().loc[['mean', '50%', 'std']].rename(index={'50%': 'median'}); display(tbl)"
        )


    # 9. Fallback: return the raw question
    return q

def patch_plot_code(code, df, user_question=None):

     # ── Early guard: abort nicely if the generated code references columns that
    #    do not exist in the DataFrame. This prevents KeyError crashes.
    import re

    
    # ── Detect columns referenced in the code ──────────────────────────
    col_refs = re.findall(r"df\[['\"](\w+)['\"]\]", code)

    # Columns that will be newly CREATED (appear left of '=')
    new_cols = re.findall(r"df\[['\"](\w+)['\"]\]\s*=", code)

    missing_cols = [
        col for col in col_refs
        if col not in df.columns and col not in new_cols
    ]

    if missing_cols:
        cols_list = ", ".join(missing_cols)
        return (
            f"print('⚠️ Column(s) \"{cols_list}\" not found in the dataset. "
            f"Please check the column names and try again.')"
        )
    
    # 1. For line plots (auto-aggregate)
    m_l = re.search(r"plt\.plot\(\s*df\[['\"](\w+)['\"]\]\s*,\s*df\[['\"](\w+)['\"]\]", code)
    if m_l:
        x, y = m_l.groups()
        if pd.api.types.is_numeric_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y]) and df[x].nunique() > 20:
            return (
                f"agg_df = df.groupby('{x}')['{y}'].mean().reset_index()\n"
                f"plt.plot(agg_df['{x}'], agg_df['{y}'], marker='o')\n"
                f"plt.xlabel('{x}')\nplt.ylabel('{y}')\nplt.title('Average {y} by {x}')\nplt.show()"
            )

    # 2. For scatter plots: sample to 1000 points max
    m_s = re.search(r"plt\.scatter\(\s*df\[['\"](\w+)['\"]\]\s*,\s*df\[['\"](\w+)['\"]\]", code)
    if m_s:
        x, y = m_s.groups()
        if len(df) > 1000:
            return (
                f"samp = df.sample(1000, random_state=42)\n"
                f"plt.scatter(samp['{x}'], samp['{y}'])\n"
                f"plt.xlabel('{x}')\nplt.ylabel('{y}')\nplt.title('{y} vs {x} (sampled)')\nplt.show()"
            )

    # 3. For histograms: use bins=20 for numeric, value_counts for categorical
    m_h = re.search(r"plt\.hist\(\s*df\[['\"](\w+)['\"]\]", code)
    if m_h:
        col = m_h.group(1)
        if pd.api.types.is_numeric_dtype(df[col]):
            return (
                f"plt.hist(df['{col}'], bins=20, edgecolor='black')\n"
                f"plt.xlabel('{col}')\nplt.ylabel('Frequency')\nplt.title('Histogram of {col}')\nplt.show()"
            )
        else:
            # If categorical, show bar plot of value counts
            return (
                f"df['{col}'].value_counts().plot(kind='bar')\n"
                f"plt.xlabel('{col}')\nplt.ylabel('Count')\nplt.title('Counts of {col}')\nplt.show()"
            )

    # 4. For bar plots: show only top 20
    m_b = re.search(r"(?:df\[['\"](\w+)['\"]\]\.value_counts\(\).plot\(kind=['\"]bar['\"]\))", code)
    if m_b:
        col = m_b.group(1)
        if df[col].nunique() > 20:
            return (
                f"topN = df['{col}'].value_counts().head(20)\n"
                f"topN.plot(kind='bar')\n"
                f"plt.xlabel('{col}')\nplt.ylabel('Count')\nplt.title('Top 20 {col} Categories')\nplt.show()"
            )

    # 5. For any DataFrame plot with len(df)>10000, sample before plotting!
    if "df.plot" in code and len(df) > 10000:
        return (
            f"samp = df.sample(1000, random_state=42)\n"
            + code.replace("df.", "samp.")
        )
    
    # ── Block assignment to an existing target column ────────────────        
    #*******************************************************
    target_match = re.search(r"\bpredict\s+([A-Za-z0-9_]+)", user_question or "", re.I)
    if target_match:
        target = target_match.group(1)

        # pattern for an assignment to that target
        assign_pat = rf"df\[['\"]{re.escape(target)}['\"]\]\s*="
        assign_line = re.search(assign_pat + r".*", code)
        if assign_line:
            # runtime check: keep the assignment **only if** the column is absent
            guard = (
                f"if '{target}' in df.columns:\n"
                f"    print('⚠️  {target} already exists – overwrite skipped.');\n"
                f"else:\n"
                f"    {assign_line.group(0)}"
            )
            # remove original assignment line and insert guarded block
            code = code.replace(assign_line.group(0), guard, 1)
    # ***************************************************
    
    # 6. Grouped bar plot for two categoricals
    # Grouped bar plot for two categoricals (.value_counts().unstack() or .groupby().size().unstack())
    if ".value_counts().unstack()" in code or ".groupby(" in code and ".size().unstack()" in code:
        # Try to infer columns from user question if possible:
        group, cat = None, None
        if user_question:
            # crude parse for "counts of X for each Y"
            m = re.search(r"counts? of (\w+) for each (\w+)", user_question)
            if m:
                cat, group = m.groups()
        if not (cat and group):
            # fallback: use two most frequent categoricals
            categoricals = [col for col in df.columns if pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == "object"]
            if len(categoricals) >= 2:
                cat, group = categoricals[:2]
            else:
                # fallback: any
                cat, group = df.columns[:2]
        return (
            f"import pandas as pd\n"
            f"import matplotlib.pyplot as plt\n"
            f"ct = pd.crosstab(df['{group}'], df['{cat}'])\n"
            f"ct.plot(kind='bar')\n"
            f"plt.title('Counts of {cat} for each {group}')\n"
            f"plt.xlabel('{group}')\nplt.ylabel('Count')\nplt.xticks(rotation=0)\nplt.show()"
        )

    # Fallback: Return original code
    return code

def ensure_output(code: str) -> str:
    """
    Guarantees that AI-generated code actually surfaces results in the UI
    by piping them through syntaxmatrix.display.show().  Works for:
      • bare expressions on the final line
      • chi2/p-value or (stat, p) tuples
      • pd.crosstab results used for χ² tests
    """
    lines = code.rstrip().splitlines()

    # ── 2· capture last bare expression into _out ───────────────────────
    if lines:
        last = lines[-1].strip()
        # not a comment / print / assignment / pyplot call
        if (last and not last.startswith(("print(", "plt.", "#")) and "=" not in last):
            lines[-1] = f"_out = {last}"
            lines.append("from syntaxmatrix.display import show")
            lines.append("show(_out)")

    # ── 3· auto-surface common stats tuples (stat, p) ───────────────────
    # Detect code that assigns something like "chi2, p, dof, expected = ..."    
    if re.search(r"\bchi2\s*,\s*p\s*,", code) and "show((" in code:
        pass   # AI already shows the tuple
    elif re.search(r"\bchi2\s*,\s*p\s*,", code):
        lines.append("from syntaxmatrix.display import show")
        lines.append("show((chi2, p))")

    # ── 4· classification report (string) ───────────────────────────────
    cr_match = re.search(r"^\s*(\w+)\s*=\s*classification_report\(", code, re.M)
    if cr_match and f"show({cr_match.group(1)})" not in "\n".join(lines):
        var = cr_match.group(1)
        lines.append("from syntaxmatrix.display import show")
        lines.append(f"show({var})")
    
    # 5-bis · pivot tables  (DataFrame)
    pivot_match = re.search(r"^\s*(\w+)\s*=\s*.*\.pivot_table\(", code, re.M)
    if pivot_match and f"show({pivot_match.group(1)})" not in "\n".join(lines):
        var = pivot_match.group(1)
        insert_at = next(i for i, l in enumerate(lines) if re.match(rf"\s*{var}\s*=", l)) + 1
        lines.insert(insert_at, "from syntaxmatrix.display import show")
        lines.insert(insert_at + 1, f"show({var})")

    # ── 5· confusion matrix (ndarray → figure) ───────────────────────────
    cm_assign = re.search(r"^\s*(\w+)\s*=\s*confusion_matrix\(", code, re.M)
    if cm_assign and "ConfusionMatrixDisplay" not in code:
        var = cm_assign.group(1)
        lines += [
            "from sklearn.metrics import ConfusionMatrixDisplay",
            "import matplotlib.pyplot as plt",
            "fig = plt.figure(figsize=(4,4))",
            "ax  = fig.gca()",
            f"ConfusionMatrixDisplay(confusion_matrix={var}).plot(ax=ax, colorbar=False)",
            "fig.tight_layout()",
            "plt.show()",
        ]
  
    # ── 6· chi-square contingency tables (pd.crosstab) ──────────────────
    # If a variable named 'crosstab' is created, make sure it's displayed.
    if "crosstab =" in code and "show(crosstab)" not in "\n".join(lines):
        # insert right after the crosstab assignment for readability
        insert_at = next(i for i, l in enumerate(lines) if "crosstab =" in l) + 1
        lines.insert(insert_at, "from syntaxmatrix.display import show")
        lines.insert(insert_at + 1, "show(crosstab)")
    
    # ── 7. AUTO-SHOW scalar counts like  df.shape[0]  or  [...].shape[0]
    assign_scalar = re.match(r"\s*(\w+)\s*=\s*.+\.shape\[\s*0\s*\]\s*$", lines[-1])
    if assign_scalar:
        var = assign_scalar.group(1)
        lines.append("from syntaxmatrix.display import show")
        lines.append(f"show({var})") 

    # ── 8. utils.ensure_output()
    assign_df = re.match(r"\s*(\w+)\s*=\s*df\[", lines[-1])
    if assign_df:
        var = assign_df.group(1)
        lines.append("from syntaxmatrix.display import show")
        lines.append(f"show({var})")
        
    return "\n".join(lines)

def get_plotting_imports(code):
    imports = []
    if "plt." in code and "import matplotlib.pyplot as plt" not in code:
        imports.append("import matplotlib.pyplot as plt")
    if "sns." in code and "import seaborn as sns" not in code:
        imports.append("import seaborn as sns")
    if "px." in code and "import plotly.express as px" not in code:
        imports.append("import plotly.express as px")
    if "pd." in code and "import pandas as pd" not in code:
        imports.append("import pandas as pd")
    if "np." in code and "import numpy as np" not in code:
        imports.append("import numpy as np")
    if "display(" in code and "from IPython.display import display" not in code:
        imports.append("from IPython.display import display")
    # Optionally, add more as you see usage (e.g., import scipy, statsmodels, etc)
    if imports:
        code = "\n".join(imports) + "\n\n" + code
    return code

def patch_pairplot(code, df):
    if "sns.pairplot" in code:
        # Always assign and print pairgrid
        code = re.sub(r"sns\.pairplot\((.+)\)", r"pairgrid = sns.pairplot(\1)", code)
        if "plt.show()" not in code:
            code += "\nplt.show()"
        if "print(pairgrid)" not in code:
            code += "\nprint(pairgrid)"
    return code

def ensure_image_output(code: str) -> str:
    """
    Injects a PNG exporter in front of every plt.show() so dashboards
    get real <img> HTML instead of a blank cell.
    """
    if "plt.show()" not in code:
        return code

    exporter = (
        # -- NEW: use display(), not print() --------------------------
        "import io, base64\n"
        "buf = io.BytesIO()\n"
        "plt.savefig(buf, format='png', bbox_inches='tight')\n"
        "buf.seek(0)\n"
        "img_b64 = base64.b64encode(buf.read()).decode('utf-8')\n"
        "from IPython.display import display, HTML\n"
        "display(HTML(f'<img src=\"data:image/png;base64,{img_b64}\" "
        "style=\"max-width:100%;\">'))\n"
        "plt.close()\n"
    )

    # exporter BEFORE the original plt.show()
    return code.replace("plt.show()", exporter + "plt.show()")

def fix_groupby_describe_slice(code: str) -> str:
    """
    Replaces  df.groupby(...).describe()[[...] ]  with a safe .agg(...)
    so it works for both SeriesGroupBy and DataFrameGroupBy.
    """
    pat = re.compile(
        r"(df\.groupby\(['\"][\w]+['\"]\)\['[\w]+['\"]\]\.describe\()\s*\[\[([^\]]+)\]\]\)", 
        re.MULTILINE
    )
    def repl(match):
        inner = match.group(0)
        # extract group and feature to build df.groupby('g')['f']
        g = re.search(r"groupby\('([\w]+)'\)", inner).group(1)
        f = re.search(r"\)\['([\w]+)'\]\.describe", inner).group(1)
        return (
            f"df.groupby('{g}')['{f}']"
            ".agg(['count','mean','std','min','median','max'])"
            ".rename(columns={'median':'50%'})"
        )
    return pat.sub(repl, code)

def fix_importance_groupby(code: str) -> str:
    pattern = re.compile(r"df\.groupby\(['\"]Importance['\"]\)\['\"?Importance['\"]?\]")
    if "importance_df" in code:
        return pattern.sub("importance_df.groupby('Importance')['Importance']", code)
    return code

def inject_auto_preprocessing(code: str) -> str:
    """
    • Detects a RandomForestClassifier in the generated code.
    • Finds the target column from `y = df['target']`.
    • Prepends a fully-dedented preprocessing snippet that:
        – auto-detects numeric & categorical columns
        – builds a ColumnTransformer (OneHotEncoder + StandardScaler)
    The dedent() call guarantees no leading-space IndentationError.
    """
    if "RandomForestClassifier" not in code:
        return code                      # nothing to patch

    y_match = re.search(r"y\s*=\s*df\[['\"]([^'\"]+)['\"]\]", code)
    if not y_match:
        return code                      # can't infer target safely
    target = y_match.group(1)

    prep_snippet = textwrap.dedent(f"""
        # ── automatic preprocessing ───────────────────────────────
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        num_cols = [c for c in num_cols if c != '{target}']
        cat_cols = [c for c in cat_cols if c != '{target}']

        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import StandardScaler, OneHotEncoder

        preproc = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), num_cols),
                ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
            ],
            remainder='drop',
        )
        # ───────────────────────────────────────────────────────────
    """).strip() + "\n\n"

    # simply prepend; model code that follows can wrap estimator in a Pipeline
    return prep_snippet + code

def fix_to_datetime_errors(code: str) -> str:
    """
    Force every pd.to_datetime(…) call to ignore bad dates so that
    ‘year 16500 is out of range’ and similar issues don’t crash runs.
    """
    import re
    # look for any pd.to_datetime( … )
    pat = re.compile(r"pd\.to_datetime\(([^)]+)\)")
    def repl(m):
        inside = m.group(1)
        # if the call already has errors=, leave it unchanged
        if "errors=" in inside:
            return m.group(0)
        return f"pd.to_datetime({inside}, errors='coerce')"
    return pat.sub(repl, code)

def fix_numeric_sum(code: str) -> str:
    """
    Rewrites every `.sum(` call so it becomes
    `.sum(numeric_only=True, …)` unless that keyword is already present.
    """
    pattern = re.compile(r"\.sum\(\s*([^\)]*)\)")

    def _repl(match):
        args = match.group(1)
        if "numeric_only" in args:      # already safe
            return match.group(0)

        args = args.strip()
        if args:                        # keep existing positional / kw args
            args += ", "
        return f".sum({args}numeric_only=True)"

    return pattern.sub(_repl, code)

def fix_numeric_aggs(code: str) -> str:
    _AGG_FUNCS = ("sum", "mean") 
    pat = re.compile(rf"\.({'|'.join(_AGG_FUNCS)})\(\s*([^)]+)?\)")
    def _repl(m):
        func, args = m.group(1), m.group(2) or ""
        if "numeric_only" in args:
            return m.group(0)
        args = args.rstrip()
        if args:
            args += ", "
        return f".{func}({args}numeric_only=True)"
    return pat.sub(_repl, code)

def ensure_accuracy_block(code: str) -> str:
    """
    If the code fits an estimator but never prints accuracy,
    inject an evaluation block that re-uses *whatever variable name*
    appears immediately before `.fit(`.
    """
    # Already prints accuracy? – bail out early
    if re.search(r"accuracy_score\s*\(", code):
        return code

    # Find the last `<var>.fit(` call
    m = list(re.finditer(r"(\w+)\.fit\s*\(", code))
    if not m:
        return code                    # no model at all

    var = m[-1].group(1)               # estimator variable name
    indent = re.match(r"\s*", code[m[-1].start():]).group(0)

    eval_block = textwrap.dedent(f"""
        {indent}# ── automatic accuracy evaluation ─────────
        {indent}from sklearn.metrics import accuracy_score
        {indent}y_pred = {var}.predict(X_test)
        {indent}acc = accuracy_score(y_test, y_pred)
        {indent}print(f"Model accuracy on hold-out set: {{acc:.2%}}")
    """)

    insert_at = code.find("\n", m[-1].end()) + 1
    return code[:insert_at] + eval_block + code[insert_at:]

def classify(prompt: str) -> str:
    """
    Very-light intent classifier.
    Returns one of:
      'stat_test' | 'time_series' | 'clustering'
      'classification' | 'regression' | 'eda'
    """
    p = prompt.lower().strip()
    greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings"}
    if any(p.startswith(g) or p == g for g in greetings):
        return "greeting"

    if any(k in p for k in ("t-test", "anova", "p-value")):
        return "stat_test"
    if "forecast" in p or "prophet" in p:
        return "time_series"
    if "cluster" in p or "kmeans" in p:
        return "clustering"
    if any(k in p for k in ("accuracy", "precision", "roc")):
        return "classification"
    if any(k in p for k in ("rmse", "r2", "mae")):
        return "regression"
    return "eda"

def auto_inject_template(code: str, intent: str, df) -> str:
    """If the LLM forgot the core logic, prepend a skeleton block."""
    has_fit = ".fit(" in code

    if intent == "classification" and not has_fit:
        # guess a y column that contains 'diabetes' as in your dataset
        target = next((c for c in df.columns if "diabetes" in c.lower()), None)
        if target:
            return classification(df, target) + "\n\n" + code
    return code

def fix_scatter_and_summary(code: str) -> str:
    """
    1. Change  cmap='spectral'  (any case) → cmap='Spectral'
    2. If the LLM forgets to close the parenthesis in
         summary_table = ( df.describe()...   <missing )>
       insert the ')' right before the next 'from' or 'show('.
    """
    # 1️⃣ colormap case
    code = re.sub(
        r"cmap\s*=\s*['\"]spectral['\"]",          # insensitive pattern
        "cmap='Spectral'",
        code,
        flags=re.IGNORECASE,
    )

    # 2️⃣ close summary_table = ( ... )
    code = re.sub(
        r"(summary_table\s*=\s*\(\s*df\.describe\([^\n]+?\n)"
        r"(?=\s*(from|show\())",                  # look-ahead: next line starts with 'from' or 'show('
        r"\1)",                                   # keep group 1 and add ')'
        code,
        flags=re.MULTILINE,
    )

    return code

def auto_format_with_black(code: str) -> str:
    """
    Format the generated code with Black. Falls back silently if Black
    is missing or raises (so the dashboard never 500s).
    """
    try:
        import black  # make sure black is in your v-env:  pip install black

        mode = black.FileMode()          # default settings
        return black.format_str(code, mode=mode)

    except Exception:
        return code        

def ensure_preproc_in_pipeline(code: str) -> str:
    """
    If code defines `preproc = ColumnTransformer(...)` but then builds
    `Pipeline([('scaler', StandardScaler()), ('clf', ...)])`, replace
    that stanza with `Pipeline([('prep', preproc), ('clf', ...)])`.
    """
    return re.sub(
        r"Pipeline\(\s*\[\('scaler',\s*StandardScaler\(\)\)",
        "Pipeline([('prep', preproc)",
        code
    )

def fix_plain_prints(code: str) -> str:
    """
    Rewrite  print(<var>)  → show(<var>)  when <var> looks like
    a pandas / numpy / sklearn object (heuristic: not a string literal).
    """
    import re
    return re.sub(
        r"print\((\w+)\)",
        r"from syntaxmatrix.display import show\nshow(\1)",
        code,
    )

# --------------------------------------------------------------------------
#  ✂
# --------------------------------------------------------------------------
def drop_bad_classification_metrics(code: str, y) -> str:
    """
    If the prediction target is continuous (i.e. a regression task) and the
    generated code mistakenly calls classification metrics such as
    `accuracy_score`, `classification_report`, or `confusion_matrix`,
    comment those lines out so the cell can still run.

    Works whether `y` is:
      • a pandas Series  ->  y.dtype.kind is available
      • a pandas DataFrame (multi-column)  ->  we infer by looking at *all*
    """
    # ── decide whether y looks continuous ────────────────────────────────
    try:
        kind = y.dtype.kind                          # Series path
    except AttributeError:
        # DataFrame path: regression if *every* column’s dtype is numeric/datetime
        numeric_kinds = set("fiuM")                  # float, int, unsigned, datetime
        col_kinds = {dt.kind for dt in getattr(y, "dtypes", [])}
        kind = "f" if col_kinds and col_kinds.issubset(numeric_kinds) else "O"

    # ── if regression, strip classification lines ───────────────────────
    if kind in "fM":                                 # float or datetime
        patterns = [
            r"\n.*accuracy_score[^\n]*",
            r"\n.*classification_report[^\n]*",
            r"\n.*confusion_matrix[^\n]*",
        ]
        for pat in patterns:
            code = re.sub(pat, "", code, flags=re.I)

    return code

# from syntaxmatrix.core import SyntaxMUI
# ai_generate_code = SyntaxMUI.ai_generate_code