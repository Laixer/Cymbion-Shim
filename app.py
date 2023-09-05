import os
from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras

psycopg2.extras.register_uuid()

app = Flask(__name__)
app.logger.setLevel("INFO")


def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
    )
    return conn


@app.post("/api/v1/<uuid:instance>/probe")
def probe(instance):
    status = request.json.get("status")
    version = request.json.get("version")
    name = request.json.get("name")
    location = request.json.get("location")
    altitude = request.json.get("altitude")
    speed = request.json.get("speed")
    satellites = request.json.get("satellites")
    memory = request.json.get("memory")
    swap = request.json.get("swap")
    cpu_1 = request.json.get("cpu_1")
    cpu_5 = request.json.get("cpu_5")
    cpu_15 = request.json.get("cpu_15")
    uptime = request.json.get("uptime")
    rpm = request.json.get("rpm")

    if status is None or version is None:
        return (
            jsonify({"status": "error", "message": "status and version are required"}),
            400,
        )

    version = int(version)

    log_str = f"Probe instance: {instance} status: {status} version: {version}"

    if name:
        log_str += f" name: {name}"

    conn = get_db_connection()
    cur = conn.cursor()

    latitude = 0
    longitude = 0

    if location and len(location) == 2:
        latitude = location[0]
        longitude = location[1]

    cur.execute(
        "insert into public.probe (instance, status, version, location, altitude, speed, satellites, memory, swap, cpu_1, cpu_5, cpu_15, uptime, rpm) values (%s, %s, %s, POINT(%s, %s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            instance,
            status,
            version,
            latitude,
            longitude,
            altitude,
            speed,
            satellites,
            memory,
            swap,
            cpu_1,
            cpu_5,
            cpu_15,
            uptime,
            rpm,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()

    app.logger.info(log_str)
    return jsonify({"status": "ok"})
