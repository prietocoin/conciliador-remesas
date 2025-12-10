from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN: TOLERANCIA +/- 1%
# =========================================================
MARGEN_TOLERANCIA = 0.01

# =========================================================
# MATRIZ DE GANANCIA (Fila=Entrada/Depósito, Col=Salida/Pago)
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
# HELPER: BUSCAR TASA HISTÓRICA POR TIEMPO
# =========================================================
def obtener_tasa_vigente(ts_pago, lista_tasas):
    if not ts_pago: return None
    tasa_candidata = None
    menor_diff = float('inf')
    
    for tasa in lista_tasas:
        try:
            ts_tasa = int(tasa.get('Timestamp', 0))
            diff = int(ts_pago) - ts_tasa 
            # Buscamos la tasa más reciente anterior al pago
            if 0 <= diff < menor_diff:
                menor_diff = diff
                tasa_candidata = tasa
        except: continue
    return tasa_candidata

@app.route('/conciliar', methods=['POST'])
def conciliar():
    try:
        data = request.json
        pagos = data.get('pagos', [])
        depositos = data.get('depositos', [])
        tasas_list = data.get('tasas', [])

        # --- PREPARACIÓN DEL POOL DE DEPÓSITOS ---
        pool = []
        for d in depositos:
            # GRUPO_1 (Base Depósitos) -> Nombre del Asesor
            # Usamos el nombre COMPLETO (sin .split)
            g1 = str(d.get('Grupo_1', '')).strip().upper()
            
            pool.append({
                "original": d,
                "nombre": g1, 
                "monto": float(d.get('Monto', 0) or 0),
                "moneda": str(d.get('Moneda', 'USD')).strip().upper(),
                "disponible": True
            })

        resultados = []

        # --- BUCLE DE CONCILIACIÓN UNO A UNO ---
        for pago in pagos:
            
            # 1. Datos del Pago
            # GRUPO_2 (Base Pagos) -> Nombre del Asesor
            # Usamos el nombre COMPLETO
            g2 = str(pago.get('Grupo_2', '')).strip().upper()
            p_nombre = g2
            
            p_monto = float(pago.get('Monto', 0) or 0)
            p_moneda = str(pago.get('Moneda', 'USD')).strip().upper()
            p_ts = int(pago.get('Timestamp', 0)) if pago.get('Timestamp') else None

            # 2. Obtener Tasa Vigente (Time Travel)
            tasa_row = obtener_tasa_vigente(p_ts, tasas_list)
            
            match_found = None
            info_debug = "Sin candidatos validos"

            # 3. Filtrar Candidatos
            # Condición: Nombre idéntico y que esté disponible
            candidatos = [d for d in pool if d['disponible'] and d['nombre'] == p_nombre]

            if not candidatos:
                info_debug = f"No hay depósitos para el asesor {p_nombre}"
            elif not tasa_row:
                info_debug = "No se encontró tasa histórica vigente"
            
            # 4. Matemática Financiera
            if candidatos and tasa_row:
                best_diff = 1000 # Diferencia inicial infinita
                
                for cand in candidatos:
                    # A. Factor de Matriz
                    # Moneda Entrada (Depósito) -> Moneda Salida (Pago)
                    factor_ganancia = MATRIZ_GANANCIA.get(cand['moneda'], {}).get(p_moneda)
                    
                    if not factor_ganancia or factor_ganancia == 0:
                        continue 

                    # B. Tasas de Cambio (+/-)
                    key_in = f"{cand['moneda']}+" # Tasa Entrada (Compra)
                    key_out = f"{p_moneda}-"      # Tasa Salida (Venta)
                    
                    try:
                        val_in = float(tasa_row.get(key_in, 0))
                        val_out = float(tasa_row.get(key_out, 0))
                        
                        if val_in > 0 and val_out > 0:
                            # C. Fórmula Maestra
                            # (MontoDep / TasaIn) * TasaOut * Factor
                            monto_teorico = cand['monto'] * (1/val_in) * val_out * factor_ganancia
                            
                            # D. Diferencia Porcentual
                            diff = abs(p_monto - monto_teorico) / p_monto
                            
                            # E. Evaluación de Tolerancia
                            if diff <= MARGEN_TOLERANCIA and diff < best_diff:
                                best_diff = diff
                                match_found = cand
                                info_debug = f"Match! Diff: {round(diff*100, 2)}% | Factor: {factor_ganancia}"
                    except: continue

            # 5. Guardar Resultado y Actualizar Pool
            res_data = {}
            if match_found:
                match_found['disponible'] = False # TACHADO (Ya no se usa)
                res_data = {
                    "STATUS": "ASIGNADO",
                    "MATCH_HASH": match_found['original'].get('Hash_Largo'),
                    "MATCH_MONTO": match_found['original'].get('Monto'),
                    "INFO": info_debug
                }
            else:
                res_data = {
                    "STATUS": "PENDIENTE", 
                    "INFO": info_debug
                }
            
            # Unimos resultado al pago
            pago.update(res_data)
            resultados.append(pago)

        return jsonify(resultados)

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
