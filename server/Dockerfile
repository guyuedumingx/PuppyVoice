FROM python:3.8.0

COPY . /app
WORKDIR ./app
RUN pip install flask
EXPOSE 8899
ENTRYPOINT ["python"]
CMD ["app.py"]