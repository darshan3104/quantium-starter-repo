import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# Load data
df = pd.read_csv("output.csv")

# Clean date
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df = df.sort_values(by='date')

# Aggregate daily sales
daily_sales = df.groupby('date', as_index=False)['sales'].sum()

# Rolling average (smooth trend)
daily_sales['rolling_avg'] = daily_sales['sales'].rolling(window=7).mean()

# Before vs After calculation
cutoff = pd.to_datetime("2021-01-15")
before_avg = daily_sales[daily_sales['date'] < cutoff]['sales'].mean()
after_avg = daily_sales[daily_sales['date'] >= cutoff]['sales'].mean()

# Explicit conclusion for visualization
conclusion = "Sales Increased!" if after_avg > before_avg else "Sales Decreased!"
conclusion_color = "green" if after_avg > before_avg else "red"

# Initialize Dash app
app = dash.Dash(__name__)

# Create figure
fig = px.line(
    daily_sales,
    x='date',
    y='sales',
    labels={"date": "Date", "sales": "Daily Sales ($)"}
)

# Add rolling average line
fig.add_scatter(
    x=daily_sales['date'],
    y=daily_sales['rolling_avg'],
    mode='lines',
    name='7-day Avg'
)

# Vertical line (price increase)
fig.add_shape(
    type="line",
    x0="2021-01-15",
    x1="2021-01-15",
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="red", width=2, dash="dash")
)

# Annotation
fig.add_annotation(
    x="2021-01-15",
    y=1,
    xref="x",
    yref="paper",
    text="Price Increase",
    showarrow=True,
    arrowhead=2,
    ax=50,
    ay=-40
)

# Before/After average lines
fig.add_hline(
    y=before_avg,
    line_dash="dot",
    line_color="green",
    annotation_text="Before Avg",
    annotation_position="bottom right"
)

fig.add_hline(
    y=after_avg,
    line_dash="dot",
    line_color="orange",
    annotation_text="After Avg",
    annotation_position="top right"
)

# 🔥 FIXED LAYOUT (this was your issue)
fig.update_layout(
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40),
    height=600,
    xaxis_title="Date",
    yaxis_title="Daily Sales ($)"
)

# App layout
app.layout = html.Div(
    style={
        'maxWidth': '1100px',
        'margin': 'auto',
        'padding': '20px',
        'fontFamily': 'Arial'
    },
    children=[
        html.H1(
            "Impact of Price Increase on Pink Morsel Sales",
            style={'textAlign': 'center'}
        ),

        html.P(
            f"Average Daily Sales → Before: ${before_avg:.2f} | After: ${after_avg:.2f}",
            style={'textAlign': 'center', 'fontSize': '18px'}
        ),
        html.H3(
            f"Conclusion: {conclusion}",
            style={'textAlign': 'center', 'color': conclusion_color, 'marginTop': '0'}
        ),

        dcc.Graph(
            figure=fig,
            style={"height": "600px"}
        )
    ]
)

if __name__ == '__main__':
    app.run(debug=True)