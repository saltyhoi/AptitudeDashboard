import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import dash_table
import plotly.express as px

# Read the data from "parsed_data.csv"
df = pd.read_csv("parsed_data.csv")
df = df[
    ["LOD", "CT", "TargetLysisConcentration", "Format", "MM", "Cell", 'Concentration', 'Enzyme', 'Buffer', 'LysisTemp',
     'LysisTime', 'InactTemp', 'InactTime', 'Added By', 'Date added', 'Data file name', 'Data Reviewed by Jim',
     'Notes']]
df = df[df.TargetLysisConcentration != "RXN Input"]

# Define the columns for which you want to provide filter options
option_columns = ["Cell", "TargetLysisConcentration", "Enzyme",
                  "Concentration", "Buffer",
                  "LysisTemp", "LysisTime", "InactTemp", "InactTime", "MM"]

# Initialize the Dash app
app = dash.Dash(__name__)

# Create a list of components for dropdowns with labels
dropdowns_with_labels = []

for col in option_columns:
    label = html.Label(f"{col}:")
    dropdown = dcc.Dropdown(id=f"{col}-dropdown",
                            options=[{'label': "All", 'value': 'All'}] + [{'label': val, 'value': val} for val in
                                                                          df[col].unique()],
                            value='All'
                            )
    dropdowns_with_labels.extend([label, dropdown])

# Dropdown for selecting x-axis column
x_axis_dropdown = [html.Label("Column for the x-axis:"),
                   dcc.Dropdown(
                       id='x-axis-dropdown',
                       options=[{'label': col, 'value': col} for col in df.columns],
                       value='CT'  # Default x-axis column
                   )]

# Define the layout of the app
app.layout = html.Div([
    html.H1("Interactive Table with Filtering"),

    # Dropdown menus with labels for selecting unique values for filtering
    html.Div(dropdowns_with_labels, style={'margin-bottom': '20px'}),  # Add margin-bottom for spacing

    html.Div(x_axis_dropdown, style={'margin-bottom': '20px'}),

    # Scatter plot with LOD on the x-axis and CT on the y-axis
    dcc.Graph(id='scatter-plot'),

    # Table to display the data
    dash_table.DataTable(id='table', columns=[{'name': col, 'id': col} for col in df.columns],
                         data=df.to_dict('records'),
                         # filter_action='custom',  # Enables custom filtering
                         sort_action='custom'  # Enables custom sorting
                         )
])


# Define a callback for updating the scatter plot
@app.callback(Output('scatter-plot', 'figure'),
              [Input(f"{col}-dropdown", 'value') for col in option_columns] + [Input('x-axis-dropdown', 'value')])
def update_scatter_plot(*args):
    # Create a filter query based on user selections
    filter_query = ' & '.join([f'{col} == "{val}"' for col, val in zip(option_columns, args) if val != 'All'])

    # Apply the filter query to the data
    if filter_query:
        filtered_data = df.query(filter_query)
    else:
        filtered_data = df

    # Create a scatter plot using Plotly Express
    fig = px.scatter(filtered_data, x=args[-1], y='LOD', title='Scatter Plot of LOD vs ' + args[-1],
                     hover_data=df.columns)  # Specify all columns for hover data

    return fig


# Define a callback for custom filtering and sorting of the table
@app.callback(
    [Output('table', 'data'),
     Output('table', 'filter_query')],
    [Input(f"{col}-dropdown", 'value') for col in option_columns]
)
def update_table(*args):
    # Create a filter query based on user selections
    filter_query = ' & '.join([f'{col} == "{val}"' for col, val in zip(option_columns, args) if val != 'All'])

    # Apply the filter query to the data
    if filter_query:
        filtered_data = df.query(filter_query)
    else:
        filtered_data = df

    # Sort the data by the "LOD" column, with "NA" values sent to the bottom
    sorted_data = filtered_data.sort_values(by='LOD', na_position='last')

    # Return the sorted data and the filter query to update the table
    return sorted_data.to_dict('records'), filter_query


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
