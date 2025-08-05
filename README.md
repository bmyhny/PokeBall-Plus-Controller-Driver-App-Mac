first time ever doing something like this i also used ChatGPT as help ;o

windows version, Maybe coming soon, or if you guys can do it for me your more then welcome! 

first of id like to give credit to this post https://www.reddit.com/r/Unity3D/comments/10pjw91/update_poke_ball_plus_in_unity/

📦 What's Inside
main.py – the GUI app (just run this to test)

requirements.txt – install needed libraries

build.sh – builds a .app using PyInstaller

make_dmg.sh – creates a .dmg file using create-dmg


✅ How to Use

cd /path/to/PokeballPlusApp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py

👉 Building the .app file
Step 1,

chmod +x build.sh
./build.sh

Step 2, 
brew install create-dmg
chmod +x make_dmg.sh
./make_dmg.sh


