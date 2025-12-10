from flask import Flask, request, jsonify
import sqlite3
import traceback

app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN
# =========================================================
DB_NAME = "espejo.db"
MARGEN_TOLERANCIA = 0.01

# LISTA DE ASESORES (TU LISTA BLANCA)
LISTA_ASESORES = {
    "ALEJANDRA", "MERLI", "JUNIOR", "KARLA", "LUIS", 
    "ROSANGEL", "BEATRIZ", "ENZO", "LUISANY", "PRACELIS", 
    "ARLETIS", "JOSE", "ANGI", "AIDA", "CINDY", "YAIR", 
    "ROSIELS", "CARLOS", "NELSON"
}

# MATRIZ DE GANANCIA
MATRIZ_GANANCIA = {
    "USDT":  {"USDT": 1.00, "PYUSD": 1.20, "PEN": 0.90, "COP": 0.90, "CLP": 0.90, "ARS": 0.90, "USD": 0.90, "ECU": 0.90, "PAN": 0.90, "MXN": 0.90, "BRL": 0.90, "VES": 0.90, "PYG": 0.90, "EUR": 0.90, "DOP": 0.90, "BOB": 0.90, "CRC": 0.90, "UYU": 0.90, "OXXO": 0.90},
    "PYUSD": {"USDT": 1.20, "PYUSD": 1.00, "PEN": 1.20, "COP": 1.20, "CLP": 1.20, "ARS": 1.20, "USD": 1.20, "ECU": 0,    "PAN": 1.20, "MXN": 0,    "BRL": 1.20, "VES": 1.20, "PYG": 1.20, "EUR": 1.20, "DOP": 1.20, "BOB": 0,    "CRC": 1.20, "UYU": 0,    "OXXO": 1.20},
    "PEN":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 1.00, "COP": 0.90, "CLP": 0.90, "ARS": 0.90, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.90, "EUR": 0.90, "DOP": 0.90, "BOB": 0,    "CRC": 0.85, "UYU": 0,    "OXXO": 0.85},
    "COP":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.90, "COP": 1.00, "CLP": 0.90, "ARS": 0.90, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.90, "EUR": 0.90, "DOP": 0.90, "BOB": 0,    "CRC": 0.85, "UYU": 0,    "OXXO": 0.85},
    "CLP":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.90, "COP": 0.90, "CLP": 1.00, "ARS": 0.90, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.90, "EUR": 0.90, "DOP": 0.90, "BOB": 0,    "CRC": 0.85, "UYU": 0,    "OXXO": 0.85},
    "ARS":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.90, "COP": 0.90, "CLP": 0.90, "ARS": 1.00, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.90, "EUR": 0.90, "DOP": 0.90, "BOB": 0,    "CRC": 0.85, "UYU": 0,    "OXXO": 0.85},
    "USD":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 1.00, "ECU": 0.85, "PAN": 0,    "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0,    "BOB": 0.85, "CRC": 0,    "UYU": 0.85, "OXXO": 0.85},
    "ECU":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 1.00, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0,    "DOP": 0.85, "BOB": 0,    "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "PAN":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0,    "PAN": 1.00, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0,    "DOP": 0.85, "BOB": 0,    "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "MXN":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 1.00, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0,    "DOP": 0.85, "BOB": 0,    "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "BRL":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.90, "COP": 0.90, "CLP": 0.90, "ARS": 0.90, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0.85, "BRL": 1.00, "VES": 0.85, "PYG": 0.85, "EUR": 0,    "DOP": 0.85, "BOB": 0,    "CRC": 0.85, "UYU": 0.85, "OXXO": 0.90},
    "VES":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.94, "COP": 0.93, "CLP": 0.93, "ARS": 0.92, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 1.00, "PYG": 0.85, "EUR": 0,    "DOP": 0.85, "BOB": 0,    "CRC": 0.85, "UYU": 0.85, "OXXO": 0.90},
    "PYG":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.90, "COP": 0.90, "CLP": 0.90, "ARS": 0.90, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 1.00, "EUR": 0.85, "DOP": 0.85, "BOB": 0,    "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "EUR":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 1.00, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "DOP":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0,    "DOP": 1.00, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "BOB":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0,    "DOP": 0.85, "BOB": 1.00, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "CRC":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0,    "DOP": 0.85, "BOB": 0.85, "CRC": 1.00, "UYU": 0.85, "OXXO": 0.85},
    "UYU":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0,    "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 1.00, "OXXO": 0.85},
    "OXXO":  {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0,    "PAN": 0.85, "MXN": 0,    "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0,    "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 1.00},
}

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def safe_float(val):
    if not val: return 0.0
    s = str(val).replace(',', '.').replace('$', '').replace(' ', '')
    try: return float(s)
    except: return 0.0

def clean_key(key):
    return str(key).strip().upper()

def encontrar_valor(item, posibles):
    for nombre in posibles:
        for k, v in item.items():
            if k.strip().upper() == nombre.upper(): return v
    return 0

# --- GESTIÓN BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabla Depósitos (Espejo)
    c.execute('''CREATE TABLE IF NOT EXISTS depositos 
                 (id INTEGER PRIMARY KEY, hash_largo TEXT, nombre TEXT, monto REAL, moneda TEXT, tasa TEXT, usado INTEGER)''')
    # Tabla Tasas (Espejo) - La guardamos como JSON string en una sola columna para simplificar
    c.execute('''CREATE TABLE IF NOT EXISTS tasas 
                 (id INTEGER PRIMARY KEY, timestamp INTEGER, datos_json TEXT)''')
    conn.commit()
    conn.close()

# Inicializamos al arrancar
init_db()

# =========================================================
# ENDPOINT 1: ACTUALIZAR LA BASE DE DATOS (ESPEJO)
# =========================================================
@app.route('/actualizar_db', methods=['POST'])
def actualizar_db():
    try:
        data = request.json
        depositos = data.get('depositos', [])
        tasas = data.get('tasas', [])
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # 1. Limpiamos lo viejo
        c.execute("DELETE FROM depositos")
        c.execute("DELETE FROM tasas")
        
        # 2. Insertamos Depósitos
        nombres_monto = ['Monto', 'monto', 'MONTO', 'Amount']
        count_deps = 0
        
        for d in depositos:
            g1 = str(d.get('Grupo_1', '')).strip().upper()
            if g1 not in LISTA_ASESORES: continue # Filtro previo
            
            monto = safe_float(encontrar_valor(d, nombres_monto))
            if monto <= 0: continue
            
            moneda = str(d.get('Moneda', 'USD')).strip().upper()
            tasa_txt = str(d.get('Tasa', '')).strip().upper()
            hash_l = str(d.get('Hash_Largo', ''))
            
            c.execute("INSERT INTO depositos (hash_largo, nombre, monto, moneda, tasa, usado) VALUES (?, ?, ?, ?, ?, 0)",
                      (hash_l, g1, monto, moneda, tasa_txt))
            count_deps += 1

        # 3. Insertamos Tasas
        import json
        for t in tasas:
            try:
                ts = int(safe_float(encontrar_valor(t, ['Timestamp', 'timestamp'])))
                if ts > 0:
                    # Limpiamos claves antes de guardar
                    clean_t = {clean_key(k): safe_float(v) for k,v in t.items()}
                    c.execute("INSERT INTO tasas (timestamp, datos_json) VALUES (?, ?)", (ts, json.dumps(clean_t)))
            except: continue

        conn.commit()
        conn.close()
        return jsonify({"status": "OK", "msg": f"Base de datos actualizada. {count_deps} depósitos cargados."})

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# =========================================================
# ENDPOINT 2: CONCILIAR UN PAGO (CONSULTA SQL)
# =========================================================
@app.route('/conciliar', methods=['POST'])
def conciliar():
    try:
        pago = request.json.get('pago', {})
        
        # Datos del Pago
        g2 = str(pago.get('Grupo_2', '')).strip().upper()
        
        if g2 not in LISTA_ASESORES:
            return jsonify({"STATUS": "IGNORADO", "INFO": "Asesor no autorizado"})

        nombres_monto = ['Monto', 'monto', 'MONTO', 'Amount']
        monto_pago = safe_float(encontrar_valor(pago, nombres_monto))
        moneda_pago = str(pago.get('Moneda', 'USD')).strip().upper()
        
        ts_pago = 0
        try: ts_pago = int(safe_float(encontrar_valor(pago, ['Timestamp', 'timestamp'])))
        except: pass

        if monto_pago <= 0:
            return jsonify({"STATUS": "ERROR", "INFO": "Monto pago 0"})

        # --- CONEXIÓN DB ---
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # 1. BUSCAR TASA VIGENTE (SQL + Python)
        # Traemos la tasa más reciente anterior al pago
        c.execute("SELECT datos_json FROM tasas WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (ts_pago,))
        row_tasa = c.fetchone()
        
        if not row_tasa:
            conn.close()
            return jsonify({"STATUS": "PENDIENTE", "INFO": "Sin tasa historica"})
            
        import json
        tasa_row = json.loads(row_tasa['datos_json'])

        # 2. BUSCAR CANDIDATOS (SQL RÁPIDO)
        # "Dame los depósitos libres que se llamen igual"
        c.execute("SELECT * FROM depositos WHERE nombre = ? AND usado = 0", (g2,))
        candidatos = c.fetchall()

        if not candidatos:
            conn.close()
            return jsonify({"STATUS": "PENDIENTE", "INFO": "Sin depositos nombre"})

        # 3. MATEMÁTICA
        match_found = None
        best_diff = 1000
        info = ""

        for cand in candidatos:
            moneda_dep = cand['moneda']
            factor = MATRIZ_GANANCIA.get(moneda_dep, {}).get(moneda_pago)
            if not factor: continue

            key_in = f"{moneda_dep}+"
            key_out = f"{moneda_pago}-"
            
            val_in = tasa_row.get(key_in, 0)
            val_out = tasa_row.get(key_out, 0)

            if val_in > 0 and val_out > 0:
                teorico = cand['monto'] * (1/val_in) * val_out * factor
                diff = abs(monto_pago - teorico) / monto_pago
                
                if diff <= MARGEN_TOLERANCIA and diff < best_diff:
                    best_diff = diff
                    match_found = cand
                    info = f"Match! Diff: {round(diff*100, 2)}%"

        # 4. GUARDAR RESULTADO
        res = {}
        if match_found:
            # Marcamos como usado en la DB
            c.execute("UPDATE depositos SET usado = 1 WHERE id = ?", (match_found['id'],))
            conn.commit()
            
            res = {
                "STATUS": "ASIGNADO",
                "MATCH_HASH": match_found['hash_largo'],
                "MATCH_MONTO": match_found['monto'],
                "INFO": info
            }
        else:
            res = {"STATUS": "PENDIENTE", "INFO": info}

        conn.close()
        
        # Devolvemos el pago enriquecido
        pago.update(res)
        return jsonify(pago)

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    # Inicializar DB al arrancar por si acaso
    init_db() 
    app.run(host='0.0.0.0', port=80)
