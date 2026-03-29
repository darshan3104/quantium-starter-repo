import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

# ── 1. Load & prepare data ────────────────────────────────────────────────────
df = pd.read_csv("output.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date']).sort_values('date')

CUTOFF = pd.to_datetime("2021-01-15")
REGIONS = ['all', 'north', 'east', 'south', 'west']

# ── 2. App initialisation ─────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.title = "Pink Morsel Sales Analysis"

# ── 3. Layout ─────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={
        'background': '#f0f2f5',
        'minHeight': '100vh',
        'padding': '40px 20px',
        'fontFamily': "'Segoe UI', Arial, sans-serif"
    },
    children=[
        # ── Card container ────────────────────────────────────────────────────
        html.Div(
            style={
                'maxWidth': '1100px',
                'margin': '0 auto',
                'background': '#ffffff',
                'borderRadius': '16px',
                'boxShadow': '0 4px 24px rgba(0,0,0,0.08)',
                'padding': '36px 48px',
            },
            children=[

                # Title
                html.H1(
                    "Pink Morsel Sales Analysis",
                    style={
                        'textAlign': 'center',
                        'color': '#1a1a2e',
                        'marginBottom': '4px',
                        'fontSize': '28px',
                        'fontWeight': '700',
                    }
                ),

                # Sub-title
                html.P(
                    "Impact of the Jan 15 2021 price increase — filter by region",
                    style={
                        'textAlign': 'center',
                        'color': '#666',
                        'marginTop': '0',
                        'marginBottom': '28px',
                        'fontSize': '15px',
                    }
                ),

                # ── Region radio buttons ──────────────────────────────────────
                html.Div(
                    style={'textAlign': 'center', 'marginBottom': '28px'},
                    children=[
                        html.Label(
                            "Filter by Region:",
                            style={
                                'fontWeight': '600',
                                'color': '#444',
                                'marginRight': '12px',
                                'fontSize': '14px',
                            }
                        ),
                        dcc.RadioItems(
                            id='region-filter',
                            options=[
                                {'label': r.title(), 'value': r} for r in REGIONS
                            ],
                            value='all',
                            inline=True,
                            inputStyle={'marginRight': '5px', 'cursor': 'pointer'},
                            labelStyle={
                                'marginRight': '18px',
                                'fontSize': '14px',
                                'color': '#333',
                                'cursor': 'pointer',
                            }
                        ),
                    ]
                ),

                # ── Stats row ────────────────────────────────────────────────
                html.Div(
                    id='stats-row',
                    style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'gap': '24px',
                        'marginBottom': '24px',
                    }
                ),

                # ── Chart ─────────────────────────────────────────────────────
                dcc.Graph(id='sales-graph', style={'height': '520px'}),
            ]
        )
    ]
)


# ── 4. Callback ───────────────────────────────────────────────────────────────
@app.callback(
    Output('sales-graph', 'figure'),
    Output('stats-row', 'children'),
    Input('region-filter', 'value'),
)
def update_chart(region):
    # Filter by region
    filtered = df if region == 'all' else df[df['region'].str.lower() == region]

    # Aggregate daily sales
    daily = filtered.groupby('date', as_index=False)['sales'].sum()

    # 7-day rolling average
    daily['rolling_avg'] = daily['sales'].rolling(window=7, min_periods=1).mean()

    # Before / after averages
    before_avg = daily[daily['date'] < CUTOFF]['sales'].mean()
    after_avg  = daily[daily['date'] >= CUTOFF]['sales'].mean()

    # Conclusion
    if after_avg > before_avg:
        conclusion, badge_color = "Sales Increased After Price Rise ▲", "#16a34a"
    else:
        conclusion, badge_color = "Sales Decreased After Price Rise ▼", "#dc2626"

    # ── Build figure ──────────────────────────────────────────────────────────
    fig = go.Figure()

    # Daily sales line
    fig.add_trace(go.Scatter(
        x=daily['date'], y=daily['sales'],
        mode='lines',
        name='Daily Sales',
        line=dict(color='#6366f1', width=2),
        opacity=0.7,
    ))

    # 7-day rolling average line
    fig.add_trace(go.Scatter(
        x=daily['date'], y=daily['rolling_avg'],
        mode='lines',
        name='7-Day Rolling Avg',
        line=dict(color='#f59e0b', width=2.5, dash='dot'),
    ))

    # Vertical dashed line at price increase date
    # NOTE: add_vline with annotation breaks on newer pandas due to Timestamp arithmetic.
    # Using add_shape + add_annotation with an ISO string as a workaround.
    fig.add_shape(
        type="line",
        x0="2021-01-15", x1="2021-01-15",
        y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(color="#ef4444", width=2, dash="dash"),
    )
    fig.add_annotation(
        x="2021-01-15", y=0.98,
        xref="x", yref="paper",
        text="Price Increase (Jan 15, 2021)",
        showarrow=False,
        xanchor="right",
        font=dict(color="#ef4444", size=12),
    )

    # Horizontal before-average line
    fig.add_hline(
        y=before_avg,
        line_dash="dot",
        line_color="#22c55e",
        line_width=1.5,
        annotation_text=f"Before Avg: ${before_avg:,.2f}",
        annotation_position="bottom right",
        annotation_font_size=11,
        annotation_font_color="#16a34a",
    )

    # Horizontal after-average line
    fig.add_hline(
        y=after_avg,
        line_dash="dot",
        line_color="#f97316",
        line_width=1.5,
        annotation_text=f"After Avg: ${after_avg:,.2f}",
        annotation_position="top right",
        annotation_font_size=11,
        annotation_font_color="#ea580c",
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Daily Sales ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=20, b=40),
        plot_bgcolor="#fafafa",
        paper_bgcolor="#ffffff",
        font=dict(family="Segoe UI, Arial, sans-serif", size=13, color="#333"),
    )

    # ── Stat cards ────────────────────────────────────────────────────────────
    def stat_card(label, value, color):
        return html.Div(
            style={
                'background': '#f8f9fa',
                'borderRadius': '10px',
                'padding': '14px 24px',
                'textAlign': 'center',
                'minWidth': '160px',
                'borderTop': f'4px solid {color}',
            },
            children=[
                html.P(label, style={'margin': '0', 'fontSize': '12px', 'color': '#888', 'fontWeight': '600'}),
                html.P(f"${value:,.2f}", style={'margin': '4px 0 0', 'fontSize': '20px', 'fontWeight': '700', 'color': color}),
            ]
        )

    stats = [
        stat_card("Avg Before Jan 15", before_avg, "#16a34a"),
        stat_card("Avg After Jan 15",  after_avg,  "#ea580c"),
        html.Div(
            style={
                'background': badge_color,
                'borderRadius': '10px',
                'padding': '14px 24px',
                'textAlign': 'center',
                'display': 'flex',
                'alignItems': 'center',
            },
            children=[
                html.P(conclusion, style={
                    'margin': '0',
                    'color': '#fff',
                    'fontWeight': '700',
                    'fontSize': '14px',
                })
            ]
        )
    ]

    return fig, stats


# ── 5. Run ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)