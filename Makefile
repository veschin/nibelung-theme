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
