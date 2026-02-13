import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Controle de Estoque", layout="wide")

# Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para ler dados
df_produtos = conn.read(worksheet="produtos")

st.title("🚀 Sistema de Gestão - Caixa e Estoque")

tab1, tab2, tab3 = st.tabs(["📦 Estoque Atual", "➕ Cadastro de Produto", "💰 Vendas"])

with tab1:
    st.subheader("Produtos em Estoque")
    st.dataframe(df_produtos, use_container_width=True)

with tab2:
    st.subheader("Novo Produto")
    with st.form("cadastro_form"):
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço", min_value=0.0, format="%.2f")
        estoque = st.number_input("Quantidade Inicial", min_value=0)
        
        if st.form_submit_button("Cadastrar"):
            # Cria nova linha
            novo_dado = pd.DataFrame([{"ID": len(df_produtos)+1, "Nome": nome, "Preco": preco, "Estoque": estoque}])
            # Adiciona ao DataFrame existente
            updated_df = pd.concat([df_produtos, novo_dado], ignore_index=True)
            # Atualiza a planilha
            conn.update(worksheet="produtos", data=updated_df)
            st.success("Produto cadastrado com sucesso! Recarregue a página.")
