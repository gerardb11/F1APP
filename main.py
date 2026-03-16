import fastf1
from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/api/v1/live')
def get_spain_gp_data():
    try:
        # Cargamos el GP de España 2025 (Race)
        session = fastf1.get_session(2025, 'Spain', 'R')
        session.load(laps=True, telemetry=False, weather=False)
        
        # Información general del GP
        total_laps = 66 # Montmeló son 66 vueltas
        track_status_code = session.session_status.iloc[-1] if not session.session_status.empty else "1"
        
        # Diccionario para traducir el estado de pista
        status_map = {"1": "Track Clear", "2": "Yellow Flag", "4": "Safety Car", "6": "Virtual Safety Car", "7": "Red Flag"}
        current_status = status_map.get(str(track_status_code), "Track Clear")

        leader_time = session.results.iloc[0]['Time']
        grid_data = []

        # Cogemos a todos los pilotos
        for index, row in session.results.iterrows():
            # Sacamos la última vuelta para ver los sectores
            driver_laps = session.laps.pick_driver(row['Abbreviation'])
            last_lap = driver_laps.iloc[-1] if not driver_laps.empty else None
            
            gap = str(row['Time'] - leader_time).split()[-1] if index > 0 else "LÍDER"
            
            grid_data.append({
                'Pos': int(row['Position']),
                'Piloto': row['Abbreviation'],
                'Equipo': row['TeamName'],
                'Gap': gap,
                'S1': str(last_lap['Sector1Time']).split()[-1] if last_lap is not None else "---",
                'S2': str(last_lap['Sector2Time']).split()[-1] if last_lap is not None else "---",
                'S3': str(last_lap['Sector3Time']).split()[-1] if last_lap is not None else "---",
                'Vueltas': f"{int(last_lap['LapNumber'])}/{total_laps}" if last_lap is not None else f"0/{total_laps}"
            })

        return jsonify({
            "status": "LIVE",
            "gp": "Spanish Grand Prix 2025",
            "track_condition": current_status,
            "grid": grid_data
        })
    except Exception as e:
        return jsonify({"status": "waiting", "message": "Cargando datos del GP...", "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
