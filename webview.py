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
                async function updateMotorSpeed(value) {{
                    document.getElementById('motorValue').textContent = 'Current: ' + value;
                    try {{
                        const response = await fetch(`/drive/motor/${{value}}`, {{
                            method: 'POST'
                        }});
                    }} catch (error) {{
                        console.error('Error:', error);
                    }}
                }}

                async function updateServoAngle(value) {{
                    document.getElementById('servoValue').textContent = 'Current: ' + value;
                    try {{
                        const response = await fetch(`/drive/servo/${{value}}`, {{
                            method: 'POST'
                        }});
                    }} catch (error) {{
                        console.error('Error:', error);
                    }}
                }}
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)