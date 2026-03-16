;;; export-palette.el --- Export nibelung palettes as JSON -*- lexical-binding: t; -*-

(require 'json)

(defun nibelung-export-palettes ()
  "Export light and dark palettes as JSON to stdout."
  (let ((to-alist (lambda (pl)
                    (let (alist)
                      (while pl
                        (push (cons (substring (symbol-name (car pl)) 1) (cadr pl)) alist)
                        (setq pl (cddr pl)))
                      (nreverse alist)))))
    (princ (json-encode
            `(("light" . ,(funcall to-alist nibelung-light-palette))
              ("dark"  . ,(funcall to-alist nibelung-dark-palette)))))))

(provide 'export-palette)
;;; export-palette.el ends here
