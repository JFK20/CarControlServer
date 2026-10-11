#!/bin/sh

# Start the FastAPI server in the background
python main.py &

# Wait for the server to start
sleep 5

# Run the tests
python -m unittest motor_tests.py
MOTOR_TESTS_STATUS=$?

if [ $MOTOR_TESTS_STATUS -eq 0 ]; then
    python -m unittest servo_test.py
    SERVO_TESTS_STATUS=$?
else
    echo "Motor tests failed with status $MOTOR_TESTS_STATUS"
    kill %1  # Kill the background FastAPI process
    exit $MOTOR_TESTS_STATUS
fi

if [ $SERVO_TESTS_STATUS -eq 0 ]; then
    python -m unittest ws_tests.py
    WS_TESTS_STATUS=$?
else
    echo "Servo tests failed with status $SERVO_TESTS_STATUS"
    kill %1  # Kill the background FastAPI process
    exit $SERVO_TESTS_STATUS
fi

if [ $WS_TESTS_STATUS -eq 0 ]; then
    echo "All tests passed successfully"
    # Keep the FastAPI server running in foreground
    wait %1
else
    echo "WebSocket tests failed with status $WS_TESTS_STATUS"
    kill %1  # Kill the background FastAPI process
    exit $WS_TESTS_STATUS
fi
