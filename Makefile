MODULE := m3db
VENV   := .venv
BIN    := ${VENV}/bin

.PHONY: all
all: ${VENV}
	${BIN}/python3 -m build

${VENV}:
	python3 -m venv ${VENV}
	${BIN}/pip install --upgrade pip
	${BIN}/pip install -r dev-requirements.txt
	${BIN}/pip install -e .

.PHONY: venv
venv: ${VENV}

.PHONY: test
test: ${VENV}
	${BIN}/coverage run -m pytest tests
	${BIN}/coverage report

.PHONY: mypy
mypy: ${VENV}
	${BIN}/mypy ${MODULE}

.PHONY: fmt
fmt: ${VENV}
	${BIN}/black ${MODULE}
	${BIN}/isort ${MODULE}

.PHONY: clean
clean:
	rm -rf .venv build dist ${MODULE}.egg-info ${MODULE}/version.py
