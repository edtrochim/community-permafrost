#!/usr/bin/env python3

import os
import json
from random import randint
import math
import numpy as np
import dash
import dash_table
import flask
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import geopandas as gpd

server = flask.Flask(__name__)
mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']
communities = pd.read_csv('Data.csv')
names = communities['Community']
path_prefix='./'
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

def calc_rolling_mean(array, ndays, location):
    annual_rolling_pcpt = []
    annual_rolling_mean = []
    rolling_pcpt = []
    for i, (index,row) in enumerate(df.iterrows()):
        rolling_pcpt.append(row[location])
        if len(rolling_pcpt) > (ndays):
            rolling_pcpt.pop(0)
        annual_rolling_mean = np.mean(rolling_pcpt)
        annual_rolling_pcpt = np.sum(rolling_pcpt)
    return {'pcpt': annual_rolling_pcpt, 'mean': annual_rolling_mean}

community = html.Div(
    className='field',
    children=[
        html.Label('Type the name of one or more communities in the box below to get started.'),
        html.Div(
            className='control',
            children=[
                dcc.Dropdown(
                    id='community',
                    options=[{'label':name, 'value':name} for name in names],
                    value='Shishmaref',
                    multi=True
                )
            ]
        )
    ]
)

risklevel = html.Div(
    className='field',
    children=[
        html.Label('Select a category to visualize on the map'),
        html.Div(
            className='control',
            children=[
                dcc.Dropdown(
                    id='risklevel',
                    options=[
                        {'label':'Risk Level', 'value':'Risk Level'},
                        {'label':'Massive Ice', 'value':'Massive Ice'},
                        {'label':'Thaw Susceptibility', 'value':'Thaw Susceptibility'},
                        {'label':'Existing Problems', 'value':'Existing Problems'},
                        {'label':'Permafrost Occurrence', 'value':'Permafrost Occurrence'},
                        {'label':'Permafrost Temperature', 'value':'Permafrost Temperature'}
                    ],
                    value='Risk Level'
                )
            ]
        )
    ]
)

risk_level = communities['Risk Level']
risk_color = []
for i in risk_level:
    if i == 'High':
        risk_color.append('#8d2520')
    if i == 'Medium':
        risk_color.append('#F2CC50')
    if i == 'Low':
        risk_color.append('#476220')
    if i == 'None':
        risk_color.append('#808080')

communities['Hover Title'] = communities[['Community', 'Risk Level']].apply(lambda x: ': '.join(x), axis=1)

map_communities_trace = go.Scattermapbox(
    lat=communities['Latitude'],
    lon=communities['Longitude'],
    mode='markers',
    marker={
        'size': 15,
        'color': risk_color
    },
    text=communities['Hover Title'],
    hoverinfo='text'
)

map_layout = go.Layout(
    height=400,
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        zoom=3,
        center=dict(lat=65, lon=-152),
        style="light",
    ),
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

map_figure = go.Figure({
    'data': [map_communities_trace],
    'layout': map_layout
})


config = {
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'CommunityRisk',
        'height': 500,
        'width': 1200,
        'scale': 1
    }
}

table_columns = [{'name': 'Community', 'id': 'Community'}, {'name': 'Confidence', 'id': 'Confidence'}, {'name': 'Permafrost Occurrence', 'id': 'Permafrost Occurrence Label'}, {'name': 'Permafrost Temperature', 'id': 'Permafrost Temperature Label'}, {'name': 'Thaw Susceptibility', 'id': 'Thaw Susceptibility Label'}, {'name': 'Massive Ice', 'id': 'Massive Ice Label'}, {'name': 'Existing Problems', 'id': 'Eexisting Problems Label'}, {'name': 'Rating Score', 'id': 'Rating Score'}, {'name': 'Risk Level', 'id': 'Risk Level'}]

data_table = dash_table.DataTable(
    id='community-table',
    columns=table_columns,
    data=communities.to_dict('records')
)

header_section = html.Div(
    className='header',
    children=[
        html.Div(
            className='container',
            children=[
                html.Div(
                    className='section',
                    children=[
                        html.Div(
                            className='columns',
                            children=[
                                html.Div(
                                    className='header--logo',
                                    children=[
                                        html.A(
                                            className='header--snap-link',
                                            href='https://snap.uaf.edu',
                                            rel='external',
                                            target='_blank',
                                            children=[
                                                html.Img(src=path_prefix + 'assets/SNAP_acronym_color_square.svg')
                                            ]
                                        )
                                    ]
                                ),
                                html.Div(
                                    className='header--titles',
                                    children=[
                                        html.H1(
                                            'Community Permafrost Data',
                                            className='title is-2'
                                        ),
                                        html.H2(
                                            'Explore community risk to permafrost.',
                                            className='subtitle is-4'
                                        )
                                    ]
                                ),
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

footer = html.Footer(
    className='footer has-text-centered',
    children=[
        html.Div(
            children=[
                html.A(
                    href='https://snap.uaf.edu',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/SNAP.svg'
                        )
                    ]
                ),
                html.A(
                    href='https://uaf.edu/uaf/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/UAF.svg'
                        )
                    ]
                ),
            ]
        ),
        dcc.Markdown(
            """
UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual. [Statement of Nondiscrimination](https://www.alaska.edu/nondiscrimination/)
            """,
            className='content is-size-6'
        )
    ]
)

help_text = html.Div(
    className='container',
    children=[
        dcc.Markdown(
            """
### Notes:
* Confidence level: * – low (no reports with ground-ice data, no HMPs; estimation is based on general information on surficial geology and PF occurrence and analysis of available imagery); ** – medium (some information on permafrost conditions is available, including several geotechnical reports, HMPs, etc.); *** – high (comprehensive data are available, including numerous reports with geotechnical information, HMPs, and other sources, or we have sufficient information that there is no PF in the area).
* Massive ice occurrence: 0 – no permafrost; 1 – no massive ice; 2 – sparse small to medium ice wedges (inactive or slightly active) and/or rare occurrence of buried ice; 3 – abundant large ice wedges close to the surface (yedoma and/or active modern wedges) and/or large bodies of buried glacier ice close to the surface. Occurrence of large ice bodies near the surface makes communities extremely vulnerable to PF thawing even in the areas with very low PF temperatures.
* Thaw susceptibility: 0 – no permafrost; 1 – almost no excess ice, thaw settlement is less than ~0.1 m; 2 – thaw settlement is ~0.2-0.7 m; 3 – thaw settlement is more than 1 m.
* Existing PF-related problems: 0 – no permafrost; 1 – no PF-related problems (or minor problems); 2 – Moderate problems; 3 – Severe problems. Estimation is based mainly on available documents (e.g., HMPs) and/or pers.com.
* Permafrost Occurrence: 0 – no permafrost; 1 – mostly unfrozen soils with isolated patches of PF; 2 – discontinuous permafrost (intermittent distribution of PF and unfrozen soils, numerous open and/or closed taliks); 3 – continuous permafrost (rare taliks exist only under large and deep waterbodies).
* Permaftost Temperature: 0 – no permafrost; 1 – Mean annual ground temperature (MAGT) < -5°C (< -8°C for saline soils); 2 – MAGT = -5 – -2°C (-8– -5°C for saline soils); 3 – MAGT = -2 –
*0°C (-5– -3°C for saline soils).
* Risk level based on the rating score: 0 – no permafrost; 5-8 – low risk level; 9-11 – medium risk level; 12-15 - high risk level. Rating score (cumulative risk level) is a sum of ranks for five different categories: PF temperature; thaw susceptibility (potential thaw settlement); occurrence of massive ice; existing PF-related problems. 
            """,
            className='content is-size-5'
        )
    ]
)

app.layout = html.Div(
    children=[
        header_section,
        html.Div(
            className='section',
            children=[
                html.Div(
                    className='container',
                    children=[
                        html.Div(
                            className='columns',
                            children=[
                                html.Div(
                                    className='column',
                                    children=[
                                        html.Div(
                                            className='column',
                                            children=[
                                                html.H2('Community Risk Data & Selection')
                                            ]
                                        ),
                                        html.Div(
                                            className='column',
                                            children=[
                                                html.Div('Explore permafrost risks and hazards for rural communities in Alaska based on massive ice, thaw sysceptibility, existing infrastructure probelms, permafrost occurence and temperature.  These are tallied to create a cumulative rating score and risk level.')
                                            ]
                                        ),
                                        html.Div(
                                            className='column',
                                            children=[
                                                risklevel
                                            ]
                                        ),
                                        html.Div(
                                            className='column',
                                            children=[
                                                community
                                            ]
                                        )
                                    ]
                                ),
                                html.Div(
                                    className='column',
                                    children=[
                                        dcc.Graph(
                                            id='map',
                                            figure=map_figure,
                                            config={
                                                'displayModeBar': 'hover',
                                                'scrollZoom': True,
                                                'modeBarButtonsToRemove': ["pan2d", "lasso2d", "toImage", "toggleHover", "select2d"]
                                            }
                                        )
                                    ]
                                ),

                            ]
                        ),
                        html.Div(
                            className='column',
                            children=[
                                dcc.Graph(
                                    id='weather-plot',
                                    config=config
                                )
                            ]
                        ),
                        data_table
                    ]
                ),
                help_text
            ]
        ),
        footer
    ]
)

color_lu = {
    'Risk Level': {
        'None': '#808080',
        'Low': '#476220',
        'Medium': '#F2CC50',
        'High': '#8d2520'
    },
    'Massive Ice': {
        'None': '#808080',
        'Low': '#406080',
        'Medium': '#4080c0',
        'High': '#40a0f0'
    },
    'Thaw Susceptibility': {
        'None': '#808080',
        'Low': '#406080',
        'Medium': '#4080c0',
        'High': '#40a0f0'
    },
    'Existing Problems': {
        'None': '#808080',
        'Low': '#406080',
        'Medium': '#4080c0',
        'High': '#40a0f0'
    },
    'Permafrost Occurrence': {
        'None': '#808080',
        'Low': '#406080',
        'Medium': '#4080c0',
        'High': '#40a0f0'
    },
    'Permafrost Temperature': {
        'None': '#808080',
        'Low': '#406080',
        'Medium': '#4080c0',
        'High': '#40a0f0'
    }
}

@app.callback(
    Output('map', 'figure'),
    [
        Input('risklevel', 'value')
    ]
)

def update_map_colors(risktype):
    risk_level = communities[risktype]
    risk_color = []
    if (risktype  == 'Risk Level'):
        newcomm_labels = communities[['Community', 'Risk Level']].apply(lambda x: ': '.join(x), axis=1)
        for i in risk_level:
            if i == 'None':
                risk_color.append(color_lu[risktype]['None'])
            if i == 'Low':
                risk_color.append(color_lu[risktype]['Low'])
            if i == 'Medium':
                risk_color.append(color_lu[risktype]['Medium'])
            if i == 'High':
                risk_color.append(color_lu[risktype]['High'])
    else:
        newcomm_labels = communities[['Community', risktype + ' Label']].apply(lambda x: ': '.join(x), axis=1)
        for i in risk_level:
            if i == 0:
                risk_color.append(color_lu[risktype]['None'])
            if i == 1:
                risk_color.append(color_lu[risktype]['Low'])
            if i == 2:
                risk_color.append(color_lu[risktype]['Medium'])
            if i == 3:
                risk_color.append(color_lu[risktype]['High'])


    map_communities_trace = go.Scattermapbox(
        lat=communities['Latitude'],
        lon=communities['Longitude'],
        mode='markers',
        marker={
            'size': 15,
            'color': risk_color
        },
        text=newcomm_labels,
        hoverinfo='text'
    )
    figure = {
        'data': [map_communities_trace],
        'layout': map_layout
    }
    return figure

@app.callback(
    Output('community', 'value'),
    [
        Input('map', 'clickData')
    ]
)

def update_mine_site_dropdown(selected_on_map):
    """ If user clicks on the map, update the drop down. """
    if selected_on_map is not None:
        # Return community name
        comm_val =  selected_on_map['points'][0]['text'].split(':')[0]
        return comm_val
    # Return a default
    return 'Shishmaref'


@app.callback(
    [Output('community-table', 'data')],
    inputs=[
        Input('community', 'value')
    ]
)

def update_graph(community):
    commarray = {}
    if (type(community) == str):
        commarray = communities[communities['Community'] == community]
    else:
        for i, obj in enumerate(community):
            if i == 0:
                commarray = communities[communities['Community'] == obj]
            else:
                commarray = pd.concat([commarray,communities[communities['Community'] == obj]])
    return [commarray.to_dict('records')]

@app.callback(
    Output('weather-plot', 'figure'),
    inputs=[
        Input('community', 'value')
    ]
)
def make_plot(community):
    figure = {}
    figure['data'] = []

    hazard_lu = ['Massive Ice', 'Thaw Susceptibility', 'Existing Problems', 'Permafrost Occurrence','Permafrost Temperature', 'Risk Level' ]
    mult = 200.0
    marker_colors = ['#1D94A5','#2A697D','#AC8B53','#2F798E','#7F9EA3', '#EA906D']




    for i in community:
        if type(community) == str: 
            df = communities[communities['Community'] == community].iloc[0]
        else:
            df = communities[communities['Community'] == i].iloc[0]
            
        marker_texts = [df[10], df[9], df[11], df[7], df[8], df[13]]
        marker_size_vals = [df[5], df[4], df[6], df[2], df[3], df[12]]

        if marker_size_vals[5] == 0:
            # Leave marker size if 0
            marker_size_vals[5] = 0
        else:
            # Normalize Risk Score from 0 - 3 from None, 6-15
            # 6-8 = Low, 9-12 = Medium, 13+ = High
            marker_size_vals[5] = math.ceil((marker_size_vals[5] - 5) / 3)
        marker_sizes = [x * 1.2 + 0.25 for x in marker_size_vals]

        figure['data'].append({
            'x': hazard_lu,
            'y': [df['Community'], df['Community'], df['Community'], df['Community'], df['Community'], df['Community']],
            'name': df['Community'],
            'showlegend': False,
            'hovertext': marker_texts,
            'hovertemplate': "%{text}",
            'text': marker_texts,
            'textposition': 'center',
            'mode': 'markers+text',
            'marker': {
                'color': marker_colors,
                'size': marker_sizes,
                'sizeref': 0.05,
                'sizemode': 'scaled',
                'opacity': 0.6
            },
        })

    ref_sizes = [0.25, 1.05, 1.85, 2.65, 0]
    ref_text = [0, 1, 2, 3, '']
    ref_colors = 'rgb(150,150,150)'
    '''
    figure['data'].append({
        'x': hazard_lu,
        'y': ['<b>Reference</b>', '<b>Reference</b>', '<b>Reference</b>', '<b>Reference</b>', '<b>Reference</b>'],
        'name': 'Reference',
        'showlegend': False,
        'hovertext': ref_text,
        'hovertemplate': "Risk Level: %{text}",
        'text': ref_text,
        'textposition': 'top center',
        'mode': 'markers+text',
        'marker': {
            'color': ref_colors,
            'size': ref_sizes,
            'sizeref': 0.05,
            'sizemode': 'scaled'
        },
    })
    '''
    plot_height = 500
    #if (type(community) == list):
        #print(len(community) * 100)
        #plot_height = 100.0 * len(community)
    layout = {
        'barmode': 'grouped',
        'hovermode': 'closest',
        'title': {
            'text': 'Community Permafrost Data',
        },
	'height': plot_height,
	'yaxis': {
            'showline': 'false',
            'hoverformat': '1f'
	},
        'margin': {
            'b': 100
        },
        'xaxis': { 
            'range': hazard_lu,
            'type': 'category',
            'showline': 'false'
        }
    }
    figure['layout'] = layout
    return figure

if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
    #app.run_server(debug=True)
