FROM python:3.12-slim

WORKDIR /app
COPY cobranova_host.py .
COPY web ./web

ENV COBRANOVA_DATA=/data
ENV COBRANOVA_NO_BROWSER=1
EXPOSE 8787

CMD ["python", "-u", "cobranova_host.py"]
