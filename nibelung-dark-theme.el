;;; nibelung-dark-theme.el --- Minimalistic dark theme -*- lexical-binding: t; -*-

(require 'nibelung-theme-base)
(require 'nibelung-palettes)

(deftheme nibelung-dark "Minimalistic dark theme inspired by doom-plain and doom-flatwhite")

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
