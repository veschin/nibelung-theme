;;; nibelung-theme.el --- Minimalistic light theme -*- lexical-binding: t; -*-

(require 'nibelung-theme-base)
(require 'nibelung-palettes)

(deftheme nibelung "Minimalistic light theme inspired by doom-plain and doom-flatwhite")

;; Theme settings
(setq custom--inhibit-theme-enable nil)
(setq org-modern-checkbox '((88 . "[d]") (32 . "[ ]")))
(setq org-modern-fold-stars '((" •" . " •") (" ◦" . " ◦") (" ∞" . " ∞")))
(setq org-src-tab-acts-natively t)
(setq rainbow-delimiters-max-face-count 4)
(set-face-attribute 'line-number nil :inherit 'default)

;; Generate theme using light palette
(nibelung-theme-create 'nibelung nibelung-light-palette)

;;;###autoload
(and load-file-name
     (boundp 'custom-theme-load-path)
     (add-to-list 'custom-theme-load-path
                  (file-name-as-directory
                   (file-name-directory load-file-name))))

(provide-theme 'nibelung)
(provide 'nibelung-theme)
;;; nibelung-theme.el ends here