# Kawa Python Server 

It is the python runtime for the Kawa platform.
Please refer to this documentation to register python runtime in the Kawa platform:
[Register python runtimes](https://github.com/kawa-analytics/kywy-documentation/blob/main/notebooks/administration/01_kawa_administration_notebook.ipynb
).

## Configure the server

Create a `.env` file in the root of the venv.
It must contain the following environment variables:

```dotenv
# This is the secret for this server.
# It will need to be set on KAWA platform too 
# to communicate with this server.
# You can generate it like that: head /dev/urandom | sha256sum | cut -d ' ' -f 1
# (REQUIRED)
KAWA_AUTOMATION_SERVER_AES_KEY=8c180b7df391a24fcdf5504fadbd37f2df79ead5c4b36987acb683bd8e8bc465

# This defines the URL of the KAWA platform this python server will be paired with
# (OPTIONAL) Defaults to http://localhost:8080
KAWA_URL=http://localhost:8080

# This will define on which host/port the python server will listen
# (OPTIONAL) Defaults to 0.0.0.0, port 8815
# KAWA_AUTOMATION_SERVER_HOST=0.0.0.0
# KAWA_AUTOMATION_SERVER_PORT=8815

# This will override the path to the pex executable.
# pex is used by the script runner to package dependencies
# https://docs.pex-tool.org/
# (OPTIONAL) Defaults to pex
# KAWA_AUTOMATION_PEX_EXECUTABLE_PATH=pex

# Defines the working dir of the python server
# It will store pex files and sync files
# (OPTIONAL) Defaults to /tmp
# KAWA_AUTOMATION_SERVER_WORKING_DIRECTORY=/tmp

# If set to true, PEX will use pip config.
# This is important if some specific configuration is required (such as a private package registry etc)
# (OPTIONAL) Defaults to false
# KW_PEX_USE_PIP_CONFIG=false
```

## Starting the server

Just run `kawapythonserver`



