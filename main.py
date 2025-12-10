from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN GLOBAL
# =========================================================
MARGEN_TOLERANCIA = 0.01

# 1. LISTA BLANCA (ASESORES)
LISTA_ASESORES = {
    "ALEJANDRA", "MERLI", "JUNIOR", "KARLA", "LUIS", 
    "ROSANGEL", "BEATRIZ", "ENZO", "LUISANY", "PRACELIS", 
    "ARLETIS", "JOSE", "ANGI", "AIDA", "CINDY", "YAIR", 
    "ROSIELS", "CARLOS", "NELSON"
}

# 2. MATRIZ DE GANANCIA (CORREGIDA)
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
    s = str(val).replace(',', '.').replace('$', '').replace(' ', '')
    try: return float(s)
    except: return 0.0

def clean_key(key):
    return str(key).strip().upper()

def encontrar_valor(item, posibles):
    """Busca un valor probando mayúsculas, minúsculas y títulos"""
    for nombre in posibles:
        for k, v in item.items():
            if k.strip().upper() == nombre.upper(): return v
    return 0

def limpiar_tasas(lista_tasas):
    nuevas = []
    for t in lista_tasas:
        new_row = {}
        for k,v in t.items():
            new_row[clean_key(k)] = v
        nuevas.append(new_row)
    return nuevas

# =========================================================
# SERVICIO 1: FILTRADO (LISTA BLANCA + REDUCCIÓN)
# =========================================================
@app.route('/servicio_filtrar', methods=['POST'])
def filtrar():
    try:
        data = request.json
        pago = data.get('pago', {})
        depositos = data.get('depositos', [])

        g2 = str(pago.get('Grupo_2', '')).strip().upper()
        
        # --- 1. ¿ES ASESOR VÁLIDO? ---
        if g2 not in LISTA_ASESORES:
            return jsonify({
                "candidatos": [],
                "status": "IGNORADO",
                "info": f"Asesor '{g2}' no está en la lista blanca"
            })

        # --- 2. BUSCAR DEPÓSITOS DEL MISMO NOMBRE ---
        # "Quiero los depósitos donde Grupo_1 sea igual a g2"
        candidatos = []
        nombres_monto = ['Monto', 'monto', 'MONTO', 'Amount']

        for d in depositos:
            g1 = str(d.get('Grupo_1', '')).strip().upper()
            
            if g1 == g2:
                # Normalizamos datos para el siguiente paso
                monto = safe_float(encontrar_valor(d, nombres_monto))
                
                # Ignorar depósitos en 0 para evitar errores después
                if monto <= 0: continue

                candidatos.append({
                    "original": d,
                    "monto": monto,
                    "moneda": str(d.get('Moneda', 'USD')).strip().upper()
                })
        
        if not candidatos:
            return jsonify({
                "candidatos": [], 
                "status": "PENDIENTE", 
                "info": f"No hay depósitos para el asesor {g2}"
            })

        return jsonify({"candidatos": candidatos, "status": "BUSCANDO"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================================
# SERVICIO 2: TASA (BÚSQUEDA TEMPORAL)
# =========================================================
@app.route('/servicio_tasa', methods=['POST'])
def tasa():
    try:
        data = request.json
        ts_pago_raw = data.get('timestamp')
        tasas = data.get('tasas', [])
        
        # Limpiamos tasas al vuelo
        tasas_limpias = limpiar_tasas(tasas)
        
        ts_pago = int(safe_float(ts_pago_raw))
        if ts_pago == 0: return jsonify({"tasa": None, "msg": "Timestamp pago 0"})

        tasa_elegida = None
        menor_diff = float('inf')

        for t in tasas_limpias:
            try:
                # Buscamos Timestamp con búsqueda flexible
                ts_tasa = int(safe_float(encontrar_valor(t, ['Timestamp', 'timestamp'])))
                if ts_tasa == 0: continue

                diff = ts_pago - ts_tasa
                # Si es del pasado (diff >= 0) y es la más cercana
                if 0 <= diff < menor_diff:
                    menor_diff = diff
                    tasa_elegida = t
            except: continue
            
        return jsonify(tasa_elegida if tasa_elegida else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================================
# SERVICIO 3: CÁLCULO (MATEMÁTICA PURA)
# =========================================================
@app.route('/servicio_calculo', methods=['POST'])
def calculo():
    try:
        data = request.json
        
        # Si el paso 1 dijo IGNORADO, no calculamos nada
        if data.get('status_previo') == "IGNORADO":
             return jsonify({"status": "IGNORADO", "info": data.get('info_previo')})
        
        if data.get('status_previo') == "PENDIENTE":
             return jsonify({"status": "PENDIENTE", "info": data.get('info_previo')})

        pago = data.get('pago', {})
        candidatos = data.get('candidatos', [])
        tasa_row = data.get('tasa', {})

        if not candidatos: return jsonify({"status": "PENDIENTE", "info": "Sin candidatos recibidos"})
        if not tasa_row: return jsonify({"status": "PENDIENTE", "info": "Sin tasa encontrada"})

        # Datos del Pago
        monto_pago = safe_float(encontrar_valor(pago, ['Monto', 'monto']))
        moneda_pago = str(pago.get('Moneda', 'USD')).strip().upper()

        if monto_pago <= 0: return jsonify({"status": "ERROR", "info": "Monto pago es 0"})

        best_diff = 1000
        match_found = None
        info = ""

        # --- BUCLE MATEMÁTICO ---
        for cand in candidatos:
            moneda_dep = cand['moneda']
            
            # 1. Matriz
            factor = MATRIZ_GANANCIA.get(moneda_dep, {}).get(moneda_pago)
            if not factor: continue

            # 2. Tasas
            key_in = f"{moneda_dep}+"
            key_out = f"{moneda_pago}-"
            
            # Búsqueda flexible de columnas en la tasa (ej: 'COP+' o 'cop+')
            val_in_raw = encontrar_valor(tasa_row, [key_in])
            val_out_raw = encontrar_valor(tasa_row, [key_out])
            
            val_in = safe_float(val_in_raw)
            val_out = safe_float(val_out_raw)

            # --- PROTECCIÓN DIVISIÓN POR CERO ---
            if val_in > 0 and val_out > 0:
                teorico = cand['monto'] * (1/val_in) * val_out * factor
                diff = abs(monto_pago - teorico) / monto_pago
                
                if diff <= MARGEN_TOLERANCIA and diff < best_diff:
                    best_diff = diff
                    match_found = cand
                    info = f"Match! Diff: {round(diff*100, 2)}% | Factor: {factor}"

        if match_found:
            return jsonify({
                "status": "ASIGNADO",
                "hash": match_found['original'].get('Hash_Largo'),
                "monto": match_found['original'].get('Monto'),
                "info": info
            })
        else:
            # Diagnóstico si falló
            return jsonify({
                "status": "PENDIENTE", 
                "info": f"Matemática falló. Mínima diff: {round(best_diff*100,2) if best_diff!=1000 else 'N/A'}%"
            })

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
