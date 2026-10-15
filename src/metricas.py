"""
Módulo para cálculo de métricas do relatório comercial
"""
import pandas as pd
from typing import Dict, List, Tuple


def calcular_total_processos(df: pd.DataFrame) -> int:
    """
    Calcula a quantidade total de processos no DataFrame limpo
    
    Regra: Conta TODOS os registros após limpeza
    
    Args:
        df: DataFrame com os dados limpos
        
    Returns:
        int: Quantidade total de processos
    """
    try:
        # Contar todas as linhas do DataFrame
        total = len(df)
        
        return int(total)
    
    except Exception as e:
        print(f"⚠️ Erro ao calcular total de processos: {str(e)}")
        return 0


def calcular_receita(df: pd.DataFrame) -> float:
    """
    Calcula a receita total dos processos pagos ou faturados
    
    Regra: Soma VALOR DO PROCESSO onde STATUS PAGAMENTO = "PAGO" ou "FATURADO"
    
    Args:
        df: DataFrame com os dados
        
    Returns:
        float: Receita total
    """
    try:
        # Filtrar processos com status PAGO ou FATURADO
        mask = df['STATUS PAGAMENTO'].str.upper().isin(['PAGO', 'FATURADO'])
        df_filtrado = df[mask]
        
        # Somar valores
        receita = df_filtrado['VALOR DO PROCESSO'].sum()
        
        return float(receita)
    
    except KeyError as e:
        if 'STATUS PAGAMENTO' in str(e):
            print("⚠️ Erro: Coluna 'STATUS PAGAMENTO' não encontrada")
        elif 'VALOR DO PROCESSO' in str(e):
            print("⚠️ Erro: Coluna 'VALOR DO PROCESSO' não encontrada")
        return 0.0
    except Exception as e:
        print(f"⚠️ Erro ao calcular receita: {str(e)}")
        return 0.0


def calcular_total_pago(df: pd.DataFrame) -> float:
    """
    Calcula o total de valores com status PAGO
    
    Regra: Soma VALOR DO PROCESSO onde STATUS PAGAMENTO = "PAGO"
    
    Args:
        df: DataFrame com os dados
        
    Returns:
        float: Total de valores pagos
    """
    try:
        # Filtrar processos com status PAGO
        mask = df['STATUS PAGAMENTO'].str.upper() == 'PAGO'
        df_filtrado = df[mask]
        
        # Somar valores
        total_pago = df_filtrado['VALOR DO PROCESSO'].sum()
        
        return float(total_pago)
    
    except KeyError as e:
        print(f"⚠️ Erro: Coluna não encontrada - {str(e)}")
        return 0.0
    except Exception as e:
        print(f"⚠️ Erro ao calcular total pago: {str(e)}")
        return 0.0


def calcular_total_faturado(df: pd.DataFrame) -> float:
    """
    Calcula o total de valores com status FATURADO
    
    Regra: Soma VALOR DO PROCESSO onde STATUS PAGAMENTO = "FATURADO"
    
    Args:
        df: DataFrame com os dados
        
    Returns:
        float: Total de valores faturados
    """
    try:
        # Filtrar processos com status FATURADO
        mask = df['STATUS PAGAMENTO'].str.upper() == 'FATURADO'
        df_filtrado = df[mask]
        
        # Somar valores
        total_faturado = df_filtrado['VALOR DO PROCESSO'].sum()
        
        return float(total_faturado)
    
    except KeyError as e:
        print(f"⚠️ Erro: Coluna não encontrada - {str(e)}")
        return 0.0
    except Exception as e:
        print(f"⚠️ Erro ao calcular total faturado: {str(e)}")
        return 0.0


def calcular_metricas(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcula todas as métricas do relatório de uma vez
    
    Args:
        df: DataFrame com os dados limpos
        
    Returns:
        dict: Dicionário com as métricas calculadas
            {
                'total_processos': int,
                'receita': float,
                'total_pago': float,
                'total_faturado': float
            }
    """
    metricas = {
        'total_processos': calcular_total_processos(df),
        'receita': calcular_receita(df),
        'total_pago': calcular_total_pago(df),
        'total_faturado': calcular_total_faturado(df)
    }
    
    return metricas


def formatar_metricas(metricas: Dict[str, float]) -> Dict[str, str]:
    """
    Formata as métricas para exibição
    
    Args:
        metricas: Dicionário com métricas calculadas
        
    Returns:
        dict: Métricas formatadas para exibição
    """
    try:
        formatadas = {
            'total_processos': f"{metricas['total_processos']:,}".replace(',', '.'),
            'receita': f"R$ {metricas['receita']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'total_pago': f"R$ {metricas['total_pago']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'total_faturado': f"R$ {metricas['total_faturado']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        }
        
        return formatadas
    
    except Exception as e:
        print(f"⚠️ Erro ao formatar métricas: {str(e)}")
        return {
            'total_processos': '0',
            'receita': 'R$ 0,00',
            'total_pago': 'R$ 0,00',
            'total_faturado': 'R$ 0,00'
        }


def processar_evolucao_semanal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa dados para evolução semanal de processos
    
    Agrupa processos por mês e semana (1-4)
    
    Lógica de semanas:
    - Semana 1: dias 1-7
    - Semana 2: dias 8-14
    - Semana 3: dias 15-21
    - Semana 4: dias 22-31
    
    Args:
        df: DataFrame com coluna 'DATA CRIAÇÃO'
        
    Returns:
        DataFrame com colunas: ['mes_ano', 'semana', 'quantidade']
    """
    try:
        # Copiar DataFrame
        df_temp = df.copy()
        
        # Converter DATA CRIAÇÃO para datetime
        df_temp['data'] = pd.to_datetime(df_temp['DATA CRIAÇÃO'], format='%d/%m/%Y %H:%M:%S')
        
        # Extrair mês/ano
        df_temp['mes_ano'] = df_temp['data'].dt.to_period('M')
        
        # Calcular semana do mês (1-4)
        df_temp['dia'] = df_temp['data'].dt.day
        df_temp['semana'] = ((df_temp['dia'] - 1) // 7) + 1
        df_temp['semana'] = df_temp['semana'].clip(upper=4)  # Máximo semana 4
        
        # Agrupar e contar
        evolucao = df_temp.groupby(['mes_ano', 'semana']).size().reset_index(name='quantidade')
        
        # Converter período para string
        evolucao['mes_ano'] = evolucao['mes_ano'].astype(str)
        
        # Ordenar
        evolucao = evolucao.sort_values(['mes_ano', 'semana'])
        
        return evolucao
    
    except KeyError as e:
        print(f"⚠️ Erro: Coluna 'DATA CRIAÇÃO' não encontrada - {str(e)}")
        return pd.DataFrame(columns=['mes_ano', 'semana', 'quantidade'])
    except Exception as e:
        print(f"⚠️ Erro ao processar evolução semanal: {str(e)}")
        return pd.DataFrame(columns=['mes_ano', 'semana', 'quantidade'])


def processar_evolucao_mensal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa dados para evolução mensal de processos
    
    Agrupa processos por mês
    
    Args:
        df: DataFrame com coluna 'DATA CRIAÇÃO'
        
    Returns:
        DataFrame com colunas: ['mes_ano', 'mes_nome', 'quantidade']
    """
    try:
        # Mapeamento de meses para português
        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        # Copiar DataFrame
        df_temp = df.copy()
        
        # Converter DATA CRIAÇÃO para datetime
        df_temp['data'] = pd.to_datetime(df_temp['DATA CRIAÇÃO'], format='%d/%m/%Y %H:%M:%S')
        
        # Extrair mês/ano
        df_temp['mes_ano'] = df_temp['data'].dt.to_period('M').astype(str)
        df_temp['ano'] = df_temp['data'].dt.year
        df_temp['mes'] = df_temp['data'].dt.month
        
        # Agrupar e contar
        evolucao = df_temp.groupby(['mes_ano', 'ano', 'mes']).size().reset_index(name='quantidade')
        
        # Criar nome do mês em português
        evolucao['mes_nome'] = evolucao['mes'].map(meses_pt) + ' ' + evolucao['ano'].astype(str)
        
        # Ordenar
        evolucao = evolucao.sort_values(['ano', 'mes'])
        
        return evolucao[['mes_ano', 'mes_nome', 'quantidade']]
    
    except KeyError as e:
        print(f"⚠️ Erro: Coluna 'DATA CRIAÇÃO' não encontrada - {str(e)}")
        return pd.DataFrame(columns=['mes_ano', 'mes_nome', 'quantidade'])
    except Exception as e:
        print(f"⚠️ Erro ao processar evolução mensal: {str(e)}")
        return pd.DataFrame(columns=['mes_ano', 'mes_nome', 'quantidade'])


def extrair_meses_disponiveis(df: pd.DataFrame) -> List[Tuple[str, str]]:
    """
    Extrai meses únicos do DataFrame e formata em português
    
    Args:
        df: DataFrame com coluna 'DATA CRIAÇÃO'
        
    Returns:
        list: Lista de tuplas (nome_exibicao, periodo)
              Ex: [("Março 2026", "2026-03"), ("Abril 2026", "2026-04")]
    """
    try:
        # Mapeamento de meses para português
        meses_pt = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }
        
        # Converter DATA CRIAÇÃO para datetime
        df_temp = df.copy()
        df_temp['data'] = pd.to_datetime(df_temp['DATA CRIAÇÃO'], format='%d/%m/%Y %H:%M:%S')
        
        # Extrair ano e mês
        df_temp['ano'] = df_temp['data'].dt.year
        df_temp['mes'] = df_temp['data'].dt.month
        df_temp['periodo'] = df_temp['data'].dt.to_period('M').astype(str)
        
        # Pegar combinações únicas
        meses_unicos = df_temp[['ano', 'mes', 'periodo']].drop_duplicates().sort_values(['ano', 'mes'])
        
        # Formatar nomes
        resultado = []
        for _, row in meses_unicos.iterrows():
            nome_mes = meses_pt[row['mes']]
            nome_exibicao = f"{nome_mes} {int(row['ano'])}"
            resultado.append((nome_exibicao, row['periodo']))
        
        return resultado
    
    except Exception as e:
        print(f"⚠️ Erro ao extrair meses disponíveis: {str(e)}")
        return []


def filtrar_por_mes(df: pd.DataFrame, periodo: str) -> pd.DataFrame:
    """
    Filtra DataFrame por período específico
    
    Args:
        df: DataFrame com coluna 'DATA CRIAÇÃO'
        periodo: Período no formato 'YYYY-MM' (ex: '2026-03') ou None para todos
        
    Returns:
        DataFrame filtrado
    """
    try:
        if periodo is None or periodo == "":
            return df
        
        # Converter DATA CRIAÇÃO para datetime
        df_temp = df.copy()
        df_temp['data'] = pd.to_datetime(df_temp['DATA CRIAÇÃO'], format='%d/%m/%Y %H:%M:%S')
        df_temp['periodo'] = df_temp['data'].dt.to_period('M').astype(str)
        
        # Filtrar
        df_filtrado = df_temp[df_temp['periodo'] == periodo]
        
        # Remover colunas temporárias
        df_filtrado = df_filtrado.drop(columns=['data', 'periodo'])
        
        return df_filtrado
    
    except Exception as e:
        print(f"⚠️ Erro ao filtrar por mês: {str(e)}")
        return df
