# ... (imports y matriz igual que antes) ...

# AGREGAMOS ESTO PARA QUE SEPAS EXACTAMENTE QUE PASA
def debug_match(pago, pool, tasa_row, matriz):
    logs = []
    
    # 1. ¿Encontramos el nombre?
    candidatos_nombre = [d for d in pool if d['nombre'] == pago['nombre_pago']]
    if not candidatos_nombre:
        return f"FALLO NOM: Busque '{pago['nombre_pago']}' en {len(pool)} deps. Nada."
    
    # 2. ¿Tenemos Tasa?
    if not tasa_row:
        return "FALLO TASA: No hay tasa para esa fecha."

    # 3. ¿Matemática?
    logs.append(f"Candidatos: {len(candidatos_nombre)}")
    
    for cand in candidatos_nombre:
        # Intenta calcular y guarda el error
        try:
            factor = matriz.get(cand['moneda'], {}).get(pago['moneda_pago'])
            if not factor:
                logs.append(f"Dep({cand['monto']}): Sin factor matriz {cand['moneda']}->{pago['moneda_pago']}")
                continue
                
            key_in = f"{cand['moneda']}+"
            key_out = f"{pago['moneda_pago']}-"
            val_in = float(tasa_row.get(key_in, 0))
            val_out = float(tasa_row.get(key_out, 0))
            
            if val_in == 0:
                logs.append(f"Dep({cand['monto']}): Tasa {key_in} es 0")
                continue

            teorico = cand['monto'] * (1/val_in) * val_out * factor
            diff = abs(pago['monto_pago'] - teorico) / pago['monto_pago']
            
            logs.append(f"Dep({cand['monto']})->Teorico({round(teorico,2)}) Diff={round(diff*100, 2)}%")
        except Exception as e:
            logs.append(f"Error calculo: {str(e)}")

    return " | ".join(logs)[:250] # Cortamos si es muy largo

# ... (resto del código igual) ...

# DENTRO DEL BUCLE FOR, CAMBIA LA PARTE DE "INFO" POR ESTO:
            
            # (Justo antes de guardar el resultado)
            if not match_found:
                # SI FALLÓ, EJECUTAMOS EL DEBUGGER PARA DECIRTE POR QUÉ
                debug_data = {
                    "nombre_pago": p_nombre,
                    "monto_pago": p_monto,
                    "moneda_pago": p_moneda
                }
                info_debug = debug_match(debug_data, pool, tasa_row, MATRIZ_GANANCIA)
