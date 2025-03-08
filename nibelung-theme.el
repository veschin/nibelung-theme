;;; nibelung-theme.el -*- lexical-binding: t; -*-

;; #F8F9FA
;; #E9ECEF
;; #DEE2E6
;; #CED4DA
;; #ADB5BD
;; #6C757D
;; #495057
;; #343A40
;; #212529
;; #000000

;; #EDF2FB
;; #E2EAFC
;; #D7E3FC
;; #CCDBFD
;; #C1D3FE
;; #B6CCFE
;; #ABC4FF

(deftheme nibelung-theme "Minimalistic theme inspired by doom-plain and doom-flatwhite")
;; (setq custom--inhibit-theme-enable nil)
;; (setq all-the-icons-color-icons nil)
;; (setq nerd-icons-color-icons nil)
(let* (;; Color palette
       (bg "#F8F9FA")
       (lightone "#E9ECEF")
       (lighttwo "#DEE2E6")

       (graylight "#CED4DA")
       (grayzero "#ADB5BD")
       (grayone "#6C757D")
       (graytwo "#495057")
       (graythree "#343A40")
       (grayfour "#212529")

       (bluelight "#E2EAFC")
       (bluezero "#D7E3FC")
       (blueone "#CCDBFD")
       (bluetwo "#C1D3FE")
       (bluethree "#B6CCFE")
       (bluefour "#ABC4FF")

       (fg graythree)
       (fgwhite "#E9ECEF")

       ;; Faces
       (code-block `((t (:extend t :background "#E9ECEF"))))
       (code-block-header `((t (:extend t :background ,lighttwo :foreground ,fg))))
       (constant `((t (:foreground ,grayone))))
       (comment `((t (:extend t :background ,grayone :foreground ,fgwhite))))
       (function `((t (:background ,graylight :foreground ,fg))))
       (header `((t (:background ,graytwo :foreground ,fgwhite))))
       (header-not-extended `((t (:extend nil :background ,graytwo :foreground ,fgwhite))))
       (highlight `((t (:background ,graytwo :foreground ,fgwhite))))
       (link `((t (:foreground ,fg :underline t))))
       (match `((t (:background ,bluefour :foreground ,fgwhite))))
       (modeline `((t (:background ,fg :foreground ,fgwhite))))
       (modeline-indicator header)
       (modeline-white `((t (:foreground ,fg :background ,fgwhite))))
       (optional `((t (:foreground ,graylight))))
       (replace-confirm `((t (:background ,grayone :foreground ,fgwhite))))
       (replace-match* `((t (:background ,graythree :foreground ,fgwhite))))
       (string* `((t (:background ,graytwo :foreground ,fgwhite))))
       (symbol `((t (:foreground ,graythree))))
       (text `((t (:foreground ,fg :weight normal :normal t))))
       (variable `((t (:background ,lightone :foreground ,grayfour))))
       ;; End palette
       )

  (custom-theme-set-faces
   'nibelung-theme
   `(default ((t (:background ,bg))))
   `(cursor ((t (:background ,fgwhite :foreground ,fgwhite))))
   `(highlight ,highlight)
   ;; Constant
   `(font-lock-builtin-face ,constant)
   `(font-lock-constant-face ,constant)
   `(highlight-quoted-symbol ,symbol)
   `(font-lock-keyword-face ((t (:foreground ,grayone))))
   `(font-lock-string-face ,string*)
   `(font-lock-type-face ((t (:foreground ,grayone))))
   `(font-lock-function-name-face ,function)
   `(font-lock-variable-name-face ,variable)
   ;; Comment
   `(font-lock-comment-delimiter-face ((t (:extend nil :foreground ,grayzero :background ,graytwo))))
   `(font-lock-comment-face ,comment)
   `(font-lock-doc-face ((t (:background ,grayzero :foreground ,graylight :slant italic))))
   `(font-lock-warning-face ((t (:foreground ,fg))))
   ;; Misc
   `(line-number ((t (:background ,bg :foreground ,fg))))
   `(message-header-newsgroups ,text)
   `(message-header-xheader ,text)
   `(message-header-cc ,text)
   `(message-header-to ,text)
   `(minibuffer-prompt ,code-block-header)
   `(custom-set ,text)
   `(icon ,optional)
   ;; Company
   (setq company-format-margin-function nil)
   `(company-tooltip ,function)
   `(company-tooltip-common ,match)
   `(company-tooltip-selection ,header)
   `(company-tooltip-scrollbar-thumb ,header)
   `(company-tooltip-scrollbar-track ,variable)
   ;; Match
   `(evil-ex-lazy-highlight ,match)
   `(match ,match)
   `(region ,match)
   `(bold ,match)
   `(orderless-match-face-0 ,match)
   `(orderless-match-face-1 ,match)
   `(show-paren-match ,match)
   `(isearch ,replace-match*)
   `(lazy-highlight ,replace-match*)
   `(evil-ex-substitute-replacement ,replace-confirm)
   ;; Warnings
   `(success ,header)
   `(warning ,header)
   `(error ,header)
   ;; Modeline
   `(doom-nano-modeline-evil-insert-state-face ,modeline-indicator)
   `(doom-nano-modeline-evil-motion-state-face ,modeline-indicator)
   `(doom-nano-modeline-evil-visual-state-face ,modeline-indicator)
   `(doom-nano-modeline-evil-emacs-state-face ,modeline-indicator)
   `(doom-nano-modeline-evil-operator-state-face ,modeline-indicator)
   `(doom-nano-modeline-evil-normal-state-face ,modeline-indicator)
   `(doom-nano-modeline-inactive ,modeline-white)
   `(doom-nano-modeline-cursor-position-face ,modeline)
   `(doom-nano-modeline-vc-branch-name-face ,modeline-indicator)
   `(mode-line ,modeline)
   `(mode-line-buffer-id ,modeline)
   `(mode-line-emphasis ,modeline)
   `(mode-line-highlight ,modeline)
   `(mode-line-faces ,modeline)
   `(mode-line-inactive ,modeline-white)
   ;; Links
   `(diary ,link)
   `(link ,link)
   ;; Org Mode
   `(org-agenda-structure ,text)
   `(org-agenda-date ,text)
   `(org-agenda-date-weekend ,text)
   `(org-modern-label ,header)
   `(org-todo ,header)
   `(org-meta-line ,header-not-extended)
   `(org-block-begin-line ,code-block-header)
   `(org-block ,code-block)
   `(org-block-end-line ,code-block-header)
   `(outline-1 ((t (:background ,bluetwo :foreground ,fg))))
   `(org-done ,optional)
   `(org-headline-done ,optional)
   `(org-agenda-done ,optional)
   `(org-modern-label ,code-block-header)
   ;; Dired
   `(diredfl-file-suffix ,constant)
   `(diredfl-compressed-file-suffix ,constant)
   `(diredfl-file-name ,text)
   `(diredfl-dir-name ,code-block-header)
   `(diredfl-dir-heading ,link)
   `(diredfl-ignored-file-name ,optional)
   `(diredfl-ignored ,optional)
   `(diredfl-symlink ,link)
   `(dgi-commit-message-face ,optional)
   ;; Rainbow delimeters
   `(rainbow-delimiters-depth-9-face ((t (:foreground ,grayone))))
   `(rainbow-delimiters-depth-8-face ((t (:foreground ,blueone))))
   `(rainbow-delimiters-depth-7-face ((t (:foreground ,graytwo))))
   `(rainbow-delimiters-depth-6-face ((t (:foreground ,bluetwo))))
   `(rainbow-delimiters-depth-5-face ((t (:foreground ,graythree))))
   `(rainbow-delimiters-depth-4-face ((t (:foreground ,bluethree))))
   `(rainbow-delimiters-depth-3-face ((t (:foreground ,grayfour))))
   `(rainbow-delimiters-depth-2-face ((t (:foreground ,bluefour))))
   `(rainbow-delimiters-depth-1-face ((t (:foreground ,grayone))))
   ;; Magit
   `(magit-tag ,header)
   `(magit-section-highlight ((t (:background ,bg :foreground ,fg))))
   `(magit-diff-context-highlight ((t (:foreground ,fg))))
   `(magit-branch-local ,match)
   `(magit-branch-remote ,header)
   `(magit-section-heading ,code-block-header)
   `(magit-branch-current ,match)
   `(magit-hash ,optional)
   `(magit-reflog-commit ,comment)
   `(magit-diff-added ,replace-match*)
   `(magit-diff-added-highlight ,replace-match*)
   `(magit-diff-removed ,replace-confirm)
   `(magit-diff-removed-highlight ,replace-confirm)
   `(diff-refine-added ,match)
   `(diff-refine-removed ,variable)
   `(magit-diff-file-heading ,code-block-header)
   `(magit-diffstat-added ,match)
   `(magit-diffstat-removed ,variable)
   `(magit-log-author ,optional)
   ;; Transient
   `(transient-key-stay ,text)
   `(transient-key-exit ,constant)
   `(transient-heading ,code-block-header)
   `(transient-value ,match)
   `(transient-argument ,match)
   ;;
   )
  )
;;;###autoload
(when (and (boundp 'custom-theme-load-path) load-file-name)
  (add-to-list 'custom-theme-load-path
    (file-name-as-directory (file-name-directory load-file-name))))

(provide-theme 'nibelung-theme)
