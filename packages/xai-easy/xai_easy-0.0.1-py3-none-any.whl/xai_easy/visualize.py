import io, base64
import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional

def plot_importance(importance_df: pd.DataFrame, top_n: int = 20, title: str = "Feature Importance"):
    df = importance_df.head(top_n).copy()
    fig, ax = plt.subplots(figsize=(8, max(3, len(df)*0.35)))
    ax.barh(df["feature"][::-1], df["importance"][::-1])
    ax.set_xlabel("Importance (normalized)")
    ax.set_title(title)
    plt.tight_layout()
    return fig

def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('ascii')
    return f"data:image/png;base64,{data}"

def save_html_report(global_df, local_df=None, title="XAI Easy Report", filename:Optional[str]=None):
    fig = plot_importance(global_df, top_n=min(30, len(global_df)))
    img_global = _fig_to_base64(fig)
    html = f"""
    <html><head><meta charset="utf-8"><title>{title}</title></head><body>
    <h1>{title}</h1>
    <h2>Global Feature Importance</h2>
    <img src="{img_global}" alt="global importance"/><br/>
    {global_df.to_html(index=False)}
    """
    if local_df is not None:
        fig2 = plot_importance(local_df.rename(columns={"contribution":"importance"}), top_n=min(30, len(local_df)), title="Local Contributions")
        img_local = _fig_to_base64(fig2)
        html += f"""<h2>Local Explanation</h2><img src="{img_local}" alt="local importance"/><br/>{local_df.to_html(index=False)}"""
    html += "</body></html>"
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
    return html
