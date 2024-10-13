venv:
	echo "Creating virtual environment..."; \
	python3 -m venv venv && \
	source venv/bin/activate && \
	python3 -m pip install -r requirements.txt --no-cache-dir && \
	echo "Virtual environment created, activate by running source venv/bin/activate";