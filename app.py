import os
from flask import Flask
from flask import jsonify
from flask import request
import json
from cerberus import Validator
from exceptions import payLoadIsMissing
from exceptions import malformedJson
from exceptions import payloadNotMatchingSchema
import rates 
from logger import Logger
LOG = Logger()

app = Flask(__name__)


@app.errorhandler(payLoadIsMissing)
@app.errorhandler(payloadNotMatchingSchema)
@app.errorhandler(malformedJson)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


payload_input_schema = {
                    'payload': {'type': 'dict', 'required': True}
                    }




@app.route("/ping")
def ping():
    return "Pong!"

@app.route("/schema")
def schema():
    return json.dumps(dict(input=payload_input_schema))

@app.route("/", methods=['GET'])
def index():
    return 'Block-Rates'

@app.route("/", methods=['POST'])
@app.route("/simulate", methods=['POST'])
def simulate():
    data = request.form.get('payload', None)
    payload = json.loads(data)
    res = rates.rates(payload)
    result = dict(success=True, payload=res)
    return json.dumps(result)

   

if __name__ == "__main__":
    port = int(os.environ.get('PORT'))
    app.run(host='0.0.0.0', port=port)