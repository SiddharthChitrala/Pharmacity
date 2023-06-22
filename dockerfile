FROM python
WORKDIR /app
ADD . /app
COPY requirements.txt /app
RUN python -m pip install -r requirements.txt
EXPOSE 5000
CMD ["python","app.py"]