# CSU Utility Scraper

NOTE: Currently only pulls gas

```bash
# Build a docker file
docker build -t csu .


# Run
docker run --rm \
 -p 8000:8000 \
 -e CSU_USERNAME=USERNAME \
 -e CSU_PASSWORD=PASSWORD \
 -it csu
```

You will need to wait a few moments for it to initially download the data prior to hitting:

http://localhost:8000/gas

