# setup.sh
# Install system dependencies
apt-get update -y
apt-get install -y libgl1-mesa-glx
apt-get install libsdl1.2-dev libsdl-image1.2 libsdl-mixer1.2 libsdl-ttf2.0
pip install streamlit --upgrade
