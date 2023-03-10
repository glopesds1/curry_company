# ===================== Importações de bibliotecas e do Dataset ====================== #
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

st.set_page_config( page_title='Visão Entregadores', page_icon='🏍', layout='wide')
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

def top_delivers(df, top_asc):
    df2 = (df1.loc[: , ['Time_taken(min)' , 'Delivery_person_ID' , 'City']]
                           .groupby(['City' , 'Delivery_person_ID']).max()
                           .sort_values( [ 'City' , 'Time_taken(min)'], ascending=top_asc )
                           .reset_index())
    dfaux01 = df2.loc[df2['City'] == 'Metropolitian' , :].head(10)
    dfaux02 = df2.loc[df2['City'] == 'Urban' , :].head(10)
    dfaux03 = df2.loc[df2['City'] == 'Semi-Urban' , :].head(10)

    df3 = pd.concat( [ dfaux01 , dfaux02, dfaux03] ).reset_index( drop=True)
            
    return df3
            
#======================================================================================#
#-------------------------Inicio da estrutura lógica do código-------------------------#
#======================================================================================#

#Import Dataset
df_raw = pd.read_csv('dataset/train.csv')


# ====================== Limpeza do Dataset ====================== #
df1 = clean_code(df_raw)

df = df1.copy()


# ====================== Barra Lateral ====================== #

st.header( 'Marketplace - Visão Entregadores' )

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
        st.title( 'Overall Metrics' )
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        
        #A maior idade dos entregadores
        with col1:
            maior_idade = df.loc[: , 'Delivery_person_Age'].max()
            col1.metric( 'Maior idade', maior_idade)
            
        #A menor idade dos entregadores    
        with col2:
            menor_idade = df.loc[: , 'Delivery_person_Age'].min()
            col2.metric( 'Menor idade', menor_idade )
            
        #A melhor condição dos veículos
        with col3:
            melhor_condicao = df.loc[: , 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição' , melhor_condicao )

        #A pior condição dos veículos    
        with col4:
            pior_condicao = df.loc[: , 'Vehicle_condition'].min()
            col4.metric( 'Pior condição' , pior_condicao )
            
    with st.container():
        st.markdown( """---""" )
        st.title( 'Avaliações' )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown( '##### Avaliações médias por entregador' )
            #selecionando linhas
            df_avg_ratings_by_deliver = (df.loc[: , ['Delivery_person_Ratings' , 'Delivery_person_ID']]
                                         .groupby('Delivery_person_ID')
                                         .mean()
                                         .reset_index())
            st.dataframe (df_avg_ratings_by_deliver)
            
        with col2:
            st.markdown( '##### Avaliações médias por trânsito' )

            #selecionando as linhas, agrupando, e fazendo as duas operações 
            df_avg_std_ratings_by_traffic_density =( df.loc[: , ['Delivery_person_Ratings' , 'Road_traffic_density']]
                                        .groupby(['Road_traffic_density'])
                                        .agg( { 'Delivery_person_Ratings' : ['mean' , 'std']} ) )

            #mudança de noma das colunas
            df_avg_std_ratings_by_traffic_density.columns = ['delivery_mean' , 'delivery_std']

            #reset do index
            df_avg_std_ratings_by_traffic_density = df_avg_std_ratings_by_traffic_density.reset_index()

            #mostrando o dataframe
            st.dataframe (df_avg_std_ratings_by_traffic_density)


            st.markdown( '##### Avaliação média por clima' )
            #selecionando as linhas, agrupando, e fazendo as duas operações
            df_avg_std_ratings_by_weathercondition =( df.loc[: , ['Delivery_person_Ratings' , 'Weatherconditions']]
                                        .groupby(['Weatherconditions'])
                                        .agg( { 'Delivery_person_Ratings' : ['mean' , 'std']} ) )

            #mudança de noma das colunas
            df_avg_std_ratings_by_weathercondition.columns = ['delivery_mean' , 'delivery_std']

            #reset do index
            df_avg_std_ratings_by_weathercondition = df_avg_std_ratings_by_weathercondition.reset_index()

            #mostrando o dataframe
            st.dataframe (df_avg_std_ratings_by_weathercondition)
            
    with st.container():
        st.markdown( """---""" )
        st.title( 'Velocidade de entrega' )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown( '##### Top entregadores mais rápidos' )
            df3 = top_delivers(df, top_asc=True)
            st.dataframe(df3) 
            
        with col2:
            st.markdown( '##### Top entregadores mais lentos' )
            df3 = top_delivers(df, top_asc=False)
            st.dataframe(df3)
            
            
            
# ====================== Fim do Layout da Página ====================== #