import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Sistema de Gestão", layout="wide", page_icon="🏦")

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNÇÃO PARA CARREGAR DADOS COM SEGURANÇA ---
def carregar_todos_os_dados():
    try:
        produtos = conn.read(worksheet="produtos")
    except:
        produtos = pd.DataFrame(columns=["ID", "Nome", "Preco", "Estoque"])
    
    try:
        clientes = conn.read(worksheet="clientes")
    except:
        clientes = pd.DataFrame(columns=["ID", "Nome", "WhatsApp", "Saldo_Devedor"])
        
    try:
        vendas = conn.read(worksheet="vendas")
    except:
        vendas = pd.DataFrame(columns=["Data", "Cliente", "Produto", "Valor", "Quantidade"])
        
    return produtos, clientes, vendas

df_p, df_c, df_v = carregar_todos_os_dados()

# --- MENU LATERAL ---
st.sidebar.title("Menu Principal")
pagina = st.sidebar.selectbox("Selecione uma página:", ["🏠 Home", "📦 Produtos", "👥 Clientes", "🛒 PDV (Vendas)"])

# --- PÁGINA: HOME ---
if pagina == "🏠 Home":
    st.title("📊 Resumo do Negócio")
    m1, m2, m3 = st.columns(3)
    m1.metric("Produtos Cadastrados", len(df_p))
    m2.metric("Clientes Ativos", len(df_c))
    total_vendas = df_v["Valor"].sum() if not df_v.empty else 0
    m3.metric("Faturamento Total", f"R$ {total_vendas:,.2f}")
    
    st.subheader("Últimas Vendas")
    st.dataframe(df_v.tail(10), use_container_width=True)

# --- PÁGINA: PRODUTOS ---
elif pagina == "📦 Produtos":
    st.title("Gerenciamento de Produtos")
    with st.expander("➕ Cadastrar Novo Produto"):
        with st.form("form_prod"):
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço de Venda", min_value=0.0)
            estoque = st.number_input("Qtd em Estoque", min_value=0)
            if st.form_submit_button("Salvar"):
                novo = pd.DataFrame([{"ID": len(df_p)+1, "Nome": nome, "Preco": preco, "Estoque": estoque}])
                df_p = pd.concat([df_p, novo], ignore_index=True)
                conn.update(worksheet="produtos", data=df_p)
                st.success("Produto cadastrado!")
                st.rerun()
    st.dataframe(df_p, use_container_width=True)

# --- PÁGINA: CLIENTES ---
elif pagina == "👥 Clientes":
    st.title("Cadastro de Clientes")
    with st.form("form_cli"):
        nome_c = st.text_input("Nome do Cliente")
        zap = st.text_input("WhatsApp")
        if st.form_submit_button("Cadastrar"):
            novo_c = pd.DataFrame([{"ID": len(df_c)+1, "Nome": nome_c, "WhatsApp": zap, "Saldo_Devedor": 0}])
            df_c = pd.concat([df_c, novo_c], ignore_index=True)
            conn.update(worksheet="clientes", data=df_c)
            st.success("Cliente salvo com sucesso!")
            st.rerun()
    st.table(df_c)

# --- PÁGINA: VENDAS (PDV) ---
elif pagina == "🛒 PDV (Vendas)":
    st.title("Finalizar Venda")
    if df_p.empty or df_c.empty:
        st.warning("Cadastre produtos e clientes antes de vender.")
    else:
        with st.form("venda_pdv"):
            cli_venda = st.selectbox("Cliente", df_c["Nome"].tolist())
            prod_venda = st.selectbox("Produto", df_p["Nome"].tolist())
            qtd_venda = st.number_input("Quantidade", min_value=1)
            
            if st.form_submit_button("Concluir Venda"):
                # Busca preço e estoque
                idx = df_p.index[df_p['Nome'] == prod_venda][0]
                preco_unit = df_p.at[idx, 'Preco']
                est_atual = df_p.at[idx, 'Estoque']
                
                if est_atual >= qtd_venda:
                    # 1. Baixa no estoque
                    df_p.at[idx, 'Estoque'] -= qtd_venda
                    conn.update(worksheet="produtos", data=df_p)
                    # 2. Registro da venda
                    nova_v = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Cliente": cli_venda, "Produto": prod_venda,
                        "Valor": preco_unit * qtd_venda, "Quantidade": qtd_venda
                    }])
                    df_v = pd.concat([df_v, nova_v], ignore_index=True)
                    conn.update(worksheet="vendas", data=df_v)
                    st.success(f"Venda concluída! Total: R$ {preco_unit * qtd_venda}")
                    st.balloons()
                else:
                    st.error("Estoque insuficiente!")
