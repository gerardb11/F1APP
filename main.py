import os
import fastf1
from flask import Flask, jsonify

# --- 1. CREAR LA CARPETA ANTES DE NADA ---
cache_dir = 'cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
# -----------------------------------------

app = Flask(__name__)

# Configurar el cache
fastf1.Cache.enable_cache(cache_dir) 

@app.route('/api/v1/live')
def get_live_data():
    try:
        # Cargamos el GP de España 2024 (un clásico para testear)
        session = fastf1.get_session(2024, 'Spain', 'R')
        session.load(laps=False, telemetry=False, weather=False)
        
        grid_data = []
        # Cogemos los 15 primeros
        for index, row in session.results.head(15).iterrows():
            grid_data.append({
                'Pos': str(row['Position']),
                'Piloto': str(row['Abbreviation']),
                'Equipo': str(row['TeamName']),
                'Gap': 'LÍDER' if index == 0 else f"+{index*1.5}s"
            })

        return jsonify({
            "status": "OK",
            "gp": "Spanish GP 2024",
            "grid": grid_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # Render usa el puerto de la variable de entorno PORT
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
