You can test the API by using the playground, add your own file or use the existing python scripts.
When a client has an issue, and they send their code. It's helpful to test their code to see possible issues

# ENABLE API ON YOUR LOCAL MACHINE

Follow the steps here https://www.notion.so/standardbots/Using-the-REST-API-b2c778d47969444dac61483f0117acad

# CONFIG

At the top of the file, use your token

# RUN

To run a script move into the `sdks/python` folder and run `python playground/filename.py`

# To create a test build

1. Update version in `setup.py`
2. Run `python3 setup.py sdist bdist_wheel`

# Tests

## Setup

To set up tests:

```bash
cd sdks/python

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Create sample data

#### Sample routine

You need to add the sample routine in [sdks/python/tests/fixtures/test_public_api_routine.json](./tests/fixtures/test_public_api_routine.json) to your target test environment (i.e. upload the routine to ).

The name of routine should be "Test Public API"

#### Sample globals

- _Variable._ Add global variable called "test_public_api_global" with any value.
- _Space._ Create a global space called "Test global space" of any kind.


## Running

Here is a basic test command:

```bash
SB_API_URL=http://34.162.0.32:3000
SB_API_TOKEN=...

python3 -m pytest ./tests --cov=standardbots --token=$SB_API_TOKEN --api-url=$SB_API_URL
```

You may also set up a `.env` file at `sdks/python/.env` with the following contents:

```bash
export SB_API_URL=http://34.162.0.32:3000
export SB_API_TOKEN=...
```

Then you can just do:

```bash
python3 -m pytest ./tests --cov=standardbots
```

### Robot state and testing (Markers)

We need the bot to be in a certain state to run certain tests. For example, we need a routine to be running in order to stop the routine.

At start of testing, robot should:

- _NOT_ be e-stopped.


The basic idea here is:

- These special tests will not be run by default.
- You may pass a flag (e.g. `--routine-running`) when the bot is in the correct state to run the tests.
- When the flag is passed:
  1. Tests with the flag are run.
  2. Tests without the flag are not run.

We use [pytest markers](https://docs.pytest.org/en/7.1.x/example/markers.html) to do this.

#### Routine running

The special sample routine ("Test Public API") should be running prior to running these tests. Then do:

```bash
python3 -m pytest ./tests --cov=standardbots --routine-running
```

#### E-stop

No marker needed for e-stop. However, we do rely on active recovery of e-stop and getting the failure state in order to do these tests.

When e-stop test runs, cannot have bot in a failure state (pre-test will fail).

## Troubleshooting

### Tests are hanging

The first test appears to start but then nothing happens for several seconds:

```bash
$ python3 -m pytest ./tests --cov=standardbots
========================================================================================================== test session starts ===========================================================================================================
platform linux -- Python 3.10.12, pytest-6.2.5, py-1.10.0, pluggy-0.13.0
rootdir: /workspaces/sb/sdks/python, configfile: pytest.ini
plugins: ament-pep257-0.12.11, ament-xmllint-0.12.11, launch-testing-1.0.6, launch-testing-ros-0.19.7, ament-flake8-0.12.11, ament-lint-0.12.11, ament-copyright-0.12.11, colcon-core-0.18.1, cov-6.0.0
collected 110 items

tests/test_apis.py
```

Fixes:

- _Make sure you can log into remote control._ Ensure that botman is connected.
- _Ensure that the robot URL is up-to-date._ Botman url will often change when you reboot.

### Custom sensors

To test custom sensors:
- go to the menu on the left bottom corner;
- Click on 'Equipment';
- Add Gripper > Custom Gripper;
- Go to the Sensors tab and click 'Add Sensor';
- Keep the default values as they are (name: 'Sensor 1', kind: 'Control Box IO', sensor value: 'low');
- Hit 'Save' and make sure the Custom Gripper is enabled.

Then run:

```bash
python3 -m pytest ./tests --cov=standardbots --custom-sensors
```
