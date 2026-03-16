import os
import fastf1
import time
from flask import Flask, jsonify

app = Flask(__name__)

cache_dir = 'cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

START_TIME = time.time()

@app.route('/api/v1/live')
def get_live_data():
    try:
        session = fastf1.get_session(2025, 'Spain', 'R')
        session.load(laps=True, telemetry=False, weather=False)
        
        # Simulación: cada 80 seg = 1 vuelta
        segundos_transcurridos = int(time.time() - START_TIME)
        vuelta_actual = (segundos_transcurridos // 80) + 1
        if vuelta_actual > 66: vuelta_actual = 66
        
        # --- LA CLAVE: Ordenar por quién pasó primero en esta vuelta ---
        vueltas_de_esta_lap = session.laps.pick_lap(vuelta_actual).sort_values(by='Time')
        top_5_vueltas = vueltas_de_esta_lap.head(5)
        
        grid_data = []
        tiempo_lider = None

        for i, (index, lap) in enumerate(top_5_vueltas.iterrows()):
            abbr = lap['Driver']
            
            # Tiempo de vuelta real
            lap_time_str = str(lap['LapTime']).split('days ')[-1][2:9]
            
            # Cálculo del Gap real respecto al líder en esa vuelta
            if i == 0:
                tiempo_lider = lap['Time']
                gap_text = "LÍDER"
            else:
                gap_diff = (lap['Time'] - tiempo_lider).total_seconds()
                gap_text = f"+{gap_diff:.3f}s"

            grid_data.append({
                'Pos': i + 1,
                'Piloto': abbr,
                'LapTime': lap_time_str,
                'Gap': gap_text
            })

        return jsonify({
            "status": "OK",
            "gp": "España 2025 (Simulación Real)",
            "info": {
                "vuelta": vuelta_actual,
                "total_vueltas": 66,
                "reloj_carrera": f"{segundos_transcurridos}s"
            },
            "grid": grid_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
