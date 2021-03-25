import os
import io
import base64
import glob
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table as dtab
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime as dt
import calendar
import pandas as pd

# Connect to main app.py file
from app import app
from app import server

# CREATION OF DATAS
def list_of_csv():
    path = os.getcwd()
    all_files = glob.glob(path + "/datas/*.csv")    
    return all_files

def available_locations():
    files = list_of_csv()
    locations = []
    for file in files:
        parsed_path = file.split("\\")[-1:]
        name = parsed_path[0].split('.')
        locations.append(name[0])
    return locations

def concatenate_all_csv(files): 
    list_of_df = []   
    for filename in files:
        data = pd.read_csv(filename, index_col=None, header=0)    
        list_of_df.append(data)
    dataframe = pd.concat(list_of_df, axis=0, ignore_index=True)
    return dataframe

def filter_datas(dataframe): 
    # Extra filters again to be sure   
    # Filter to be sure all row and column are not empty
    dataframe = dataframe.dropna(how='any')
    # Filter to be sure we have only specific flight type
    dataframe = dataframe[dataframe['flight type'].isin(['Dist libre','Dist 1 pt','Dist 2 pts','Dist 3 pts','triangle','triangle FAI'])]
    return dataframe

def format_date(dataframe):
    dataframe['date'] = pd.to_datetime(dataframe['date'], format= '%d/%m/%Y',errors='coerce') 
    dataframe = dataframe.sort_values("year")
    return dataframe

def create_initial_df():
    csv_files = list_of_csv()
    df = concatenate_all_csv(csv_files)
    return df

def filter_df(dataframe):
    dataframe = filter_datas(dataframe)
    #dataframe = add_gender(dataframe)
    dataframe = format_date(dataframe)
    return dataframe

def compute_user_selection(dataframe, site, years, months, flighttype, duration, distance, sex, gps, cat):     
    try:
        dff = dataframe[dataframe["launch"].isin(site)]
        dff = dff[dff["date"].dt.year.isin(years)]
        dff = dff[(dff["date"].dt.month >= months[0]) & (dff["date"].dt.month <= months[1])]
        dff = dff[dff["flight type"].isin(flighttype)]
        dff = dff[(dff['duration'] >= duration[0]) & (dff['duration'] <= duration[1])]
        dff = dff[(dff['kms'] >= distance[0]) & (dff['kms'] <= distance[1])]
        if sex == 'male':
            dff = dff[dff['sex'] == 'male']
        elif sex == 'female':
            dff = dff[dff['sex'] == 'female']
        else:
            pass            
        if gps == 'yes':
            dff = dff[dff['speed'] != 0]
        elif gps == 'no':
            dff = dff[dff['speed'] == 0]
        else:
            pass
        dff = dff[dff['cat'].isin(cat)]             
        dff['date'] = dff['date'].dt.date            
        return dff
    except Exception as e:
        print(e)

# INITIALIZE
initial_available_locations = available_locations()
initial_available_years = [2000, 2001, 2002, 2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021]
AVAILABLE_FLIGHTTYPE = ['Dist libre','Dist 1 pt','Dist 2 pts','Dist 3 pts','triangle','triangle FAI']

# CREATION OF LAYOUT 
def serve_layout():
    return(
        html.Div([
            
            # DIALOGS AND ALERTS
            html.Div(
                children=[
                    dcc.ConfirmDialog(
                        id='confirm-location-add',
                        message='Take off succesfully added to locations dropdown',
                    ),
                    dcc.ConfirmDialog(
                        id='empty-datas-confirm',
                        message='Could not update graphs layout ! Missing or inexsisting currently selected datas.',
                    ),
                ],
            ),
            
            # HEADER (LOGO .png à trouver)
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src=app.get_asset_url(""),
                                id="plotly-image",
                                style={
                                    "height": "60px",
                                    "width": "auto",
                                    "margin-bottom": "25px",
                                },
                            )
                        ],
                        className="one-third column",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H1(
                                        "EXPLORE PARAGLIDING XC-FLIGHTS",
                                        style={"margin-bottom": "0px"},
                                    ),
                                ]
                            )
                        ],
                        className="one-half column",
                        id="title",
                    ),
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),
            
            html.Div(
                className='row flex-diplay',
                children=[            
                    # Table + Histo
                    html.Div(
                        id="right-column",
                        className="pretty_container eight columns",
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        [html.P("Best pilot : "), html.H6(id="best-pilot")],
                                        id="pilot",
                                        className="mini_container",
                                    ),                                    
                                    html.Div(
                                        [html.P("Max overall distance : "), html.H6(id="max-kms")],
                                        id="max",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.P("Max overall duration : "), html.H6(id="max-duration")],
                                        id="duration",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.P("Avg overall kms : "), html.H6(id="average-kms")],
                                        id="avg",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.P("Total selected XC pilot(s) :"), html.H6(id="total-number-pilots-selected")],
                                        id="pilots",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [html.P("Total selected XC flight(s) :"), html.H6(id="total-number-flights-selected")],
                                        id="selection",
                                        className="mini_container",
                                    ),
                                ],
                                id="info-container",
                                className="row container-display",
                            ),
                            html.Div(
                                id="",
                                className="",
                                children=[
                                    dtab.DataTable(
                                        id='table',
                                        columns=[
                                            {"name": "Launch site", "id": "launch"},
                                            {
                                                "name": "Dep",
                                                "id": "dep",
                                            },
                                            {
                                                "name": "Date",
                                                "id": "date",
                                                # currenttly an issue from dash
                                                # https://github.com/plotly/dash-core-components/issues/781
                                                "type":"text", 
                                            },
                                            {
                                                "name": "Pilot name",
                                                "id": "pilot name",
                                            },
                                            {
                                                "name": "Flight type",
                                                "id": "flight type",
                                            },
                                            {
                                                "name": "Score (pts CFD)",
                                                "id": "points",
                                            },
                                            {
                                                "name": "Distance(km)",
                                                "id": "kms",
                                            },
                                            {
                                                "name": "Duration (hr)",
                                                "id": "duration",
                                                "type": "numeric",
                                                "format": {"specifier": ".1f"},
                                            },
                                            {
                                                "name": "Average speed (km/h)",
                                                "id": "speed",
                                            },
                                            {
                                                "name": "Wing",
                                                "id": "wing",
                                            },
                                            {
                                                "name": "Cat",
                                                "id": "cat",
                                            },
                                            {
                                                "name": "Season",
                                                "id": "year",
                                            },
                                        ],
                                        page_size=10,
                                        page_action='native',
                                        style_header={
                                                'backgroundColor': 'white',
                                                'color': 'black',
                                                'fontWeight': 'bold',
                                                'textAlign': 'center',
                                                'font-size': '2.2 rem',                    
                                            },
                                        style_cell={
                                            'backgroundColor': 'white',
                                            'color': 'black',
                                            'textAlign': 'left',
                                            'fontWeight': 'bold',
                                            'textOverflow': 'ellipsis',
                                            'maxWidth': 0,
                                        },
                                        editable=True,
                                        sort_action="native",
                                        sort_mode="multi",
                                        style_table={'overflowX': 'auto'},            
                                    )
                            ]),
                            html.Div(
                                dcc.Graph(
                                    id="histo", figure={}
                                )
                            ),                            
                        ],
                    ),
                    # SELECTIONS AND OPTIONS - UI TABS
                    html.Div(
                        className="pretty_container three columns",
                        #id="cross-filter-options",
                        children=[
                            dcc.Tabs(
                                id="tabs",
                                value='launch',
                                children=[
                                    dcc.Tab(label='Launch', value='launch',
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.Br(),
                                                    html.H1('Explore XC launch'),
                                                    html.Br(),
                                                    html.P('''
                                                        Evolution of number of flight and pilots ?
                                                        What kind of flight is mostly flown ?
                                                        What are the best flights and best sites ?
                                                        At wich period it seems to be more flyable ?'''),
                                                    html.Br(),
                                                    html.Div(
                                                        children=[
                                                            html.P("Select location(s) : "),
                                                            dcc.RadioItems(
                                                                id="all-location-radio",
                                                                options=[
                                                                    {'label':'All', 'value':'all'},
                                                                    {'label':'Customize', 'value':'customize'},
                                                                ],
                                                                value='customize',
                                                                persistence=False,
                                                                labelStyle={'display': 'inline-block'},
                                                                className="dcc_control",
                                                            ),
                                                            dcc.Dropdown(
                                                                id="location-dropdown",
                                                                options=[                                                            
                                                                ],
                                                                value=initial_available_locations[2:7],
                                                                multi=True,
                                                                persistence=False,
                                                                placeholder="Select a location(s)",
                                                                className="dcc_control",
                                                            ),
                                                        ],
                                                    ),
                                                    html.Br(),
                                                    html.Div(
                                                        children=[
                                                            html.P("Select year(s) : "),
                                                            dcc.RadioItems(
                                                                id="all-year-radio",
                                                                options=[
                                                                    {'label':'All', 'value':'all'},
                                                                    {'label':'Customize', 'value':'customize'},
                                                                ],
                                                                value='all',
                                                                persistence=False,
                                                                labelStyle={'display': 'inline-block'},
                                                                className="dcc_control",
                                                            ),
                                                            dcc.Dropdown(
                                                                id="year-dropdown",
                                                                options=[
                                                                    {'label':year, 'value':year} for year in initial_available_years
                                                                ],
                                                                value=initial_available_years,
                                                                multi=True,
                                                                persistence=False,
                                                                placeholder="Select year(s)",
                                                                className="dcc_control",
                                                                ),
                                                        ],
                                                    ),
                                                    html.Br(),
                                                    html.Div(
                                                        children=[
                                                            html.P("Select month(s) : "),
                                                            dcc.RangeSlider(
                                                                id="month-slider",
                                                                min=1,
                                                                max=12,
                                                                step=1,
                                                                marks={
                                                                    1: 'Jan',
                                                                    2: 'Feb',
                                                                    3: 'Mar',
                                                                    4: 'Apr',
                                                                    5: 'May',
                                                                    6: 'Jun',
                                                                    7: 'Jul',
                                                                    8: 'Aug',
                                                                    9: 'Sep',
                                                                    10: 'Oct',
                                                                    11: 'Nov',
                                                                    12: 'Dec',
                                                                },
                                                                value=[1, 12],
                                                                allowCross=False,
                                                                pushable=False,
                                                                included=True,
                                                                persistence=False,
                                                                className="dcc_control",
                                                            ),
                                                        ],
                                                    ),
                                                    html.Br(),
                                                    html.Br(),
                                                    dcc.Upload( # Temporairement pour test
                                                        id='upload-data', 
                                                        #multiple=True, Need code improvment in callbacks to handle multiple file once at a time
                                                        children=[
                                                            html.P("Download a .csv file and add new location and datas:"),
                                                            html.Button(id='upload-data-button',children=['Upload file']),
                                                            html.P('*Files are joined within the app folder, contact me for more sites*'),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                        ]
                                    ),
                                    dcc.Tab(label='Flight', value='flight',
                                        children=[
                                            html.Br(),
                                            html.H1('Explore XC flights'),
                                            html.Br(),
                                            html.P(
                                                """What kind of flight are mostly flown ? Is flat triangle and FAI
                                                common practice on this launch ? 
                                                What is the average duration and distance of flight ? 
                                                According to my level and ambition what kind of flight are possible ?
                                                """
                                            ),
                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    html.P('Select flight type : '),
                                                    dcc.Checklist(
                                                        id="flighttype-checklist",
                                                        options=[
                                                            {"label": i, "value": i}
                                                            for i in AVAILABLE_FLIGHTTYPE
                                                        ],
                                                        value=AVAILABLE_FLIGHTTYPE,           
                                                        persistence=False,
                                                        className="dcc_control",
                                                    ),
                                                ],
                                            ),
                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    html.P('Select duration :'),
                                                    dcc.RangeSlider(
                                                        id="duration-slider",
                                                        min=0,
                                                        max=8,
                                                        step=0.5,
                                                        value=[0, 8],                
                                                        included=True,
                                                        marks={0:'0h',1:'1h',2:'2h',3:'3h',4:'4h',5:'5h',
                                                            6:'6h',7:'7h',8:'8h'},
                                                        pushable=True,
                                                        persistence=False,
                                                        className="dcc_control",
                                                    ),
                                                ],
                                            ),
                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    html.P('Select distance :'),
                                                    dcc.RangeSlider(
                                                        id="distance-slider",
                                                        min=0,
                                                        max=300,
                                                        step=25,
                                                        value=[0, 300],                
                                                        included=True,
                                                        marks={0:'0 km',50:'50 kms',100:'100km',
                                                            150:'150 kms',200:'200 kms',
                                                            250:'250 kms', 300:'300 kms'},
                                                        pushable=True,
                                                        persistence=False,
                                                        className="dcc_control",
                                                    ),
                                                ],
                                            ),
                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    html.P('Select flight with/without gps tracks :'),
                                                    dcc.RadioItems(
                                                        id='gps-radio',
                                                        options=[
                                                            {'label':'All', 'value':'all'},
                                                            {'label':'Only', 'value':'yes'},
                                                            {'label':'Whithout', 'value':'no'},
                                                        ],
                                                        value='yes',
                                                        persistence=False,
                                                        labelStyle={'display': 'inline-block'},
                                                        className="dcc_control",
                                                    )
                                                ]    
                                            ),
                                        ]
                                    ),
                                    dcc.Tab(label='Pilot', value='pilot',
                                        children=[
                                            html.Br(),
                                            html.H1('Explore XC pilots'),
                                            html.Br(),
                                            html.P(
                                                """ What kind of wings pilots love to fly ?
                                                Any difference between wing's EN class ?
                                                Find flight flown by pilot sex ?
                                                """
                                            ),
                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    html.P('Select pilot(s) by genre :'),
                                                    dcc.RadioItems(
                                                        id="sex-radio",
                                                        options=[
                                                            {'label': 'All pilots', 'value': 'all'},
                                                            {'label': 'Male', 'value': 'male'},
                                                            {'label': 'Female', 'value': 'female'}
                                                        ],
                                                        value='all',
                                                        persistence=False,
                                                        labelStyle={'display': 'inline-block'},
                                                        className="dcc_control",
                                                    )
                                                ],
                                            ),
                                            html.Br(),
                                            html.Div(
                                                children=[
                                                    html.P('Select wing class :'),
                                                    dcc.Checklist(
                                                        id="wing-checklist",
                                                        options=[
                                                            {'label': 'A', 'value': 'A'},
                                                            {'label': 'B', 'value': 'B'},
                                                            {'label': 'C', 'value': 'C'},
                                                            {'label': 'D', 'value': 'D'},
                                                            {'label': 'Competitions', 'value': 'K'},                   
                                                            {'label': 'Prototypes', 'value': 'O'},                   
                                                            {'label': 'Biplace', 'value': 'bi'},                   
                                                        ],
                                                        value=['A','B','C','C','D','K','O','bi'],
                                                        persistence=False,
                                                        className="dcc_control",
                                                    )
                                                ],
                                            ),
                                        ]
                                    ),
                                    dcc.Tab(label='Graphs', value='other',
                                        children=[
                                            html.Br(),
                                            html.H5("DATA TABLE SETTINGS"),                                    
                                            html.Div(
                                                children=[ 
                                                    html.P("Highlight best score (blue) :"),                                           
                                                    dcc.RadioItems(
                                                        id="highlight-best-flight",
                                                        options=[
                                                            {'label': 'Yes', 'value': 'yes'},
                                                            {'label': 'No', 'value': 'no'},                   
                                                        ],
                                                        value='yes',
                                                        persistence=False,
                                                        className="dcc_control",
                                                    )
                                                ],
                                            ),
                                            html.H5("HISTOGRAM SETTINGS"),                                    
                                            html.Div(
                                                children=[ 
                                                    html.P("X-Axis :"),                                           
                                                    dcc.Dropdown(
                                                        id="histo-xaxis-dropdown",
                                                        options=[
                                                            {'label': 'Season(s)', 'value': 'season'},
                                                            {'label': 'Month(s)', 'value': 'month'},                   
                                                        ],
                                                        value='season',
                                                        multi=False,
                                                        persistence=False,
                                                        className="dcc_control",
                                                    ),
                                                    html.P("Y-Axis: "),                                           
                                                    dcc.Dropdown(
                                                        id="histo-yaxis-dropdown",
                                                        options=[
                                                            {'label': 'Kms', 'value': 'kms'},
                                                            #{'label': 'Number of flight', 'value': 'count'},                   
                                                            {'label': 'Max alt', 'value': 'max alt'}, 
                                                            {'label': 'Speed', 'value': 'speed'},                                                                               
                                                        ],
                                                        value='kms',
                                                        multi=False,
                                                        persistence=False,
                                                        className="dcc_control",
                                                    ),
                                                ],
                                            ),
                                            html.H5("SCATTER PLOT SETTINGS"),                                    
                                            html.Div(
                                                children=[ 
                                                    html.P("X-Axis:"),                                           
                                                    dcc.Dropdown(
                                                        id="scatter-xaxis-dropdown",
                                                        options=[
                                                            {'label': 'Kms', 'value': 'kms'},
                                                            {'label': 'Speed', 'value': 'speed'},                   
                                                            {'label': 'Max Alt', 'value': 'max alt'},                   
                                                        ],
                                                        value='speed',
                                                        persistence=False,
                                                        clearable=False,
                                                        multi=False,
                                                        className="dcc_control",
                                                    )
                                                ],
                                            ),
                                            html.Div(
                                                children=[ 
                                                    html.P("Y-Axis:"),                                           
                                                    dcc.Dropdown(
                                                        id="scatter-yaxis-dropdown",
                                                        options=[
                                                            {'label': 'Kms', 'value': 'kms'},
                                                            {'label': 'Speed', 'value': 'speed'},                   
                                                            {'label': 'Max Alt', 'value': 'max alt'},                   
                                                        ],
                                                        value='kms',
                                                        persistence=False,
                                                        clearable=False,
                                                        multi=False,
                                                        className="dcc_control",
                                                    )
                                                ],
                                            ),
                                            html.Div(
                                                children=[ 
                                                    html.P("Color by :"),                                           
                                                    dcc.RadioItems(
                                                        id="scatter-color-radio",
                                                        options=[
                                                            {'label': 'Launch', 'value': 'launch'},
                                                            {'label': 'Category', 'value': 'cat'},                   
                                                        ],
                                                        value='launch',
                                                        labelStyle={'display': 'inline-block'},
                                                        persistence=False,
                                                        className="dcc_control",
                                                    )
                                                ],
                                            ),
                                            html.Div(
                                                children=[ 
                                                    html.P("Logarithmic axis : "),                                           
                                                    dcc.Checklist(
                                                        id="scatter-logx-checklist",
                                                        options=[
                                                            {'label': 'Log-X', 'value': 'True'},                   
                                                        ],
                                                        persistence=False,
                                                        labelStyle={'display': 'inline-block'},
                                                        className="dcc_control",
                                                    ),
                                                    dcc.Checklist(
                                                        id="scatter-logy-checklist",
                                                        options=[
                                                            {'label': 'Log-Y', 'value': 'True'},                   
                                                        ],
                                                        persistence=False,
                                                        labelStyle={'display': 'inline-block'},
                                                        className="dcc_control",
                                                    )
                                                ],
                                            ),
                                        ]
                                    )
                                ],
                            ),
                            html.Br(),
                        ],
                    ),
                ],
            ),
            
            html.Div(
                className='row flex-diplay',
                children=[
                    # Sunburst
                    html.Div(
                        className="pretty_container five columns",
                        children=[
                            dcc.Graph(
                                id="sunburst", figure={}
                            )
                        ],
                    ),                                          
                    # Scatter 1
                    html.Div(
                        className="pretty_container five columns",
                        children=[
                            dcc.Graph(
                                id="scatter-1", figure={}
                            )
                        ],
                    ),
                ],
            ),
            
            #html.Div(
                #className='row flex-diplay',
                #children=[                                         
                    # Scatter 2
                   # html.Div(
                        #className="pretty_container ten columns",
                        #children=[
                           # dcc.Graph(
                             #   id="scatter-2", figure={}
                            #)
                        #],
                   # ),
               # ],
           # ),
            
            # DATAS STORAGES
            dcc.Store(id='data-storage', storage_type='memory'),
            dcc.Store(id='selected-data-storage', storage_type='memory'),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
        )
    )

# APPLICATION LAYOUT 
app.layout=serve_layout

# CALLBACKS
# INITIAL DATAFRAME TO JSON AND ADDING  FILE
@app.callback(
    Output('data-storage', 'data'),
    Output('confirm-location-add','displayed'),
    [
    Input('upload-data', 'contents')],
    State('data-storage', 'data')
)
def initial_data(contents, jsonified_cleaned_data):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # Check if upload data has been triggered
    if not 'upload-data' in changed_id:
        if jsonified_cleaned_data is None:
            global_df = create_initial_df()
            global_df = filter_df(global_df)
            return global_df.to_json(date_format='iso', orient='split'), False
        else:
            raise dash.exceptions.PreventUpdate        
    else:
        global_df = pd.read_json(jsonified_cleaned_data, orient='split')
        current_locations = global_df['launch'].unique().tolist()
        print(current_locations)
        try:                   
            content_string = contents.split(',')        
            decoded = base64.b64decode(content_string[1])
            #print(decoded)
            try:
                df_new = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            except:
                df_new = pd.read_csv(io.StringIO(decoded.decode('latin-1')))
            new_location = df_new['launch'].unique().tolist()
            if new_location[0] in current_locations:                
                return global_df.to_json(date_format='iso', orient='split'), False
            else:
                df_new = filter_df(df_new)
                global_df = global_df.append(df_new)  
                locations = global_df['launch'].unique()                    
                return global_df.to_json(date_format='iso', orient='split'), True
        except Exception as e:
            print(e) 

# LOCATIONS UPDATES AND ALL/CUSTOMIZE
@app.callback(
    Output('location-dropdown', 'value'),
    Output('location-dropdown', 'options'),
    Input('all-location-radio', 'value'),
    Input('data-storage', 'data'),
)
def location_radio_option(value, jsonified_data):
    if len(jsonified_data) == 0:
       return initial_available_locations, [{'label':location, 'value':location} for location in initial_available_locations]    
    df = pd.read_json(jsonified_data, orient='split')
    new_locations = df['launch'].unique()
    if value == 'all':
        return new_locations.tolist(), [{'label':location, 'value':location} for location in new_locations.tolist()] 
    elif value == 'customize':
        return dash.no_update, [{'label':location, 'value':location} for location in new_locations.tolist()]
    raise dash.exceptions.PreventUpdate

# YEAR ALL/CUSTOMIZE
@app.callback(
    Output('year-dropdown', 'value'),
    Input('all-year-radio', 'value'),
)
def location_radio_option(value):
    if value == 'all':
        return initial_available_years
    elif value == 'customize':
        return []
    else:
        raise dash.exceptions.PreventUpdate
 
# OVERALL DATA TO SELECTED DATA
@app.callback(
    Output('total-number-flights-selected', 'children'),
    Output('empty-datas-confirm','displayed'),
    Output('selected-data-storage', 'data'),
    [
    Input('location-dropdown', 'value'),
    Input('year-dropdown','value'),
    Input('month-slider','value'),
    Input('flighttype-checklist','value'),
    Input('duration-slider','value'),
    Input('distance-slider','value'),
    Input('sex-radio','value'),
    Input('gps-radio', 'value'),
    Input('wing-checklist', 'value'),
    Input('data-storage', 'data'),
    ],      
)
def selected_data_and_update(site, years, months, flighttype, duration, distance, sex, gps, cat, jsonified_data):       
    ctx = dash.callback_context
    df = pd.read_json(jsonified_data, orient='split')
    # Wait for a trigger
    if ctx.triggered:
        # If triggered, check if empty list
        if len(site) == 0 or len(cat) == 0:       
            return "0", True, []       
        
        # Otherwise it computes current selection        
        dff = compute_user_selection(df, site, years, months, flighttype, duration, distance, sex, gps, cat) 
        #print(dff)
        # If compution lead to no existing datas
        if dff is None:
            return "0", True, []
        
        # Store and send the selected data to other graphs callbacks
        selected_datas = dff.to_json(date_format='iso', orient='split')
        
        # Return selected data to another storage before being dispatched to graphs.
        return "{}".format(len(dff.index)), False, selected_datas
    else:
        raise dash.exceptions.PreventUpdate   

# MINI CONTAINER LAYOUTS AND UPDATES:
@app.callback(
    Output('best-pilot', 'children'),
    Output('max-kms', 'children'),
    Output('max-duration', 'children'),
    Output('average-kms', 'children'),     
    Output('total-number-pilots-selected', 'children'),
    Input('selected-data-storage', 'data')    
)
def update_overall_stats(selected_data):
    if len(selected_data) == 0:
        return 0,0,0,0,0
    else:        
        dff = pd.read_json(selected_data, orient='split')
        #print(dff['pilot name'].unique())
        #print(len(dff['pilot name'].unique()))
        return (
            '{}'.format(dff.loc[dff['kms'] == dff['kms'].max(), 'pilot name'].values[0]),
            '{} kms'.format(dff['kms'].max()),
            '{} hr'.format(dff['duration'].max()),
            '{} kms'.format(round(dff['kms'].mean())),
            '{}'.format(len(dff['pilot name'].unique()))
        )
        
# GRAPHS LAYOUTS AND UPDATES

# 1-Table   
@app.callback(
    Output('table', 'data'),
    Output('table', 'style_data_conditional'),
    [Input('selected-data-storage', 'data'),
    Input('highlight-best-flight','value')]  
) 
def update_table(selected_data, value): 
    if len(selected_data) == 0:
        return [], []
    dff = pd.read_json(selected_data, orient='split')
    dff['date'] = dff['date'].dt.strftime("%d/%m/%Y")
    if value == 'yes':
        style_data_conditional=[
            {
            'if': {
                'filter_query': '{{points}} = {}'.format(dff['points'].max()),
            },
            'backgroundColor': '#57A4DD',
            'color': 'white'
            },
        ]   
        return dff.to_dict('records'), style_data_conditional 
    else:
        return dff.to_dict('records'), []    
 
# 2-Histo evolution
@app.callback(
    Output('histo', 'figure'),
    [Input('selected-data-storage', 'data'),
    Input('histo-xaxis-dropdown','value'),
    Input('histo-yaxis-dropdown','value'),
    ]   
) 
def update_histogram(selected_data, value, y_axis): 
    if len(selected_data) == 0:
        return {}
    dff = pd.read_json(selected_data, orient='split')
    yaxis=y_axis
    if value == 'season':
        histo = px.histogram(
            dff, 
            title='EVOLUTION BY SEASON', 
            x='year',
            y=yaxis,
            histfunc="avg",
            color='launch',                       
            marginal='box', 
            barmode='overlay',
            opacity=0.95, 
            labels=dict
                (x="Seasons",
                y="Average kilometers", 
                ),
            template="ggplot2",
            )      
    #by months
    else: 
        month = dff['date'].dt.month
        histo = px.histogram(
            dff, 
            title='EVOLUTION BY MONTHS', 
            x=month,
            y=yaxis,
            histfunc="avg",
            color='launch',                       
            marginal='box', 
            barmode='overlay',
            opacity=0.95, 
            labels=dict
                (x="Month",
                ),
            template="ggplot2"
            )     
    histo.update_layout(hovermode="y unified")
    return histo

# 3 - Sunburst
@app.callback(
    Output('sunburst', 'figure'),
    Input('selected-data-storage', 'data')    
)
def update_sunburst(selected_data): 
    if len(selected_data) == 0:
        return {}
    dff = pd.read_json(selected_data, orient='split')      
    sunburst = px.sunburst(
        dff, 
        title ='XC FLIGHTS REPARTITIONS', 
        path=['launch', 'flight type', 'cat'], 
        values='kms', 
        color='kms',
        template="ggplot2",        
    )
    sunburst.update_layout(height=650)
    return sunburst 

# 4 - Scatter
@app.callback(
    Output('scatter-1', 'figure'),
    [Input('selected-data-storage', 'data'),    
    Input('scatter-xaxis-dropdown', 'value'),    
    Input('scatter-yaxis-dropdown', 'value'),
    Input('scatter-color-radio', 'value'),
    Input('scatter-logx-checklist', 'value'),
    Input('scatter-logy-checklist', 'value'),
    
    ]   
)
def update_scatter_1(selected_data,x_axis,y_axis,color_by,is_logx,is_logy):
    if len(selected_data) == 0 or x_axis is None or y_axis is None:
        return {}
    x = x_axis
    y = y_axis
    color = color_by
    logx=is_logx
    logy=is_logy
    dff = pd.read_json(selected_data, orient='split')
    scatter = px.scatter(
        dff, 
        title="XC FLIGHTS PERFORMANCES", 
        x=x_axis, 
        y=y_axis, 
        color=color,
        template="ggplot2", 
        size='points', 
        size_max=25,
        hover_name='launch', 
        log_x=logx,
        log_y=logy,
    )
    scatter.update_layout(height=650)  
    return scatter    
         

if __name__ == '__main__':
    app.run_server(debug= True)