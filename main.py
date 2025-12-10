from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "espejo.db"

# --- 1. INICIALIZAR BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Tabla Depósitos (Limpia y simple)
    c.execute('''CREATE TABLE IF NOT EXISTS depositos 
                 (id INTEGER PRIMARY KEY, 
                  grupo_1 TEXT, 
                  monto REAL, 
                  moneda TEXT, 
                  tasa TEXT, 
                  hash_largo TEXT,
                  usado INTEGER DEFAULT 0)''')
                  
    # Tabla Tasas (Guardamos el JSON crudo por facilidad o columnas clave)
    c.execute('''CREATE TABLE IF NOT EXISTS tasas 
                 (id INTEGER PRIMARY KEY, 
                  timestamp INTEGER, 
                  datos_json TEXT)''')
                  
    conn.commit()
    conn.close()

# Ejecutamos al arrancar
init_db()

# --- FUNCION AUXILIAR PARA LIMPIAR NUMEROS ---
def safe_float(val):
    if not val: return 0.0
    s = str(val).replace(',', '.').replace('$', '').replace(' ', '')
    try: return float(s)
    except: return 0.0

# =========================================================
# ENDPOINT: LLENAR EL ESPEJO (Borra lo viejo, escribe lo nuevo)
# =========================================================
@app.route('/actualizar_espejo', methods=['POST'])
def actualizar_espejo():
    try:
        data = request.json
        depositos = data.get('depositos', [])
        tasas = data.get('tasas', [])
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # 1. BORRAR TODO (Empezamos de cero para tener el espejo fiel)
        c.execute("DELETE FROM depositos")
        c.execute("DELETE FROM tasas")
        
        # 2. INSERTAR DEPÓSITOS
        count_dep = 0
        for d in depositos:
            # Mapeo de columnas (Asegurando que existan)
            g1 = str(d.get('Grupo_1', '')).strip().upper()
            monto = safe_float(d.get('Monto', d.get('monto', 0))) # Busca "Monto" o "monto"
            moneda = str(d.get('Moneda', 'USD')).strip().upper()
            tasa = str(d.get('Tasa', '')).strip().upper()
            hash_l = str(d.get('Hash_Largo', ''))
            
            if monto > 0:
                c.execute("""INSERT INTO depositos (grupo_1, monto, moneda, tasa, hash_largo, usado) 
                             VALUES (?, ?, ?, ?, ?, 0)""", 
                             (g1, monto, moneda, tasa, hash_l))
                count_dep += 1

        # 3. INSERTAR TASAS
        import json
        count_tasas = 0
        for t in tasas:
            # Buscamos timestamp
            ts_val = t.get('Timestamp', t.get('timestamp', 0))
            ts = int(safe_float(ts_val))
            
            if ts > 0:
                # Guardamos toda la fila como JSON para no perder columnas dinámicas
                c.execute("INSERT INTO tasas (timestamp, datos_json) VALUES (?, ?)", 
                          (ts, json.dumps(t)))
                count_tasas += 1

        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "OK", 
            "mensaje": "Base de datos espejo actualizada",
            "registros_depositos": count_dep,
            "registros_tasas": count_tasas
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint de prueba para ver si el servidor vive
@app.route('/', methods=['GET'])
def health():
    return "Servidor de Base de Datos Espejo ACTIVO"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
