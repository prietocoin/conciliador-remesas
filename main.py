from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN
# =========================================================
MARGEN_TOLERANCIA = 0.01

# LISTA BLANCA DE ASESORES (Solo estos se procesan)
LISTA_ASESORES = {
    "ALEJANDRA", "MERLI", "JUNIOR", "KARLA", "LUIS", 
    "ROSANGEL", "BEATRIZ", "ENZO", "LUISANY", "PRACELIS", 
    "ARLETIS", "JOSE", "ANGI", "AIDA", "CINDY", "YAIR", 
    "ROSIELS", "CARLOS", "NELSON"
}

# =========================================================
# MATRIZ DE GANANCIA (TRANSCRITA DE TU IMAGEN)
# =========================================================
# Fila (Vertical) = Moneda Entrada (Depósito)
# Columna (Horizontal) = Moneda Salida (Pago)
MATRIZ_GANANCIA = {
    "USDT":  {"USDT": 1.00, "PYUSD": 1.20, "PEN": 0.90, "COP": 0.90, "CLP": 0.90, "ARS": 0.90, "USD": 0.90, "ECU": 0.90, "PAN": 0.90, "MXN": 0.90, "BRL": 0.90, "VES": 0.90, "PYG": 0.90, "EUR": 0.90, "DOP": 0.90, "BOB": 0.90, "CRC": 0.90, "UYU": 0.90, "OXXO": 0.90},
    "PYUSD": {"USDT": 1.20, "PYUSD": 1.00, "PEN": 1.20, "COP": 1.20, "CLP": 1.20, "ARS": 1.20, "USD": 1.20, "ECU": 1.20, "PAN": 1.20, "MXN": 1.20, "BRL": 1.20, "VES": 1.20, "PYG": 1.20, "EUR": 1.20, "DOP": 1.20, "BOB": 1.20, "CRC": 1.20, "UYU": 1.20, "OXXO": 1.20},
    "PEN":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 1.00, "COP": 0.90, "CLP": 0.90, "ARS": 0.90, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.80, "VES": 0.80, "PYG": 0.90, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "COP":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.80, "COP": 1.00, "CLP": 0.90, "ARS": 0.90, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.80, "VES": 0.80, "PYG": 0.90, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "CLP":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.80, "COP": 0.90, "CLP": 1.00, "ARS": 0.90, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.80, "VES": 0.80, "PYG": 0.90, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "ARS":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.80, "COP": 0.90, "CLP": 0.90, "ARS": 1.00, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.80, "VES": 0.80, "PYG": 0.90, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "USD":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 1.00, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "ECU":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 1.00, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "PAN":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0.85, "PAN": 1.00, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "MXN":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 1.00, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "BRL":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.90, "COP": 0.90, "CLP": 0.90, "ARS": 0.90, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 1.00, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.90},
    "VES":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.94, "COP": 0.93, "CLP": 0.93, "ARS": 0.92, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 1.00, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.90},
    "PYG":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.90, "COP": 0.90, "CLP": 0.90, "ARS": 0.90, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 1.00, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "EUR":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 1.00, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "DOP":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 1.00, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "BOB":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 1.00, "CRC": 0.85, "UYU": 0.85, "OXXO": 0.85},
    "CRC":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 1.00, "UYU": 0.85, "OXXO": 0.85},
    "UYU":   {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 1.00, "OXXO": 0.85},
    "OXXO":  {"USDT": 0.90, "PYUSD": 1.20, "PEN": 0.85, "COP": 0.85, "CLP": 0.85, "ARS": 0.85, "USD": 0.85, "ECU": 0.85, "PAN": 0.85, "MXN": 0.85, "BRL": 0.85, "VES": 0.85, "PYG": 0.85, "EUR": 0.85, "DOP": 0.85, "BOB": 0.85, "CRC": 0.85, "UYU": 0.85, "OXXO": 1.00},
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

# =========================================================
# HELPER: CHISMOSO (DEBUGGER)
# =========================================================
def debug_match(pago, pool, tasa_row):
    logs = []
    
    if pago['monto'] <= 0:
        return "FALLO: Monto del Pago es 0 o inválido."

    candidatos_nombre = [d for d in pool if d['nombre'] == pago['nombre']]
    if not candidatos_nombre:
        return f"FALLO: Asesor '{pago['nombre']}' no tiene depósitos."
    
    if not tasa_row:
        return f"FALLO: Sin Tasa IDTAS para timestamp {pago['ts']}."

    logs.append(f"Cand: {len(candidatos_nombre)}")
    
    for cand in candidatos_nombre:
        if not cand['disponible']:
            logs.append(f"Dep({cand['monto']}): USADO.")
            continue

        factor = MATRIZ_GANANCIA.get(cand['moneda'], {}).get(pago['moneda'])
        if not factor:
            logs.append(f"Dep({cand['moneda']}->{pago['moneda']}): Sin Matriz.")
            continue
            
        key_in = f"{cand['moneda']}+"
        key_out = f"{pago['moneda']}-"
        
        val_in = safe_float(tasa_row.get(key_in, 0))
        val_out = safe_float(tasa_row.get(key_out, 0))
        
        if val_in == 0:
            logs.append(f"ERR: Tasa '{key_in}' es 0.")
            continue
            
        teorico = cand['monto'] * (1/val_in) * val_out * factor
        diff = abs(pago['monto'] - teorico) / pago['monto']
        logs.append(f"Dep({cand['monto']})->Calc({round(teorico,2)}) Diff={round(diff*100, 2)}%")

    return " | ".join(logs)[:500] 

# =========================================================
# HELPER: TASA POR TIEMPO
# =========================================================
def obtener_tasa_vigente(ts_pago, lista_tasas):
    if not ts_pago: return None
    tasa_candidata = None
    menor_diff = float('inf')
    
    for tasa in lista_tasas:
        try:
            ts_tasa = int(safe_float(encontrar_valor(tasa, ['Timestamp', 'timestamp'])))
            diff = int(ts_pago) - ts_tasa 
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
        
        tasas_sucias = data.get('tasas', [])
        tasas_list = []
        for tasa in tasas_sucias:
            clean_row = {}
            for k, v in tasa.items():
                clean_row[clean_key(k)] = v
            tasas_list.append(clean_row)

        # Pool de Depósitos
        nombres_monto = ['Monto', 'monto', 'MONTO', 'Amount']
        pool = []
        for d in depositos:
            g1 = str(d.get('Grupo_1', '')).strip().upper()
            raw_monto = encontrar_valor(d, nombres_monto)
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

        for pago in pagos:
            g2 = str(pago.get('Grupo_2', '')).strip().upper()
            
            # --- FILTRO LISTA BLANCA ---
            if g2 not in LISTA_ASESORES:
                pago['STATUS'] = "IGNORADO"
                pago['INFO'] = f"Asesor '{g2}' no autorizado"
                resultados.append(pago)
                continue

            raw_monto_p = encontrar_valor(pago, nombres_monto)
            monto_p = safe_float(raw_monto_p)
            
            p_data = {
                "nombre": g2,
                "monto": monto_p,
                "moneda": str(pago.get('Moneda', 'USD')).strip().upper(),
                "ts": None
            }
            
            ts_raw = encontrar_valor(pago, ['Timestamp', 'timestamp'])
            try: p_data['ts'] = int(safe_float(ts_raw))
            except: pass

            tasa_row = obtener_tasa_vigente(p_data['ts'], tasas_list)
            match_found = None
            info_debug = ""

            if p_data['monto'] > 0 and tasa_row:
                candidatos = [d for d in pool if d['disponible'] and d['nombre'] == p_data['nombre']]
                best_diff = 1000
                
                for cand in candidatos:
                    factor = MATRIZ_GANANCIA.get(cand['moneda'], {}).get(p_data['moneda'])
                    if not factor: continue 

                    key_in = f"{cand['moneda']}+"
                    key_out = f"{p_data['moneda']}-"
                    
                    val_in = safe_float(tasa_row.get(key_in, 0))
                    val_out = safe_float(tasa_row.get(key_out, 0))
                    
                    if val_in > 0 and val_out > 0:
                        monto_teorico = cand['monto'] * (1/val_in) * val_out * factor
                        diff = abs(p_data['monto'] - monto_teorico) / p_data['monto']
                        
                        if diff <= MARGEN_TOLERANCIA and diff < best_diff:
                            best_diff = diff
                            match_found = cand
                            info_debug = f"Match! Diff: {round(diff*100, 2)}% | Factor: {factor}"

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
