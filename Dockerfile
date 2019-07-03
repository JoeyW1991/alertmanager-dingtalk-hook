FROM python:3.6.4-slim

RUN groupadd user && useradd --create-home --home-dir /home/user -g user user
WORKDIR /home/user
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
ADD . .

USER user
CMD python app.py
