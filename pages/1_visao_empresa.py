# ====================== Importações de bibliotecas e do Dataset ===================== #
#Libraries
from haversine import haversine
import plotly.graph_objects as go
import plotly.express as px

#Bibliotecas necessarias
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide')

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


def order_metric(df):
    cols = ['ID' , 'Order_Date']
    dfaux = df.loc[: , cols].groupby("Order_Date").count().reset_index()
    fig = px.bar( dfaux, x='Order_Date', y='ID' )
    return fig


def traffic_order_share(df):
    dfaux2 = (df.loc[: , ['ID' , 'Road_traffic_density']]
              .groupby('Road_traffic_density')
              .count()
              .reset_index())
    dfaux2 = dfaux2.loc[dfaux2['Road_traffic_density'] != 'NaN', :]
    dfaux2['Entregas_perc'] = dfaux2['ID'] / dfaux2['ID'].sum()
    fig = px.pie(dfaux2 , values='Entregas_perc' , names='Road_traffic_density')
    return fig
        
    
def traffic_order_city(df):
    dfaux3 = (df.loc[ : , ['ID' , 'City' , 'Road_traffic_density']]
              .groupby(['City' , 'Road_traffic_density'])
              .count()
              .reset_index())
    fig = px.scatter(dfaux3 , x='City' , y='Road_traffic_density' , size='ID', color='City')
    return fig


def order_by_week(df):
    df['week_of_year'] = df['Order_Date'].dt.strftime( '%U' )
    dfaux = (df.loc[: , ['ID' , 'week_of_year']]
             .groupby('week_of_year')
             .count()
             .reset_index())
    
    fig = px.line( dfaux , x = 'week_of_year' , y = 'ID')
    
    return fig


def order_share_by_week(df):
    dfaux1 = (df.loc[: , ['ID' , 'week_of_year']]
                  .groupby('week_of_year')
                  .count()
                  .reset_index())
    dfaux2 = (df.loc[: , ['Delivery_person_ID' , 'week_of_year']]
                  .groupby('week_of_year')
                  .nunique()
                  .reset_index())
        
    dfaux = pd.merge(dfaux1 , dfaux2 , how='inner')
    dfaux['order_by_deliver'] = dfaux['ID'] / dfaux['Delivery_person_ID']
    fig = px.line(dfaux , x='week_of_year' , y='order_by_deliver')
    return fig


def country_maps(df):
    dfaux = (df.loc[: , ['City' , 'Road_traffic_density' , 'Delivery_location_latitude' , 'Delivery_location_longitude']]
             .groupby( [ 'City' , 'Road_traffic_density'])
             .median()
             .reset_index())

    dfaux = dfaux.loc[dfaux['City'] != 'NaN' , :]
    dfaux = dfaux.loc[dfaux['Road_traffic_density'] != 'NaN' , :]

    map = folium.Map()

    for index , location_info in dfaux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], 
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City' , 'Road_traffic_density']]).add_to(map)

    folium_static( map, width= 1024, height=600)
#======================================================================================#
#-------------------------Inicio da estrutura lógica do código-------------------------#
#======================================================================================#

#Import Dataset
df_raw = pd.read_csv('dataset/train.csv')

#Limpando os dados
df1 = clean_code(df_raw)

df = df1.copy()

# ====================== Barra Lateral ====================== #

st.header( 'Marketplace - Visão Cliente' )

#image_path = '/Users/gabri/Documents/repos/Python_ Da_Logica_a_Analise/logo.png'
image = Image.open ( 'logo.png' )
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

st.sidebar.markdown( '### Powered by Comunidade DS' )

#filtro de data
linhas_selecionadas = df['Order_Date'] < data_slider
df = df.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas, :]
             

# ====================== Fim da Barra Lateral ====================== #


# ====================== Layout da Página ====================== #

tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial' , 'Visão Prática' , 'Visão Geográfica' ] )

with tab1:
    with st.container():
        fig = order_metric(df)
        st.markdown('# Orders by Day')
        st.plotly_chart( fig , use_container_width = True )
        
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = traffic_order_share(df)
            st.header('Traffic Order Share')
            st.plotly_chart(fig , use_container_width = True)
           
        with col2:
            fig = traffic_order_city(df)
            st.header('Traffic Order City')
            st.plotly_chart(fig, use_container_width = True)
            
            
with tab2:
    with st.container():
        st.markdown( '# Order by week' )
        fig=order_by_week(df)
        st.plotly_chart( fig, use_container_width = True)
        
    with st.container():
        st.markdown( '# Order Share by week' )
        fig = order_share_by_week(df)
        st.plotly_chart(fig, use_container_width = True)

with tab3:
    st.markdown( '# Country maps' )
    country_maps(df)
    
# ====================== Fim do Layout da Página ====================== #

