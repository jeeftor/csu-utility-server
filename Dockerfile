FROM mcr.microsoft.com/playwright:v1.27.0-focal

RUN apt-get update && apt-get install -y pip
RUN pip3 install playwright fastapi uvicorn[standard] aiofiles fastapi-utils rich
COPY src ./src
CMD uvicorn src.main:app --host 0.0.0.0
