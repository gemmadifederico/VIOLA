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
... 
```

Create the EGSM process model:
```sh
... 
```

### Online Phase
Run the EGSM engine:
```sh
... 
```

Process the stream of data:
```sh
python Server.py 
```

And visualize the results!
