import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import random

# SQLiteデータベースのセットアップ
def init_db():
    conn = sqlite3.connect("empresa_db.sqlite")
    cursor = conn.cursor()

    # テーブルを削除して再作成する場合
    # cursor.execute("DROP TABLE IF EXISTS empresas")

    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            sector TEXT,
            uso_fondos TEXT,
            no_empleados REAL,
            ventas_anuales REAL,
            costos_deventas REAL,
            costos_administrativos REAL, 
            costos_financieros REAL,
            activos_corrientes REAL,
            activos_fijos REAL,
            pasivos REAL,
            capital_propio REAL,
            monto_préstamos REAL,
            plazo_préstamos REAL,
            tasa_préstamos REAL,
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
            nombre, sector, uso_fondos, no_empleados, ventas_anuales, costos_deventas, costos_administrativos, 
            costos_financieros, activos_corrientes, activos_fijos, pasivos, capital_propio, monto_préstamos, plazo_préstamos, tasa_préstamos, retraso_pago
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    
# データベースの初期化
conn = init_db()

# サイドバーの選択ボックス
opcion = st.sidebar.selectbox("Seleccionar pantalla", [
    "Inscribir datos de PyME",
    "Analizar PyME",
    "Analizar moras"
])

if opcion == "Inscribir datos de PyME":
    # Streamlitアプリの開始
    st.title("Sistema de Gestión de Información para Créditos a PyMEs")
    st.header("Inscribir datos de PyME solicitante")
    
    # 最新の企業IDを取得
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM empresas")
    max_id = cursor.fetchone()[0]
    nuevo_id = max_id + 1 if max_id is not None else 1  # 既存の最大ID + 1、または1

    # 企業IDを表示
    st.write(f"**ID de la nueva empresa:** {nuevo_id}")

    # データ挿入フォーム（3列レイアウト）
    with st.form("empresa_form"):  # フォームの開始
        col1, col2, col3, col4 = st.columns(4)  # 3列を作成
    
        # 1列目
        with col1:
            st.write("###### :blue[Perfil principal (Perfilamiento)]") 
            nombre = st.text_input("Nombre de la empresa")
            sector = st.selectbox("Sector de la empresa", ["Carpintería", "Comedor", "Panadería", "Herrería", "Comercio", "Otros"])
            uso_fondos = st.selectbox("Uso de fondo solicitado", ["Capital de trabajo", "Capital de inversión"])
            no_empleados = st.number_input("Número de trabajadores", min_value=0, step=1)
 
        # 2列目
        with col2:
            st.write("###### :blue[Balance General (Análisis)]") 
            activos_corrientes = st.number_input("Activos corrientes", min_value=0, step=1)
            activos_fijos = st.number_input("Activos fijos", min_value=0, step=1)
            pasivos = st.number_input("Pasivos", min_value=0, step=1)
            capital_propio = st.number_input("Capital propio", min_value=0, step=1)
    
        # 3列目
        with col3:
            st.write("###### :blue[Estado Resultados (Análisis)]") 
            ventas_anuales = st.number_input("Ventas anuales", min_value=0, step=1)
            costos_deventas = st.number_input("Costos de ventas", min_value=0, step=1)
            costos_administrativos = st.number_input("Costos administrativos", min_value=0, step=1)
            costos_financieros = st.number_input("Costos financieros", min_value=0, step=1)

        # 4列目
        with col4:
            st.write("###### :blue[Créditos (Seguimiento)]") 
            monto_préstamos = st.number_input("monto de créditos (lps.)", min_value=0, step=1)
            plazo_préstamos = st.number_input("plazo de créditos (meses)", min_value=0, step=1)
            tasa_préstamos = st.number_input("tasa interés (%)", min_value=0, step=1)
            retraso_pago = st.checkbox("¿Hubo demora en pagos?")

        
        # フォーム送信ボタン
        enviado = st.form_submit_button("Guardar datos")
    
        # データタプルの作成時にデフォルト値を設定
        if enviado:
            datos = (
                nombre,  
                sector,  
                uso_fondos,
                no_empleados or 0,
                ventas_anuales or 0,
                costos_deventas or 0,
                costos_administrativos or 0,
                costos_financieros or 0,
                activos_corrientes or 0,
                activos_fijos or 0,
                pasivos or 0,
                capital_propio or 0,
                monto_préstamos or 0,
                plazo_préstamos or 0,
                tasa_préstamos or 0,
                1 if retraso_pago else 0  # チェックボックスの値は整数型に変換
            )
            insertar_empresa(conn, datos)
            st.success("¡Información guardada exitosamente!")

    # 「Borrar todos los datos registrados」ボタン
    borrar_datos = st.button("Borrar todos los datos registrados")
    if borrar_datos:
        # 全データを削除する処理
        cursor.execute("DELETE FROM empresas")
        conn.commit()
        st.success("Todos los datos han sido eliminados.")

elif opcion == "Analizar PyME":
    st.header("Analizar PyME solicitante (Dashboard)")

    # 検索フォーム
    empresa_id = st.number_input("Ingrese el código de la empresa", min_value=1, step=1)
    buscar = st.button("Buscar")

    if buscar:
        empresa = buscar_empresa_por_id(conn, empresa_id)

        if empresa:
            # 財務分析の計算
            def calcular_indicadores(ventas_anuales, costos_deventas, costos_administrativos, costos_financieros, capital_propio, activos_corrientes, activos_fijos):
                if costos_financieros == 0:
                    costos_financieros = 1  # ゼロ除算を防ぐため
                if ventas_anuales == 0:
                    ventas_anuales = 1  # ゼロ除算を防ぐため
                if activos_corrientes + activos_fijos == 0:
                    total_activos = 1  # ゼロ除算を防ぐため
                else:
                    total_activos = activos_corrientes + activos_fijos
            
                times_interest_earned = (ventas_anuales - costos_deventas - costos_administrativos) / costos_financieros
                operating_income_margin = ((ventas_anuales - costos_deventas - costos_administrativos) / ventas_anuales) * 100
                razon_capital_propio = (capital_propio / total_activos) * 100
            
                return times_interest_earned, operating_income_margin, razon_capital_propio
            
            
            # 全企業の平均値を計算
            todas_empresas = obtener_todas_empresas(conn)
            
            df_empresas = pd.DataFrame(todas_empresas, columns=[
                "id", "nombre", "sector", "uso_fondos", "no_empleados", "ventas_anuales", "costos_deventas", "costos_administrativos",
                "costos_financieros", "activos_corrientes", "activos_fijos", "pasivos", "capital_propio", "monto_préstamos", "plazo_préstamos", "tasa_préstamos", "retraso_pago"
            ])
        
            # 各指標の平均値を計算
            promedio_tie = (
                (df_empresas["ventas_anuales"] - df_empresas["costos_deventas"] - df_empresas["costos_administrativos"])
                / df_empresas["costos_financieros"]
            ).mean()
            
            promedio_margin = (
                ((df_empresas["ventas_anuales"] - df_empresas["costos_deventas"] - df_empresas["costos_administrativos"])
                 / df_empresas["ventas_anuales"]) * 100
            ).mean()
            
            promedio_capital_propio = (
                (df_empresas["capital_propio"] / (df_empresas["activos_corrientes"] + df_empresas["activos_fijos"])) * 100
            ).mean()
            
            # 現在の企業データに基づく指標を計算
            times_interest_earned, operating_income_margin, razon_capital_propio = calcular_indicadores(
                empresa[5], empresa[6], empresa[7], empresa[8], empresa[12], empresa[9], empresa[10]
            )
            
            # 結果の表示
            col1, col2 = st.columns(2)  # 2列を作成
            
            with col1:
                st.write("##### :green[Indicadores principales]")
                st.write(f"**Nombre PyME:** {empresa[1]}")
                st.write(f"**Razón de veces cubriendo el interés (TIE):** {times_interest_earned:.1f} veces (Promedio: {promedio_tie:.1f} veces)")
                st.write(f"**Margen operativo:** {operating_income_margin:.1f}% (Promedio: {promedio_margin:.1f}%)")
                st.write(f"**Razón de capital propio:** {razon_capital_propio:.1f}% (Promedio: {promedio_capital_propio:.1f}%)")

                # Warnings
                if operating_income_margin <= 0.05:
                    st.warning("La rentabilidad del negocio puede ser baja.")
                if times_interest_earned <= 1.3 or razon_capital_propio <= 35:
                    st.warning("El negocio puede estar altamente endeudado, considerando su nivel de ganancias o nivel del capital propio.")
            
            with col2:
                # 損益分岐点分析
                st.write("##### :green[Análisis del punto de equilibrio]")
                # empresaからデータを取得
                ventas_anuales = empresa[5] or 0  # ventas_anualesは6番目の列
                costos_deventas = empresa[6] or 0  # costos_deventasは7番目の列
                costos_administrativos = empresa[7] or 0  # costos_administrativos
                costos_financieros = empresa[8] or 0  # costos_financieros
                
                # 安全対策：ゼロ除算とNone値のチェック
                if ventas_anuales == 0 or costos_deventas is None or ventas_anuales is None:
                    st.error("No se puede calcular el punto de equilibrio porque las ventas anuales o los costos de ventas son 0 o no están definidos.")
                else:
                    # コスト比率を計算
                    variable_ratio = costos_deventas / ventas_anuales
                    if variable_ratio >= 1:
                        st.error("El punto de equilibrio no puede ser calculado porque los costos variables superan o igualan las ventas anuales.")
                    else:
                        # 損益分岐点の売上を計算
                        breakeven_sales = (costos_administrativos + costos_financieros) / (1 - variable_ratio)
                        margen_seguridad = ((ventas_anuales-breakeven_sales)/ventas_anuales)*100
                
                        st.write(f"Ventas anuales en el punto de equilibrio: {breakeven_sales:.0f} Lps")
                        st.write(f"Ratio de margen de seguridad: {margen_seguridad:.1f} %")
    
                        # Warnings
                        if margen_seguridad <= 10:
                            st.warning("La rentabilidad del negocio puede ser baja, considerando su margen de seguridad.")
                
                        # 損益分岐点のグラフを描画
                        fig, ax = plt.subplots()
                        
                        sales_range = list(range(int(breakeven_sales * 0.8), int(breakeven_sales * 1.2), 100))
                        total_costs = [costos_administrativos + costos_financieros + (variable_ratio * s) for s in sales_range]
                        
                        ax.plot(sales_range, total_costs, color='skyblue', label="Costos totales (Costos fijos + Costos variables)", marker='o')
                        ax.plot(sales_range, sales_range, color='orange', label="Ventas", marker='o')
                        
                        ax.set_title("Estimación del punto de equilibrio")
                        ax.set_xlabel("Ventas (Lps)")
                        ax.set_ylabel("Costos y ventas (Lps)")
                        
                        ax.axvline(breakeven_sales, color='red', linestyle='--', label=f"Punto de equilibrio: {breakeven_sales:.1f} Lps")
                        
                        ax.fill_between(sales_range, total_costs, sales_range, where=[s > breakeven_sales for s in sales_range], color='skyblue', alpha=0.3, interpolate=True)
                        
                        mid_x = breakeven_sales * 1.1
                        mid_y = (max(total_costs) + max(sales_range)) / 2
                        ax.text(mid_x, mid_y, "Ganancia = Área del color azul claro", color="blue", fontsize=7, ha="left")
                
                        ax.legend()  # Show the legend
                        st.pyplot(fig)
                        st.write("Nota: Costos de venta se clasifican en costos variables y los otros costos en fijos, en est análisis.")

        else:
            st.error("No se encontró la empresa con el ID especificado.")

elif opcion == "Analizar moras":
    st.header("Estimar la probabilidad de mora por IA")
    st.write("La estimacion se realiza por SVM, un método de aprendisaje automatico, en base a las PyMEs registrados en base de datos. Como esta herramienta es prototipo, no se presenta cifra analizada sino cifra seleccionada al azar.")
    
    # 入力フィールドの設定
    uso_fondos = st.selectbox("Uso de fondos (1=Capital de trabajo, 0=Inversion)", [1, 0])
    monto_préstamos = st.slider("Monto de préstamo (Lps)", 10000, 10000000, step=10000)
    capital_propio = st.slider("Razón de capital propio (%)", 1, 100)
    times_interest_earned = st.slider("Times interest earned (veces)", 0.5, 5.0, step=0.1)
    operating_margin = st.slider("Margen operativo (%)", 0.0, 50.0, step=0.5)
    safety_margin = st.slider("Margen de seguridad (%)", 0.0, 50.0, step=0.5)
    
    # モデルのトレーニングと予測
    if st.button("Calcular probabilidad de mora"):
        # 0.1%～25.0%の範囲でランダムな値を生成
        prediction_prob = random.uniform(0.1, 25.0)
    
        # 結果の表示
        if prediction_prob > 12:  # 高い確率（例: 12%以上の場合にエラー表示）
            st.error(f"**Predicción:** Hay alta probabilidad de mora ({prediction_prob:.2f}%).")
        else:  # 低い確率（例: 12%未満の場合に成功表示）
            st.success(f"**Predicción:** Baja probabilidad de mora ({prediction_prob:.2f}%).")

        # データフレーム作成
        # todas_empresas = obtener_todas_empresas(conn)
        # if todas_empresas:
            # df = pd.DataFrame(todas_empresas, columns=["id", "nombre", "sector", "uso_fondos", "monto_préstamos", "ventas_anuales", "costos_deventas", "costos_administrativos", "costos_financieros", "activos_corrientes", "activos_fijos", "pasivos", "capital_propio", "retraso_pago"])
            
            # df["uso_fondos"] = df["Uso_fondos"].apply(lambda x: 1 if x == "capital de trabajo" else 0)
            # df["times interest earned"] = ((df["ventas_anuales"] - df["Costos_deventas"] - df["costos_administrativos"]) / (df["Costos_financieros"] + 1e-6))
            # df["Operating margin"] = ( ((df["Ventas_anuales"] - df["costos_deventas"] - df["costos_administrativos"]) / df["ventas_anuales"]) * 100)
            # df["Safety margin"] = (((df["ventas_anuales"] -  (df["costos_deventas"] + df["costos_administrativos"])) / df["ventas_anuales"]) * 100)
            
            # 必要な列を選択
            # features = df[["uso_fondos", "monto_préstamos", "Times interest earned", "Operating margin", "Safety margin"]]
            # target = df["retraso_pago"]
            
            # SVMモデルのトレーニング
            # from sklearn.svm import SVC
            # from sklearn.model_selection import train_test_split
            # from sklearn.preprocessing import StandardScaler
            
            # X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
            # scaler = StandardScaler()
            # X_train_scaled = scaler.fit_transform(X_train)
            # X_test_scaled = scaler.transform(X_test)
            
            # model = SVC(probability=True, random_state=42)
            # model.fit(X_train_scaled, y_train)
            
            # 入力データのスケーリング
            # input_data = scaler.transform([[uso_fondos, monto_préstamos, capital_propio, times_interest_earned, operating_margin, safety_margin]])
            
            # 予測結果
            # prediction = model.predict(input_data)
            # prediction_prob = model.predict_proba(input_data)[0][1]
            
            # 結果の表示
            # if prediction[0] == 1:
                # st.error(f"**Predicción:** Hay alta probabilidad de mora ({prediction_prob:.2%}).")
            # else:
                # st.success(f"**Predicción:** Baja probabilidad de mora ({prediction_prob:.2%}).")
 










