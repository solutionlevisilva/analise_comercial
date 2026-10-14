import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Relatório de Análise Comercial",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.header("Menu")
    
    # Drag and drop de arquivo Excel
    uploaded_file = st.file_uploader(
        "Arraste e solte seu arquivo Excel aqui",
        type=['xlsx', 'xls'],
        help="Formatos aceitos: .xlsx, .xls"
    )

# Título principal
st.title("Relatório de análise comercial")
