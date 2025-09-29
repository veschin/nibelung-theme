.PHONY: test clean

test: test-light test-dark

test-light:
	@echo "Testing nibelung light theme..."
	@emacs --batch --eval "(progn \
		(add-to-list 'load-path \".\") \
		(load-file \"nibelung-theme.el\") \
		(message \"✓ Light theme loaded successfully\"))" 2>&1 | grep -E "(✓|error|Error)"

test-dark:
	@echo "Testing nibelung dark theme..."
	@emacs --batch --eval "(progn \
		(add-to-list 'load-path \".\") \
		(load-file \"nibelung-dark-theme.el\") \
		(message \"✓ Dark theme loaded successfully\"))" 2>&1 | grep -E "(✓|error|Error)"

clean:
	@find . -name "*.elc" -delete
	@echo "Cleaned compiled files"