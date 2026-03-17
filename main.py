import os
import fastf1
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Cache para que los datos carguen instantáneamente tras el primer arranque
cache_dir = 'cache'
if not os.path.exists(cache_dir): os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

# 🏁 EL MOMENTO DE LA SALIDA
# Al guardar START_TIME aquí, el segundo 0 de la carrera es cuando Render arranca el proceso
START_TIME = time.time()

@app.route('/api/v1/live')
def get_live_data():
    try:
        # Cargamos la sesión de España (puedes usar 2024 que tiene datos completos)
        session = fastf1.get_session(2024, 'Spain', 'R') 
        session.load(laps=True, telemetry=True)
        
        # 1. Calculamos el tiempo real transcurrido desde el "Apagado de Semáforos"
        tiempo_transcurrido = int(time.time() - START_TIME)
        
        # 2. Definimos la duración de vuelta (80s para Barcelona es realista)
        vuelta_actual = (tiempo_transcurrido // 80) + 1
        segundo_en_vuelta = tiempo_transcurrido % 80
        
        # Límite de la carrera (66 vueltas)
        if vuelta_actual > 66:
            return jsonify({"status": "FINISH", "message": "Carrera terminada"})

        # 3. Cogemos los 5 primeros de esa vuelta específica
        # Usamos los datos reales de esa vuelta para saber quiénes eran los líderes
        laps_vuelta = session.laps.pick_lap(vuelta_actual).sort_values(by='Time')
        top_5 = laps_vuelta.head(5)
        
        grid_data = []
        tiempo_lider = None

        for i, (index, lap) in enumerate(top_5.iterrows()):
            driver = lap['Driver']
            tel = lap.get_telemetry()
            
            # Buscamos la posición exacta en este SEGUNDO de la carrera
            # La telemetría tiene 10 muestras por segundo (10Hz)
            indice_tel = min(segundo_en_vuelta * 10, len(tel) - 1)
            muestra = tel.iloc[indice_tel]
            
            # El tiempo relativo del coche en ese punto de la pista
            tiempo_coche = muestra['Time'].total_seconds()
            
            if i == 0:
                tiempo_lider = tiempo_coche
                gap_text = "LÍDER"
            else:
                # El GAP que verás moverse segundo a segundo en el Apple Watch
                diff = tiempo_coche - tiempo_lider
                gap_text = f"+{abs(diff):.3f}s"

            grid_data.append({
                'Pos': i + 1,
                'Piloto': driver,
                'Gap': gap_text,
                'LapTime': str(lap['LapTime'])[7:15],
                'Sectores': {
                    'S1': f"{lap['Sector1Time'].total_seconds():.3f}",
                    'S2': f"{lap['Sector2Time'].total_seconds():.3f}",
                    'S3': f"{lap['Sector3Time'].total_seconds():.3f}"
                }
            })

        return jsonify({
            "status": "OK",
            "info": {
                "vuelta": vuelta_actual,
                "segundo": segundo_en_vuelta,
                "fase": "CARRERA EN VIVO"
            },
            "grid": grid_data
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
