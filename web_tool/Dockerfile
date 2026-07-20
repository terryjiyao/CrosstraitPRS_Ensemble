FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/pages/data && \
    python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/terryjiyao/CrosstraitPRS_Ensemble/releases/download/v0.1-alpha/prs_cross_trait_ranking.parquet', '/app/pages/data/prs_cross_trait_ranking.parquet')"

EXPOSE 8080

CMD streamlit run About.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true