# Genius client side SDK

Python library which provides access to the Genius API. For a full tour of functionality see `demos/client-sdk/00_sdk_demo.ipynb`.

# Configuration

- Copy .env.template to .env
- Set the following variables if running a remote agent:
```
AGENT_HTTP_PROTOCOL={your protocol (http or https)} - defaults to http
AGENT_HOSTNAME={your agent hostname} - defaults to localhost
AGENT_PORT={your port, use 443 if https} - defaults to 3000
```

## Authentication

See [the agent authentication docs](/README.md#authentication) on running the agent with authentication.

By default, the SDK does not use authentication. To configure the SDK with authentication, pass in a valid
[`AuthConfig`](./src/genius_client_sdk/auth.py) when creating `GeniusAgent` and `GeniusModel`.

Example with API Key:
```python
from genius_client_sdk.auth import ApiKeyConfig
from genius_client_sdk.agent import GeniusAgent

api_key = "<YOUR_API_KEY>"
agent = GeniusAgent(auth_config=ApiKeyConfig(api_key=api_key))
```

Example with OAuth2 bearer token:
```python
from genius_client_sdk.auth import OAuth2BearerConfig
from genius_client_sdk.agent import GeniusAgent

token = "<YOUR_OAUTH2_BEARER_TOKEN>"
agent = GeniusAgent(auth_config=OAuth2BearerConfig(token=token))
```

Example with OAuth2 client credentials:
```python
from genius_client_sdk.auth import OAuth2ClientCredentialsConfig
from genius_client_sdk.agent import GeniusAgent

client_id = "<YOUR_CLIENT_ID>"
client_secret = "<YOUR_CLIENT_SECRET>"
agent = GeniusAgent(auth_config=OAuth2ClientCredentialsConfig(client_id=client_id, client_secret=client_secret))
```

# Features

MCP Integration Diagram
![Diagram](./docs/mcp/MCP-SDK-gpil-server-diagram.jpg)

## Developer/End-user

Fill out the placeholder:

<GPIL_SERVER> = GPIL-Server hostname. ex.: `gpil-server-default.preview.dev.verses.build`
<API_KEY> = API Key similar a UUID. ex.: `00000000-0000-0000-0000-000000000001`

### MCP (stdio) by Genius SDK

*Claude Desktop*

```json
{
  "genius-infer": {
    "command": "uvx",
    "args": [
        "--from",
        "genius-client-sdk",
        "mcp-genius-agent"
    ],
    "env": {
      "SDK_AGENT_API_KEY": "<API_KEY>",
      "SDK_AGENT_HTTP_PROTOCOL": "https",
      "SDK_AGENT_HOSTNAME": "<GPIL_SERVER>",
      "SDK_AGENT_PORT": "443"
    }
  }
}
```
*Programmatically*

```python
# MCP Python SDK
# Ref.: https://github.com/modelcontextprotocol/python-sdk
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_mcp():
  server_params = StdioServerParameters(
      command="mcp-genius-agent",
      env={
          "SDK_AGENT_HTTP_PROTOCOL": "https",
          "SDK_AGENT_HOSTNAME": "<GPIL_SERVER>",
          "SDK_AGENT_PORT": "443",
          "SDK_AGENT_API_KEY": "<API_KEY>",
      },
  )
  async with stdio_client(server_params) as (read, write):
      async with ClientSession(read, write) as session:
        await session.initialize()
        mcp_response = await session.list_tools()

        print(f"Tools: {mcp_response}")

asyncio.run(run_mcp())
```

### MCP (http /mcp) by GPIL-Server

*Claude Desktop*

MCP-Remote to connect to Streamable MCP. 
Reference: [CloudFlare](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)

```json
{
  "genius-infer": {
      "command": "npx",
      "args": [
          "-y",
          "mcp-remote",
          "https://<GPIL_SERVER>/mcp",
          "--transport", "http-only",
          "--header", "x-api-key: ${AUTH_API_KEY}"
      ],
      "env": {
        "AUTH_API_KEY": "<API_KEY>"
      }
  }  
}
```

*Programmatically*

```python
# MCP Python SDK
# Ref.: https://github.com/modelcontextprotocol/python-sdk
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def run_mcp():
  async with streamablehttp_client(
      url="https://<GPIL_SERVER>/mcp",
      headers={
        "x-api-key": "<API_KEY>"
      },
  ) as (
      read_stream,
      write_stream,
      _,
  ):
      async with ClientSession(read_stream, write_stream) as session:
          await session.initialize()
          mcp_response = await session.list_tools()

          print(f"Tools: {mcp_response}")

asyncio.run(run_mcp())
```

## MCP Host

There are two options for testing and debugging MCP locally.

Testing using the Docker Compose:

Using `docker-compose` will download and install dependencies via containers.

Testing via manual installation:

This option requires installing all dependencies and setting up the environment manually.


### Testing using Docker Compose

Instead of installing all dependencies below, the compose already has a container for each component:

| Component | Container           | Description                                         |
| :-------: | :-----------------: | :-------------------------------------------------- |
| ollama    | ollama              | local LLM (It consumes a lot of memory and storage) |
| mcphost   | mcp-ollama          | LLM Prompt + Genius MCP                             |
| inspector | mcp-inspector-debug | Anthropic debug tool                                |

Note: This docker compose will load the "sprinkler" model as default.

> This compose requires `SDK_AGENT_API_KEY` to be filled out in .env. Besides that, it is required that the all other variables from the .env.template are filled out as well. These variables are mentioned on the root [README.md](../../README.md)

#### Running Prompt Ollama locally and Claude Desktop remotely

```sh
docker compose -f docker-compose.yaml -f docker-compose.mcp-debug.yaml up -d --build

# To access the prompt:
# Or "/app/run.sh" through docker terminal to access the prompt
docker exec -it gpil-pipeline-mcp-ollama-1 /app/run.sh 
```

##### Ollama prompts:

*Prompt*
```sh
What is the probability of "wet_grass" being yes if "cloudy" is "yes" and "sprinkler" is "off"?
```

*Prompt*
```sh
What is the probability of "wet_grass" being yes if there is no evidence? 
```

*Prompt*
```sh
# It will show the payload created to make the request
/history
```

![docker-desktop](./docs/mcp/docker-run-prompt.png)

##### Claude Desktop

Change claude.json through menu `settings` and tab `developer`:

```json
{
  "genius-infer": {
      "command": "npx",
      "args": [
          "-y",
          "mcp-remote",
          "https://<GPIL_SERVER>/mcp",
          "--allow-http",
          "--transport", "http-only",
          "--header", "x-api-key: ${AUTH_API_KEY}"
      ],
      "env": {
        "AUTH_API_KEY": "<API_KEY>"
      }
  }
}
```

#### Debugging

1. Go to this link `http://localhost:6274/` (incognito mode is better)

2. Add configurations

Transport Type: `Streamable HTTP`

URL: `http://gpil-server:3000/mcp`

![](./docs/mcp/inspector-through-proxy.png)

| Note: If Inspector is force to use "Oauth/Bearer Token", it is possible to setup `Bearer Token`.

Header Name: `Authorization`

Bearer Token: <ACCESS_TOKEN> (Getting `access_token` from Zitadel: [here](https://genius-core-login.dev-kosm-core.dev.verses.build/?provider=zitadel) )

3. Run it

Click on `connect` > `List Tools` then just add the variable (ex.: "wet_grass") and click on `Run tool`.

![http-inspector](./docs/mcp/inspector-http.png)

### Testing via manual installation

#### Dependencies

Dependencies:

Anthropic inspector

* uv - python package manager
* nvm - nodejs package manager (Nodejs v22)

Ollama

* golang - v1.24.2
  * mcphost - Integration Ollama + MCP Server [mcphost](github.com/mark3labs/mcphost@latest)
* ollama - Local LLM [ollama](https://ollama.com/)

It is possible to use brew.sh (https://brew.sh/) to install these dependencies:

Inspector

```sh
brew install uv

brew install nvm
```

LLM locally

```sh
brew install golang

brew install ollama

# MCPHost
go install github.com/mark3labs/mcphost@latest
```

After installing these tools, check and setup them properly.

Inspector

```sh
# Nodejs v22
nvm install 22

# > v22.15.1
node --version

# > uv-tool-uvx 0.6.2
uvx --version
```

LLM locally

```sh
# > go1.24.2
go version

# Pull llama3.2 model
# Check if there is a "Llama" icon on the top menu. 
# To enable the service go to "LaunchPad" and click on "Ollama" icon to start the server.
#
ollama pull llama3.2

# Check if it is included on PATH
mcphost --help
```

*Common issues*

* `nvm` not found

Check if nvm script is loaded on your shell profile(ex.: ~/.zshrc):

```sh
export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"  # This loads nvm
```

* After running `golang install github.com/mark3labs/mcphost@latest`, the command-line is not found

Check if "$(go env GOPATH)/bin" is included on your shell $PATH.

```sh
# For example zshell: ~/.zshrc
# golang apps
export PATH="$PATH:$(go env GOPATH)/bin"
```

#### Debuggging Protocol (Inspector)

Using Antropic tool from ModelContextProtocol

Reference: [Antropic MCP](https://github.com/modelcontextprotocol/python-sdk)

Dependencies:

* uv - python package manager
* npx - NodeJS

Launch web browser

```sh
# Before to call the inspector, it needs a loaded environment `source ./venv/bin/activate` in the current terminal
# On gpil-pipeline root folder
uv sync

source .venv/bin/activate

npx @modelcontextprotocol/inspector
```

After openning the web browser, type and select this configuration:

transport type: `STDIO`

Command: `uvx`

Argument: `--from genius-client-sdk  mcp-genius-agent`
![uvx](./docs/mcp/inspector-stdio.png)


Add on environment: SDK_AGENT_API_KEY <API_KEY>
![env](./docs/mcp/inspector-env.png)

Calling infer tool:
![infer](./docs/mcp/inspector-run.png)

*Common issues*

* `warning: Package `genius-client-sdk` does not provide any executables.`.

Usually, it is missing to run `uv sync and source .venv/bin/activate`.

* Random issues to `connect to` or run the tool.

I would suggest to use the browser on `incognito mode` to avoid old session opened.


#### Testing using LLM Ollama(llama3.2) locally

Dependencies:

* Ollama - llama3.2(latest version 3b that is around 2GB)
* mcphost - https://github.com/mark3labs/mcphost (Using golang)
* uv - Python package manager

```sh
# Install Ollama
brew install ollama

# Pull llama3.2
ollama pull llama3.2

# MCPHost
go install github.com/mark3labs/mcphost@latest
```

Running Genius SDK infer tool:

```sh
# Before running mcphost, it is required to start gpil-server with the "sprinkler" model
docker compose up -d
# Or 
make compose

#
# After that, go to this link http://localhost:3000/docs#/default/set_graph_graph_post
# Try out the `POST Graph` using the sprinkler example
#
open http://localhost:3000/docs#/default/set_graph_graph_post

# Change the API_KEY inside mcphost.json before running this command
mcphost -m ollama:llama3.2 --config ./packages/genius-client-sdk/tests/mcp/mcphost.json

# In order to see the request and response, you can enable the debug
mcphost -m ollama:llama3.2 --config ./packages/genius-client-sdk/tests/mcp/mcphost.json --debug
```

Prompt:
```sh

What is the probability of "wet_grass" being yes if "cloudy" is "yes" and "sprinkler" is "off"?
```

*Result:*
```sh
INFO Model loaded provider=ollama model=llama3.2
INFO Initializing server... name=inference
INFO Server connected name=inference
INFO Tools loaded server=inference count=2

  You: What is the probability of "wet_grass" being yes if "cloudy" is "yes" and "sprinkler" is "off"?
INFO 🔧 Using tool name=inference__infer
INFO 🔧 Using tool name=inference__infer

  Assistant:


  The probability of "wet_grass" being yes is approximately 72%. This is because the presence of a sprinkler system is off, which makes it less likely that there will be wet grass due to watering. However, on a cloudy day,
  it's more likely that there will be wet grass even if the sprinkler is off, as the rain from the cloud can cause the grass to get wet.

```

Prompt:
```sh

  /history
```

*Result:*
```sh
  ## Assistant

  ### Tool Use

  Tool: inference__infer

  Input:

    {
      "evidence": "{\"cloudy\": \"yes\", \"sprinkler\": \"off\"}",
      "variables": "[\"wet_grass\"]"
    }

  --------

  ## User

  ### Tool Result

  Tool ID: tc_inference__infer_1747093281684215000

  --------

  ## Assistant

  ### Text

  The probability of "wet_grass" being yes is approximately 72%. This is because the presence of a sprinkler system is off, which makes it less likely that there will be wet grass due to watering. However, on a cloudy day,
  it's more likely that there will be wet grass even if the sprinkler is off, as the rain from the cloud can cause the grass to get wet.

```

#### Testing using Claude Desktop remotely

Change claude.json through menu `settings` and tab `developer`:

Official instructions

```json
{
  "genius-infer": {
      "command": "npx",
      "args": [
          "-y",
          "mcp-remote",
          "https://<GPIL_SERVER>/mcp",
          "--transport", "http-only",
          "--header", "x-api-key: ${AUTH_API_KEY}"
      ],
      "env": {
        "AUTH_API_KEY": "<API_KEY>"
      }
  }  
}


> Workaround to handle NodeJS issue with MacOS and Claude Desktop. Install globally mcp-remote package and use absolute path instead of just `node` or `npx`

1 - Install mcp-remote globally

```sh

npm install -g mcp-remote

# Get absolute paths of node and mcp-remote

where node

where mcp-remote
```

Usually these are the paths if you are using `nvm`:

/Users/<user>/.nvm/versions/node/<node_version>/bin/node

/Users/<user>/.nvm/versions/node/<node_version>/bin/mcp-remote

> Placeholder: <user> = user and <node_version> = v20.17.0

2 - Use these paths 

```json
{
  "remote-infer": {
      "command": "/Users/<user>/.nvm/versions/node/<node_version>/bin/node",
      "args": [
          "/Users/<user>/.nvm/versions/node/<node_version>/bin/mcp-remote",
          "https://<GPIL_SERVER>/mcp",
          "--transport", "http-only",
          "--header", "x-api-key: ${AUTH_API_KEY}"
      ],
      "env": {
        "AUTH_API_KEY": "<API_KEY>"
      }      
  }
}
```

## Build a factor graph from scratch

The `GeniusModel` class is used to build factor graphs from scratch. The class has the following capabilities:
- Create a model from a JSON file path
- Construct model by adding variables or factors
- Validate a constructed model with `POST /validate` in the fastAPI
- Save (export) a model to JSON
- Visualize the model with networkx
- Get variable names and values for a given model
- Get factor attributes for a given model

## Build a POMDP model from scratch

Creates a POMDP style factor graph model. This class is really just a wrapper around the `GeniusModel` class with constrained functionality to enable the user to create a POMDP model. Strictly speaking, one can create it with the GeniusModel class but the convenience functions in this class make the process easier and include checks to make sure all the necessary model components are present.

## Query a model with Genius

The `GeniusAgent` class is used as a wrapper around fastAPI to communicate to and from a running Genius agent. This class has the following capabilities enabled by the API calls:
- `POST /graph` of genius model loaded from a JSON or from the `GeniusModel` class
- `GET /graph` of genius model and print/view its contents
- `POST /infer` to perform inference given some evidence and a variable of interest
- `POST /learn` to perform parameter learning given an input CSV or list of variables and their observations
- `POST /actionselection` to perform action selection given a POMDP model structure and observation vector
    
At the moment, it is assumed that the user connects to a local `GeniusAgent` as specified in the `.env` file. In the future, initializing this class will have options to specify a URL and port.

# Testing
## Fast and slow
Real world use cases have been added to the regression tests, using large data sets and complex factor shapes.  These tests are grouped under the `slow` pytest mark and are not executed by default.

* Default (fast) tests - `make test`
* Slow tests - `make test-slow`


## Environment variables
env variable added to approximate the instance memory limit in Mb - default tp 1024 * 14  (14 GB)

```
SDK_MEMORY_LIMIT
```

env variable added to allow slow tests to complete in seconds - default to 20 * 60 seconds
```
SDK_REQUEST_TIMEOUT 
```

# Remaining work

- TODO: VFG wrapping

- TODO: Add todos from PR
- TODO: Fix remaining todos in code
- TODO: SDK Gridworld full demo
- TODO: SDK MAB full demo
- TODO: Add structure learning
- TODO: Connecting to a Genius agent (GPAI-148)
- TODO: Unit tests and production quality (GPAI-149)
- TODO: (maybe) reevaluate the way genius_client_sdk is built and used in the notebooks once we work with this a little bit more

