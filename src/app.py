from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import urllib.request
import json

# Load data
wb = pd.read_csv('../csv/wellbeing-local-authority-time-series-v4.csv')
anxiety = wb[wb['measure-of-wellbeing'] == 'anxiety']
anxiety_clean = anxiety.dropna(subset=['v4_3'])
london_boroughs = anxiety_clean[anxiety_clean['administrative-geography'].str.startswith('E09')]
london_boroughs = london_boroughs[london_boroughs['Estimate'] == 'Average (mean)'].copy()
london_boroughs = london_boroughs.rename(columns={'v4_3': 'mean_anxiety_score'})
borough_means = london_boroughs.groupby('Geography')['mean_anxiety_score'].mean().reset_index()

# Time series data
london_boroughs_ts = london_boroughs.copy()
london_boroughs_ts['year_start'] = london_boroughs_ts['yyyy-yy'].str[:4].astype(int)
london_boroughs_ts = london_boroughs_ts.sort_values(['Geography', 'year_start'])

# Build time series chart
fig2 = px.line(
    london_boroughs_ts,
    x='year_start',
    y='mean_anxiety_score',
    color='Geography',
    title='Anxiety Levels by London Borough Over Time (2011-2022)',
    hover_name='Geography',
    line_shape='spline',
)
fig2.update_traces(
    line=dict(width=1.5),
    opacity=0.5,
    hovertemplate='<b>%{fullData.name}</b><br>Year: %{x}<br>Anxiety: %{y:.2f}<extra></extra>'
)
fig2.update_layout(
    plot_bgcolor='#111111',
    paper_bgcolor='#111111',
    font_color='#FF6B00',
    title_font_color='#FF6B00',
    xaxis=dict(gridcolor='#222222', title='Year'),
    yaxis=dict(gridcolor='#222222', title='Mean Anxiety Score'),
    legend=dict(
        bgcolor='#111111',
        font=dict(size=10),
        itemclick='toggleothers',
        itemdoubleclick='toggle'
    ),
    height=600,
    hovermode='closest'
)
fig2.add_vline(x=2020, line_width=1, line_dash='dash', line_color='#FF6B00', opacity=0.5)
fig2.add_annotation(
    x=2020, y=4.0, text="Covid-19", showarrow=True,
    arrowhead=2, arrowcolor='#FF6B00', font=dict(color='#FF6B00')
)

# Borough heatmap
heatmap_data = london_boroughs_ts.pivot(
    index='Geography',
    columns='year_start',
    values='mean_anxiety_score'
)
fig5 = px.imshow(
    heatmap_data,
    color_continuous_scale=['#111111', '#FF6B00'],
    title='Anxiety Levels by London Borough and Year',
    labels=dict(x='Year', y='Borough', color='Anxiety Score'),
    aspect='auto'
)
fig5.update_layout(
    paper_bgcolor='#111111',
    plot_bgcolor='#111111',
    font_color='#FF6B00',
    title_font_color='#FF6B00',
    height=700,
    margin=dict(l=150, r=0, t=40, b=0)
)

# Animated race
fig6 = px.bar(
    london_boroughs_ts.sort_values(['year_start', 'mean_anxiety_score'], ascending=[True, True]),
    x='mean_anxiety_score',
    y='Geography',
    orientation='h',
    animation_frame='year_start',
    range_x=[2, 4.5],
    color='mean_anxiety_score',
    color_continuous_scale=['#111111', '#FF6B00'],
    title='London Borough Anxiety Scores Over Time',
    labels=dict(mean_anxiety_score='Mean Anxiety Score', Geography='Borough')
)
fig6.update_layout(
    paper_bgcolor='#111111',
    plot_bgcolor='#111111',
    font_color='#FF6B00',
    title_font_color='#FF6B00',
    height=700,
    margin=dict(l=150, r=0, t=40, b=0),
    coloraxis_showscale=False
)

# Load GeoJSON
url = "https://raw.githubusercontent.com/radoi90/housequest-data/master/london_boroughs.geojson"
with urllib.request.urlopen(url) as response:
    london_geojson = json.load(response)

# Build choropleth
fig1 = px.choropleth_mapbox(
    borough_means,
    geojson=london_geojson,
    locations='Geography',
    featureidkey='properties.name',
    color='mean_anxiety_score',
    color_continuous_scale=['#1a1a1a', '#FF6B00'],
    mapbox_style='carto-darkmatter',
    zoom=8.5,
    center={'lat': 51.5074, 'lon': -0.1278},
    opacity=0.8,
    title='Mean Anxiety Score by London Borough (2011-2022)',
    hover_name='Geography',
    hover_data={'mean_anxiety_score': ':.2f'}
)
fig1.update_layout(
    paper_bgcolor='#111111',
    font_color='#FF6B00',
    title_font_color='#FF6B00',
    margin=dict(l=0, r=0, t=40, b=0),
    height=600
)

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div(
    style={'backgroundColor': '#111111', 'minHeight': '100vh', 'fontFamily': 'sans-serif'},
    children=[

        # Header
        html.Div(
            style={'padding': '60px 40px 20px 40px', 'borderBottom': '1px solid #333333'},
            children=[
                html.H1("PROTECT YOUR ZEN",
                    style={'color': '#FF6B00', 'fontSize': '48px', 'marginBottom': '10px'}),
                html.P("Exploring mental health across London and the UK through data.",
                    style={'color': '#ffffff', 'fontSize': '18px', 'marginBottom': '0px'}),
            ]
        ),

        # Section 1: London
        html.Div(
            style={'padding': '40px'},
            children=[
                html.H2("London", style={'color': '#FF6B00', 'marginBottom': '20px'}),
                html.Div(
                    style={'display': 'flex', 'gap': '20px'},
                    children=[
                        html.Div(dcc.Graph(figure=fig1), style={'flex': '1'}),
                        html.Div(dcc.Graph(figure=fig2), style={'flex': '1'}),
                    ]
                ),
            ]
        ),

        # Section 2: Deeper London
        html.Div(
            style={'padding': '40px', 'borderTop': '1px solid #333333'},
            children=[
                html.H2("Deeper London", style={'color': '#FF6B00', 'marginBottom': '20px'}),
                dcc.Graph(figure=fig5),
                dcc.Graph(figure=fig6),
            ]
        ),

    ]
)

if __name__ == '__main__':
    app.run(debug=True)