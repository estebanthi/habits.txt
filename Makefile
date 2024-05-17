PYINSTALLER_LINUX=poetry run pyinstaller
PYINSTALLER_WINDOWS=wine C:/Python312/Scripts/pyinstaller.exe
SCRIPT=bin/hbtxt.py
SPEC_FILE=bin/hbtxt.spec
DIST_DIR=dist
BUILD_DIR=build
PYINSTALLER_OPTS=--onefile -p ./ --specpath bin

all: build

publish: poetry publish --build

build:
	$(PYINSTALLER_LINUX) $(PYINSTALLER_OPTS) $(SCRIPT) && $(PYINSTALLER_WINDOWS) $(SCRIPT) $(PYINSTALLER_OPTS)

clean:
	rm -rf $(DIST_DIR) $(BUILD_DIR) __pycache__ $(SPEC_FILE)

.PHONY: all build clean
