;;; nibelung-palettes.el --- Color palettes for nibelung themes -*- lexical-binding: t; -*-

(defconst nibelung-light-palette
  '(;; Base colors
    :bg         "#F8F9FA"
    :fg         "#495057"

    ;; Lightness levels (light to dark)
    :level0     "#E9ECEF"
    :level1     "#DEE2E6"
    :level2     "#CED4DA"
    :level3     "#ADB5BD"
    :level4     "#6C757D"
    :level5     "#343A40"
    :level6     "#212529"

    ;; Accent colors (blue shades)
    :accent-subtle  "#E2EAFC"
    :accent-light   "#B6CCFE"
    :accent-bright  "#ABC4FF"
    :accent-match   "#9BB1FF"

    ;; Semantic roles
    :emphasis     "#9BB1FF"
    :link         "#9BB1FF"
    :string-bg    "#E9ECEF"
    :comment-bg   "#E9ECEF"

    ;; Rainbow colors (darker)
    :rainbow-blue       "#7B8CDE"
    :rainbow-red        "#E08E8E"
    :rainbow-orange     "#D4A574"
    :rainbow-yellow     "#C9C97D"
    :rainbow-green      "#8FBF9F"
    :rainbow-cyan       "#7EB8B8"
    :rainbow-bluelight  "#8BA3D7"
    :rainbow-magenta    "#C99BC9")
  "Color palette for the light nibelung theme.")

(defconst nibelung-dark-palette
  '(;; Base colors
    :bg         "#212529"
    :fg         "#CED4DA"

    ;; Lightness levels (dark to light)
    :level0     "#2B3035"
    :level1     "#343A40"
    :level2     "#495057"
    :level3     "#6C757D"
    :level4     "#ADB5BD"
    :level5     "#DEE2E6"
    :level6     "#F8F9FA"

    ;; Accent colors (blue shades)
    :accent-subtle  "#2B375C"
    :accent-light   "#577DB7"
    :accent-bright  "#628ECE"
    :accent-match   "#9BB1FF"

    ;; Semantic roles
    :emphasis     "#9BB1FF"
    :link         "#9BB1FF"
    :string-bg    "#343A40"
    :comment-bg   "#2B3035"

    ;; Rainbow colors
    :rainbow-blue       "#9FA0FF"
    :rainbow-red        "#FFADAD"
    :rainbow-orange     "#FFD6A5"
    :rainbow-yellow     "#FDFFB6"
    :rainbow-green      "#CAFFBF"
    :rainbow-cyan       "#9BF6FF"
    :rainbow-bluelight  "#A0C4FF"
    :rainbow-magenta    "#FFC6FF")
  "Color palette for the dark nibelung theme.")

(provide 'nibelung-palettes)
;;; nibelung-palettes.el ends here