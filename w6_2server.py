import socket

weather_data = {
    "mangalore": {"temp": "30°C", "humidity": "70%", "condition": "Sunny"},
    "delhi": {"temp": "40°C", "humidity": "50%", "condition": "Hot"},
    "chennai": {"temp": "35°C", "humidity": "60%", "condition": "Humid"},
    "bengaluru": {"temp": "25°C", "humidity": "55%", "condition": "Cloudy"}
}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 12345))
server.listen(5)
print("Server started and listening on port 12345")

while True:
    conn, addr = server.accept()
    city = conn.recv(1024).decode().lower()
    report = weather_data.get(city, "No data available for this city")
    if isinstance(report, dict):
        response = f"Weather in {city.title()}:\nTemperature: {report['temp']}\nHumidity: {report['humidity']}\nCondition: {report['condition']}"
    else:
        response = report
    conn.send(response.encode())
    conn.close()

