from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN
# =========================================================
MARGEN_TOLERANCIA = 0.01

# =========================================================
# MATRIZ DE GANANCIA NATIVA
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
# HELPER: CHISMOSO (DEBUGGER)
# =========================================================
def debug_match(pago, pool, tasa_row):
    logs = []
    
    # 1. Buscamos candidatos por Nombre
    candidatos_nombre = [d for d in pool if d['nombre'] == pago['nombre']]
    if not candidatos_nombre:
        return f"FALLO: No hay depósitos para el asesor '{pago['nombre']}'."
    
    # 2. ¿Tenemos Tasa Histórica?
    if not tasa_row:
        return "FALLO: No se encontró una Tasa (IDTAS) para la fecha del pago."

    logs.append(f"Cand: {len(candidatos_nombre)}")
    
    for cand in candidatos_nombre:
        if not cand['disponible']:
            logs.append(f"Dep({cand['monto']}): YA USADO.")
            continue

        try:
            factor = MATRIZ_GANANCIA.get(cand['moneda'], {}).get(pago['moneda'])
            if not factor:
                logs.append(f"Dep({cand['moneda']}->{pago['moneda']}): Sin factor matriz.")
                continue
                
            key_in = f"{cand['moneda']}+"
            key_out = f"{pago['moneda']}-"
            
            # --- PROTECCIÓN CONTRA CERO ---
            val_in = float(tasa_row.get(key_in, 0))
            val_out = float(tasa_row.get(key_out, 0))
            
            if val_in == 0:
                logs.append(f"Dep({cand['monto']}): Tasa '{key_in}' es 0.")
                continue
                
            if val_out == 0:
                logs.append(f"Dep({cand['monto']}): Tasa '{key_out}' es 0.")
                continue

            teorico = cand['monto'] * (1/val_in) * val_out * factor
            diff = abs(pago['monto'] - teorico) / pago['monto']
            
            logs.append(f"Dep({cand['monto']}) -> Calc({round(teorico,2)}) Diff={round(diff*100, 2)}%")
        except Exception as e:
            logs.append(f"Error calc: {str(e)}")

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
            ts_tasa = int(tasa.get('Timestamp', 0))
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
        tasas_list = data.get('tasas', [])

        # Pool de Depósitos
        pool = []
        for d in depositos:
            g1 = str(d.get('Grupo_1', '')).strip().upper()
            try: monto = float(d.get('Monto', 0) or 0)
            except: monto = 0.0
            
            pool.append({
                "original": d,
                "nombre": g1, 
                "monto": monto,
                "moneda": str(d.get('Moneda', 'USD')).strip().upper(),
                "disponible": True
            })

        resultados = []

        # Bucle Uno a Uno
        for pago in pagos:
            g2 = str(pago.get('Grupo_2', '')).strip().upper()
            
            p_data = {
                "nombre": g2,
                "monto": 0.0,
                "moneda": str(pago.get('Moneda', 'USD')).strip().upper(),
                "ts": None
            }
            try: p_data['monto'] = float(pago.get('Monto', 0) or 0)
            except: pass
            
            if pago.get('Timestamp'):
                try: p_data['ts'] = int(pago.get('Timestamp'))
                except: pass

            # Tasa Vigente
            tasa_row = obtener_tasa_vigente(p_data['ts'], tasas_list)
            
            match_found = None
            info_debug = ""

            # Filtro Candidatos
            candidatos = [d for d in pool if d['disponible'] and d['nombre'] == p_data['nombre']]

            if candidatos and tasa_row:
                best_diff = 1000
                
                for cand in candidatos:
                    # 1. Matriz
                    factor = MATRIZ_GANANCIA.get(cand['moneda'], {}).get(p_data['moneda'])
                    if not factor: continue 

                    # 2. Tasas
                    key_in = f"{cand['moneda']}+"
                    key_out = f"{p_data['moneda']}-"
                    
                    try:
                        val_in = float(tasa_row.get(key_in, 0))
                        val_out = float(tasa_row.get(key_out, 0))
                        
                        # --- PROTECCIÓN ANTI-CRASH ---
                        if val_in > 0 and val_out > 0:
                            monto_teorico = cand['monto'] * (1/val_in) * val_out * factor
                            diff = abs(p_data['monto'] - monto_teorico) / p_data['monto']
                            
                            if diff <= MARGEN_TOLERANCIA and diff < best_diff:
                                best_diff = diff
                                match_found = cand
                                info_debug = f"Match! Diff: {round(diff*100, 2)}% | Factor: {factor}"
                    except: continue

            # Guardar Resultado
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
                # DEBUG CUANDO FALLA
                debug_msg = debug_match(p_data, pool, tasa_row)
                res_data = {"STATUS": "PENDIENTE", "INFO": debug_msg}
            
            pago.update(res_data)
            resultados.append(pago)

        return jsonify(resultados)

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
