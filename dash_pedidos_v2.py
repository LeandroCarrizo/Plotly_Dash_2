from datetime import date, datetime
import json
import dash
import dash_auth
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State

from pymongo import *

from funciones2 import *
from funciones2 import getOrdersV4, getShops

external_script = ["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}]

VALID_USERNAME_PASSWORD_PAIRS = {
    'user: 'pass'
}


td = pd.Timedelta(-31, "d")
fecha_final=date.today()
fecha_inicial= date.today()+td



dff= getShops()
options= dff[0].tolist()
options.append('todos')
options=np.sort(options)
dias=['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
turnos=['Mañana', 'Tarde', 'Noche', 'todos']
app = dash.Dash(__name__, external_scripts=external_script,)
app.scripts.config.serve_locally = True
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

server = app.server







app.layout = html.Div([
    
    html.Img(),
    
    html.Div([  
        
        html.Div([
            
            html.Div([
                html.Label('Cliente:',className="etiqueta"),#"w-20 text-right px-1"), 
                dcc.Dropdown(options,'todos',id='client-selection',className="drop")],className="mini"),
            html.Div([
                html.Label('Ciudad:',className="etiqueta"), 
                dcc.Dropdown(['La Plata', 'City Bell','Gonnet', 'todos'], 'todos',id='city-selection',className="drop")
            ],className="mini"),
    
            html.Div([
                html.Label('Fecha:'), 
                dcc.DatePickerRange(
                id='date-picker-range',
                start_date = fecha_inicial,
                display_format='Y-MM-DD',
                end_date= fecha_final,
            )],className="fecha"),
        ],className="filtros"),
        
        html.Div([
            html.Div([
                html.Div([dash_table.DataTable(
                    id = 'update-table', 
                    style_cell={'textAlign': 'center'},
                    style_data_conditional=[{
                        'if': {'filter_query': '{shift}=Noche'},
                        'backgroundColor': 'rgb(220, 220, 220)',
                    }],
                    style_header={
                        'backgroundColor': 'rgb(210, 210, 210)',
                        'color': 'black',
                        'fontWeight': 'bold'
                    }
                
                )
                
             ],className="")
            ],className="tabla"),

            html.Div([
        
                html.Div([
                    dcc.Graph(
                        id='grafico'
                
                ),      
    
                ]),
            ],className="grafico"),
        ],className="inferior")
    ],className="outer")
])





@app.callback(
    Output('grafico', 'figure'),
    Output('update-table', 'data'),
    Output('update-table', 'columns'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('client-selection', 'value'),
    Input('city-selection', 'value')
    )
def update_output(start_date, end_date, client, city):
    
    df=getOrdersV4(start_date, end_date, client, city)
    
    df=corregirCreatedDate(df)
        
    df['weekday']=df['created_date'].dt.day_name()
    df['fecha'] = pd.to_datetime(df['created_date']).dt.date
    df = df.replace({"Thursday": 'Jueves', "Monday": 'Lunes', 'Friday': 'Viernes', 'Tuesday':'Martes','Wednesday':'Miércoles',
                    'Saturday':'Sábado','Sunday':'Domingo','M':'Mañana','T':'Tarde','N':'Noche'})
    df=deleteCanceled(df)
    dfaux=df
    
    
    df=groupByDayAndShift(df)
    group=df.groupby(['weekday','shift'])
    df_columns =group['count']
    df_promedios=df_columns.mean().astype(int).to_frame('promedio').reset_index()

    

    data1 = df_promedios.to_dict('records')
    columns1=[{"name": i, "id": i} for i in df_promedios.columns]   
    print(columns1)
    
    df['colors'] = df['shift'].apply(lambda x: '#ffff00' if x=='Mañana' else ('#ff8000' if x=='Tarde' else '#ff0000'))
    names={'#ffff00':'Mañana','#ff8000':'Tarde', '#ff0000':'Noche'}
    fig = go.Figure()

    for c in df['colors'].unique():
        df_color= df[df['colors'] == c]
        fig.add_trace(
            go.Scatter(
                x=df_color.weekday, 
                y=df_color['count'],
                name=names[c],
                mode='markers',
                marker=dict(color=df_color['colors']), showlegend=True,
            
            )
        )
    fig.update_layout({'plot_bgcolor' : 'rgba(0,0,0,0)','paper_bgcolor' : 'rgba(0,0,0,0)', 'font_size' : 20})
    fig.update_layout(height=700)
    fig.update_layout(font = dict(color = '#b154c1'))
    fig. update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightPink')
    fig. update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightPink',title_text='Cantidad de pedidos')
    fig.update_traces(marker=dict(size=15,line=dict(width=1,color='DarkSlateGrey')),selector=dict(mode='markers'))
    


    return (fig,data1,columns1)


if __name__ == '__main__':
    app.run_server(debug=True)