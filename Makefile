.PHONY: install create-venv activate-venv run-telegram-notify

install:
	@echo "Installing requirements..."
	pip install -r requirements.txt

create-env:
	@echo "Creating virtual environment..."
	python3 -m venv solax-cloud-notifier
	@echo "Activate it using 'source solax-cloud-notifier/bin/activate'"

activate-venv:
	@echo "Activating virtual environment..."
	./solax-cloud-notifier/bin/activate

run-telegram-notify:
	@echo "Running Telegram notifier..."
	python3 ./src/telegram-notifier.py

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


