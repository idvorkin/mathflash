# mathflash

Flashcards, based on the https://hyperdiv.io/ framework.
Connect to it in "production" [here](https://bit.ly/imathflash)

Setup the environment with:
```
pipenv install
pipenv shell

```
Run the debug server with:
```
./main.py

```
Deploy the server with the following command:
```
modal deploy modal_server.py
```

Do local testing of deployment environment with (but careful of caching)
```
modal serve modal_server.py
```

See user stats with: https://idvorkin--mathflash-fastapi-app.modal.run/attempts. Use curl/wget and import to platform of your choice.

    curl https://idvorkin--mathflash-fastapi-app.modal.run/attempts > foo.csv

You can pass in the operator and the maxnumber on the path:

* http://localhost:8888/+/15
* http://localhost:8888/*/15
