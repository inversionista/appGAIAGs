import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

import sys
sys.path.append("..")

import librerias.GAIAGs_funtions as GAIAGs

import plotly.graph_objects as go

import dash
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

from datetime import date

# Inputs
accion = 'XP'
ventana_estadisticas = 20 #Dias
dias_intradiarios= 60     #Dias max 60 para velas intradiarias
velas_en_minutos = 5 # Minutos
visualizar_dias = 4

desviacion_short = 3.44
desviacion_long = -3.44
desviacion_volumen = 2.129
grafico_velas= go.Figure()
grafico_signals = go.Figure()

#desviaciones=[1.316, 2.129]
#desviaciones=[1.316, 2.129, 3.444, 5.57]
desviaciones=[1.316, 2.129, 3.444, 5.57,  9.016]
#desviaciones=[1.316, 2.129, 3.444, 5.572, 9.016, 14.58]

#colores= ['steelblue', 'tomato']
#colores= ['steelblue', 'tomato', 'black', 'yellowgreen']
colores= ['steelblue', 'tomato','black', 'yellowgreen', 'green']
#colores= ['steelblue', 'tomato','black', 'yellowgreen', 'green', 'violet']


today = datetime.now()
f_inicio = today - timedelta(days = (dias_intradiarios + ventana_estadisticas+40))

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

header = html.H1(children="GAIAGsGroup - Analisís Cuantitativo",style={"text-align": "center"})

texto_1= '''

### Niveles GAIAGs
Pretenden ser una medida anticipada de los limites o espectativas de movimiento
próximos del precio de una acción.

Son una medida estádistica que refleja la cantidad de desviaciones
que el precio de un activo esta alejado de su promedio.

La idea de trading esta basada en el modelo de Retornos logaritmicos Normales.

En [GAIAGs Group](https://GAIAGsGroup.com/) somos:

1. Creadores de estrategias cuantitativas
2. Acompañamiento trading Room

En esta pagina podra analizar una acción deseada.

'''

Mensaje_1 = dcc.Markdown(texto_1)

solicitar_seleccion = html.P("Escriba una Accion: ")

accione_seleccionada = dcc.Input(
            id="ticker",
            type='text',
            value="XP",
            
        )

boton_calcular = dbc.Button('CALCULAR', id='boton-c', color="secondary")

grafico_1 = dcc.Graph(id='Grafico_Niveles_GAIAGs')
grafico_2 = dcc.Graph(id='Grafico_Señales')


fila1 = html.Div(children=[solicitar_seleccion, accione_seleccionada],)
fila2 = html.Div(children=[boton_calcular])
fila3 = html.Div(children=[grafico_1])
fila4 = html.Div(children=[grafico_2])

layout = dbc.Container(children=[header, Mensaje_1, fila1, fila2, fila3, fila4], )


@app.callback(
    Output("Grafico_Niveles_GAIAGs", "figure"),
    Output("Grafico_Señales", "figure"),
    [Input("boton-c", 'n_clicks')],
    [State('ticker', 'value')]
)
def update_output(n_clicks, value):
    global grafico_velas, grafico_signals
    if n_clicks:

        accion = value
        
        precios_diarios = yf.download(accion , start=f_inicio.strftime('%Y-%m-%d'), auto_adjust = True, progress=False)
        precios_intraday = yf.download(accion , period=str(dias_intradiarios)+"d", interval=str(velas_en_minutos)+"m", auto_adjust=True, progress=False)
        GAIAGs.niveles_log_gap(precios_diarios, Niveles_Desviaciones = desviaciones)

        precios_diarios['Close_prev'] = precios_diarios['Close'].shift(1)
        precios_diarios['High_prev'] = precios_diarios['High'].shift(1)
        precios_diarios['Low_prev'] = precios_diarios['Low'].shift(1)

        for d in precios_diarios.index[-dias_intradiarios:]:
            for i in desviaciones:
                precios_intraday.loc[d.strftime("%Y-%m-%d"), ('+'+str(i)+'Std')] = precios_diarios.loc[d,'+'+str(i)]
                precios_intraday.loc[d.strftime("%Y-%m-%d"), ('-'+str(i)+'Std')] = precios_diarios.loc[d,'-'+str(i)]
            
            precios_intraday.loc[d.strftime("%Y-%m-%d"),'Open_day'] = precios_diarios.loc[d.strftime("%Y-%m-%d"),'Open']

            precios_intraday.loc[d.strftime("%Y-%m-%d"),'Close_prev'] = precios_diarios.loc[d.strftime("%Y-%m-%d"),'Close_prev']
            precios_intraday.loc[d.strftime("%Y-%m-%d"),'High_prev'] = precios_diarios.loc[d.strftime("%Y-%m-%d"),'High_prev']
            precios_intraday.loc[d.strftime("%Y-%m-%d"),'Low_prev'] = precios_diarios.loc[d.strftime("%Y-%m-%d"),'Low_prev']

            precios_intraday.loc[d.strftime("%Y-%m-%d"),'mov_est'] = precios_diarios.loc[d.strftime("%Y-%m-%d"),'mov_est']
            precios_intraday.loc[d.strftime("%Y-%m-%d"),'vol_mean'] = precios_diarios.loc[d.strftime("%Y-%m-%d"),'vol_mean']
            precios_intraday.loc[d.strftime("%Y-%m-%d"),'vol_std'] = precios_diarios.loc[d.strftime("%Y-%m-%d"),'vol_std']
        
        for d in precios_diarios.index[-dias_intradiarios:]:
            precios_intraday.loc[d.strftime("%Y-%m-%d"),'vol_cumm'] = precios_intraday.loc[d.strftime("%Y-%m-%d"), 'Volume'].cumsum()
        
        # 8.1 Alternativa con niveles GzScore con el precio de cierre del dia anterior
        precios_intraday['GzScore'] = (precios_intraday['Close'] - precios_intraday['Close_prev'])/(precios_intraday['Close_prev']*precios_intraday['mov_est'])*10
        precios_intraday['Zscore_vol'] = (precios_intraday['vol_cumm'] - precios_intraday['vol_mean'])/(precios_intraday['vol_std'])

        grafico_velas = GAIAGs.graficar_velas_y_niveles(accion , intervalo_dias= visualizar_dias, minutos = velas_en_minutos, data_intradia=precios_intraday, desviaciones = desviaciones, colores = colores)
        GAIAGs.GZScore_signals(precios_intraday, desviacion_long, desviacion_short, desviacion_volumen)
        grafico_signals = GAIAGs.graficar_periodo_signal(accion, intervalo_dias= visualizar_dias, minutos = velas_en_minutos, data_intradia=precios_intraday)

        

    return grafico_velas, grafico_signals

app.layout = layout

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)