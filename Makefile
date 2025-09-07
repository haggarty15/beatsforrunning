.PHONY: install run clean

install:
	.venv\Scripts\activate && pip install -r requirements.txt

run:
	.venv\Scripts\activate && python client.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +