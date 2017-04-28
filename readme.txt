http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/
https://cloud.google.com/python/getting-started/hello-world#deploy_and_run_hello_world_on_app_engine

pip freeze > requirements.txt
pip install -r requirements.txt

—
virtualenv env
source env/bin/activate
pip install -r requirements.txt

python main.py

deactivate



