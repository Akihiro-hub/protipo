import streamlit as st
import sqlite3
import pandas as pd

# SQLiteデータベースのセットアップ
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

# データを挿入
def insertar_empresa(conn, datos):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO empresas (
            nombre, sector, uso_fondos, ventas_anuales, costos_deventas, costos_administrativos, costos_financieros, activos_corrientes, activos_fijos, pasivos, capital_propio, retraso_pago
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()

# データを検索
def buscar_empresa_por_id(conn, empresa_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empresas WHERE id = ?", (empresa_id,))
    return cursor.fetchone()

# 全データを取得
def obtener_todas_empresas(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empresas")
    return cursor.fetchall()

# 財務分析を計算
def calcular_indicadores(activos_corrientes, activos_fijos, pasivos, capital_propio):
    if pasivos == 0:
        pasivos = 1  # ゼロ除算を防ぐため
    if activos_corrientes + activos_fijos == 0:
        total_activos = 1  # ゼロ除算を防ぐため
    else:
        total_activos = activos_corrientes + activos_fijos
    
    razon_corriente = activos_corrientes / pasivos
    razon_capital_propio = capital_propio / total_activos
    return razon_corriente, razon_capital_propio

# Streamlitアプリの開始
st.title("Sistema de Gestión de Información para Créditos a PyMEs")

# データベースの初期化
conn = init_db()

# サイドバーの選択ボックス
opcion = st.sidebar.selectbox("Seleccionar pantalla", [
    "Ingresar información de la empresa",
    "Buscar información de la empresa"
])

if opcion == "Ingresar información de la empresa":
    st.header("Ingresar información de la empresa")

    # データ挿入フォーム（3列レイアウト）
    with st.form("empresa_form"):  # フォームの開始
        col1, col2, col3 = st.columns(3)  # 3列を作成
    
        # 1列目
        with col1:
            nombre = st.text_input("Nombre de la empresa")
            ventas_anuales = st.number_input("Ventas anuales", min_value=0, step=1)
            costos_deventas = st.number_input("Costos de ventas", min_value=0, step=1)
            costos_administrativos = st.number_input("Costos administrativos", min_value=0, step=1)
            costos_financieros = st.number_input("Costos financieros", min_value=0, step=1)
    
        # 2列目
        with col2:
            sector = st.selectbox("Sector de la empresa", [
                "Carpintería", "Comedor", "Corte y confección", "Panadería", "Herrería", "Comercio", "Otros"
            ])
            activos_corrientes = st.number_input("Activos corrientes", min_value=0, step=1)
            activos_fijos = st.number_input("Activos fijos", min_value=0, step=1)
            pasivos = st.number_input("Pasivos", min_value=0, step=1)
            capital_propio = st.number_input("Capital propio", min_value=0, step=1)
    
        # 3列目
        with col3:
            uso_fondos = st.selectbox("Uso de los fondos", [
                "Capital de trabajo", "Capital de inversión"
            ])
            retraso_pago = st.checkbox("¿Hubo retrasos en el pago?")
    
        # フォーム送信ボタン
        enviado = st.form_submit_button("Guardar datos")
    
        # データタプルの作成時にデフォルト値を設定
        if enviado:
            datos = (
                nombre,  
                sector,  
                uso_fondos,
                ventas_anuales or 0,
                costos_deventas or 0,
                costos_administrativos or 0,
                costos_financieros or 0,
                activos_corrientes or 0,
                activos_fijos or 0,
                pasivos or 0,
                capital_propio or 0,
                1 if retraso_pago else 0  # チェックボックスの値は整数型に変換
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
