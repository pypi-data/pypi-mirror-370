import io, base64
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from typing import Optional
from datetime import datetime

def plot_importance(importance_df: pd.DataFrame, top_n: int = 20, title: str = "Feature Importance", color_scheme='viridis'):
    """Create an attractive horizontal bar chart for feature importance"""
    df = importance_df.head(top_n).copy()
    
    # Set style for better appearance
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, max(4, len(df)*0.4)))
    
    # Create horizontal bar chart with gradient colors
    bars = ax.barh(df["feature"][::-1], df["importance"][::-1], 
                   color=plt.cm.get_cmap(color_scheme)(df["importance"][::-1] / df["importance"].max()))
    
    # Styling
    ax.set_xlabel("Importance Score", fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', ha='left', va='center', fontweight='bold', fontsize=10)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add professional signature
    fig.text(0.99, 0.01, 'XAI Easy by Prajwal', ha='right', va='bottom', 
             fontsize=8, alpha=0.6, style='italic')
    
    plt.tight_layout()
    return fig

def _fig_to_base64(fig, dpi=150):
    """Convert matplotlib figure to base64 string with high quality"""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=dpi, facecolor='white')
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('ascii')
    plt.close(fig)  # Close figure to prevent memory leaks
    return f"data:image/png;base64,{data}"

def _get_modern_css():
    """Return modern CSS styles for the HTML report"""
    return """
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --success-color: #27ae60;
            --background-color: #f8f9fa;
            --card-background: #ffffff;
            --text-color: #2c3e50;
            --border-color: #dee2e6;
            --shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
            margin: 0;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: var(--card-background);
            border-radius: 12px;
            box-shadow: var(--shadow);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        
        .header .timestamp {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .header .creator {
            font-size: 1em;
            opacity: 0.85;
            margin-top: 8px;
            font-style: italic;
        }
        
        .content {
            padding: 0;
        }
        
        .section {
            padding: 30px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .section:last-child {
            border-bottom: none;
        }
        
        .section h2 {
            color: var(--primary-color);
            font-size: 1.8em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            border-left: 4px solid var(--secondary-color);
            padding-left: 15px;
        }
        
        .section h2::before {
            content: '';
            width: 20px;
            height: 20px;
            background: var(--secondary-color);
            border-radius: 50%;
            margin-right: 10px;
            display: inline-block;
        }
        
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
        }
        
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        th {
            background: var(--primary-color);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
            transition: background-color 0.2s ease;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        
        .rank-cell {
            font-weight: bold;
            color: var(--secondary-color);
            text-align: center;
            width: 60px;
        }
        
        .feature-cell {
            font-weight: 600;
            color: var(--primary-color);
        }
        
        .importance-cell {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            text-align: right;
            width: 120px;
        }
        
        .explanation-cell {
            font-size: 0.9em;
            color: #666;
        }
        
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border-left: 4px solid var(--secondary-color);
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: var(--secondary-color);
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid var(--border-color);
        }
        
        .footer .package-info {
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 5px;
        }
        
        .footer .author-info {
            font-size: 0.85em;
            color: #777;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            background: var(--secondary-color);
            color: white;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 2px;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            .header h1 {
                font-size: 2em;
            }
            .section {
                padding: 20px;
            }
            table {
                font-size: 0.9em;
            }
            th, td {
                padding: 10px;
            }
        }
    </style>
    """

def _format_dataframe_html(df, table_type="global"):
    """Format DataFrame as HTML with custom styling"""
    if table_type == "global":
        # Format global importance table
        html = '<table class="data-table">\n<thead>\n<tr>'
        html += '<th>Rank</th><th>Feature</th><th>Importance</th><th>Explanation</th>'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        for _, row in df.iterrows():
            html += f'<tr>'
            html += f'<td class="rank-cell">#{int(row["rank"])}</td>'
            html += f'<td class="feature-cell">{row["feature"]}</td>'
            html += f'<td class="importance-cell">{row["importance"]:.4f}</td>'
            html += f'<td class="explanation-cell">{row["explanation"]}</td>'
            html += f'</tr>\n'
    else:
        # Format local explanation table
        html = '<table class="data-table">\n<thead>\n<tr>'
        html += '<th>Feature</th><th>Contribution</th><th>Explanation</th>'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        for _, row in df.iterrows():
            html += f'<tr>'
            html += f'<td class="feature-cell">{row["feature"]}</td>'
            html += f'<td class="importance-cell">{row["contribution"]:.4f}</td>'
            html += f'<td class="explanation-cell">{row["explanation"]}</td>'
            html += f'</tr>\n'
    
    html += '</tbody>\n</table>'
    return html

def save_html_report(global_df, local_df=None, title="XAI Easy Report", filename: Optional[str] = None):
    """Create a professional HTML report with modern styling and layout"""
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    # Create enhanced plots
    fig_global = plot_importance(global_df, top_n=min(20, len(global_df)), 
                                title="Global Feature Importance", color_scheme='viridis')
    img_global = _fig_to_base64(fig_global, dpi=150)
    
    # Calculate summary statistics
    total_features = len(global_df)
    top_feature = global_df.iloc[0]['feature'] if len(global_df) > 0 else "N/A"
    top_importance = global_df.iloc[0]['importance'] if len(global_df) > 0 else 0
    
    # Start building HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {_get_modern_css()}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
                <div class="subtitle">Model Explainability Analysis</div>
                <div class="creator">Powered by XAI Easy </div>
                <div class="timestamp">Generated on {timestamp}</div>
            </div>
            
            <div class="content">
                <div class="section">
                    <div class="summary-stats">
                        <div class="stat-card">
                            <div class="stat-value">{total_features}</div>
                            <div class="stat-label">Total Features</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{top_importance:.3f}</div>
                            <div class="stat-label">Top Importance Score</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{top_feature}</div>
                            <div class="stat-label">Most Important Feature</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Global Feature Importance</h2>
                    <p>This chart shows the relative importance of each feature in the trained model. Features are ranked by their contribution to the model's overall predictive performance.</p>
                    
                    <div class="chart-container">
                        <img src="{img_global}" alt="Global Feature Importance Chart"/>
                    </div>
                    
                    {_format_dataframe_html(global_df, "global")}
                </div>
    """
    
    # Add local explanation section if provided
    if local_df is not None:
        fig_local = plot_importance(
            local_df.rename(columns={"contribution": "importance"}), 
            top_n=min(15, len(local_df)), 
            title="Local Feature Contributions",
            color_scheme='RdYlBu'
        )
        img_local = _fig_to_base64(fig_local, dpi=150)
        
        # Local explanation statistics
        top_local_feature = local_df.iloc[0]['feature'] if len(local_df) > 0 else "N/A"
        top_local_contribution = local_df.iloc[0]['contribution'] if len(local_df) > 0 else 0
        positive_contributions = len(local_df[local_df['contribution'] > 0])
        negative_contributions = len(local_df[local_df['contribution'] < 0])
        
        html += f"""
                <div class="section">
                    <h2>Local Instance Explanation</h2>
                    <p>This analysis explains the model's prediction for a specific instance, showing how each feature contributed to the final decision.</p>
                    
                    <div class="summary-stats">
                        <div class="stat-card">
                            <div class="stat-value">{positive_contributions}</div>
                            <div class="stat-label">Positive Contributors</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{negative_contributions}</div>
                            <div class="stat-label">Negative Contributors</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{top_local_feature}</div>
                            <div class="stat-label">Top Local Feature</div>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <img src="{img_local}" alt="Local Feature Contributions Chart"/>
                    </div>
                    
                    {_format_dataframe_html(local_df, "local")}
                </div>
        """
    
    # Add footer
    html += """
            </div>
            
            <div class="footer">
                <div class="package-info">Generated with XAI Easy - Explainable AI Package</div>
                <div class="author-info">Created and developed by <strong>Prajwal</strong> | Making Machine Learning Transparent and Interpretable</div>
                <div style="margin-top: 10px; font-size: 0.8em; color: #999;">
                    Built with ❤️ for responsible and explainable artificial intelligence
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save to file if filename provided
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
    
    return html
