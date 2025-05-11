apibot:
	cd ./src; \
	uvicorn --reload ApiServices.apiServices:app

telegrambot:
	python3 ./src/app.py

tailwind:
	cd ./src/ApiServices; \
	npx tailwindcss -i ./static/styles.css -o ./static/output.css --watch