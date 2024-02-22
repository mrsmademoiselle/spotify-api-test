
# Spotify Api Test

Collects meta data from random songs using the spotify API.

## Setup

### Env-File

Create your .env file

```bash
cp .env.test .env
``` 

Fill in the `CLIENT_ID` and `CLIENT_SECRET` with your authorization credentials the spotify api. See: https://developer.spotify.com

#### OPTIONAL

Adjust `WORKERS` if you want to use more workers during your fetch.

Specify a `CSV_DIRECTORY` for your csv file if you wish to have it somewhere else.

### Dependencies

Install the dependencies specified in the Pipfile

```bash
pipenv install
```


### Run 

Execute main.py

```bash
pipenv run python main.py
```