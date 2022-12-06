# VIOLA
## Viola: Detecting Violations of Behaviors from Streams of Sensor Data

Viola is a streaming conformance checking approach which allows the discovery and conformance of a process, where the data is generated from IoT devices.

## Features

- Automatically derive a EGSM process model starting from a labeled sensor log
- Process a stream of unlabeled data, in order to be provided to the EGSM engine
- Recognize activities starting from a stream of data
- Verify the conformance at runtime

## How it works

VIOLA requires [Python](https://www.python.org/) and [Node.js](https://nodejs.org/) to run.

### Offline Phase

Pre-process the labeled sensor log:

```sh
run LogPreprocessing - Windowing.ipynb
```

Derive a Decision Tree and convert it to rules:

```sh
run Dtree - Classifier.ipynb
```

Discover a Directly-Follows Graph:

```sh
python discover-dfg.py
```

Create the EGSM process model:

```sh
python build-egsm.py 
```

### Online Phase

Run the EGSM engine:

- Download the [SMARTifact E-GSM Engine](https://bitbucket.org/polimiisgroup/egsmengine/src/master/)
- Copy the files siena.xml and infoModel.xsd produced during the offline phase inside the data/dfg folder (create the folder if does not exist)
- Start the engine:

```sh
node server.js 
```

Process the stream of data:
- Run the CEP system:
* Linac:
```sh
python Server.py 
```
* Kasteren - l-base:
```sh
python Server-lnormal.py 
```
* Kasteren - l-error-1:
```sh
python Server-lerror1.py 
```
* Kasteren - l-error-2:
```sh
python Server-lerror2.py 
```
- Start streaming events:
* Make a REST GET call to the following endpoint (e.g., with a web browser, cURL or Postman):
http://localhost:8080/api/start

And visualize the results!

```sh
python validator.py
```