# Diego Beghin's solution to the powerplant-coding-challenge

This guide assumes that you are working with a Unix command line.


## Setup

Clone the repository from github and enter the project directory:

`git clone https://github.com/dbeghin/powerplant-coding-challenge.git`

`cd powerplant-coding-challenge`

Set up a new virtual environment and activate it:

`python3 -m venv clean-env`

`source clean-env/bin/activate`

Install the minimum requirements:

`pip install -r requirements.txt`



## Run the application

Host the server locally:

`python app.py`

The application will start in debug mode.

To submit a POST request to the endpoint `/productionplan` of the API, open a new terminal and go to the project directory. Then use the following CURL command to submit the payload `example_payloads/payload1.json`:

`curl -X POST -d @example_payloads/payload1.json -H "Content-Type: application/json" http://127.0.0.1:8888/productionplan`

You can replace `example_payloads/payload1.json` with any other data you wish to submit. The response will either be the solution to the optimisation problem or an error message. The file `error_and_info.log` is updated and logs some information about the nature of the solution and how the code is running, and if there are any errors, it shows a copy of the response printed on the terminal and sometimes gives more detail.

On the window where the server is hosted (`python app.py`), you can stop hosting with a keyboard interrupt. If you start hosting again, the file `error_and_info.log` will be overwritten and started anew.

