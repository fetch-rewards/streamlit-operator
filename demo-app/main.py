from dash import Dash, html, dash_table
import pandas as pd

app = Dash(__name__)

df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
})

app.layout = html.Div([
    html.H1("Dash Demo"),
    dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df.columns],
        style_header={'backgroundColor': '#262730', 'color': 'white', 'fontWeight': 'bold'},
        style_cell={'backgroundColor': '#0e1117', 'color': 'white', 'border': '1px solid #333'},
        style_table={'width': '50%', 'margin': '0 auto'}
    )
], style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'backgroundColor': '#0e1117',
          'minHeight': '100vh', 'padding': '50px', 'color': 'white'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
