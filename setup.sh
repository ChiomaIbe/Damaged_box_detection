#!/bin/bash

# Create and activate Python virtual environment
echo "Creating Python virtual environment..."
# python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd ../frontend
export NODE_TLS_REJECT_UNAUTHORIZED=0
npm install --registry=http://registry.npmjs.org/

# Create start script
cd ..
echo '#!/bin/bash

# Start backend server
cd backend
source ../venv/bin/activate && python3 main.py &

# Start frontend server
cd ../frontend
npm start' > start.sh

# Make scripts executable
chmod +x start.sh
chmod +x setup.sh

echo "Setup complete! Run './start.sh' to start the application."
