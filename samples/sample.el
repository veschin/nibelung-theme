;; Simple function to count words in buffer
(defun count-words-in-buffer ()
  "Count words in current buffer."
  (interactive)
  (save-excursion
    (goto-char (point-min))
    (let ((count 0))
      (while (forward-word)
        (setq count (1+ count)))
      (message "Word count: %d" count))))

;; Filter even numbers from a list
(defun filter-even (lst)
  (delq nil (mapcar (lambda (x) (if (evenp x) x nil)) lst)))
