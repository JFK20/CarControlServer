from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    with open('constants.json') as json_data:
        constants = json.load(json_data)
        app.MOTOR_MIN_SPEED = constants["MOTOR_MIN_SPEED"]
        app.MOTOR_MAX_SPEED = constants["MOTOR_MAX_SPEED"]
        app.MOTOR_MID_SPEED = constants["MOTOR_MID_SPEED"]
        app.motor_speed = app.MOTOR_MID_SPEED
    yield


app = FastAPI(lifespan=lifespan)
app.MOTOR_MIN_SPEED = -1
app.MOTOR_MAX_SPEED = -1
app.MOTOR_MID_SPEED = -1
app.motor_speed = -1


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/motor/{speed}", status_code=200)
async def set_motor_speed(speed: int):
    if speed < app.MOTOR_MIN_SPEED:
        app.motor_speed = app.MOTOR_MIN_SPEED
        raise HTTPException(status_code=400, detail=f"Speed {speed} is out of range set to minimum")
    elif speed > app.MOTOR_MAX_SPEED:
        app.motor_speed = app.MOTOR_MAX_SPEED
        raise HTTPException(status_code=400, detail=f"Speed {speed} is out of range set to maximum")

    app.motor_speed = speed
    return {"message": f"Setting motor speed to {speed}"}


@app.get("/motor/speed", status_code=200)
async def get_motor_speed():
    return {"speed": app.motor_speed}
