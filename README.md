# 📊 Relatório de Análise Comercial

Aplicação web desenvolvida com Streamlit para análise de dados comerciais através de relatórios em Excel.

## 🚀 Funcionalidades

- Upload de arquivos Excel (.xlsx, .xls)
- Análise exploratória de dados
- Visualização de métricas comerciais
- Interface intuitiva com sidebar

## 🛠️ Tecnologias

- **Python 3.8+**
- **Streamlit** - Framework web
- **Pandas** - Manipulação de dados
- **Matplotlib & Seaborn** - Visualizações
- **OpenPyXL** - Leitura de arquivos Excel

## 📦 Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

2. Crie um ambiente virtual:
```bash
python -m venv .venv
```

3. Ative o ambiente virtual:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## ▶️ Como Executar

```bash
streamlit run main.py
```

O aplicativo será aberto automaticamente no navegador em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
.
├── main.py                          # Aplicação Streamlit principal
├── utils/                           # Módulos utilitários
│   ├── __init__.py
│   ├── data_loader.py              # Carregamento e limpeza de dados
│   └── analysis.py                 # Análise e métricas
├── data/                            # Arquivos de dados
├── analise_exploratoria/           # Notebooks de análise
│   ├── exploracao.ipynb
│   └── metricas.ipynb
├── requirements.txt                # Dependências Python
└── README.md                       # Este arquivo
```

## 🌐 Deploy

Esta aplicação está configurada para deploy no Streamlit Cloud.

## 📝 Licença

Este projeto está sob a licença MIT.

## 👨‍💻 Autor

Desenvolvido com ❤️ para análise de dados comerciais.
