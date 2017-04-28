http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/


virtualenv -p python3.6 imdb --no-site-packages
source imdb/bin/activate

pip install requests
pip install panda

pip freeze > requirements.txt
deactivate
rm -rf 

pip install -r requirements.txt
