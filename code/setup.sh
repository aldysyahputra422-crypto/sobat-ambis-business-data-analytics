# Blok 1 · setup · NCG Core Dataset v2.0.0
shasum -a 256 -c SHA256SUMS.txt

# Blok 2 · setup · NCG Core Dataset v2.0.0
python -m venv bda-env
source bda-env/bin/activate          # Windows: bda-env\Scripts\activate
pip install -r tools/requirements.txt
python tools/verify_environment.py
jupyter lab

# Blok 3 · setup · NCG Core Dataset v2.0.0
git config --global user.name "Nama Anda"
git config --global user.email "email-anda@contoh.com"
