from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN
# =========================================================
MARGEN_TOLERANCIA = 0.01

# =========================================================
# MATRIZ DE GANANCIA
# =========================================================
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
# FUNCIONES AUXILIARES (LIMPIEZA)
# =========================================================
def safe_float(val):
    if not val: return 0.0
    # Limpiamos $, comas y espacios
    s = str(val).replace(',', '.').replace('$', '').replace(' ', '')
    try: return float(s)
    except: return 0.0

def clean_key(key):
    return str(key).strip().upper()

def encontrar_valor_flexible(item, posibles_nombres):
    for nombre in posibles_nombres:
        if nombre in item: return item[nombre]
        if nombre.upper() in item: return item[nombre.upper()]
        if nombre.lower() in item: return item[nombre.lower()]
        if nombre.title() in item: return item[nombre.title()]
    return 0

# =========================================================
# DEBUGGER SIMPLE
# =========================================================
def debug_match(pago, pool, tasa_row):
    # Solo chequeos básicos para no saturar memoria
    if pago['monto'] <= 0:
        return f"FALLO: Monto 0. Cols: {list(pago['raw'].keys())}"
    
    if not tasa_row:
        return f"FALLO: Sin Tasa para fecha {pago['ts']}"

    candidatos = [d for d in pool if d['nombre'] == pago['nombre']]
    if not candidatos:
        return f"FALLO: Sin depósitos para {pago['nombre']}"
        
    return f"FALLO: {len(candidatos)} candidatos pero matemáticas no cuadran (Monto pago: {pago['monto']})"

# =========================================================
# TASA VIGENTE (SIMPLE Y LINEAL)
# =========================================================
def obtener_tasa_vigente(ts_pago, lista_tasas):
    if not ts_pago: return None
    tasa_candidata = None
    menor_diff = float('inf')
    
    for tasa in lista_tasas:
        try:
            # Buscamos 'Timestamp' o 'timestamp'
            ts_raw = encontrar_valor_flexible(tasa, ['Timestamp', 'timestamp'])
            ts_tasa = int(safe_float(ts_raw))
            
            diff = int(ts_pago) - ts_tasa
            
            # Si la tasa es del pasado (diff >= 0) y es la más cercana
            if 0 <= diff < menor_diff:
                menor_diff = diff
                tasa_candidata = tasa
        except: continue
        
    return tasa_candidata

# =========================================================
# ENDPOINT PRINCIPAL
# =========================================================
@app.route('/conciliar', methods=['POST'])
def conciliar():
    try:
        data = request.json
        pagos = data.get('pagos', [])
        depositos = data.get('depositos', [])
        tasas_list = data.get('tasas', [])

        # 1. Preparar Pool de Depósitos
        nombres_monto = ['Monto', 'monto', 'MONTO', 'Amount']
        pool = []
        
        for d in depositos:
            g1 = str(d.get('Grupo_1', '')).strip().upper()
            raw_monto = encontrar_valor_flexible(d, nombres_monto)
            monto = safe_float(raw_monto)
            
            if monto <= 0: continue

            pool.append({
                "original": d,
                "nombre": g1, 
                "monto": monto,
                "moneda": str(d.get('Moneda', 'USD')).strip().upper(),
                "disponible": True
            })

        resultados = []

        # 2. Bucle de Pagos
        for pago in pagos:
            g2 = str(pago.get('Grupo_2', '')).strip().upper()
            raw_monto_p = encontrar_valor_flexible(pago, nombres_monto)
            monto_p = safe_float(raw_monto_p)
            
            p_data = {
                "raw": pago,
                "nombre": g2,
                "monto": monto_p,
                "moneda": str(pago.get('Moneda', 'USD')).strip().upper(),
                "ts": None
            }
            
            ts_raw = encontrar_valor_flexible(pago, ['Timestamp', 'timestamp'])
            try: p_data['ts'] = int(safe_float(ts_raw))
            except: pass

            tasa_row = obtener_tasa_vigente(p_data['ts'], tasas_list)
            
            match_found = None
            info_debug = ""

            # --- PROTECCIÓN DIVISIÓN POR CERO ---
            if p_data['monto'] > 0 and tasa_row:
                candidatos = [d for d in pool if d['disponible'] and d['nombre'] == p_data['nombre']]
                best_diff = 1000
                
                for cand in candidatos:
                    factor = MATRIZ_GANANCIA.get(cand['moneda'], {}).get(p_data['moneda'])
                    if not factor: continue 

                    # Nombres de columnas en la hoja de tasas
                    key_in = f"{cand['moneda']}+"
                    key_out = f"{p_data['moneda']}-"
                    
                    # Usamos búsqueda flexible también para las tasas (por si "COP+" es "cop+")
                    val_in_raw = encontrar_valor_flexible(tasa_row, [key_in, key_in.lower(), key_in.upper()])
                    val_out_raw = encontrar_valor_flexible(tasa_row, [key_out, key_out.lower(), key_out.upper()])
                    
                    val_in = safe_float(val_in_raw)
                    val_out = safe_float(val_out_raw)
                    
                    # --- AQUÍ EVITAMOS EL ERROR ---
                    if val_in > 0 and val_out > 0:
                        monto_teorico = cand['monto'] * (1/val_in) * val_out * factor
                        diff = abs(p_data['monto'] - monto_teorico) / p_data['monto']
                        
                        if diff <= MARGEN_TOLERANCIA and diff < best_diff:
                            best_diff = diff
                            match_found = cand
                            info_debug = f"Match! Diff: {round(diff*100, 2)}%"

            # Resultado
            res_data = {}
            if match_found:
                match_found['disponible'] = False
                res_data = {
                    "STATUS": "ASIGNADO",
                    "MATCH_HASH": match_found['original'].get('Hash_Largo'),
                    "MATCH_MONTO": match_found['original'].get('Monto'),
                    "INFO": info_debug
                }
            else:
                debug_msg = debug_match(p_data, pool, tasa_row)
                res_data = {"STATUS": "PENDIENTE", "INFO": debug_msg}
            
            pago.update(res_data)
            resultados.append(pago)

        return jsonify(resultados)

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
