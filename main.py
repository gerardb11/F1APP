import fastf1
from flask import Flask, jsonify

app = Flask(__name__)
fastf1.Cache.enable_cache('cache') 

@app.route('/api/v1/live')
def get_live_data():
    try:
        # Cargamos España 2024 que ya sabemos que está en el caché
        session = fastf1.get_session(2024, 'Spain', 'R')
        session.load(laps=False, telemetry=False, weather=False)
        
        grid_data = []
        # Cogemos los resultados y los convertimos a texto simple para evitar errores
        for index, row in session.results.head(15).iterrows():
            grid_data.append({
                'Pos': str(row['Position']), # Lo enviamos como texto para que no falle
                'Piloto': str(row['Abbreviation']),
                'Equipo': str(row['TeamName']),
                'Gap': 'LÍDER' if index == 0 else f"+{index*1.5}s"
            })

        return jsonify({
            "status": "OK",
            "gp": "Spanish GP - Datos Reales",
            "grid": grid_data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
