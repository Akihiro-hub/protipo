import streamlit as st
import sqlite3
import pandas as pd

# データベース接続
def init_db():
    conn = sqlite3.connect("empresa_db.sqlite")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            sector TEXT,
            uso_fondos TEXT,
            ventas_anuales REAL,
            costos_deventas REAL,
            costos_administrativos REAL,
            costos_financieros REAL,
            activos_corrientes REAL,
            activos_fijos REAL,
            pasivos REAL,
            capital_propio REAL,
            retraso_pago INTEGER
        )
    """)
    conn.commit()
    return conn

# 企業情報の挿入
def insertar_empresa(conn, datos):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO empresas (
            nombre, sector, uso_fondos, ventas_anuales, costos_deventas, costos_administrativos, costos_financieros,
            activos_corrientes, activos_fijos, pasivos, capital_propio, retraso_pago
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()

# Streamlitアプリの開始
st.title("Sistema de Gestión de Información para Créditos a PyMEs")

# データベースの初期化
conn = init_db()

# 新規企業の入力フォーム
with st.form("empresa_form"):  # フォームの開始
    # 企業IDを表示
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM empresas")
    max_id = cursor.fetchone()[0]
    nuevo_id = max_id + 1 if max_id is not None else 1  # 最後のID + 1を生成

    st.write(f"**ID de la nueva empresa:** {nuevo_id}")  # 新しい企業IDを表示
    
    # 入力フォーム
    nombre = st.text_input("Nombre de la empresa")
    sector = st.selectbox("Sector de la empresa", ["Carpintería", "Comedor", "Corte y confección", "Panadería", "Herrería", "Comercio", "Otros"])
    uso_fondos = st.selectbox("Uso de los fondos", ["Capital de trabajo", "Capital de inversión"])
    ventas_anuales = st.number_input("Ventas anuales", min_value=0, step=1)
    
    # 他の入力フィールドも追加する

    # フォーム送信ボタン
    enviado = st.form_submit_button("Guardar datos")
    
    if enviado:
        # 新しい企業情報をデータベースに挿入
        datos = (
            nombre or "N/A",
            sector or "Otros",
            uso_fondos or "Capital de trabajo",
            ventas_anuales or 0,
            # 他のフィールドのデータも追加
        )
        insertar_empresa(conn, datos)
        st.success("¡Información guardada exitosamente!")



elif opcion == "Buscar información de la empresa":
    st.header("Buscar información de la empresa")

    # 検索フォーム
    empresa_id = st.number_input("Ingrese el número de la empresa", min_value=1, step=1)
    buscar = st.button("Buscar")

    if buscar:
        empresa = buscar_empresa_por_id(conn, empresa_id)

        if empresa:
            st.subheader("Información de la empresa")
            st.write(f"**Nombre:** {empresa[1]}")
            st.write(f"**Sector:** {empresa[2]}")
            st.write(f"**Uso de fondos:** {empresa[3]}")

            # 財務分析の計算
            razon_corriente, razon_capital_propio = calcular_indicadores(
                empresa[4], empresa[5], empresa[6], empresa[7]
            )

            # 全企業の平均値を計算
            todas_empresas = obtener_todas_empresas(conn)

            df_empresas = pd.DataFrame(todas_empresas, columns=[
                "ID", "Nombre", "Sector", "Uso_fondos", "Ventas_anuales", "Costos_deventas", "Costos_administrativos",
                "Costos_financieros", "Activos_corrientes", "Activos_fijos", "Pasivos", "Capital_propio", "Retraso_pago"
            ])

            promedio_corriente = (df_empresas["Activos_corrientes"] / df_empresas["Pasivos"]).mean()
            promedio_capital_propio = (df_empresas["Capital_propio"] / (df_empresas["Activos_corrientes"] + df_empresas["Activos_fijos"])).mean()

            st.subheader("Resultados financieros")
            st.write(f"**Razón corriente:** {razon_corriente:.2f} (Promedio: {promedio_corriente:.2f})")
            st.write(f"**Razón de capital propio:** {razon_capital_propio:.2f} (Promedio: {promedio_capital_propio:.2f})")
        else:
            st.error("No se encontró la empresa con el ID especificado.")
