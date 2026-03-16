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

# El servidor guarda la hora de inicio para saber cuándo empezó la vuelta 1
START_TIME = time.time()

@app.route('/api/v1/live')
def get_live_data():
    try:
        # Cargamos los datos reales del GP de España 2025
        session = fastf1.get_session(2025, 'Spain', 'R')
        session.load(laps=True, telemetry=False, weather=False)
        
        # --- CÁLCULO DE VUELTA REAL ---
        segundos_transcurridos = int(time.time() - START_TIME)
        # Cada 80 segundos pasamos de vuelta
        vuelta_actual = (segundos_transcurridos // 80) + 1
        
        # Límite de la carrera (66 vueltas)
        if vuelta_actual > 66: vuelta_actual = 66
        
        grid_data = []
        top_5 = session.results.head(5)
        
        for i, (index, row) in enumerate(top_5.iterrows()):
            abbr = row['Abbreviation']
            
            # Buscamos el tiempo REAL que hizo este piloto en esta vuelta específica
            try:
                laps_driver = session.laps.pick_driver(abbr)
                lap_info = laps_driver[laps_driver['LapNumber'] == vuelta_actual].iloc[0]
                # Formato: 1:19.432
                lap_time = str(lap_info['LapTime']).split('days ')[-1][2:9]
            except:
                lap_time = "BOXES"

            # Gap dinámico basado en la vuelta
            gap_real = "LÍDER" if i == 0 else f"+{0.8 * vuelta_actual * (i+1):.3f}s"

            grid_data.append({
                'Pos': i + 1,
                'Piloto': abbr,
                'Equipo': row['TeamName'],
                'LapTime': lap_time,
                'Gap': gap_real
            })

        return jsonify({
            "status": "OK",
            "gp": "España 2025 (Simulación en vivo)",
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
