import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página - DEVE ser o primeiro comando Streamlit
st.set_page_config(page_title="Sistema de Gestão 1.0", layout="wide", page_icon="📊")

# Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO PARA CARREGAR DADOS ---
def carregar_dados():
    prod = conn.read(worksheet="produtos")
    # Tenta ler vendas e clientes, se não existirem, cria um DataFrame vazio
    try:
        vend = conn.read(worksheet="vendas")
    except:
        vend = pd.DataFrame(columns=["Data", "Cliente", "Produto", "Valor", "Quantidade"])
    return prod, vend

df_produtos, df_vendas = carregar_dados()

# --- BARRA LATERAL (MENU) ---
st.sidebar.title("🎮 Navegação")
menu = st.sidebar.radio("Ir para:", ["🏠 Home", "📦 Estoque", "👥 Clientes", "💰 PDV / Vendas"])

# --- PÁGINA INICIAL (HOME) ---
if menu == "🏠 Home":
    st.title("📊 Painel de Controle")
    st.markdown(f"Bem-vindo ao seu sistema de gestão, **{st.experimental_user.name if 'name' in st.experimental_user else 'Usuário'}**!")
    
    st.divider()

    # --- MÉTRICAS PRINCIPAIS ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_estoque = df_produtos["Estoque"].sum()
    valor_estoque = (df_produtos["Estoque"] * df_produtos["Preco"]).sum()
    total_vendas_valor = df_vendas["Valor"].astype(float).sum() if not df_vendas.empty else 0.0
    qtd_vendas = len(df_vendas)

    col1.metric("Itens em Estoque", f"{total_estoque} un")
    col2.metric("Valor em Estoque", f"R$ {valor_estoque:,.2f}")
    col3.metric("Vendas Totais (R$)", f"R$ {total_vendas_valor:,.2f}")
    col4.metric("Nº de Vendas", f"{qtd_vendas}")

    st.divider()

    # --- ALERTAS E GRÁFICOS ---
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("⚠️ Alerta de Estoque Baixo")
        estoque_baixo = df_produtos[df_produtos["Estoque"] <= 5]
        if not estoque_baixo.empty:
            st.warning(f"Existem {len(estoque_baixo)} produtos com menos de 5 unidades!")
            st.dataframe(estoque_baixo[["Nome", "Estoque"]], use_container_width=True)
        else:
            st.success("Tudo em dia! Nenhum produto com estoque crítico.")

    with c2:
        st.subheader("📈 Últimas Vendas")
        if not df_vendas.empty:
            st.table(df_vendas.tail(5)) # Mostra as últimas 5 vendas
        else:
            st.info("Nenhuma venda registrada ainda.")

# --- OUTRAS PÁGINAS (ESTRUTURA) ---
elif menu == "📦 Estoque":
    st.title("📦 Gerenciamento de Estoque")
    # Aqui você move aquele código de cadastro que fizemos antes...

elif menu == "👥 Clientes":
    st.title("👥 Cadastro de Clientes")
    st.info("Em breve: Módulo de gestão de clientes e fiado.")

elif menu == "💰 PDV / Vendas":
    st.title("💰 Frente de Caixa")
    # Aqui você move o código de realizar vendas...
