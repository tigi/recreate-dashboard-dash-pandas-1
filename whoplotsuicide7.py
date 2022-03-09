# -*- coding: utf-8 -*-
# trying to recreate https://www.who.int/data/gho/data/themes/mental-health/suicide-rates
# author: Marie-Anne Melis

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd


df = pd.read_csv(r'D:\Studie\2022-udemy-python-dash\suiciderates\alledata2.csv',
                 sep=',',
                 header=(0)
                 )

#a dict is easier to use for creating a dropdownlist said someone on Google

dict_continent = df[['ParentLocationCode','ParentLocation']].drop_duplicates().to_dict('records')

#continent, country frame
df_continent_country = df[['ParentLocationCode','ParentLocation','SpatialDimValueCode','Location']].drop_duplicates()

#mean value, aggregate by ParentLocation, group by Dim1, Dim1 + values both sexes, male, female

df_suicide= df.groupby(['ParentLocationCode','ParentLocation','SpatialDimValueCode','Location','Dim1']).agg({"FactValueNumeric": "mean"}).reset_index()


#join on location .join(df_continent,on = 'Location')
df_suicide_pivoted = df_suicide.pivot(index='SpatialDimValueCode', columns='Dim1', values='FactValueNumeric').join(df_continent_country.set_index('SpatialDimValueCode'), on='SpatialDimValueCode').sort_values(by='Male', ascending=False)
df_suicide_percontinent = df_suicide_pivoted.groupby('ParentLocation').agg({"Both sexes":"mean"}).sort_values(by='Both sexes', ascending=True).reset_index()



#some generic functions and styledefinitions, some css is added in /assets
#and is automatically loaded. Maybe putting everything in there would be better
#otherwise css below overrides the css file(s) as inline css, hence !important

def style_h3():
    layout_style={'textAlign': 'center', 'color': "#ffffff",'background-color': '#008dc9'}
    return layout_style

def style_h2():
    layout_style={'textAlign': 'center'}
    return layout_style

def style_radiobuttons():
    layout_style={'display':'block','background-color': 'orange',
    'padding': '10px 5px',
    'border-radius': '4px',
    'margin': '4px',
    'cursor':'pointer'}
    return layout_style

def global_value():
    alldata = df_suicide.copy(deep=True)
    uitslag=int(alldata[alldata['Dim1']=='Both sexes'].agg({"FactValueNumeric":"mean"}))
    return uitslag

def bar_chart():
    alldata = df_suicide_percontinent.copy(deep=True)
    alldata.sort_values(by=['ParentLocation'], ascending=False)
    bar_fig_continent=px.bar(alldata, x='Both sexes', y='ParentLocation', text_auto='.2s',height=450,color_discrete_sequence =['#5bc2e7']*len(alldata))
    bar_fig_continent.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False)
    bar_fig_continent.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    return  bar_fig_continent


app=dash.Dash()
#load css bootstrap 5:
app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])


app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col([
            html.H1(id = 'H1', children = 'Trying to recreate a dashboard'),
            ],xl=12,lg=12,md = 12,sm=12,xs = 12)
        ],style = {'textAlign':'center', 'marginTop':30, 'marginBottom':30}),

            
    dbc.Row([
        dbc.Col([
    
            html.H3(children='Global value',style=style_h3()),
            html.Br(),   
            html.H2(children=global_value(),id = 'output-text',style=style_h2()),
            html.Br(),
            html.Br(),

            ],xl=2,lg=2,md = 2,sm=12,xs = 12),
        
        
        dbc.Col([
            html.H3(children='Regional values',style=style_h3()),
            dcc.Graph(id = 'bar-chart',figure=bar_chart()),
   
    
            ],xl=8,lg=8,md = 8,sm=12,xs = 12),
        
        dbc.Col([
            dcc.RadioItems(id='dropdown-continent', options=[
                {'label': i['ParentLocation'], 'value': i['ParentLocationCode']} for i in dict_continent
                ], labelStyle=style_radiobuttons(),  value='EUR'),
  
            ],xl=2,lg=2,md = 2,sm=12,xs = 12),        

        ]),
    dbc.Row([
        dbc.Col([
            html.H3(id="update_continent",style=style_h3()),
            dcc.Graph(id="line-chart",figure='line_fig_country'),
            ],xl=12,lg=12,md = 6,sm=12,xs = 12),

        ]),
    ])



@app.callback([Output(component_id='line-chart', component_property='figure'),
               Output(component_id='update_continent', component_property='children')],
               [Input(component_id='dropdown-continent',component_property='value')])


def linechart_callback(selected_continent):
    #save original dataframe
    
    alldata=df_suicide_pivoted.copy(deep=True)
    
    if not selected_continent:
        continent_filter = 'Eur'
    
    #filter op input_value = ParentLocationCode
    if selected_continent:
        continent_filter = selected_continent
    #filter dataframe
    alldata=alldata[alldata["ParentLocationCode"] == continent_filter]

   #define the line
    line_fig_country= px.scatter(alldata, x="Location", y=["Male","Female","Both sexes"])
    
    #define label for plotblock, horrible solution.
    fullnamedict = list(filter(lambda x:x["ParentLocationCode"] == continent_filter, dict_continent))
    fullname=fullnamedict[0]['ParentLocation']
                           
    return line_fig_country,html.Div('Distribution per country: {}'.format(fullname))







if __name__== '__main__':
    app.run_server()
