import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from PIL import Image
import io

def crear_tabla():
    conn = sqlite3.connect('tareas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            fecha_inicio TEXT,
            tipo_prueba TEXT,
            operador TEXT,
            material TEXT,
            estado TEXT,
            observaciones TEXT,
            foto BLOB
        )
    ''')
    conn.commit()
    conn.close()

crear_tabla()

def agregar_tarea(titulo, fecha_inicio, tipo_prueba, operador, material, estado, observaciones, foto):
    conn = sqlite3.connect('tareas.db')
    cursor = conn.cursor()
    if foto is not None:
        img_byte_arr = foto.read()
    else:
        img_byte_arr = None

    cursor.execute('''
        INSERT INTO tareas (titulo, fecha_inicio, tipo_prueba, operador, material, estado, observaciones, foto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (titulo, fecha_inicio, tipo_prueba, operador, material, estado, observaciones, img_byte_arr))
    conn.commit()
    conn.close()

def cargar_tareas():
    conn = sqlite3.connect('tareas.db')
    df = pd.read_sql_query("SELECT * FROM tareas", conn)
    conn.close()
    return df

def actualizar_tarea(id, titulo, fecha_inicio, tipo_prueba, operador, material, estado, observaciones, foto):
    conn = sqlite3.connect('tareas.db')
    cursor = conn.cursor()
    if foto is not None:
        img_byte_arr = foto.read()
    else:
        img_byte_arr = None

    cursor.execute('''
        UPDATE tareas
        SET titulo=?, fecha_inicio=?, tipo_prueba=?, operador=?, material=?, estado=?, observaciones=?, foto=?
        WHERE id=?
    ''', (titulo, fecha_inicio, tipo_prueba, operador, material, estado, observaciones, img_byte_arr, id))
    conn.commit()
    conn.close()

def main():
    st.sidebar.title("Navegación")
    page = st.sidebar.radio("Ir a", ["Registro de Tareas", "Actualización de Tareas"])

    if page == "Registro de Tareas":
        registro_tareas()
    elif page == "Actualización de Tareas":
        actualizacion_tareas()

def registro_tareas():
    st.title("Registro de Tareas")

    with st.form(key='nueva_tarea_form'):
        titulo = st.text_input("Título de la tarea")
        fecha_inicio = st.date_input("Fecha de inicio", datetime.today())
        tipo_prueba = st.selectbox("Tipo de prueba", ["leaching", "mesh classification"])
        operador = st.selectbox("Operador", ["Brayan", "Yeferson"])
        material = st.selectbox("Material", ["over flow", "leach tails", "szg"])
        estado = st.selectbox("Estado", ["en proceso", "por reportar", "terminado"])
        observaciones = st.text_area("Observaciones")
        foto = st.file_uploader("Subir foto", type=["png", "jpg", "jpeg"])

        submit_button_nueva_tarea = st.form_submit_button(label='Agregar tarea')

    if submit_button_nueva_tarea:
        agregar_tarea(titulo, str(fecha_inicio), tipo_prueba, operador, material, estado, observaciones, foto)
        st.success("Tarea agregada con éxito")
        st.rerun() #Here is the change.

def actualizacion_tareas():
    st.title("Actualización de Tareas")

    tareas = cargar_tareas()

    if tareas.empty:
        st.warning("No hay tareas disponibles.")
    else:
        # Visualización de estado con colores
        tareas['Estado_Color'] = tareas['estado'].apply(lambda x: "🟡" if x == "en proceso" else ("🟠" if x == "por reportar" else "🟢"))
        tareas['Estado_Display'] = tareas['Estado_Color'] + " " + tareas['estado']
        st.write(tareas[['id', 'titulo', 'Estado_Display']])

        tarea_a_editar = st.selectbox("Seleccionar tarea para editar", tareas['id'].tolist())
        tarea_seleccionada = tareas[tareas['id'] == tarea_a_editar]

        if not tarea_seleccionada.empty:
            tarea_seleccionada = tarea_seleccionada.iloc[0]

            with st.form(key='editar_tarea_form'):
                titulo = st.text_input("Título de la tarea", tarea_seleccionada['titulo'])
                try:
                    fecha_inicio = st.date_input("Fecha de inicio", datetime.strptime(tarea_seleccionada['fecha_inicio'], '%Y-%m-%d'))
                except ValueError:
                    st.error("Formato de fecha inválido en la base de datos.")
                    fecha_inicio = datetime.today()
                tipo_prueba = st.selectbox("Tipo de prueba", ["leaching", "mesh classification"], index=["leaching", "mesh classification"].index(tarea_seleccionada['tipo_prueba']))
                operador = st.selectbox("Operador", ["Brayan", "Yeferson"], index=["Brayan", "Yeferson"].index(tarea_seleccionada['operador']))
                material = st.selectbox("Material", ["over flow", "leach tails", "szg"], index=["over flow", "leach tails", "szg"].index(tarea_seleccionada['material']))
                estado = st.selectbox("Estado", ["en proceso", "por reportar", "terminado"], index=["en proceso", "por reportar", "terminado"].index(tarea_seleccionada['estado']))
                observaciones = st.text_area("Observaciones", tarea_seleccionada['observaciones'])
                foto = st.file_uploader("Subir foto", type=["png", "jpg", "jpeg"])

                submit_button = st.form_submit_button(label='Guardar cambios')

            if submit_button:
                actualizar_tarea(tarea_a_editar, titulo, str(fecha_inicio), tipo_prueba, operador, material, estado, observaciones, foto)
                st.success("Tarea actualizada con éxito")
                st.rerun() #Here is the change.
        else:
            st.warning("La tarea seleccionada no existe.")

        tareas_actualizadas = cargar_tareas()
        if not tareas_actualizadas.empty:
            for index, row in tareas_actualizadas.iterrows():
                if row['foto']:
                    st.image(row['foto'], caption=f"Foto de la tarea {row['id']}")

if __name__ == "__main__":
    main()