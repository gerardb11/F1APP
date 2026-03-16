import fastf1
from flask import Flask, jsonify

app = Flask(__name__)
fastf1.Cache.enable_cache('cache') 

@app.route('/api/v1/live')
def get_live_data():
    try:
        # Cargamos España 2024 (un GP que ya conocemos)
        session = fastf1.get_session(2024, 'Spain', 'R')
        session.load(laps=False, telemetry=False, weather=False)
        
        grid_data = []
        results = session.results.head(15) # Cogemos los 15 primeros
        
        for index, row in results.iterrows():
            # Limpiamos los datos para que siempre sean números o strings válidos
            try:
                pos = int(row['Position'])
            except:
                pos = 0

            grid_data.append({
                'Pos': pos,
                'Piloto': str(row['Abbreviation']),
                'Equipo': str(row['TeamName']),
                'Gap': 'LÍDER' if index == 0 else f"+{index*1.5}s"
            })

        return jsonify({
            "status": "OK",
            "gp": "Spanish GP 2024 - Estable",
            "grid": grid_data
        })
    except Exception as e:
        # Este mensaje nos dirá exactamente qué falla si ocurre algo
        return jsonify({
            "status": "error", 
            "message": "Ajustando motores...",
            "debug": str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
