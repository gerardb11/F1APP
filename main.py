from flask import Flask, jsonify
import fastf1
# ... otras librerías ...

app = Flask(__name__)

# RUTA QUE BUSCA EL RELOJ
@app.route('/api/v1/live')
def live_data():
    try:
        # Aquí iría tu lógica de FastF1 para sacar los datos reales
        # Por ahora, devolvemos una estructura fija para probar que el "tubo" funciona
        data = {
            "grid": [
                {"Pos": 1, "Piloto": "VERSTAPPEN", "Gap": "INTERVAL", "LapTime": "1:18.1"},
                {"Pos": 2, "Piloto": "NORRIS", "Gap": "+0.150", "LapTime": "1:18.2"},
                {"Pos": 3, "Piloto": "HAMILTON", "Gap": "+0.400", "LapTime": "1:18.5"}
            ],
            "info": {
                "vuelta": 1,
                "segundo": 10
            }
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
