from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/init', methods=['POST'])
def init():
    # Логируем информацию о новом соединении
    print("New connection initialized")
    return jsonify(message='Chat initialized!'), 200

@app.route('/message', methods=['POST'])
def message():
    data = request.json
    if 'message' in data:
        # Логируем полученное сообщение
        print(f"Received message: {data['message']}")
        # Отправляем обратно то же сообщение
        return jsonify(response=data['message']), 200
    return jsonify(error='No message found'), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)