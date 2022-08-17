import pandas as pd
import numpy as np
from datetime import datetime, timedelta

#Calculo de Niveles retornos algebraicos
def niveles(data_d, ventana_estadisticas=20,Nivel_Desviacion_1=1.316, Nivel_Desviacion_2=2.129, Nivel_Desviacion_3 = 3.444):
  df_D = data_d.copy()
  df_D['Retornos_close'] = df_D['Close'].pct_change()
  df_D['volatilidad_Retornos'] = df_D['Retornos_close'].rolling(window = ventana_estadisticas).std()*100
  
  df_D['Mov_est_dia'] =  df_D['volatilidad_Retornos'] /np.sqrt(252)

  df_D['data_GZScore_dia'] = (df_D['Close'].shift(1) - df_D['Open'].shift(1) )/(df_D['Open'].shift(1)*df_D['Mov_est_dia'] )
  df_D['media_GZScore_dia'] = df_D['data_GZScore_dia'].rolling(window = ventana_estadisticas).mean()*100
  df_D['std_GZScore_dia'] = df_D['data_GZScore_dia'].rolling(window = ventana_estadisticas).std()*100

  df_D['L1+'] = df_D['Open'] + df_D['Open'].shift(1)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] + df_D['std_GZScore_dia']* Nivel_Desviacion_1)/100)
  df_D['L1-'] = df_D['Open'] + df_D['Open'].shift(1)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] - df_D['std_GZScore_dia']* Nivel_Desviacion_1)/100)

  df_D['L2+'] = df_D['Open'] + df_D['Open'].shift(1)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] + df_D['std_GZScore_dia']* Nivel_Desviacion_2)/100)
  df_D['L2-'] = df_D['Open'] + df_D['Open'].shift(1)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] - df_D['std_GZScore_dia']* Nivel_Desviacion_2)/100)

  df_D['L3+'] = df_D['Open'] + df_D['Open'].shift(1)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] + df_D['std_GZScore_dia']* Nivel_Desviacion_3)/100)
  df_D['L3-'] = df_D['Open'] + df_D['Open'].shift(1)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] - df_D['std_GZScore_dia']* Nivel_Desviacion_3)/100)

  data_d[['L1+', 'L1-','L2+', 'L2-','L3+', 'L3-']]= df_D[['L1+', 'L1-','L2+', 'L2-','L3+', 'L3-']]
  return data_d

#Calculo de Niveles retornos logaritmicos #Nivel_Desviacion_1=1.316, Nivel_Desviacion_2=2.129, Nivel_Desviacion_3 = 3.444
def niveles_log(data_d, ventana_estadisticas=20, Niveles_Desviaciones=[1,2,3]):
  df_D = data_d.copy()
  df_D['Retornos_close'] = np.log(df_D['Close'].shift(1)/df_D['Close'].shift(2))
  df_D['volatilidad_Retornos'] = df_D['Retornos_close'].rolling(window = ventana_estadisticas).std()*100
  
  df_D['Mov_est_dia'] =  df_D['volatilidad_Retornos'] /np.sqrt(252)

  df_D['data_GZScore_dia'] = (df_D['Close'].shift(1) - df_D['Open'].shift(1) )/(df_D['Open'].shift(1)*df_D['Mov_est_dia'] )

  df_D['media_GZScore_dia'] = df_D['data_GZScore_dia'].rolling(window = ventana_estadisticas).mean()*100
  df_D['std_GZScore_dia'] = df_D['data_GZScore_dia'].rolling(window = ventana_estadisticas).std()*100

  for d in Niveles_Desviaciones:
    df_D['+'+str(d)] = df_D['Open'] + df_D['Open'].shift(1)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] + df_D['std_GZScore_dia']* d)/100)
    df_D['-'+str(d)] = df_D['Open'] + df_D['Open'].shift(1)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] - df_D['std_GZScore_dia']* d)/100)
    data_d[['+'+str(d), '-'+str(d)]] = df_D[['+'+str(d), '-'+str(d)]]
  
  data_d['mov_est']=df_D['Mov_est_dia']
  data_d['vol_mean'] = data_d['Volume'].rolling(window = ventana_estadisticas).mean()
  data_d['vol_std'] = data_d['Volume'].rolling(window = ventana_estadisticas).std()

  return data_d

# Niveles GZScore desde Close anterior, (Tiene en cuenta los GAPs)
def niveles_log_gap(data_d, ventana_estadisticas=20, Niveles_Desviaciones=[1,2,3]):
  df_D = data_d.copy()
  df_D['Retornos_close'] = np.log(df_D['Close'].shift(1)/df_D['Close'].shift(2))
  df_D['volatilidad_Retornos'] = df_D['Retornos_close'].rolling(window = ventana_estadisticas).std()*100
  
  df_D['Mov_est_dia'] =  df_D['volatilidad_Retornos'] /np.sqrt(252)

  df_D['data_GZScore_dia'] = (df_D['Close'].shift(1) - df_D['Close'].shift(2) )/(df_D['Close'].shift(2)*df_D['Mov_est_dia'] )

  df_D['media_GZScore_dia'] = df_D['data_GZScore_dia'].rolling(window = ventana_estadisticas).mean()*100
  df_D['std_GZScore_dia'] = df_D['data_GZScore_dia'].rolling(window = ventana_estadisticas).std()*100

  for d in Niveles_Desviaciones:
    df_D['+'+str(d)] = df_D['Close'].shift(1) + df_D['Close'].shift(2)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] + df_D['std_GZScore_dia']* d)/100)
    df_D['-'+str(d)] = df_D['Close'].shift(1) + df_D['Close'].shift(2)* (df_D['Mov_est_dia']*(df_D['media_GZScore_dia'] - df_D['std_GZScore_dia']* d)/100)
    data_d[['+'+str(d), '-'+str(d)]] = df_D[['+'+str(d), '-'+str(d)]]
  
  data_d['mov_est']=df_D['Mov_est_dia']
  data_d['vol_mean'] = data_d['Volume'].rolling(window = ventana_estadisticas).mean()
  data_d['vol_std'] = data_d['Volume'].rolling(window = ventana_estadisticas).std()

  return data_d


def graficar_velas_y_niveles(accion, intervalo_dias, minutos, data_intradia, desviaciones, colores ):
    ## Esta en Desarrollo
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    velas_intradiarias = int(390/minutos)

    df = data_intradia[-velas_intradiarias * intervalo_dias: ]
    
    fig = make_subplots(specs=[[{"secondary_y": False}],[{"secondary_y": False}],[{"secondary_y": True}]],rows=3, cols=1, shared_xaxes=True, 
               vertical_spacing=0.03, subplot_titles=('Precio', 'GZscore_precio', 'Zscore_volumen'), 
               row_width=[0.15, 0.15, 0.7])
    #Velas Japonesas
    fig.add_trace(go.Candlestick(x=df.index,
                                            open=df.Open,
                                            high=df.High,
                                            low=df.Low,
                                            close=df.Close), row=1, col=1)
    cl=0
    for i in desviaciones:
        fig.add_trace(go.Scatter(x=df.index, y=df['+'+str(i)+'Std'],
                            mode='lines',
                            name='+'+str(i)+'Std',line=dict(color=colores[cl])))
        fig.add_trace(go.Scatter(x=df.index, y=df['-'+str(i)+'Std'],
                            mode='lines',
                            name='-'+str(i)+'Std',line=dict(color=colores[cl])))

        cl=cl+1

    fig.update_layout(
            title=('Precios Intradiarios de '+ accion +" Velas de "+str(minutos)+"m"),
            yaxis_title= 'precio del activo'
            )

    fig.add_trace(go.Scatter(x=df.index, y=df['GzScore'], line=dict(color='black')), row=2, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['Zscore_vol'], line=dict(color='blue')), row=3, col=1, secondary_y=True)
    fig.add_trace(go.Bar(x=df.index, y=df['vol_cumm']), row=3, col=1, secondary_y=False )
    
    #Ocultar Barra de rango
    fig.update_layout(xaxis_rangeslider_visible=False)

    #Ocultar horas fuera de mercado
    fig.update_xaxes(
    rangebreaks=[
        dict(bounds=["sat", "mon"]), #Ocultar Fines de semana
        dict(bounds=[15.98, 9.5], pattern="hour")
    ]
    )

    #Mostrar grafico
    return fig

def GZScore_signals(precios_intraday, desviacion_long, desviacion_short, desviacion_volumen):
    precios_intraday['signal_long'] = np.where((precios_intraday['GzScore'] <= desviacion_long) & (precios_intraday['Zscore_vol']<=desviacion_volumen), -1, 0)
    precios_intraday['signal_short'] = np.where((precios_intraday['GzScore'] >= desviacion_short) & (precios_intraday['Zscore_vol']<=desviacion_volumen), 1, 0)
    return precios_intraday

def graficar_periodo_signal(accion, intervalo_dias, minutos , data_intradia):

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots


    velas_intradiarias = int(390/minutos)
    df = data_intradia[-velas_intradiarias * intervalo_dias: ]

    velas_japonesas = go.Candlestick(   x  = df.index,
                                    open  = df.Open,
                                    high  = df.High,
                                    low   = df.Low,
                                    close = df.Close)

    linea_long = go.Scatter(x=df.index, y=df.signal_long,
                                mode='lines',
                                name='Señal Long',line=dict(color='green'),fill='tozeroy')

    linea_short = go.Scatter(x=df.index, y=df.signal_short,
                                mode='lines',
                                name='Señal Short',line=dict(color='red'), fill='tozeroy')

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig= go.Figure(data=[velas_japonesas])

    fig.add_trace(velas_japonesas, secondary_y=False )
    fig.add_trace(linea_long, secondary_y=True)
    fig.add_trace(linea_short, secondary_y=True)

    #Ocultar Barra de rango
    fig.update_layout(xaxis_rangeslider_visible=False)

    #Adicionar titulo
    fig.update_layout(
        title='Periodos Long o Short en la acción ' +str(accion)
    )

    #Adicionar texto eje x
    fig.update_xaxes(title_text="Fecha y hora")

    #Adicionar texto a ejes y
    fig.update_yaxes(title_text="<b>Precio</b> USD", secondary_y=False)
    fig.update_yaxes(title_text="Señal <b>long/short</b>", secondary_y=True)

    #Ocultar horas fuera de mercado
    fig.update_xaxes(
    rangebreaks=[
        dict(bounds=["sat", "mon"]), #Ocultar Fines de semana
        dict(bounds=[15.97, 9.5], pattern="hour")
    ]
    )

    return fig

def obtener_max_drawdown(df_drawdown):
    fecha_valle = df_drawdown.drawdown.idxmin()
    precio_valle = df_drawdown.loc[fecha_valle].Close

    # Listar todos los puntos B- antes del gran bajo
    # nos quedamos con el ultimo dato que corresponde
    # al pico desde donde inicio la gran caida
    fecha_pivote_b  = df_drawdown[:fecha_valle][df_drawdown.drawdown[:fecha_valle] == 0].index[-1]
    precio_pivote_b = df_drawdown.loc[df_drawdown[:fecha_valle][df_drawdown.drawdown[:fecha_valle] == 0].index[-1]].Close

    #duracion_caida = fecha_valle - fecha_pivote_b
    duracion_caida = len(pd.date_range(fecha_pivote_b, fecha_valle, freq='D'))

    porcentaje_drawdown_max = df_drawdown.drawdown.min()
    valor_drawdown_max_usd = precio_valle - precio_pivote_b    


    # Listar los puntos B+ luego del gran bajo
    # Nos quedamos con el primer dato que corresponde 
    # al punto de recuperación
    try:
        fecha_pivote_r  = df_drawdown[fecha_valle:][df_drawdown.drawdown[fecha_valle:] == 0].index[0]
        precio_pivote_r = df_drawdown.loc[df_drawdown[fecha_valle:][df_drawdown.drawdown[fecha_valle:] == 0].index[0]].Close
        duración_recuperacion = len(pd.date_range(fecha_valle, fecha_pivote_r, freq='D'))
    
    except IndexError:
        fecha_pivote_r = np.nan
        precio_pivote_r = np.nan
        duración_recuperacion = np.nan

    return porcentaje_drawdown_max, precio_pivote_b, precio_valle, valor_drawdown_max_usd, fecha_pivote_b, fecha_valle, duracion_caida, fecha_pivote_r, duración_recuperacion

def obtener_top_drawdowns(df_drawdown, top=10):
    copia_precios = df_drawdown.copy()

    top_drawdowns = []
    for _ in range(top):
        porcentaje_drawdown_max,precio_pivote_b,precio_valle,valor_drawdown_max_usd,fecha_pivote_b,fecha_valle,duracion_caida,fecha_pivote_r,duración_recuperacion = obtener_max_drawdown(copia_precios)

        if not pd.isnull(fecha_pivote_r):
            copia_precios.drop(copia_precios[fecha_pivote_b:fecha_pivote_r].index[1:-1], inplace =True)
        else:
            copia_precios = copia_precios.loc[:fecha_pivote_b]

        top_drawdowns.append((porcentaje_drawdown_max,
        precio_pivote_b,
        precio_valle,
        valor_drawdown_max_usd,
        fecha_pivote_b,
        fecha_valle,
        duracion_caida,
        fecha_pivote_r,
        duración_recuperacion))
        if (len(copia_precios) == 0) or (len(copia_precios) == 0) or (np.min(copia_precios.drawdown) == 0):
            break

    return top_drawdowns

def generar_tabla_drawdowns(df_drawdown, top=10):
    info_pivotes = obtener_top_drawdowns(df_drawdown, top=top)
    tabla_drawdowns = pd.DataFrame(index=list(range(top)), 
                                    columns=['Máximo drawdown %',
                                             '$Antes de caida',
                                             '$Del Bajo(punto_C)',
                                             '$De Caida en USD',
                                             'Fecha inicio caida',
                                             'Fecha fin caida',
                                             'Duración Caida',
                                             'Fecha recuperación',
                                             'Duración recuperación',
                                             'Duracion Total'])
    for i, (porcentaje_drawdown_max,precio_pivote_b,precio_valle,valor_drawdown_max_usd,fecha_pivote_b,fecha_valle,duracion_caida,fecha_pivote_r,duración_recuperacion) in enumerate(info_pivotes):
        if pd.isnull(fecha_pivote_r):
            tabla_drawdowns.loc[i, 'Duracion Total'] = len(pd.date_range(fecha_pivote_b,
                                                                pd.Timestamp.today().date(),
                                                                freq='D'))
        else:
            tabla_drawdowns.loc[i, 'Duracion Total'] = len(pd.date_range(fecha_pivote_b,
                                                                fecha_pivote_r,
                                                                freq='D'))
        tabla_drawdowns.loc[i, 'Fecha inicio caida'] = (fecha_pivote_b.to_pydatetime()
                                            .strftime('%Y-%m-%d'))
        tabla_drawdowns.loc[i, 'Fecha fin caida'] = (fecha_valle.to_pydatetime()
                                              .strftime('%Y-%m-%d'))
        if isinstance(fecha_pivote_b, float):
            tabla_drawdowns.loc[i, 'Fecha recuperación'] = fecha_pivote_r
        else:
            tabla_drawdowns.loc[i, 'Fecha recuperación'] = (fecha_pivote_r)
        tabla_drawdowns.loc[i, 'Máximo drawdown %'] = round(porcentaje_drawdown_max,2)
        tabla_drawdowns.loc[i, '$Antes de caida'] = round(precio_pivote_b,2)
        tabla_drawdowns.loc[i, '$Del Bajo(punto_C)'] = round(precio_valle,2)
        tabla_drawdowns.loc[i, '$De Caida en USD'] = round(valor_drawdown_max_usd,2)
        tabla_drawdowns.loc[i,'Duración Caida'] = duracion_caida
        tabla_drawdowns.loc[i,'Duración recuperación'] = duración_recuperacion


    tabla_drawdowns['Fecha inicio caida'] = \
        pd.to_datetime(tabla_drawdowns['Fecha inicio caida']).dt.strftime('%Y-%m-%d')
    tabla_drawdowns['Fecha fin caida'] = \
        pd.to_datetime(tabla_drawdowns['Fecha fin caida']).dt.strftime('%Y-%m-%d')
    tabla_drawdowns['Fecha recuperación'] = \
        pd.to_datetime(tabla_drawdowns['Fecha recuperación']).dt.strftime('%Y-%m-%d')
    
    

    return tabla_drawdowns

