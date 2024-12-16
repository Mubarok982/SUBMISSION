Setup Environment - Anaconda
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt

mkdir SINAU
cd DATA ANALIS
cd dicoding
cd SUBMISSION
cd DASHBOARD
pipenv shell
pip install -r requirements.txt

streamlit run Dashboard.py
