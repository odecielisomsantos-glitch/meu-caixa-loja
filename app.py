import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema de Gestão", layout="wide", page_icon="💰")

# Conexão
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para carregar dados (com cache para ser rápido)
def load_data():
    prod = conn.read(worksheet="produtos")
    cli = conn.read(worksheet="clientes")
    try:
        vend = conn.read(worksheet="vendas")
    except:
        vend = pd.DataFrame(columns=["Data", "Cliente", "Produto", "Valor", "Quantidade"])
    return prod, cli, vend

df_produtos, df_clientes, df_vendas = load_data()

# Menu Lateral
menu = st.sidebar.radio("Navegação", ["🏠 Home", "📦 Produtos", "👥 Clientes", "🛒 Nova Venda"])

# --- PÁGINA: HOME ---
if menu == "🏠 Home":
    st.title("Painel Geral")
    col1, col2 = st.columns(2)
    col1.metric("Total de Clientes", len(df_clientes))
    col2.metric("Itens no Estoque", df_produtos["Estoque"].sum())
    st.dataframe(df_produtos)

# --- PÁGINA: PRODUTOS ---
elif menu == "📦 Produtos":
    st.title("Cadastro de Produtos")
    with st.form("cad_prod"):
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço", min_value=0.0)
        qtd = st.number_input("Estoque Inicial", min_value=0)
        if st.form_submit_button("Salvar Produto"):
            novo_p = pd.DataFrame([{"ID": len(df_produtos)+1, "Nome": nome, "Preco": preco, "Estoque": qtd}])
            updated_p = pd.concat([df_produtos, novo_p], ignore_index=True)
            conn.update(worksheet="produtos", data=updated_p)
            st.success("Produto salvo!")
            st.rerun()

# --- PÁGINA: CLIENTES ---
elif menu == "👥 Clientes":
    st.title("Gestão de Clientes")
    with st.form("cad_cli"):
        nome_cli = st.text_input("Nome Completo")
        zap = st.text_input("WhatsApp")
        if st.form_submit_button("Cadastrar Cliente"):
            novo_c = pd.DataFrame([{"ID": len(df_clientes)+1, "Nome": nome_cli, "WhatsApp": zap, "Saldo_Devedor": 0}])
            updated_c = pd.concat([df_clientes, novo_c], ignore_index=True)
            conn.update(worksheet="clientes", data=updated_c)
            st.success("Cliente cadastrado!")
            st.rerun()
    st.write("### Lista de Clientes")
    st.table(df_clientes)

# --- PÁGINA: VENDAS (PDV) ---
elif menu == "🛒 Nova Venda":
    st.title("Frente de Caixa")
    
    with st.form("venda"):
        cliente = st.selectbox("Cliente", df_clientes["Nome"].tolist())
        produto = st.selectbox("Produto", df_produtos["Nome"].tolist())
        qtd_venda = st.number_input("Quantidade", min_value=1)
        
        if st.form_submit_button("Finalizar Venda"):
            # Achar o preço e o estoque atual
            idx_prod = df_produtos.index[df_produtos['Nome'] == produto][0]
            preco_unit = df_produtos.at[idx_prod, 'Preco']
            estoque_atual = df_produtos.at[idx_prod, 'Estoque']
            
            if estoque_atual >= qtd_venda:
                # 1. Atualizar Estoque
                df_produtos.at[idx_prod, 'Estoque'] -= qtd_venda
                conn.update(worksheet="produtos", data=df_produtos)
                
                # 2. Registrar Venda
                nova_venda = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Cliente": cliente,
                    "Produto": produto,
                    "Valor": preco_unit * qtd_venda,
                    "Quantidade": qtd_venda
                }])
                updated_v = pd.concat([df_vendas, nova_venda], ignore_index=True)
                conn.update(worksheet="vendas", data=updated_v)
                
                st.success("Venda realizada com sucesso!")
                st.balloons()
            else:
                st.error("Estoque insuficiente!")
