import asyncio
import json
import os
import time
from contextlib import asynccontextmanager

import pigpio
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

from sonar import Sonar
from webview import get_constants_view

DEBUG_MODE = True
WEBVIEW_MODE = True


async def sonar_loop(sonar: Sonar):
    # measures permanently, 100 ms per cycle (datasheet minimum is 60 ms)
    state = app.state
    while True:
        sonar.trigger()
        await asyncio.sleep(0.1)
        distance = sonar.distance
        state.obstacle = distance is not None and distance < state.SONAR_BRAKE_DISTANCE
        if state.obstacle:
            print(f"Distance: {distance:.1f} cm")
            # forward commands are blocked while the obstacle is there, so this only fires once
            if state.motor_speed > state.MOTOR_CENTER:
                await emergency_brake()


async def emergency_brake():
    # full brake for BRAKE_TIME, then neutral so the ESC doesn't switch into reverse
    state = app.state
    print("Obstacle ahead, braking")
    state.braking = True
    try:
        write_motor(state.MOTOR_CENTER - state.MOTOR_OFFSET)
        await asyncio.sleep(state.BRAKE_TIME)
    finally:
        write_motor(state.MOTOR_CENTER)
        state.braking = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    state = app.state

    if not DEBUG_MODE:
        #setup pigpio
        os.system("sudo systemctl start pigpiod")
        time.sleep(3)
        state.pi = pigpio.pi()
        time.sleep(3)

    print("Pigpio started")

    with open('constants.json') as json_data:
        constants = json.load(json_data)
        state.MOTOR_PIN = constants["MOTOR_PIN"]
        state.MOTOR_CENTER = constants["MOTOR_CENTER"]
        state.MOTOR_OFFSET = constants["MOTOR_OFFSET"]
        state.motor_speed = state.MOTOR_CENTER

        state.SERVO_PIN = constants["SERVO_PIN"]
        state.SERVO_CENTER = constants["SERVO_CENTER"]
        state.SERVO_OFFSET = constants["SERVO_OFFSET"]
        state.servo_angle = state.SERVO_CENTER

        state.SONAR_TRIGGER_PIN = constants["SONAR_TRIGGER_PIN"]
        state.SONAR_ECHO_PIN = constants["SONAR_ECHO_PIN"]
        state.SONAR_BRAKE_DISTANCE = constants["SONAR_BRAKE_DISTANCE"]
        state.BRAKE_TIME = constants["BRAKE_TIME"]

    sonar = None
    sonar_task = None
    if not DEBUG_MODE:
        sonar = Sonar(state.pi, state.SONAR_TRIGGER_PIN, state.SONAR_ECHO_PIN)
        sonar_task = asyncio.create_task(sonar_loop(sonar))
    yield

    if sonar_task is not None:
        sonar_task.cancel()
        sonar.cancel()
    if state.pi is not None:
        state.pi.stop()


app = FastAPI(lifespan=lifespan)
app.state.MOTOR_PIN = -1
app.state.MOTOR_CENTER = -1
app.state.MOTOR_OFFSET = -1
app.state.motor_speed = -1

app.state.SERVO_PIN = -1
app.state.SERVO_CENTER = -1
app.state.SERVO_OFFSET = -1
app.state.servo_angle = -1

app.state.SONAR_TRIGGER_PIN = -1
app.state.SONAR_ECHO_PIN = -1
app.state.SONAR_BRAKE_DISTANCE = -1
app.state.BRAKE_TIME = -1
app.state.obstacle = False
app.state.braking = False
app.state.pi = None

app.state.LKAS = False


def get_constants_data() -> dict:
    state = app.state
    return {
        'motorCenter': state.MOTOR_CENTER,
        'motorOffset': state.MOTOR_OFFSET,
        'servoCenter': state.SERVO_CENTER,
        'servoOffset': state.SERVO_OFFSET
    }


def get_state() -> dict:
    state = app.state
    return {
        'motor': state.motor_speed,
        'servo': state.servo_angle,
        'lkas': state.LKAS
    }


def apply_motor(speed: int) -> str | None:
    # clamps to the allowed range, writes to the pin and returns an error message if clamped
    state = app.state
    error = None
    if speed < state.MOTOR_CENTER - state.MOTOR_OFFSET:
        error = f"Speed {speed} is out of range set to minimum"
        speed = state.MOTOR_CENTER - state.MOTOR_OFFSET
    elif speed > state.MOTOR_CENTER + state.MOTOR_OFFSET:
        error = f"Speed {speed} is out of range set to maximum"
        speed = state.MOTOR_CENTER + state.MOTOR_OFFSET

    if state.braking:
        return "Emergency brake active, motor command ignored"
    if state.obstacle and speed > state.MOTOR_CENTER:
        error = "Obstacle ahead, forward blocked"
        speed = state.MOTOR_CENTER

    write_motor(speed)
    return error


def write_motor(speed: int):
    state = app.state
    if not DEBUG_MODE:
        state.pi.set_servo_pulsewidth(state.MOTOR_PIN, speed)
    state.motor_speed = speed


def apply_servo(angle: int) -> str | None:
    # clamps to the allowed range, writes to the pin and returns an error message if clamped
    state = app.state
    error = None
    if angle < state.SERVO_CENTER - state.SERVO_OFFSET:
        error = f"Angle {angle} is out of range set to minimum"
        angle = state.SERVO_CENTER - state.SERVO_OFFSET
    elif angle > state.SERVO_CENTER + state.SERVO_OFFSET:
        error = f"Angle {angle} is out of range set to maximum"
        angle = state.SERVO_CENTER + state.SERVO_OFFSET

    if not DEBUG_MODE:
        state.pi.set_servo_pulsewidth(state.SERVO_PIN, angle)
    state.servo_angle = angle
    return error


@app.get("/")
async def root():
    return {"message": "Hello World"}


# region Motor

@app.post("/drive/motor/{speed}", status_code=200)
async def set_motor_speed(speed: int):
    error = apply_motor(speed)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"motor": app.state.motor_speed}


@app.get("/drive/motor/speed", status_code=200)
async def get_motor_speed():
    return {"motor": app.state.motor_speed}

# endregion

# region Servo

@app.post("/drive/servo/{angle}", status_code=200)
async def set_servo_angle(angle: int):
    error = apply_servo(angle)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"servo": app.state.servo_angle}


@app.get("/drive/servo/angle", status_code=200)
async def get_servo_angle():
    return {"servo": app.state.servo_angle}

# endregion

# region Constants

@app.get("/drive/constants", status_code=200)
async def get_constants():
    return JSONResponse(content=get_constants_data())

# endregion

# region LKAS

@app.post("/drive/lkas/activate", status_code=200)
async def activate_lkas():
    app.state.LKAS = True
    return True


@app.post("/drive/lkas/deactivate", status_code=200)
async def deactivate_lkas():
    app.state.LKAS = False
    return False

# endregion

# region WebSocket

def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


@app.websocket("/ws/drive")
async def drive_ws(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"type": "state", **get_state(), "constants": get_constants_data()})
    try:
        while True:
            try:
                msg = json.loads(await ws.receive_text())
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "error": "Invalid JSON"})
                continue
            if not isinstance(msg, dict):
                await ws.send_json({"type": "error", "error": "Message must be a JSON object"})
                continue

            if "motor" in msg and not _is_number(msg["motor"]):
                await ws.send_json({"type": "error", "error": "motor must be a number"})
                continue
            if "servo" in msg and not _is_number(msg["servo"]):
                await ws.send_json({"type": "error", "error": "servo must be a number"})
                continue
            if "lkas" in msg and not isinstance(msg["lkas"], bool):
                await ws.send_json({"type": "error", "error": "lkas must be a boolean"})
                continue

            errors = []
            if "motor" in msg:
                errors.append(apply_motor(int(msg["motor"])))
            if "servo" in msg:
                errors.append(apply_servo(int(msg["servo"])))
            if "lkas" in msg:
                app.state.LKAS = msg["lkas"]

            response = {"type": "state", **get_state()}
            errors = [e for e in errors if e]
            if errors:
                response["error"] = "; ".join(errors)
            await ws.send_json(response)
    except WebSocketDisconnect:
        pass
    finally:
        # failsafe: stop the car when the connection drops
        apply_motor(app.state.MOTOR_CENTER)

# endregion

# region Webview

if WEBVIEW_MODE:
    @app.get("/webview/constants", response_class=HTMLResponse)
    async def view_constants():
        return get_constants_view(get_constants_data())

# endregion

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
