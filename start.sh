#!/bin/bash

# Start backend server
cd backend
source ../venv/bin/activate && python3 main.py &

# Start frontend server
cd ../frontend
npm start
