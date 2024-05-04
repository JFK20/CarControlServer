import uvicorn
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import json
import os
import time
import pigpio


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")

    # setup pigpio
    os.system("sudo pigpiod")
    time.sleep(3)
    app.pi = pigpio.pi()
    time.sleep(3)

    print("Pigpio started")

    with open('constants.json') as json_data:
        constants = json.load(json_data)
        app.MOTOR_PIN = constants["MOTOR_PIN"]
        app.MOTOR_CENTER = constants["MOTOR_CENTER"]
        app.MOTOR_OFFSET = constants["MOTOR_OFFSET"]
        app.motor_speed = app.MOTOR_CENTER

        app.SERVO_PIN = constants["SERVO_PIN"]
        app.SERVO_CENTER = constants["SERVO_CENTER"]
        app.SERVO_OFFSET = constants["SERVO_OFFSET"]
        app.servo_angle = app.SERVO_CENTER
    yield


app = FastAPI(lifespan=lifespan)
app.MOTOR_PIN = -1
app.MOTOR_CENTER = -1
app.MOTOR_OFFSET = -1
app.motor_speed = -1

app.SERVO_PIN = -1
app.SERVO_CENTER = -1
app.SERVO_OFFSET = -1
app.servo_angle = -1
app.pi = None

app.LKAS = False


@app.get("/")
async def root():
    return {"message": "Hello World"}


#region Motor

@app.post("/drive/motor/{speed}", status_code=200)
async def set_motor_speed(speed: int):
    if speed < app.MOTOR_CENTER - app.MOTOR_OFFSET:
        app.motor_speed = app.MOTOR_CENTER - app.MOTOR_OFFSET
        raise HTTPException(status_code=400, detail=f"Speed {speed} is out of range set to minimum")
    elif speed > app.MOTOR_CENTER + app.MOTOR_OFFSET:
        app.motor_speed = app.MOTOR_CENTER + app.MOTOR_OFFSET
        raise HTTPException(status_code=400, detail=f"Speed {speed} is out of range set to maximum")

    app.motor_speed = speed
    app.pi.set_servo_pulsewidth(app.SERVO_PIN, speed)
    return {"message": f"Setting motor speed to {speed}"}


@app.get("/drive/motor/speed", status_code=200)
async def get_motor_speed():
    return {"speed": app.motor_speed}


#endregion

#region Servo

@app.post("/drive/servo/{angle}", status_code=200)
async def set_servo_angle(angle: int):
    if angle < app.SERVO_CENTER - app.SERVO_OFFSET:
        app.servo_angle = app.SERVO_CENTER - app.SERVO_OFFSET
        raise HTTPException(status_code=400, detail=f"Angle {angle} is out of range set to minimum")
    elif angle > app.SERVO_CENTER + app.SERVO_OFFSET:
        app.servo_angle = app.SERVO_CENTER + app.SERVO_OFFSET
        raise HTTPException(status_code=400, detail=f"Angle {angle} is out of range set to maximum")

    app.pi.set_servo_pulsewidth(app.SERVO_PIN, angle)
    app.servo_angle = angle
    return {"message": f"Setting servo angle to {angle}"}


@app.get("/drive/servo/angle", status_code=200)
async def get_servo_angle():
    return {"angle": app.servo_angle}


#endregion

#region Constants

@app.post("/drive/constants", status_code=200)
async def post_constants():
    data = {
        'motorCenter': app.MOTOR_CENTER,
        'motorOffset': app.MOTOR_OFFSET,
        'servoCenter': app.SERVO_CENTER,
        'servoOffset': app.SERVO_OFFSET
    }
    return data


#endregion

#region LKAS

@app.post("/drive/lkas/activate", status_code=200)
async def activate_lkas():
    app.LKAS = True
    return {"message": f"LKAS activated"}


@app.post("/drive/lkas/deactivate", status_code=200)
async def deactivate_lkas():
    app.LKAS = False
    return {"message": f"LKAS deactivated"}

#endregion

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
