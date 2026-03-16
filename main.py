import os
import fastf1
from flask import Flask, jsonify

# 1. Crear carpeta de cache al principio
cache_dir = os.path.join(os.getcwd(), 'cache')
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
        # Cogemos los resultados reales de los 20 pilotos
        results = session.results
        
        for i, (index, row) in enumerate(results.iterrows()):
            # FORZAMOS TODO A TEXTO (STR) PARA EVITAR ERRORES
            pos = str(row['Position'])
            piloto = str(row['Abbreviation'])
            equipo = str(row['TeamName'])
            
            # Gap simplificado para que no haya cálculos matemáticos
            if i == 0:
                gap_val = "LÍDER"
            else:
                gap_val = f"+{i}.234s" # Texto estático para el test

            grid_data.append({
                'Pos': pos,
                'Piloto': piloto,
                'Equipo': equipo,
                'Gap': gap_val
            })

        return jsonify({
            "status": "OK",
            "gp": "Spanish GP 2024 - TEST",
            "grid": grid_data
        })
    except Exception as e:
        # Esto nos dirá exactamente en qué línea falla si algo pasa
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
