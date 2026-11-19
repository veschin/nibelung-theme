EMACS ?= emacs
BATCH = $(EMACS) --batch -L .

EL_FILES = nibelung-palettes.el nibelung-theme-base.el nibelung-theme.el nibelung-dark-theme.el
ELC_FILES = $(EL_FILES:.el=.elc)

.PHONY: test test-load test-compile test-faces clean

test: test-compile test-load test-faces

test-compile: clean
	@echo "=== Byte-compiling ==="
	@for f in $(EL_FILES); do \
		printf "  %-30s" "$$f"; \
		output=$$($(BATCH) --eval "(setq byte-compile-error-on-warn t)" -f batch-byte-compile "$$f" 2>&1); \
		if [ $$? -eq 0 ] && ! echo "$$output" | grep -qi "error"; then \
			echo "OK"; \
		else \
			echo "FAIL"; \
			echo "$$output"; \
			exit 1; \
		fi; \
	done

test-load:
	@echo "=== Loading themes ==="
	@printf "  %-30s" "nibelung (light)"
	@$(BATCH) --eval "(progn \
		(load-file \"nibelung-theme.el\") \
		(load-theme 'nibelung t) \
		(kill-emacs 0))" 2>&1 && echo "OK" || (echo "FAIL" && exit 1)
	@printf "  %-30s" "nibelung-dark"
	@$(BATCH) --eval "(progn \
		(load-file \"nibelung-dark-theme.el\") \
		(load-theme 'nibelung-dark t) \
		(kill-emacs 0))" 2>&1 && echo "OK" || (echo "FAIL" && exit 1)

test-faces:
	@echo "=== Checking faces ==="
	@$(BATCH) --eval " \
	(progn \
	  (load-file \"nibelung-theme.el\") \
	  (load-theme (quote nibelung) t) \
	  (let ((errors 0) (total 0)) \
	    (dolist (entry (get (quote nibelung) (quote theme-settings))) \
	      (when (eq (nth 0 entry) (quote theme-face)) \
	        (let ((face (nth 1 entry))) \
	          (setq total (1+ total)) \
	          (unless (facep face) \
	            (setq errors (1+ errors)) \
	            (message \"  WARN: %s is not a known face (package not loaded)\" face))))) \
	    (message \"  %d faces registered\" total) \
	    (when (> errors 0) \
	      (message \"  %d faces unknown (expected if packages not installed)\" errors))) \
	  (kill-emacs 0))" 2>&1

clean:
	@rm -f *.elc

.PHONY: export export-clean test-export test-terminal-themes

export:
	python3 export/generate.py --emacs $(EMACS) --output-dir dist

export-clean:
	rm -rf dist/

test-terminal-themes:
	python3 export/test_terminal_themes.py "$(EMACS)"

test-export: test-terminal-themes
	@echo "=== Validating export ==="
	@python3 -m json.tool dist/vscode/themes/nibelung-color-theme.json > /dev/null
	@python3 -m json.tool dist/vscode/themes/nibelung-dark-color-theme.json > /dev/null
	@python3 -m json.tool dist/vscode/package.json > /dev/null
	@python3 -m json.tool dist/zed/themes/nibelung.json > /dev/null
	@python3 -c "import xml.etree.ElementTree as ET; ET.parse('dist/intellij/Nibelung.icls')"
	@python3 -c "import xml.etree.ElementTree as ET; ET.parse('dist/intellij/Nibelung_Dark.icls')"
	@if command -v luac >/dev/null; then luac -p dist/neovim/colors/nibelung.lua; else echo "  WARN: luac not found, skipping Lua validation"; fi
	@python3 -m json.tool dist/caelestia/nibelung-scheme.json > /dev/null
	@python3 -m json.tool dist/caelestia/nibelung-dark-scheme.json > /dev/null
	@python3 -m json.tool dist/pi/themes/nibelung.json > /dev/null
	@python3 -m json.tool dist/pi/themes/nibelung-dark.json > /dev/null
	@echo "All export validations passed"

.PHONY: install install-alacritty install-caelestia install-omp install-zed

install: install-alacritty install-caelestia install-omp install-zed

install-alacritty: export
	@echo "=== Installing Alacritty themes ==="
	mkdir -p ~/.config/alacritty
	cp dist/alacritty/nibelung.toml ~/.config/alacritty/nibelung.toml
	cp dist/alacritty/nibelung-dark.toml ~/.config/alacritty/nibelung-dark.toml
	@echo "Alacritty: installed to ~/.config/alacritty/"

install-caelestia: export
	@echo "=== Installing Caelestia schemes ==="
	@DEST=$$(python3 -c "import caelestia, os; print(os.path.join(os.path.dirname(caelestia.__file__), 'data', 'schemes'))"); \
	sudo mkdir -p "$$DEST/nibelung/default" && \
	sudo cp dist/caelestia/default/light.txt "$$DEST/nibelung/default/light.txt" && \
	sudo cp dist/caelestia/default/dark.txt "$$DEST/nibelung/default/dark.txt" && \
	echo "Caelestia: installed to $$DEST/nibelung/"


install-omp: export
	mkdir -p "$${PI_CODING_AGENT_DIR:-$$HOME/.omp/agent}/themes" "$${PI_CODING_AGENT_DIR:-$$HOME/.omp/agent}/extensions"
	cp dist/omp/themes/*.json "$${PI_CODING_AGENT_DIR:-$$HOME/.omp/agent}/themes/"
	cp export/omp-alacritty-appearance.ts "$${PI_CODING_AGENT_DIR:-$$HOME/.omp/agent}/extensions/"


install-zed: export
	@echo "=== Installing Zed theme ==="
	mkdir -p ~/.config/zed/themes
	cp dist/zed/themes/nibelung.json ~/.config/zed/themes/nibelung.json
	@echo "Zed: installed to ~/.config/zed/themes/"
