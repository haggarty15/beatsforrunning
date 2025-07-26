.PHONY: install run clean

install:
    pip install -r requirements.txt

run:
    python spotify/client.py

clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +