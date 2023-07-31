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

    if status is None or version is None:
        return (
            jsonify({"status": "error", "message": "status and version are required"}),
            400,
        )

    version = int(version)

    log_str = f"Probe instance: {instance} status: {status} version: {version}"

    if name:
        log_str += f" name: {name}"

    if location and len(location) == 2:
        log_str += f" location: {location}"

    conn = get_db_connection()
    cur = conn.cursor()
    if location and len(location) == 2:
        cur.execute(
            "insert into public.probe (instance, status, version, location) values (%s, %s, %s, POINT(%s, %s))",
            (instance, status, version, location[0], location[1]),
        )
    else:
        cur.execute(
            "insert into public.probe (instance, status, version) values (%s, %s, %s)",
            (instance, status, version),
        )
    conn.commit()
    cur.close()
    conn.close()

    app.logger.info(log_str)
    return jsonify({"status": "ok"})
