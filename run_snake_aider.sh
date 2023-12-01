docker run -it --rm -v $(pwd)/snake_game.py:/snake_game.py -v $(pwd)/requirements.txt:/requirements.txt python:latest /bin/bash -c "pip install -r /requirements.txt && python /snake_game.py"
