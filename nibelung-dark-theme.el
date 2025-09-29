;;; nibelung-dark-theme.el --- Minimalistic dark theme -*- lexical-binding: t; -*-

(require 'nibelung-theme-base)
(require 'nibelung-palettes)

(deftheme nibelung-dark "Minimalistic dark theme inspired by doom-plain and doom-flatwhite")

;; Theme settings
(setq custom--inhibit-theme-enable nil)
(setq org-modern-checkbox '((88 . "[d]") (32 . "[ ]")))
(setq org-modern-fold-stars '((" •" . " •") (" ◦" . " ◦") (" ∞" . " ∞")))
(setq org-src-tab-acts-natively t)
(setq rainbow-delimiters-max-face-count 4)
(set-face-attribute 'line-number nil :inherit 'default)

;; Generate theme using dark palette
(nibelung-theme-create 'nibelung-dark nibelung-dark-palette)

;;;###autoload
(and load-file-name
     (boundp 'custom-theme-load-path)
     (add-to-list 'custom-theme-load-path
                  (file-name-as-directory
                   (file-name-directory load-file-name))))

(provide-theme 'nibelung-dark)
(provide 'nibelung-dark-theme)
;;; nibelung-dark-theme.el ends here