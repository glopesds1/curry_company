# ===================== Importações de bibliotecas e do Dataset ====================== #
#Libraries
from haversine import haversine
import plotly.graph_objects as go
import plotly.express as px

#Bibliotecas necessarias
import pandas as pd
import streamlit as st
import numpy as np
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍛', layout='wide')

#======================================================================================#
#Funções
#======================================================================================#
def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1- remoção de NaN
        2- mudança do tipo da coluna
        3- remoção dos espaços das variaveis de texto
        4- formatação da coluna de data
        5- limpeza da coluna de tempo (remoção do texto da variavel numerica)
    
        Input: Dataframe
        Output: Dataframe
    """
    
    #Removendo espacos de dentro dos textos
    df1.loc[: , 'ID'] = df1.loc[: , 'ID'].str.strip()
    df1.loc[: , 'Delivery_person_ID'] = df1.loc[: , 'Delivery_person_ID'].str.strip()
    df1.loc[: , 'Road_traffic_density'] = df1.loc[: , 'Road_traffic_density'].str.strip()
    df1.loc[: , 'Type_of_order'] = df1.loc[: , 'Type_of_order'].str.strip()
    df1.loc[: , 'Type_of_vehicle'] = df1.loc[: , 'Type_of_vehicle'].str.strip()
    df1.loc[: , 'Festival'] = df1.loc[: , 'Festival'].str.strip()
    df1.loc[: , 'City'] = df1.loc[: , 'City'].str.strip()

    #Convertendo e limpando coluna Delivery_person_Age
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas , :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #Convertendo a coluna Delivery_person_Ratings
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float ) 

    #Convertendo e limpando coluna multiple_deliveries
    linhas_selecionadas2 = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas2 , :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    #Limpando coluna Road Traffic Density
    linhas_selecionadas3 = (df1['Road_traffic_density'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas3 , :].copy()
    
    #Limpando coluna City
    linhas_selecionadas3 = (df1['City'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas3 , :].copy()

    #Convertendo a coluna Order_Date
    df1[ 'Order_Date' ] =  pd.to_datetime( df1['Order_Date'], format= '%d-%m-%Y')

    #Resetando index
    df1 = df1.reset_index( drop=True )

    #Limpando a coluna de time taken
    df1.loc[: , 'Time_taken(min)'] = df1.loc[: , 'Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1])
    df1.loc[: , 'Time_taken(min)'] = df1.loc[: , 'Time_taken(min)'].astype( int )
    return df1

def distance(df, fig):
    if fig==False:
        cols = ['Delivery_location_latitude' , 'Delivery_location_longitude' , 'Restaurant_latitude' , 'Restaurant_longitude']
        df['distance'] = (df.loc[:, cols].apply( lambda x: haversine( 
                      (x['Restaurant_latitude'],
                       x['Restaurant_longitude']),
                      (x['Delivery_location_latitude'],
                       x['Delivery_location_longitude']) ), axis=1))
        avg_distance = np.round( df['distance'].mean() , 2)

        return avg_distance
    
    else:
        cols = ['Delivery_location_latitude' , 'Delivery_location_longitude' , 'Restaurant_latitude' , 'Restaurant_longitude']
        df['distance'] = (df.loc[:, cols].apply( lambda x: haversine( 
                  (x['Restaurant_latitude'],
                   x['Restaurant_longitude']),
                  (x['Delivery_location_latitude'],
                   x['Delivery_location_longitude'])), axis=1))
        avg_distance = df.loc[: , ['City', 'distance']].groupby( 'City' ).mean().reset_index()
        fig = go.Figure( data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1 , 0])])
        return fig

def avg_std_time_delivery(df, festival, op):
    """
        Esta função calcula o tempo medio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input: 
                - df: Dataframe com os dados necessários.
                - op: Tipo de operação que precisa ser calculado.
                    'avg_time': tempo médio
                    'std_time': desvio padrao
            Output:
                - df: Dataframe com 2 colunas e 1 linha.
    """
    
    dfaux =( df.loc[:, ['Time_taken(min)' , 'Festival']]
                                .groupby('Festival')
                                .agg ( {'Time_taken(min)' : ['mean', 'std' ] } ) )
    dfaux.columns = ['avg_time', 'std_time']
    dfaux = dfaux.reset_index()
    dfaux = np.round(dfaux.loc[dfaux['Festival'] == festival , op], 2)
    return dfaux

def avg_std_time_graph(df):
    dfaux = (df.loc[: ,['City', 'Time_taken(min)']]
                     .groupby('City')
                     .agg( {'Time_taken(min)' : ['mean' , 'std'] } ))
    dfaux.columns = ['avg_time' , 'std_time']
    dfaux = dfaux.reset_index()
    
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=dfaux['City'], y=dfaux['avg_time'], error_y= dict(type='data', array=dfaux['std_time'])))
    fig.update_layout(barmode='group')
                
    return fig

def avg_std_time_on_traffic(df):
    dfaux = df.loc[: , ['City', 'Time_taken(min)' , 'Road_traffic_density' ,]].groupby(['City', 'Road_traffic_density']).agg ( {'Time_taken(min)' : ['mean' , 'std']})
    dfaux.columns = ['avg_time' , 'std_time']
    dfaux = dfaux.reset_index()
            
    fig = px.sunburst(dfaux, path=['City', 'Road_traffic_density'], values= 'avg_time', color= 'std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(dfaux['std_time']))
                
    return fig

#======================================================================================#
#-------------------------Inicio da estrutura lógica do código-------------------------#
#======================================================================================#

#Import Dataset
df_raw = pd.read_csv('dataset/train.csv')

# ====================== Limpeza do Dataset ====================== #
df1 = df_raw.copy()

df1 = clean_code(df1)

df = df1.copy()


# ====================== Barra Lateral ====================== #

st.header( 'Marketplace - Visão Restaurantes' )

#image_path = '/Users/gabri/Documents/repos/Python_ Da_Logica_a_Analise/logo.png'
image = Image.open ('logo.png')
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest delivery in town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4 , 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY' )

st.header( data_slider )
st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?', 
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] )
st.sidebar.markdown( """---""" )

weather_conditions = st.sidebar.multiselect(
    'Quais as condições do climáticas?', 
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy' , 'conditions Sunny' , 'conditions Windy'], 
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy' , 'conditions Sunny' , 'conditions Windy'] )
st.sidebar.markdown( """---""" )


st.sidebar.markdown( '### Powered by Comunidade DS' )

#filtro de data
linhas_selecionadas1 = df['Order_Date'] < data_slider
df = df.loc[linhas_selecionadas1, :]

#filtro de transito
linhas_selecionadas2 = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas2, :]

#filtro de climas
linhas_selecionadas3 = df['Weatherconditions'].isin( weather_conditions )
df = df.loc[linhas_selecionadas3, :]


# ====================== Fim da Barra Lateral ====================== #


# ====================== Layout da Página ====================== #

tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial' , '' , '' ] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        
        with col1:
            delivery_unique = len( df.loc[: , 'Delivery_person_ID'].unique())
            col1.metric ('Entregadores' , delivery_unique)
            
        with col2:
            avg_distance = distance(df, fig=False)
            col2.metric('Distancia media', avg_distance)
            
        with col3:
            dfaux = avg_std_time_delivery( df1 , 'Yes', 'avg_time')
            col3.metric('AVG c/festival', dfaux)
            
        with col4:
            dfaux = avg_std_time_delivery( df1 , 'Yes', 'std_time')
            col4.metric('STD c/festival', dfaux)
            
            
        with col5:
            dfaux = avg_std_time_delivery( df1 , 'No', 'avg_time')
            col5.metric('AVG s/festival', dfaux)
            
        with col6:
            dfaux = avg_std_time_delivery( df1 , 'No', 'std_time')
            col6.metric('STD s/festival', dfaux)
    
    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graph(df)
            st.plotly_chart(fig)
            
        with col2:
            dfaux = (df.loc[: , ['Time_taken(min)' , 'City' , 'Type_of_order']]
                                      .groupby(['City' , 'Type_of_order'])
                                      .agg ( {'Time_taken(min)' : ['mean' , 'std']}))
            dfaux.columns = ['Time_taken_mean' , 'Time_taken_std']
            dfaux = dfaux.reset_index()
        
            st.dataframe(dfaux, use_container_width=True)
            
    
    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2)
        with col1:
            fig = distance(df, fig=True)
            st.plotly_chart(fig)
        
        with col2:
            fig = avg_std_time_on_traffic(df)
            st.plotly_chart(fig)
        