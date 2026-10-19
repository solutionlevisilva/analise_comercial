import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.metricas import (
    calcular_metricas, 
    formatar_metricas,
    obter_limites_datas,
    filtrar_por_data_range,
    processar_evolucao_mensal,
    processar_evolucao_semanal
)

# Configuração da página
st.set_page_config(
    page_title="Relatório de Análise Comercial",
    layout="wide"
)

# CSS para ajustar tamanho da fonte das métricas
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

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
        # Carregar dados direto com pandas (sheet_name=1 para segunda planilha)
        with st.spinner("⏳ Carregando dados..."):
            df = pd.read_excel(uploaded_file, sheet_name=1)
            st.session_state.df_original = df
            st.success(f"✅ Carregado com sucesso!")
        
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
        
        # Obter limites de datas dos dados
        data_min, data_max = obter_limites_datas(st.session_state.df_limpo)
        
        if data_min and data_max:
            st.write("📅 **Período dos Dados:**")
            st.write(f"{data_min.strftime('%d/%m/%Y')} até {data_max.strftime('%d/%m/%Y')}")
            st.write("")
            
            # Opções de filtro rápido
            filtro_rapido = st.radio(
                "Selecione o período:",
                ["Todos os meses", "Personalizado"],
                index=0
            )
            
            if filtro_rapido == "Personalizado":
                # Date range picker
                st.write("**Selecione o intervalo:**")
                
                col_data1, col_data2 = st.columns(2)
                
                with col_data1:
                    data_inicial = st.date_input(
                        "De:",
                        value=data_min,
                        min_value=data_min,
                        max_value=data_max,
                        key="data_inicio"
                    )
                
                with col_data2:
                    data_final = st.date_input(
                        "Até:",
                        value=data_max,
                        min_value=data_min,
                        max_value=data_max,
                        key="data_fim"
                    )
                
                # Armazenar no session_state
                st.session_state.data_inicio_filtro = data_inicial
                st.session_state.data_fim_filtro = data_final
                st.session_state.filtro_ativo = True
                
                # Mostrar quantos meses selecionados
                meses_diff = (data_final.year - data_inicial.year) * 12 + (data_final.month - data_inicial.month) + 1
                st.info(f"📊 Período: {meses_diff} {'mês' if meses_diff == 1 else 'meses'}")
            else:
                # Sem filtro
                st.session_state.data_inicio_filtro = None
                st.session_state.data_fim_filtro = None
                st.session_state.filtro_ativo = False

# ==================== APLICAR FILTROS ====================
df_exibicao = st.session_state.df_limpo
metricas_exibicao = st.session_state.metricas

if st.session_state.df_limpo is not None and st.session_state.get('filtro_ativo', False):
    # Aplicar filtro de data range
    df_exibicao = filtrar_por_data_range(
        st.session_state.df_limpo, 
        st.session_state.get('data_inicio_filtro'),
        st.session_state.get('data_fim_filtro')
    )
    
    # Recalcular métricas com dados filtrados
    if len(df_exibicao) > 0:
        metricas_exibicao = calcular_metricas(df_exibicao)
    else:
        metricas_exibicao = {
            'total_processos': 0,
            'processos_concluidos': 0,
            'receita': 0.0,
            'total_pago': 0.0,
            'total_faturado': 0.0
        }
        st.warning(f"⚠️ Nenhum processo encontrado para o período selecionado")

# ==================== EXIBIÇÃO DAS MÉTRICAS ====================
if metricas_exibicao is not None:
    st.markdown("---")
    st.subheader("📈 Métricas Principais")
    
    # Mostrar indicador de filtro ativo
    if st.session_state.get('filtro_ativo', False):
        data_inicio = st.session_state.get('data_inicio_filtro')
        data_fim = st.session_state.get('data_fim_filtro')
        st.info(f"📅 Exibindo dados de: **{data_inicio.strftime('%d/%m/%Y')}** até **{data_fim.strftime('%d/%m/%Y')}**")
    
    # Formatar métricas
    metricas_formatadas = formatar_metricas(metricas_exibicao)
    
    # Criar cards de métricas (5 colunas)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="🔢 Total de Processos",
            value=metricas_formatadas['total_processos'],
            help="Total de processos no relatório após limpeza"
        )
    
    with col2:
        st.metric(
            label="✅ Processos Concluídos",
            value=metricas_formatadas['processos_concluidos'],
            help="Processos com status PAGO ou FATURADO"
        )
    
    with col3:
        st.metric(
            label="💰 Receita Total",
            value=metricas_formatadas['receita'],
            help="Soma do valor dos processos pagos/faturados"
        )
    
    with col4:
        st.metric(
            label="💵 Total Pago",
            value=metricas_formatadas['total_pago'],
            help="Soma dos valores com status PAGO"
        )
    
    with col5:
        st.metric(
            label="🧾 Total Faturado",
            value=metricas_formatadas['total_faturado'],
            help="Soma dos valores com status FATURADO"
        )
    
    # ==================== GRÁFICO DE EVOLUÇÃO ====================
    st.markdown("---")
    st.subheader("📈 Evolução dos Processos")
    
    # Decidir qual tipo de gráfico exibir baseado no filtro
    if not st.session_state.get('filtro_ativo', False):
        # SEM FILTRO: Mostrar evolução mensal
        with st.spinner("📊 Gerando gráfico mensal..."):
            df_evolucao = processar_evolucao_mensal(df_exibicao)
        
        if not df_evolucao.empty:
            # Criar gráfico misto (barras + linhas)
            fig = go.Figure()
            
            # Barras: Quantidade total
            fig.add_trace(go.Bar(
                x=df_evolucao['mes_nome'],
                y=df_evolucao['quantidade'],
                text=df_evolucao['quantidade'],
                textposition='outside',
                marker_color='#1f77b4',
                name='Total de Processos',
                yaxis='y'
            ))
            
            # Linha 1: Valores Pagos
            fig.add_trace(go.Scatter(
                x=df_evolucao['mes_nome'],
                y=df_evolucao['valor_pago'],
                mode='lines+markers',
                name='Total Pago',
                line=dict(color='#2ca02c', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))
            
            # Linha 2: Valores Faturados
            fig.add_trace(go.Scatter(
                x=df_evolucao['mes_nome'],
                y=df_evolucao['valor_faturado'],
                mode='lines+markers',
                name='Total Faturado',
                line=dict(color='#ff7f0e', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))
            
            # Linha 3: Processos Cancelados
            fig.add_trace(go.Scatter(
                x=df_evolucao['mes_nome'],
                y=df_evolucao['processos_cancelados'],
                mode='lines+markers',
                name='Processos Cancelados',
                line=dict(color='#d62728', width=3, dash='dot'),
                marker=dict(size=8),
                yaxis='y'
            ))
            
            # Configurar layout com dois eixos Y
            fig.update_layout(
                title="Evolução Mensal de Processos e Valores",
                xaxis_title="Mês",
                yaxis=dict(
                    title="Quantidade de Processos",
                    side='left'
                ),
                yaxis2=dict(
                    title="Valores (R$)",
                    overlaying='y',
                    side='right'
                ),
                height=500,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Exibir gráfico
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Não foi possível gerar o gráfico de evolução.")
    
    else:
        # COM FILTRO: Mostrar evolução semanal ou mensal dependendo do range
        with st.spinner("📊 Gerando gráfico..."):
            # Verificar quantos meses no filtro
            data_inicio = st.session_state.get('data_inicio_filtro')
            data_fim = st.session_state.get('data_fim_filtro')
            meses_diff = (data_fim.year - data_inicio.year) * 12 + (data_fim.month - data_inicio.month) + 1
            
            # Se for 1 mês, mostrar semanal. Se for mais, mostrar mensal
            if meses_diff == 1:
                # Gráfico SEMANAL
                df_evolucao = processar_evolucao_semanal(df_exibicao)
            else:
                # Gráfico MENSAL (múltiplos meses)
                df_evolucao = processar_evolucao_mensal(df_exibicao)
        
        if not df_evolucao.empty:
            if meses_diff == 1:
                # Gráfico semanal (1 mês selecionado)
                # Filtrar apenas o mês se houver múltiplos
                if len(df_evolucao['mes_ano'].unique()) > 1:
                    # Pegar o primeiro mês
                    mes_unico = sorted(df_evolucao['mes_ano'].unique())[0]
                    dados_periodo = df_evolucao[df_evolucao['mes_ano'] == mes_unico]
                else:
                    dados_periodo = df_evolucao
                
                if not dados_periodo.empty:
                    # Criar gráfico misto (barras + linhas)
                    fig = go.Figure()
                    
                    # Barras: Quantidade total
                    fig.add_trace(go.Bar(
                        x=[f"Semana {s}" for s in dados_periodo['semana']],
                        y=dados_periodo['quantidade'],
                        text=dados_periodo['quantidade'],
                        textposition='outside',
                        marker_color='#1f77b4',
                        name='Total de Processos',
                        yaxis='y'
                    ))
                    
                    # Linha 1: Valores Pagos
                    fig.add_trace(go.Scatter(
                        x=[f"Semana {s}" for s in dados_periodo['semana']],
                        y=dados_periodo['valor_pago'],
                        mode='lines+markers',
                        name='Total Pago',
                        line=dict(color='#2ca02c', width=3),
                        marker=dict(size=8),
                        yaxis='y2'
                    ))
                    
                    # Linha 2: Valores Faturados
                    fig.add_trace(go.Scatter(
                        x=[f"Semana {s}" for s in dados_periodo['semana']],
                        y=dados_periodo['valor_faturado'],
                        mode='lines+markers',
                        name='Total Faturado',
                        line=dict(color='#ff7f0e', width=3),
                        marker=dict(size=8),
                        yaxis='y2'
                    ))
                    
                    # Linha 3: Processos Cancelados
                    fig.add_trace(go.Scatter(
                        x=[f"Semana {s}" for s in dados_periodo['semana']],
                        y=dados_periodo['processos_cancelados'],
                        mode='lines+markers',
                        name='Processos Cancelados',
                        line=dict(color='#d62728', width=3, dash='dot'),
                        marker=dict(size=8),
                        yaxis='y'
                    ))
                    
                    # Configurar layout com dois eixos Y
                    nome_mes = f"{data_inicio.strftime('%B %Y')}"
                    fig.update_layout(
                        title=f"Evolução Semanal - {nome_mes}",
                        xaxis_title="Semanas do Mês",
                        yaxis=dict(
                            title="Quantidade de Processos",
                            side='left'
                        ),
                        yaxis2=dict(
                            title="Valores (R$)",
                            overlaying='y',
                            side='right'
                        ),
                        height=500,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    # Exibir gráfico
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"⚠️ Nenhum dado encontrado para o período selecionado")
            else:
                # Gráfico mensal (múltiplos meses)
                # Criar gráfico misto (barras + linhas)
                fig = go.Figure()
                
                # Barras: Quantidade total
                fig.add_trace(go.Bar(
                    x=df_evolucao['mes_nome'],
                    y=df_evolucao['quantidade'],
                    text=df_evolucao['quantidade'],
                    textposition='outside',
                    marker_color='#1f77b4',
                    name='Total de Processos',
                    yaxis='y'
                ))
                
                # Linha 1: Valores Pagos
                fig.add_trace(go.Scatter(
                    x=df_evolucao['mes_nome'],
                    y=df_evolucao['valor_pago'],
                    mode='lines+markers',
                    name='Total Pago',
                    line=dict(color='#2ca02c', width=3),
                    marker=dict(size=8),
                    yaxis='y2'
                ))
                
                # Linha 2: Valores Faturados
                fig.add_trace(go.Scatter(
                    x=df_evolucao['mes_nome'],
                    y=df_evolucao['valor_faturado'],
                    mode='lines+markers',
                    name='Total Faturado',
                    line=dict(color='#ff7f0e', width=3),
                    marker=dict(size=8),
                    yaxis='y2'
                ))
                
                # Linha 3: Processos Cancelados
                fig.add_trace(go.Scatter(
                    x=df_evolucao['mes_nome'],
                    y=df_evolucao['processos_cancelados'],
                    mode='lines+markers',
                    name='Processos Cancelados',
                    line=dict(color='#d62728', width=3, dash='dot'),
                    marker=dict(size=8),
                    yaxis='y'
                ))
                
                # Configurar layout com dois eixos Y
                fig.update_layout(
                    title=f"Evolução Mensal - {data_inicio.strftime('%m/%Y')} até {data_fim.strftime('%m/%Y')}",
                    xaxis_title="Mês",
                    yaxis=dict(
                        title="Quantidade de Processos",
                        side='left'
                    ),
                    yaxis2=dict(
                        title="Valores (R$)",
                        overlaying='y',
                        side='right'
                    ),
                    height=500,
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Exibir gráfico
                st.plotly_chart(fig, use_container_width=True)
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
