from fastapi.responses import HTMLResponse

def get_constants_view(constants: dict) -> HTMLResponse:
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Constants Overview</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    display: flex;
                    gap: 40px;
                }}
                .container {{
                    flex: 1;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    max-width: 600px;
                    margin-bottom: 30px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .slider-container {{
                    margin: 20px 0;
                }}
                .slider-value {{
                    margin-top: 5px;
                    font-weight: bold;
                }}
                .connected {{
                    color: green;
                }}
                .disconnected {{
                    color: red;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>System Constants</h1>
                <table>
                    <tr>
                        <th>Constant</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Motor Center</td>
                        <td>{constants['motorCenter']}</td>
                    </tr>
                    <tr>
                        <td>Motor Offset</td>
                        <td>{constants['motorOffset']}</td>
                    </tr>
                    <tr>
                        <td>Servo Center</td>
                        <td>{constants['servoCenter']}</td>
                    </tr>
                    <tr>
                        <td>Servo Offset</td>
                        <td>{constants['servoOffset']}</td>
                    </tr>
                </table>
            </div>
            <div class="container">
                <h1>Controls</h1>
                <div id="wsStatus" class="disconnected">Disconnected</div>
                <div class="slider-container">
                    <h3>Motor Speed</h3>
                    <input type="range" 
                           id="motorSlider" 
                           min="{constants['motorCenter'] - constants['motorOffset']}" 
                           max="{constants['motorCenter'] + constants['motorOffset']}" 
                           value="{constants['motorCenter']}"
                           oninput="updateMotorSpeed(this.value)">
                    <div id="motorValue" class="slider-value">Current: {constants['motorCenter']}</div>
                </div>
                <div class="slider-container">
                    <h3>Servo Angle</h3>
                    <input type="range" 
                           id="servoSlider" 
                           min="{constants['servoCenter'] - constants['servoOffset']}" 
                           max="{constants['servoCenter'] + constants['servoOffset']}" 
                           value="{constants['servoCenter']}"
                           oninput="updateServoAngle(this.value)">
                    <div id="servoValue" class="slider-value">Current: {constants['servoCenter']}</div>
                </div>
            </div>
            <script>
                const wsUrl = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/drive';
                let ws = null;
                let pending = {{}};
                let flushScheduled = false;

                function setStatus(connected) {{
                    const status = document.getElementById('wsStatus');
                    status.textContent = connected ? 'Connected' : 'Disconnected';
                    status.className = connected ? 'connected' : 'disconnected';
                }}

                function connect() {{
                    ws = new WebSocket(wsUrl);
                    ws.onopen = () => {{
                        setStatus(true);
                        flush();
                    }};
                    ws.onmessage = (event) => {{
                        const msg = JSON.parse(event.data);
                        if (msg.error) console.error('Error:', msg.error);
                        if (msg.type !== 'state') return;
                        document.getElementById('motorValue').textContent = 'Current: ' + msg.motor;
                        document.getElementById('servoValue').textContent = 'Current: ' + msg.servo;
                    }};
                    ws.onclose = () => {{
                        setStatus(false);
                        setTimeout(connect, 1000);
                    }};
                }}

                // send at most one combined message per animation frame
                function scheduleFlush() {{
                    if (flushScheduled) return;
                    flushScheduled = true;
                    requestAnimationFrame(() => {{
                        flushScheduled = false;
                        flush();
                    }});
                }}

                function flush() {{
                    if (!ws || ws.readyState !== WebSocket.OPEN || Object.keys(pending).length === 0) return;
                    ws.send(JSON.stringify(pending));
                    pending = {{}};
                }}

                function updateMotorSpeed(value) {{
                    document.getElementById('motorValue').textContent = 'Current: ' + value;
                    pending.motor = Number(value);
                    scheduleFlush();
                }}

                function updateServoAngle(value) {{
                    document.getElementById('servoValue').textContent = 'Current: ' + value;
                    pending.servo = Number(value);
                    scheduleFlush();
                }}

                connect();
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)