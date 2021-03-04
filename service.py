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
        logger.info("Setting env vars via helpers.json")
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

    request_data = request.get_data()
    json_data = json.loads(str(request_data.decode("utf-8")))

    for element in json_data:
        invi_username = element["username"]

        if element['deleted'] == True:
            data = requests.delete(f"{config.github_base_url}/orgs/{org}/memberships/{invi_username}", auth=(username, token))
            if data.status_code == 204:
                logger.info('User has been removed from organization')
            if data.status_code == 403:
                logger.info('Not allowed to remove user from organization. Status code: 403')
            else:
                logger.warning(f'Failing with content: {data.content} and status code: {data.status_code}')

        else:
            data = requests.get(f"{config.github_base_url}/orgs/{org}/members/{invi_username}", auth=(username, token))
            if data.status_code == 204:
                logger.info('User already part of organization')
                
            if data.status_code == 404:
                logger.info('User not part of organization')
                logger.info(f'Trying to add user: {invi_username}')
                invi_response = requests.put(f"{config.github_base_url}/orgs/{org}/memberships/{invi_username}", auth=(username, token))
                if invi_response.ok:
                    if invi_response.status_code == 200:
                        decoded_data = json.loads(invi_response.content.decode('utf-8-sig'))
                        if decoded_data.get('state') == "pending":
                            logger.info(f"Organization invitation sent to username: {invi_username}")
                        if decoded_data.get('state') == "active":
                            logger.info(f"User with username: {invi_username}, already part of organization")
                    else:
                        logger.warning(f"User with username: {invi_username} invited, but unexpected response with status code: {invi_response.status_code}")
                else:
                    if invi_response.status_code == 422 or invi_response.status_code == 403:
                        logger.warning(f"Organization invitation could not be sent to username: {invi_username}")
                        logger.warning(f"Failed with error code: {invi_response.status_code}")
                    else:
                        logger.warning(f"Failed to invite user: {invi_username} with status code: {invi_response.status_code}")
                    
    return jsonify({'Steve reporting': "work complete..."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
