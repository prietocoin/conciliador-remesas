from flask import Flask, request, jsonify
import traceback
import bisect

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
# FUNCIONES AUXILIARES (OPTIMIZADAS)
# =========================================================
def safe_float(val):
    if not val: return 0.0
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
# ENDPOINT PRINCIPAL (LÓGICA TURBO)
# =========================================================
@app.route('/conciliar', methods=['POST'])
def conciliar():
    try:
        data = request.json
        pagos = data.get('pagos', [])
        depositos = data.get('depositos', [])
        tasas_sucias = data.get('tasas', [])

        # 1. PRE-PROCESAMIENTO DE TASAS (UNA SOLA VEZ)
        # Convertimos todo a números y ordenamos por Timestamp para búsqueda binaria
        tasas_ordenadas = []
        for tasa in tasas_sucias:
            try:
                # Extraemos el Timestamp y lo convertimos
                ts_raw = encontrar_valor_flexible(tasa, ['Timestamp', 'timestamp'])
                ts = int(safe_float(ts_raw))
                if ts == 0: continue

                # Limpiamos las claves de la fila (PEN+, etc.)
                fila_limpia = {}
                for k, v in tasa.items():
                    fila_limpia[clean_key(k)] = safe_float(v)
                
                fila_limpia['_TS'] = ts
                fila_limpia['_IDTAS'] = str(tasa.get('IDTAS', '')).strip().upper()
                tasas_ordenadas.append(fila_limpia)
            except: continue
        
        # Ordenamos por timestamp (Vital para bisect)
        tasas_ordenadas.sort(key=lambda x: x['_TS'])
        
        # Extraemos solo los timestamps para buscar rápido
        keys_timestamps = [t['_TS'] for t in tasas_ordenadas]

        # 2. PRE-PROCESAMIENTO DE DEPÓSITOS (POOL)
        nombres_monto = ['Monto', 'monto', 'MONTO', 'Amount', 'amount']
        pool = []
        
        for d in depositos:
            g1 = str(d.get('Grupo_1', '')).strip().upper()
            monto = safe_float(encontrar_valor_flexible(d, nombres_monto))
            
            if monto <= 0: continue

            pool.append({
                "original": d,
                "nombre": g1, 
                "monto": monto,
                "moneda": str(d.get('Moneda', 'USD')).strip().upper(),
                "disponible": True
            })

        resultados = []

        # 3. BUCLE DE PAGOS
        for pago in pagos:
            g2 = str(pago.get('Grupo_2', '')).strip().upper()
            monto_pago = safe_float(encontrar_valor_flexible(pago, nombres_monto))
            moneda_pago = str(pago.get('Moneda', 'USD')).strip().upper()
            
            ts_pago = 0
            ts_raw = encontrar_valor_flexible(pago, ['Timestamp', 'timestamp'])
            try: ts_pago = int(safe_float(ts_raw))
            except: pass

            info_debug = ""
            match_found = None

            # --- A. BÚSQUEDA DE TASA (BINARY SEARCH) ---
            # Encontramos la tasa vigente en 0.0001 segundos
            tasa_row = None
            if ts_pago > 0 and keys_timestamps:
                # bisect_right encuentra el punto de inserción a la derecha
                idx = bisect.bisect_right(keys_timestamps, ts_pago)
                if idx > 0:
                    tasa_row = tasas_ordenadas[idx - 1]
            
            # --- B. MATCHING ---
            if monto_pago > 0:
                candidatos = [d for d in pool if d['disponible'] and d['nombre'] == g2]

                if not candidatos:
                    info_debug = f"Sin depósitos para {g2}"
                elif not tasa_row:
                    info_debug = f"Sin tasa para fecha {ts_pago}"
                else:
                    best_diff = 1000
                    
                    for cand in candidatos:
                        factor = MATRIZ_GANANCIA.get(cand['moneda'], {}).get(moneda_pago)
                        if not factor: continue 

                        key_in = f"{cand['moneda']}+"
                        key_out = f"{moneda_pago}-"
                        
                        val_in = tasa_row.get(key_in, 0)
                        val_out = tasa_row.get(key_out, 0)
                        
                        if val_in > 0 and val_out > 0:
                            monto_teorico = cand['monto'] * (1/val_in) * val_out * factor
                            diff = abs(monto_pago - monto_teorico) / monto_pago
                            
                            if diff <= MARGEN_TOLERANCIA and diff < best_diff:
                                best_diff = diff
                                match_found = cand
                                info_debug = f"Match! Diff: {round(diff*100, 2)}%"
            else:
                info_debug = "Monto pago inválido (0)"

            # --- C. RESULTADO ---
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
                res_data = {"STATUS": "PENDIENTE", "INFO": info_debug}
            
            pago.update(res_data)
            resultados.append(pago)

        return jsonify(resultados)

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

import bisect # Importante para la optimización
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
