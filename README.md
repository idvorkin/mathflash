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
just run
```

Deploy the server with the following command:
```
just deploy
```

Do local testing of deployment environment with (but careful of caching):
```
just serve
```

See user stats with:
```
just stats
```
This will save the stats to a file named `user_stats.csv`.

You can pass in the operator and the maxnumber on the path:

* For addition (max number 15): `just open-add`
* For multiplication (max number 15): `just open-multiply`

These commands will open the appropriate URL in your default web browser.
