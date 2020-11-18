from flask import Flask, request, jsonify, Response
import json
import requests
import os
import sys
from sesamutils import VariablesConfig, sesam_logger

app = Flask(__name__)
logger = sesam_logger("Steve the logger", app=app)

## Logic for running program in dev
try:
    with open("helpers.json", "r") as stream:
        env_vars = json.load(stream)
        os.environ['github_username'] = env_vars['github-username']
        os.environ['github_token'] = env_vars['github-token']
        os.environ['github_base_url'] = env_vars['github-base-url']
except OSError as e:
    logger.info("Using env vars defined in SESAM")

## Helpers
required_env_vars = ['github_username', 'github_token', 'github_base_url']
optional_env_vars = ["page_size"]
username = os.getenv('github_username')
token = os.getenv('github_token')

@app.route('/')
def index():
    output = {
        'service': 'GitHub is running',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)

@app.route('/org_user/<org>', methods=['GET', 'POST'])
def org_user(org):
    ## Validating env vars
    config = VariablesConfig(required_env_vars, optional_env_vars)
    if not config.validate():
        sys.exit(1)

    ## helper
    return_msg = None

    request_data = request.get_data()
    json_data = json.loads(str(request_data.decode("utf-8")))

    payload = {"email": json_data["email"]}
    invi_username = json_data["username"]
    email = json_data["email"]
    return_msg = None


    if json_data['deleted'] == True:
        data = requests.delete(f"{config.github_base_url}/orgs/{org}/members/{invi_username}", auth=(username, token))
        if data.status_code == 204:
            logger.info('User has been removed from organization')
            return_msg = 'User has been removed from organization'
        if data.status_code == 403:
            logger.info('Not allowed to remove user from organization. Status code: 403')
            return_msg = 'Not allowed to remove user from organization. Status code: 403'
        else:
            logger.warning(f'Failing with content: {data.content} and status code: {data.status_code}')

    else:
        data = requests.get(f"{config.github_base_url}/orgs/{org}/members/{invi_username}", auth=(username, token))
        if data.status_code == 204:
            logger.info('User already part of organization')
            return_msg = 'User already part of organization'
            
        if data.status_code == 404:
            logger.info('User not part of organization')
            logger.info(f'Trying to add user: {invi_username}')
            invi_response = requests.post(f"{config.github_base_url}/orgs/{org}/invitations", auth=(username, token), data=json.dumps(payload))
            if invi_response.status_code == 201:
                logger.info(f"Organization invitation sent to email: {email}")
                return_msg = f"Organization invitation sent to email: {email}"
            if invi_response.status_code == 422:
                logger.info(f"Organization invitation could not be sent to email: {email}")
                return_msg = f"Organization invitation could not be sent to email: {email}"

    return return_msg

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)