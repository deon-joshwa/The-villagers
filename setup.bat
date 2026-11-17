:: setup.bat -- run ONCE, hours before the hackathon (model download is large)
:: Requires Python 3.12 installed (YuE2 pins 3.12; the system 3.15 will NOT work).
python3.12 -m venv .venv 2>nul || py -3.12 -m venv .venv 2>nul || python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cu128
git clone https://github.com/multimodal-art-projection/YuE.git yue2-repo
python -m pip install .\yue2-repo
python -m pip install gradio soundfile
yue2 doctor
echo.
echo Setup done. Next: python make_presets.py  (background, renders showcase tracks)
