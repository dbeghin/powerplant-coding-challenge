# powerplant-coding-challenge

Open one terminal, go to the top-level directory of the application, and run

`python app.py`

Open another terminal, and run

`curl -X POST -d @payload.json -H "Content-Type: application/json" http://127.0.0.1:8888/productionplan`

Where 'payload.json' is the payload you want to give to the optimiser function.

