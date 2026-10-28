PYTHON ?= python3
MYNA ?= myna
NODE ?= node
RUFF ?= uvx ruff
MKDOCS ?= uvx --with mkdocs-material mkdocs
BUILD ?= build

.PHONY: check lint lint-py test-py test-js build-py js-portable run selftest serve serve-asgi zipapp zipapp-smoke demo demo-smoke docs site openapi openapi-check clean

check: lint test-py lint-py openapi-check test-js demo demo-smoke docs site selftest zipapp-smoke

lint:
	@bash tools/check_targets.sh
	@bash tools/check_portable.sh
	@python3 tools/check_imports.py --extra tools/web.txt
	@python3 tools/check_collisions.py --extra tools/web.txt

build-py:
	@rm -rf $(BUILD)/py
	@mkdir -p $(BUILD)/py
	@set -e; \
	for f in $$(find src tests -name '*.myna' | sort); do \
		if grep -q '^@target(js)$$' "$$f"; then continue; fi; \
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

demo:
	@mkdir -p $(BUILD) site/demo
	@python3 tools/assemble.py --extra tools/web.txt $(BUILD)/demo.myna
	@$(MYNA) compile -t js $(BUILD)/demo.myna -o $(BUILD)/demo.mjs
	@$(NODE) --check $(BUILD)/demo.mjs
	@cp $(BUILD)/demo.mjs site/demo/app.js
	@cp web/styles.css site/demo/styles.css
	@cp web/index.html site/demo/index.html

demo-smoke: demo
	@$(NODE) --test tests/js/demo-smoke.mjs

docs: openapi
	@$(MKDOCS) build --strict

site: demo docs
	@python3 tools/build_site.py
	@rm -rf site/docs
	@cp -r $(BUILD)/docs site/docs
	@python3 tools/audit_site.py

test-js: js-portable
	@$(NODE) --test tests/js/*.test.mjs

run:
	@$(MYNA) run src/mynastock/main.myna

selftest:
	@$(MYNA) run src/mynastock/cli.myna --selftest

serve:
	@mkdir -p $(BUILD)
	@$(MYNA) run src/mynastock/cli.myna serve --db $(BUILD)/mynastock.db $(ARGS)

serve-asgi:
	@mkdir -p $(BUILD)
	@PYTHONPATH=$(BUILD)/py MYNASTOCK_DB=$(BUILD)/mynastock.db $(PYTHON) -m uvicorn mynastock.adapters.asgi_server:asgi_app --host 127.0.0.1 --port 8081

openapi: build-py
	@python3 tools/build_openapi.py

openapi-check: build-py
	@python3 tools/build_openapi.py --check

zipapp:
	@mkdir -p $(BUILD)
	@$(MYNA) bundle src/mynastock/cli.myna --zipapp -o $(BUILD)/mynastock.pyz

zipapp-smoke: zipapp
	@$(PYTHON) -I $(BUILD)/mynastock.pyz --selftest

clean:
	@rm -rf $(BUILD)
