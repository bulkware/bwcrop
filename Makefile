scripts := $(wildcard src/*.py)
tests := $(wildcard tests/*.py)

all: clean gsettings-schema checkstyle dist

checkstyle: $(scripts) $(tests) setup.py
	find . -name "*.py" -exec pycodestyle \{\} \; | tee checkstyle

dconf-schema:
	sudo cp src/org.bulkware.bwcrop.gschema.xml /usr/share/glib-2.0/schemas/
	sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

dist: $(scripts) $(tests) setup.py
	python3 setup.py sdist --format=gztar

clean:
	find . -name "*.pyc" -delete
	rm -rf *.egg-info
	rm -rf dist
	rm -f checkstyle
