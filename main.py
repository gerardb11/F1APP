import fastf1
import os
from flask import Flask, jsonify
import threading
import time
from datetime import datetime

app = Flask(__name__)
master_f1_data = {"session_info": {}, "grid": []}

def update_master_engine():
    global master_f1_data
    if not os.path.exists('cache'): os.makedirs('cache')
    fastf1.Cache.enable_cache('cache')

    while True:
        try:
            # Simulamos sesión (puedes volver al modo automático cuando quieras)
            session = fastf1.get_session(2025, 'Las Vegas', 'R')
            # Cargamos Laps y TrackStatus (fundamental para banderas)
            session.load(telemetry=False, laps=True, weather=False)

            # --- DETECCIÓN DE BANDERAS Y SAFETY CAR ---
            # Miramos el estado de la pista en el último mensaje
            # 1 = Verde, 2 = Amarilla, 4 = SC, 6 = VSC, 7 = Roja
            track_status_code = session.laps.iloc[-1]['TrackStatus']
            
            status_map = {
                '1': 'GREEN',
                '2': 'YELLOW',
                '4': 'SAFETY CAR',
                '5': 'RED FLAG',
                '6': 'VIRTUAL SAFETY CAR',
                '7': 'FINISH'
            }
            current_status = status_map.get(track_status_code, "GREEN")

            drivers_list = []
            for driver_number in session.drivers:
                try:
                    results = session.laps.pick_driver(driver_number)
                    if results.empty: continue
                    last_lap = results.iloc[-1]
                    
                    # Estado individual: Si el piloto está en el pit lane
                    is_stop = "STOP" if last_lap['TrackStatus'] == '2' or last_lap['LapTime'].total_seconds() > 115 else "TRACK"

                    drivers_list.append({
                        "pos": int(last_lap['Position']),
                        "code": last_lap['Driver'],
                        "team": last_lap['Team'],
                        "time": str(last_lap['LapTime']).split('0 days ')[-1][:10],
                        "s1": f"{last_lap['Sector1Time'].total_seconds():.2f}",
                        "s2": f"{last_lap['Sector2Time'].total_seconds():.2f}",
                        "s3": f"{last_lap['Sector3Time'].total_seconds():.2f}",
                        "tyre": str(last_lap['Compound']),
                        "life": int(last_lap['TyreLife']),
                        "is_pit": is_stop
                    })
                except: continue

            # --- OBJETO MAESTRO ACTUALIZADO ---
            master_f1_data = {
                "session_info": {
                    "gp": "Las Vegas",
                    "track_status": current_status, # AQUÍ ESTÁ LA BANDERA
                    "status_code": track_status_code,
                    "last_update": datetime.now().strftime("%H:%M:%S")
                },
                "grid": sorted(drivers_list, key=lambda x: x['pos'])
            }
            print(f"✅ Status: {current_status} | {len(drivers_list)} Pilotos")
            time.sleep(30)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

@app.route('/api/v1/live')
def get_live():
    return jsonify(master_f1_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)