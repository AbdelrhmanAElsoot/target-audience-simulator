# Small image for rendering reports without installing Pango on your system.
# Build:   docker build -t tas-render .
# Render:  docker run --rm -v "$PWD:/data" tas-render python generate_pdf.py --input-json temp_data.json --output /data/report.pdf
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 \
    fonts-noto-core fonts-noto-naskh-arabic \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Mount your working folder at /data so outputs land on your machine.
CMD ["bash"]
