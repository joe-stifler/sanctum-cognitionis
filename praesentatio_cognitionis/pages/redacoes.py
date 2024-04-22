import streamlit as st

def main():
    st.title('Página de Redações')
    
    # Layout de três colunas
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        st.header("Vestibulares")
        vestibular = st.radio("Escolha o vestibular", ["Unicamp", "USP", "ENEM"])

        st.header("Redações")
        tipo_redacao = st.radio("Visualizar redações", ["Finalizadas", "Pendentes"])

        if tipo_redacao == "Finalizadas":
            st.subheader("Redações Finalizadas")
            # Simulando redações finalizadas
            st.write("Redação 1 - Nota: 8")
            st.write("Redação 2 - Nota: 7")
        else:
            st.subheader("Redações Pendentes")
            st.write("Proposta 3 - Iniciada")
            st.write("Proposta 4 - Não iniciada")

        # Galeria de Imagens (opcional)
        st.image("path_to_image.jpg", caption="Imagem Redação")

    with col2:
        st.header("Coletânea de Textos")
        # Aqui entrariam os textos da coletânea para a redação
        st.text_area("Texto Coletânea", "Texto exemplo coletânea", height=300)

        st.header("Escreva sua redação")
        texto_redacao = st.text_area("Redação", "Digite sua redação aqui", height=300)

        st.button("Enviar para Correção")
        st.button("Refazer Redação")
        st.button("Enviar para o Notion")

    with col3:
        st.header("Feedback do Tutor")
        # Feedback simulado do tutor
        st.write("Bom uso de argumentos, mas precisa melhorar a coesão.")

        st.header("Notas por Critério")
        st.json({
            "Proposta Temática (Pt)": 2,
            "Gênero (G)": 3,
            "Leitura (Lt)": 3,
            "Convenções da Escrita e Coesão (CeC)": 4
        })

        st.button("Atualizar Notion")

if __name__ == "__main__":
    main()
