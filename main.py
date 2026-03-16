import os
import fastf1
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Configuración de caché
cache_dir = 'cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

@app.route('/api/v1/live')
def get_live_data():
    try:
        # --- CARGAMOS LA CARRERA REAL DE 2025 ---
        session = fastf1.get_session(2025, 'Spain', 'R')
        session.load(laps=True, telemetry=False, weather=False)
        
        # Calculamos en qué vuelta "estamos" para el test (cambia cada 2 seg)
        segundos_actuales = int(time.time())
        vuelta_test = (segundos_actuales // 2) % 66 
        if vuelta_test == 0: vuelta_test = 1
        
        grid_data = []
        # Cogemos los 5 primeros de la clasificación final de 2025
        top_5 = session.results.head(5)
        
        for i, (index, row) in enumerate(top_5.iterrows()):
            abbr = row['Abbreviation']
            equipo = row['TeamName']
            
            # Buscamos el tiempo de vuelta real de 2025
            try:
                laps_driver = session.laps.pick_driver(abbr)
                lap_info = laps_driver[laps_driver['LapNumber'] == vuelta_test].iloc[0]
                # Formato del tiempo: 1:18.432
                lap_time = str(lap_info['LapTime']).split('days ')[-1][2:9]
            except:
                lap_time = "--:--.---"

            # Gap dinámico para que el reloj "se mueva" cada 2 segundos
            movimiento = (segundos_actuales % 10) / 7
            gap_real = "LÍDER" if i == 0 else f"+{1.5 + (i * 0.8) + movimiento:.3f}s"

            grid_data.append({
                'Pos': i + 1,
                'Piloto': abbr,
                'Equipo': equipo,
                'LapTime': lap_time,
                'Gap': gap_real
            })

        return jsonify({
            "status": "OK",
            "gp": "España 2025 - Datos Reales",
            "vuelta_actual": vuelta_test,
            "grid": grid_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
