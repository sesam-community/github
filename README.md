# GitHub
A connector for using the GitHub API. Currently concerned with using resources concerning organizations.

## Prerequisites
python3

## API Capabalities
Supports GET, POST, DELETE

## How to:

*Run program in development*

This repo uses the file ```package.json``` and [yarn](https://yarnpkg.com/lang/en/) to run the required commands.

1. Make sure you have installed yarn.
2. Creata a file called ```helpers.json``` and set username, token and base_url in the following format:
```
{
    "github-username": "some username",
    "github-token": "some token",
    "github-base-url": "some url"
}
```
3. run:
    ```
        yarn install
    ```
4. execute to run the script:
    ```
        yarn swagger
    ```

*Run program in production*

Make sure the required env variables are defined.

*Use program as a SESAM connector*

#### System config :

```
    {
    "_id": "github",
    "type": "system:microservice",
    "docker": {
        "environment": {
        "token": "$SECRET(github-token)",
        "username": "$ENV(github-user)",
        "base_url": "$ENV(github-base-url)"
        },
        "image": "sesamcommunity/github:latest",
        "port": 5000
    },
    "verify_ssl": true
    }
```

#### Example Pipe config :

```
    {
        "_id": "github-users-outbound",
        "type": "pipe",
        "source": {
        "type": "dataset",
        "dataset": "github-users-preparation"
        },
        "sink": {
            "type": "json",
            "system": "github",
            "url": "/org_user/<name_of_organization>"
        },
        "transform": {
            "type": "dtl",
            "rules": {
            "default": [
                ["add", "::username", "_S.username"],
                ["add, "::email", "_S.email"],
                ["if", ["eq", "_S._deleted", true],
                ["add", "::deleted", true],
                ["add", "::deleted", false]]
            ]
            }
        }
    }
```

## Routes
```
    /org_user/<org>
```

## Expected payload:
```
    {
	"email": "this.is@email.com",
	"username": "userGithub007",
	"deleted": false
    }
```