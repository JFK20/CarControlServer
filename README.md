# RC Car Control Server

A FastAPI-based server to control an RC car with a Raspberry Pi, featuring manual controls and LKAS (Lane Keeping Assist System).

## Features

- REST API for RC car control
- WebSocket API for low-overhead real-time control
- Web interface for real-time control
- Motor speed and servo angle control
- Debug mode for testing without hardware
#### WIP
- Lane Keeping Assist System (LKAS) 

## Prerequisites

- Python 3.13+
- Raspberry Pi (when not in debug mode)
- pigpio daemon (when not in debug mode)

## WebSocket API

Connect to `ws://<host>:8000/ws/drive`. After the handshake, every control update is a small JSON frame with no HTTP overhead.

On connect, the server sends the current state including the constants:
`{"type": "state", "motor": 1450, "servo": 1550, "lkas": false, "constants": {...}}`

| Client → server | Meaning |
|---|---|
| `{"motor": 1500}` | set motor speed |
| `{"servo": 1600}` | set servo angle |
| `{"motor": 1500, "servo": 1600}` | set both in one frame |
| `{"lkas": true}` | activate / deactivate LKAS |
| `{"get": "state"}` | request the current state |

The server replies to every message with `{"type": "state", "motor": .., "servo": .., "lkas": ..}`.
Out-of-range values are clamped, and the reply includes an `"error"` field.
Invalid messages get `{"type": "error", "error": "..."}`, and the connection stays open.

**Failsafe:** when a WebSocket connection closes, the motor is reset to `MOTOR_CENTER` (neutral).