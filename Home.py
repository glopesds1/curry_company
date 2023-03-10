import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home',page_icon='🐷',layout='wide')

#image_path='C:/Users/gabri/Documents/repos/Python_ Da_Logica_a_Analise/'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest delivery in town' )
st.sidebar.markdown( """---""" )

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes. 
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: métricas gerais de comportamento.
        - Visão Tática: indicadores semanais de crescimento.
        - Visão Geográfica: insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for help
    - Time de Data Science no Discord
        - @Gabriel
    """
)