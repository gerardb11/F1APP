from flask import Flask, jsonify
import fastf1
import os

app = Flask(__name__)

# CONFIGURACIÓN DE CACHÉ (Vital para no saturar la RAM)
cache_dir = 'cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

@app.route('/api/v1/live')
def get_f1_data():
    try:
        # 1. Cargamos solo lo básico (Race del GP de España 2024 como ejemplo)
        # Cargamos 'laps' pero NO telemetría pesada
        session = fastf1.get_session(2024, 'Spain', 'R')
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        
        # 2. Obtenemos la última vuelta de cada piloto
        results = []
        for driver in session.drivers:
            driver_laps = session.laps.pick_driver(driver)
            if not driver_laps.empty:
                last_lap = driver_laps.iloc[-1]
                # Sacamos el nombre del piloto (abreviado: VER, NOR, etc.)
                driver_info = session.get_driver(driver)
                
                results.append({
                    "Pos": int(last_lap['Position']),
                    "Piloto": driver_info['Abbreviation'],
                    "Gap": str(last_lap['Time']).split()[-1][:8], # Formato simple
                    "LapTime": str(last_lap['LapTime']).split()[-1][2:9]
                })

        # Ordenar por posición
        results.sort(key=lambda x: x['Pos'])

        # 3. Respuesta JSON
        return jsonify({
            "grid": results,
            "info": {
                "vuelta": int(session.laps['LapNumber'].max()),
                "segundo": 0
            }
        })

    except Exception as e:
        print(f"Error en boxes: {e}")
        return jsonify({"error": "Fallo al cargar datos", "details": str(e)}), 500

@app.route('/')
def home():
    return "Servidor F1 Activo - Busca /api/v1/live"

if __name__ == '__main__':
    # Usamos el puerto que Render nos asigna
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
