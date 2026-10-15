import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.metricas import calcular_metricas, formatar_metricas

# Configuração da página
st.set_page_config(
    page_title="Relatório de Análise Comercial",
    layout="wide"
)

# Inicializar session state
if 'df_original' not in st.session_state:
    st.session_state.df_original = None
if 'df_limpo' not in st.session_state:
    st.session_state.df_limpo = None
if 'metricas' not in st.session_state:
    st.session_state.metricas = None
if 'periodo_filtro' not in st.session_state:
    st.session_state.periodo_filtro = None
if 'nome_periodo' not in st.session_state:
    st.session_state.nome_periodo = "Todos os meses"

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
st.title("📊 Relatório de Análise Comercial")

# ==================== PROCESSAMENTO DOS DADOS ====================
if uploaded_file is not None:
    try:
        # Carregar dados direto com pandas
        with st.spinner("⏳ Carregando dados..."):
            df = pd.read_excel(uploaded_file)
            st.session_state.df_original = df
            st.success(f"✅ {len(df)} linhas carregadas!")
        
        # Limpar dados automaticamente
        with st.spinner("🧹 Limpando dados..."):
            # Contadores
            linhas_originais = len(df)
            
            # Remover linhas completamente vazias
            df_limpo = df.dropna(how='all')
            vazias_removidas = linhas_originais - len(df_limpo)
            
            # Remover duplicatas
            linhas_antes_dup = len(df_limpo)
            df_limpo = df_limpo.drop_duplicates()
            duplicatas_removidas = linhas_antes_dup - len(df_limpo)
            
            # Armazenar dados limpos
            st.session_state.df_limpo = df_limpo
            
            # Log
            total_removido = linhas_originais - len(df_limpo)
            if total_removido > 0:
                st.success(f"✅ Limpeza concluída! {total_removido} linhas removidas ({vazias_removidas} vazias + {duplicatas_removidas} duplicatas)")
        
        # Calcular métricas
        with st.spinner("📊 Calculando métricas..."):
            metricas = calcular_metricas(df_limpo)
            st.session_state.metricas = metricas
            st.session_state.metricas_sem_filtro = metricas  # Backup das métricas totais
    
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")

# ==================== SIDEBAR - FILTROS ====================
# Renderizar filtros no sidebar após carregar dados
with st.sidebar:
    if st.session_state.df_limpo is not None:
        st.markdown("---")
        st.subheader("🔍 Filtros")
        
        from src.metricas import extrair_meses_disponiveis
        
        # Extrair meses disponíveis
        meses_disponiveis = extrair_meses_disponiveis(st.session_state.df_limpo)
        
        if meses_disponiveis:
            # Criar opções para o selectbox
            opcoes = [("Todos os meses", None)] + meses_disponiveis
            nomes_opcoes = [nome for nome, _ in opcoes]
            
            # Selectbox de filtro
            selecao_nome = st.selectbox(
                "📅 Filtrar por Período",
                options=nomes_opcoes,
                index=0,
                key="filtro_periodo"
            )
            
            # Encontrar o período correspondente
            periodo_selecionado = None
            for nome, periodo in opcoes:
                if nome == selecao_nome:
                    periodo_selecionado = periodo
                    break
            
            # Armazenar no session_state
            st.session_state.periodo_filtro = periodo_selecionado
            st.session_state.nome_periodo = selecao_nome

# ==================== APLICAR FILTROS ====================
df_exibicao = st.session_state.df_limpo
metricas_exibicao = st.session_state.metricas

if st.session_state.df_limpo is not None and st.session_state.periodo_filtro is not None:
    from src.metricas import filtrar_por_mes
    
    # Aplicar filtro
    df_exibicao = filtrar_por_mes(st.session_state.df_limpo, st.session_state.periodo_filtro)
    
    # Recalcular métricas com dados filtrados
    if len(df_exibicao) > 0:
        metricas_exibicao = calcular_metricas(df_exibicao)
    else:
        metricas_exibicao = {
            'total_processos': 0, 
            'receita': 0.0,
            'total_pago': 0.0,
            'total_faturado': 0.0
        }
        st.warning(f"⚠️ Nenhum processo encontrado para {st.session_state.nome_periodo}")

# ==================== EXIBIÇÃO DAS MÉTRICAS ====================
if metricas_exibicao is not None:
    st.markdown("---")
    st.subheader("📈 Métricas Principais")
    
    # Mostrar indicador de filtro ativo
    if st.session_state.periodo_filtro is not None:
        st.info(f"📅 Exibindo dados de: **{st.session_state.nome_periodo}**")
    
    # Formatar métricas
    metricas_formatadas = formatar_metricas(metricas_exibicao)
    
    # Criar cards de métricas (4 colunas)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔢 Total de Processos",
            value=metricas_formatadas['total_processos'],
            help="Total de processos no relatório após limpeza"
        )
    
    with col2:
        st.metric(
            label="💰 Receita Total",
            value=metricas_formatadas['receita'],
            help="Soma do valor dos processos pagos/faturados"
        )
    
    with col3:
        st.metric(
            label="💵 Total Pago",
            value=metricas_formatadas['total_pago'],
            help="Soma dos valores com status PAGO"
        )
    
    with col4:
        st.metric(
            label="🧾 Total Faturado",
            value=metricas_formatadas['total_faturado'],
            help="Soma dos valores com status FATURADO"
        )
    
    # ==================== GRÁFICO DE EVOLUÇÃO ====================
    st.markdown("---")
    st.subheader("📈 Evolução dos Processos")
    
    from src.metricas import processar_evolucao_mensal, processar_evolucao_semanal
    
    # Decidir qual tipo de gráfico exibir baseado no filtro
    if st.session_state.periodo_filtro is None:
        # SEM FILTRO: Mostrar evolução mensal
        with st.spinner("📊 Gerando gráfico mensal..."):
            df_evolucao = processar_evolucao_mensal(df_exibicao)
        
        if not df_evolucao.empty:
            # Criar gráfico mensal
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df_evolucao['mes_nome'],
                y=df_evolucao['quantidade'],
                text=df_evolucao['quantidade'],
                textposition='outside',
                marker_color='#1f77b4',
                name='Processos por Mês'
            ))
            
            # Configurar layout
            fig.update_layout(
                title="Quantidade de Processos por Mês",
                xaxis_title="Mês",
                yaxis_title="Quantidade de Processos",
                height=450,
                showlegend=False,
                hovermode='x'
            )
            
            # Exibir gráfico
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Não foi possível gerar o gráfico de evolução.")
    
    else:
        # COM FILTRO: Mostrar evolução semanal do mês selecionado
        with st.spinner("📊 Gerando gráfico semanal..."):
            df_evolucao = processar_evolucao_semanal(df_exibicao)
        
        if not df_evolucao.empty:
            # Filtrar apenas o mês selecionado
            dados_mes = df_evolucao[df_evolucao['mes_ano'] == st.session_state.periodo_filtro]
            
            if not dados_mes.empty:
                # Criar gráfico semanal
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=[f"Semana {s}" for s in dados_mes['semana']],
                    y=dados_mes['quantidade'],
                    text=dados_mes['quantidade'],
                    textposition='outside',
                    marker_color='#1f77b4',
                    name=f'Semanas de {st.session_state.nome_periodo}'
                ))
                
                # Configurar layout
                fig.update_layout(
                    title=f"Semanas de {st.session_state.nome_periodo}",
                    xaxis_title="Semanas do Mês",
                    yaxis_title="Quantidade de Processos",
                    height=450,
                    showlegend=False,
                    hovermode='x'
                )
                
                # Exibir gráfico
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"⚠️ Nenhum dado encontrado para {st.session_state.nome_periodo}")
        else:
            st.warning("⚠️ Não foi possível gerar o gráfico de evolução.")

elif uploaded_file is None:
    # Instruções quando nenhum arquivo foi carregado
    st.info("👈 Faça upload de um arquivo Excel usando o menu lateral para começar!")
    
    st.markdown("### 📋 Como usar:")
    st.markdown(""" 
    1. Clique em **"Upload"** no menu lateral ou arraste seu arquivo Excel
    2. Aguarde o processamento automático dos dados
    3. Visualize as métricas calculadas
    """)
