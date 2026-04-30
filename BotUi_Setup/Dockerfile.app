FROM python:3.10-slim

WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     && rm -rf /var/lib/apt/lists/*



COPY packages/botui-dashboard /app/packages/botui-dashboard

RUN pip install --no-cache-dir -e /app/packages/botui-dashboard

EXPOSE 8501

ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["botui-dashboard"]