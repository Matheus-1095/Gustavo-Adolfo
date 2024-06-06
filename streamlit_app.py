import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import date  # Importar a data atual

# Display Title and description
st.title("Sistema de votação de alunos")
st.markdown("Coloque a sua nota")

# Establishing a Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing students
existing_data = conn.read(worksheet="Resultados", usecols=list(range(4)), ttl=3)
existing_data = existing_data.dropna(how="all")

# List of students
STUDENTS = [
    "Aluno 1",
    "Aluno 2",
    "Aluno 3",
    "Aluno 4",
    "Aluno 5",
    "Aluno 6",
    "Aluno 7",
]

# Onboarding New Student form
with st.form(key="student_form"):
    student_name = st.selectbox("Nome do aluno", options=STUDENTS, index=None)
    today = date.today()  # Data de hoje
    date_votes = st.date_input(label="Data de hoje", value=today, min_value=today, max_value=today)  # Limitar ao dia de hoje
    final_vote = st.slider("Nota de hoje", 0, 10, 1)
    additional_info = st.text_area(label="Comentários Adicionais")
    
    # Mark mandatory fields
    st.markdown("**Obrigatório**")

    submit_button = st.form_submit_button(label='Enviar nota')

    if submit_button:
        # Verifique se os campos obrigatórios estão preenchidos
        if not student_name or final_vote is None:
            st.warning("Preencha o seu nome e a nota")
        else:
            # Filtrar para verificar se o aluno já votou hoje
            today_str = today.strftime("%Y-%m-%d")
            existing_vote = existing_data[
                (existing_data["Aluno"] == student_name) &
                (existing_data["Data da votação"] == today_str)
            ]
            
            if not existing_vote.empty:
                st.warning("Você já votou hoje. Espere o próximo dia.")
            else:
                student_data = pd.DataFrame(
                    {
                        "Aluno": [student_name],  # Use listas
                        "Data da votação": [today_str],  # Use listas
                        "Nota": [final_vote],  # Use listas
                        "Comentários adicionais": [additional_info]  # Use listas
                    }
                )
                
                # Add the new info data to existing data
                update_df = pd.concat([existing_data, student_data], ignore_index=True)
                
                # Update Google Sheets with new student data
                conn.update(worksheet="Resultados", data=update_df)
                st.success("Nota enviada com sucesso!!!", icon="✅")
