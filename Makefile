PYTHON ?= python3
MYNA ?= myna
NODE ?= node
RUFF ?= uvx ruff
BUILD ?= build

.PHONY: check lint lint-py test-py test-js build-py js-portable run clean

check: lint test-py lint-py test-js

lint:
	@bash tools/check_targets.sh
	@bash tools/check_portable.sh

build-py:
	@rm -rf $(BUILD)/py
	@mkdir -p $(BUILD)/py
	@set -e; \
	for f in $$(find src tests -name '*.myna' | sort); do \
		case $$f in \
			src/*) out="$(BUILD)/py/$${f#src/}" ;; \
			tests/*) out="$(BUILD)/py/tests/$${f#tests/}" ;; \
		esac; \
		out="$${out%.myna}.py"; \
		mkdir -p "$$(dirname "$$out")"; \
		$(MYNA) compile "$$f" -o "$$out"; \
	done

test-py: build-py
	@PYTHONPATH=$(BUILD)/py $(PYTHON) -m unittest discover -s $(BUILD)/py/tests -p 'test_*.py' -v

# Generated Python is machine output; this checks syntax and undefined names only.
lint-py: build-py
	@$(RUFF) check $(BUILD)/py

js-portable:
	@mkdir -p $(BUILD)/js
	@$(MYNA) compile -t js src/mynastock/core.myna -o $(BUILD)/js/core.mjs
	@$(NODE) --check $(BUILD)/js/core.mjs

test-js: js-portable
	@$(NODE) --test tests/js

run:
	@$(MYNA) run src/mynastock/main.myna

clean:
	@rm -rf $(BUILD)
