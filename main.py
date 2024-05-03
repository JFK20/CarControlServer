from fastapi import FastAPI, HTTPException

app = FastAPI()

app.motor_speed = 1200


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/motor/{speed}", status_code=200)
async def set_motor_speed(speed: int):
    if speed < 800:
        app.motor_speed = 800
        raise HTTPException(status_code=400, detail=f"Speed {speed} is out of range set to minimum")
    elif speed > 1600:
        app.motor_speed = 1600
        raise HTTPException(status_code=400, detail=f"Speed {speed} is out of range set to maximum")
    return {"message": f"Setting motor speed to {speed}"}
