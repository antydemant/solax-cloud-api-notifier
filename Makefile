.PHONY: install create-env activate-env telegram-notify telegram-subscriber build-tranlsations extract-translations lint-check

install:
	@echo "Installing requirements..."
	pip install -r requirements.txt

create-env:
	@echo "Creating virtual environment..."
	python -m venv solax-cloud-notifier
	@echo "Activate it using 'source solax-cloud-notifier/bin/activate'"

activate-env:
	@echo "Activating virtual environment..."
	./solax-cloud-notifier/bin/activate

telegram-notify:
	@echo "Running Telegram notifier..."
	python ./src/telegram-notifier.py

telegram-subscriber:
	@echo "Running Telegram subscriber..."
	python ./src/telegram-subscriber.py

build-tranlsations:
	@echo "Building translations..."
	msgfmt src/locales/uk/LC_MESSAGES/messages.po -o src/locales/uk/LC_MESSAGES/messages.mo
	msgfmt src/locales/en/LC_MESSAGES/messages.po -o src/locales/en/LC_MESSAGES/messages.mo

extract-translations:
	@echo "Extracting translations..."
	xgettext --from-code=UTF-8 -o src/locales/messages.pot src/**.py
	msgmerge --update src/locales/uk/LC_MESSAGES/messages.po src/locales/messages.pot
	msgmerge --update src/locales/en/LC_MESSAGES/messages.po src/locales/messages.pot
	@echo "Translations extracted and updated."

lint-check:
	@echo "Running lint checks..."
	python -m black --check src/
	python -m flake8 --quiet --verbose src/

lint:
	@echo "Running and applying lint checks..."
	python -m black src/
	python -m flake8 src/


