import json
import os
import time
from contextlib import asynccontextmanager

import pigpio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from webview import get_constants_view

DEBUG_MODE = True
WEBVIEW_MODE = True


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
    yield

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


@app.get("/")
async def root():
    return {"message": "Hello World"}


# region Motor

@app.post("/drive/motor/{speed}", status_code=200)
async def set_motor_speed(speed: int):
    state = app.state
    if speed < state.MOTOR_CENTER - state.MOTOR_OFFSET:
        state.motor_speed = state.MOTOR_CENTER - state.MOTOR_OFFSET
        raise HTTPException(status_code=400, detail=f"Speed {speed} is out of range set to minimum")
    elif speed > state.MOTOR_CENTER + state.MOTOR_OFFSET:
        state.motor_speed = state.MOTOR_CENTER + state.MOTOR_OFFSET
        raise HTTPException(status_code=400, detail=f"Speed {speed} is out of range set to maximum")

    if not DEBUG_MODE:
        state.pi.set_servo_pulsewidth(state.MOTOR_PIN, speed)
    state.motor_speed = speed
    return {"motor": state.motor_speed}


@app.get("/drive/motor/speed", status_code=200)
async def get_motor_speed():
    return {"motor": app.state.motor_speed}

# endregion

# region Servo

@app.post("/drive/servo/{angle}", status_code=200)
async def set_servo_angle(angle: int):
    state = app.state
    if angle < state.SERVO_CENTER - state.SERVO_OFFSET:
        state.servo_angle = state.SERVO_CENTER - state.SERVO_OFFSET
        raise HTTPException(status_code=400, detail=f"Angle {angle} is out of range set to minimum")
    elif angle > state.SERVO_CENTER + state.SERVO_OFFSET:
        state.servo_angle = state.SERVO_CENTER + state.SERVO_OFFSET
        raise HTTPException(status_code=400, detail=f"Angle {angle} is out of range set to maximum")

    if not DEBUG_MODE:
        state.pi.set_servo_pulsewidth(state.SERVO_PIN, angle)
    state.servo_angle = angle
    return {"servo": state.servo_angle}


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

# region Webview

if WEBVIEW_MODE:
    @app.get("/webview/constants", response_class=HTMLResponse)
    async def view_constants():
        return get_constants_view(get_constants_data())

# endregion

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
