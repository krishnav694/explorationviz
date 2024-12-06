import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# Load the corrected dataset
ball_data_df = pd.read_csv("corrected_ball_data_with_metrics.csv")

# Ensure points have a minimum size for `runs_batter`
ball_data_df['runs_batter_size'] = ball_data_df['runs_batter'].apply(lambda x: max(x, 1))

# Create Dash app
app = dash.Dash(__name__)
server = app.server

# App layout
app.layout = html.Div([
    html.H1("ICC 2007 Cricket Tournament Explorer", style={'textAlign': 'center'}),
    html.P(
        "Explore batting performance of all teams in the ICC 2007 Cricket Tournament. "
        "Each point represents a ball bowled, colored by the batting team. "
        "Bubble size corresponds to the runs scored by the batter. ",
        style={'textAlign': 'center', 'padding': '10px', 'margin-bottom': '20px'}
    ),
    html.Div([
        html.Label("Filter by Team:"),
        dcc.Dropdown(
            id='team-dropdown',
            options=[{'label': team, 'value': team} for team in ball_data_df['batting_team'].unique()],
            value=None,
            multi=True,
            placeholder="Select Teams"
        ),
        html.Label("Filter by Bowler:"),
        dcc.Dropdown(
            id='bowler-dropdown',
            options=[{'label': bowler, 'value': bowler} for bowler in ball_data_df['bowler'].dropna().unique()],
            value=None,
            multi=True,
            placeholder="Select Bowlers"
        ),
        html.Label("Filter by Over Range:"),
        dcc.RangeSlider(
            id='over-slider',
            min=0,
            max=20,
            step=1,
            marks={i: str(i) for i in range(0, 21)},
            value=[0, 20]
        ),
    ], style={'padding': '10px', 'margin-bottom': '20px'}),
    dcc.Graph(id='immersive-plot', style={'height': '80vh'})
])

# Callback for immersive visualization with manual jitter
@app.callback(
    Output('immersive-plot', 'figure'),
    [Input('team-dropdown', 'value'),
     Input('bowler-dropdown', 'value'),
     Input('over-slider', 'value')]
)
def update_immersive_visualization(selected_teams, selected_bowlers, selected_over_range):
    filtered_df = ball_data_df

    # Apply filters
    if selected_teams:
        filtered_df = filtered_df[filtered_df['batting_team'].isin(selected_teams)]
    if selected_bowlers:
        filtered_df = filtered_df[filtered_df['bowler'].isin(selected_bowlers)]
    if selected_over_range:
        filtered_df = filtered_df[(filtered_df['over'] >= selected_over_range[0]) & (filtered_df['over'] <= selected_over_range[1])]

    # Add horizontal jitter to the 'over' values for better distribution
    filtered_df['over_jittered'] = filtered_df['over'] + np.random.uniform(-0.1, 0.1, size=len(filtered_df))

    # Immersive scatter plot with horizontal jitter and adjusted size
    immersive_fig = px.scatter(
        filtered_df,
        x="over_jittered",
        y="runs_total",
        size="runs_batter_size",  # Size of dots based on adjusted `runs_batter`
        color="batting_team",
        opacity=0.6,
        hover_data=["batter", "bowler", "over", "non_striker", "runs_batter", "runs_extras", "runs_total", "venue", "date"],  # Relevant hover data
    )

    return immersive_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
