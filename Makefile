PYTHON ?= python3
MYNA ?= myna
NODE ?= node
RUFF ?= uvx ruff
BUILD ?= build

.PHONY: check lint lint-py test-py test-js build-py js-portable run selftest serve zipapp zipapp-smoke clean

check: lint test-py lint-py test-js selftest zipapp-smoke

lint:
	@bash tools/check_targets.sh
	@bash tools/check_portable.sh
	@python3 tools/check_imports.py
	@python3 tools/check_collisions.py

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
	@python3 tools/assemble.py $(BUILD)/js/portable.myna
	@$(MYNA) compile -t js $(BUILD)/js/portable.myna -o $(BUILD)/js/portable.mjs
	@$(NODE) --check $(BUILD)/js/portable.mjs

test-js: js-portable
	@$(NODE) --test tests/js/*.test.mjs

run:
	@$(MYNA) run src/mynastock/main.myna

selftest:
	@$(MYNA) run src/mynastock/cli.myna --selftest

serve:
	@mkdir -p $(BUILD)
	@$(MYNA) run src/mynastock/cli.myna serve --db $(BUILD)/mynastock.db $(ARGS)

zipapp:
	@mkdir -p $(BUILD)
	@$(MYNA) bundle src/mynastock/cli.myna --zipapp -o $(BUILD)/mynastock.pyz

zipapp-smoke: zipapp
	@$(PYTHON) -I $(BUILD)/mynastock.pyz --selftest

clean:
	@rm -rf $(BUILD)
