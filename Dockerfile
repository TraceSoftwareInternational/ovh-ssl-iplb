FROM python:3.6

RUN curl -o /usr/bin/dehydrated https://raw.githubusercontent.com/lukas2511/dehydrated/master/dehydrated && \
    chmod +x /usr/bin/dehydrated

WORKDIR "/home/working"
COPY src .

RUN pip install -r requirements.txt

VOLUME /etc/dehydrated/certs
VOLUME /etc/dehydrated/accounts


ENTRYPOINT ["python", "main.py"]
