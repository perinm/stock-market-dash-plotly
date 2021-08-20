FROM python:3.9.5-buster

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app

CMD python app.py 
# gunicorn -w 4 -b 0.0.0.0:8050 app:server
# CMD python -m http.server
#CMD ["python","-m","http.server","8000"]
# "python", "main.py", "&&",