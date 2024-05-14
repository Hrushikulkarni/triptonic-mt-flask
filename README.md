### TripTonic - REST API Backend

---

- Add .env file to the root

```
GOOGLE_GEMINI_API_KEY=
GOOGLE_MAPS_API_KEY=
```

- To resolve spacy error run the following (Will be deprecated later)
  `python -m spacy download en_core_web_sm`

- Install dependencies by running
  `pip install -r requirements.txt`

- Run server as follows
  `python app.py`

##### TODO

- transits should not be part of main visit pages
- handle the multi contry data(when data points are in multiple contries).
