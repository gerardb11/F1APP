import os
import fastf1
from flask import Flask, jsonify

# 1. Crear carpeta de cache
cache_dir = 'cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

app = Flask(__name__)
fastf1.Cache.enable_cache(cache_dir) 

@app.route('/api/v1/live')
def get_live_data():
    try:
        # Cargamos el GP de España 2024
        session = fastf1.get_session(2024, 'Spain', 'R')
        session.load(laps=False, telemetry=False, weather=False)
        
        grid_data = []
        # Cogemos los resultados reales
        for index, row in session.results.head(15).iterrows():
            # Evitamos errores matemáticos forzando a que todo sea texto seguro
            posicion = str(row['Position'])
            abreviatura = str(row['Abbreviation'])
            equipo = str(row['TeamName'])
            
            # Si es el primero es LÍDER, si no, ponemos un tiempo fijo para el test
            gap_texto = "LÍDER" if index == 0 else f"+{index * 1.5}s"

            grid_data.append({
                'Pos': posicion,
                'Piloto': abreviatura,
                'Equipo': equipo,
                'Gap': gap_texto
            })

        return jsonify({
            "status": "OK",
            "gp": "Spanish GP 2024 - TEST",
            "grid": grid_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
