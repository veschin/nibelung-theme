#!/usr/bin/env python3
"""Nibelung theme generator -- exports palettes from Emacs and generates themes
for VSCode, Neovim, IntelliJ IDEA, Alacritty, and Caelestia/Quickshell."""

import argparse
import json
import os
import subprocess
import xml.etree.ElementTree as ET


# ---------------------------------------------------------------------------
# Palette extraction
# ---------------------------------------------------------------------------

def extract_palettes(emacs):
    result = subprocess.run(
        [emacs, "--batch", "-L", ".", "-l", "nibelung-palettes.el",
         "-l", "export/export-palette.el", "--eval", "(nibelung-export-palettes)"],
        capture_output=True, text=True, check=True,
    )
    palettes = json.loads(result.stdout)
    if set(palettes["light"].keys()) != set(palettes["dark"].keys()):
        raise ValueError("Light and dark palettes have different keys")
    return palettes["light"], palettes["dark"]


# ---------------------------------------------------------------------------
# Role and ANSI maps
# ---------------------------------------------------------------------------

def _blend(hex1, hex2, ratio=0.5):
    """Blend two #RRGGBB colors. ratio=0 returns hex1, ratio=1 returns hex2."""
    r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
    r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"


def roles(p):
    return {
        "bold":     p["emphasis"],
        "builtin":  p["level3"],
        "comment":  p["level3"],
        "constant": p["level4"],
        "function": p["level5"],
        "optional": p["level2"],
        "quiet":    p["level2"],
    }


def ansi(p):
    return {
        "black":          p["level1"],
        "red":            p["rainbow-red"],
        "green":          p["rainbow-green"],
        "yellow":         p["rainbow-yellow"],
        "blue":           p["rainbow-blue"],
        "magenta":        p["rainbow-magenta"],
        "cyan":           p["rainbow-cyan"],
        "white":          p["level4"],
        "bright_black":   p["level3"],
        "bright_red":     p["rainbow-red"],
        "bright_green":   p["rainbow-green"],
        "bright_yellow":  p["rainbow-yellow"],
        "bright_blue":    p["rainbow-bluelight"],
        "bright_magenta": p["rainbow-magenta"],
        "bright_cyan":    p["rainbow-cyan"],
        "bright_white":   p["level6"],
    }


# ---------------------------------------------------------------------------
# VSCode backend
# ---------------------------------------------------------------------------

def alpha(color, a):
    return color + a


def _vscode_theme(p, r, a, name, ui_theme):
    colors = {
        "editor.background":                     p["bg"],
        "editor.foreground":                     p["fg"],
        "editorCursor.foreground":               p["fg"],
        "editor.selectionBackground":            p["accent-subtle"],
        "editor.lineHighlightBackground":        p["level0"],
        "editor.findMatchBackground":            alpha(p["level5"], "80"),
        "editor.findMatchHighlightBackground":   alpha(p["level4"], "40"),
        "editorLineNumber.foreground":           p["fg"],
        "editorLineNumber.activeForeground":     p["emphasis"],
        "editorIndentGuide.background":          p["level0"],
        "editorIndentGuide.activeBackground":    p["level1"],
        "editorBracketMatch.background":         alpha(p["emphasis"], "40"),
        "editorBracketMatch.border":             p["emphasis"],
        "editorBracketHighlight.foreground1":    p["accent-light"],
        "editorBracketHighlight.foreground2":    p["level3"],
        "editorBracketHighlight.foreground3":    p["rainbow-blue"],
        "editorBracketHighlight.foreground4":    p["level4"],
        "editorWidget.background":               p["level0"],
        "editorWidget.border":                   p["level2"],
        "editorGutter.addedBackground":          p["rainbow-green"],
        "editorGutter.modifiedBackground":       p["rainbow-yellow"],
        "editorGutter.deletedBackground":        p["rainbow-red"],
        "gitDecoration.modifiedResourceForeground":  p["level4"],
        "gitDecoration.untrackedResourceForeground": p["level3"],
        "gitDecoration.deletedResourceForeground":   p["level5"],
        "gitDecoration.ignoredResourceForeground":   p["level2"],
        "sideBar.background":                    p["level0"],
        "sideBar.foreground":                    p["fg"],
        "sideBarTitle.foreground":               p["fg"],
        "titleBar.activeBackground":             p["bg"],
        "titleBar.activeForeground":             p["fg"],
        "statusBar.background":                  p["fg"],
        "statusBar.foreground":                  p["level0"],
        "tab.activeBackground":                  p["bg"],
        "tab.inactiveBackground":                p["level0"],
        "tab.activeForeground":                  p["fg"],
        "tab.inactiveForeground":                p["level3"],
        "list.activeSelectionBackground":        alpha(p["emphasis"], "40"),
        "list.hoverBackground":                  alpha(p["level0"], "80"),
        "list.focusBackground":                  p["level0"],
        "panel.background":                      p["level0"],
        "panel.border":                          p["level1"],
        "scrollbarSlider.background":            alpha(p["level2"], "60"),
        "scrollbarSlider.hoverBackground":       alpha(p["level3"], "60"),
        "diffEditor.insertedTextBackground":     alpha(p["rainbow-green"], "20"),
        "diffEditor.removedTextBackground":      alpha(p["rainbow-red"], "20"),
        "minimap.background":                    p["bg"],
        "terminal.ansiBlack":                    a["black"],
        "terminal.ansiRed":                      a["red"],
        "terminal.ansiGreen":                    a["green"],
        "terminal.ansiYellow":                   a["yellow"],
        "terminal.ansiBlue":                     a["blue"],
        "terminal.ansiMagenta":                  a["magenta"],
        "terminal.ansiCyan":                     a["cyan"],
        "terminal.ansiWhite":                    a["white"],
        "terminal.ansiBrightBlack":              a["bright_black"],
        "terminal.ansiBrightRed":                a["bright_red"],
        "terminal.ansiBrightGreen":              a["bright_green"],
        "terminal.ansiBrightYellow":             a["bright_yellow"],
        "terminal.ansiBrightBlue":               a["bright_blue"],
        "terminal.ansiBrightMagenta":            a["bright_magenta"],
        "terminal.ansiBrightCyan":               a["bright_cyan"],
        "terminal.ansiBrightWhite":              a["bright_white"],
    }

    # NOTE: VSCode tokenColors do not support per-scope backgroundColor.
    # Comment background highlighting (the Emacs theme's signature feature)
    # cannot be reproduced here. IntelliJ and Neovim support it.
    token_colors = [
        {"scope": "comment",
         "settings": {"fontStyle": "", "foreground": r["comment"]}},
        {"scope": "comment.block.documentation",
         "settings": {"fontStyle": "", "foreground": r["optional"]}},
        {"scope": "keyword, keyword.control, keyword.other",
         "settings": {"fontStyle": "", "foreground": r["constant"]}},
        {"scope": "storage.type, storage.modifier",
         "settings": {"fontStyle": "", "foreground": r["builtin"]}},
        {"scope": "string, string.quoted.single, string.quoted.double",
         "settings": {"fontStyle": "", "foreground": r["optional"]}},
        {"scope": "string.regexp",
         "settings": {"fontStyle": "", "foreground": r["constant"]}},
        {"scope": "entity.name.function",
         "settings": {"fontStyle": "", "foreground": r["bold"]}},
        {"scope": "entity.name.function.definition",
         "settings": {"fontStyle": "", "foreground": r["optional"]}},
        {"scope": "entity.name.type, entity.name.class, support.class, entity.other.inherited-class",
         "settings": {"fontStyle": "", "foreground": r["builtin"]}},
        {"scope": "variable, variable.other.readwrite",
         "settings": {"fontStyle": "", "foreground": r["builtin"]}},
        {"scope": "variable.parameter",
         "settings": {"fontStyle": "", "foreground": r["optional"]}},
        {"scope": "variable.language",
         "settings": {"fontStyle": "", "foreground": r["builtin"]}},
        {"scope": "variable.other.property",
         "settings": {"fontStyle": "", "foreground": r["optional"]}},
        {"scope": "constant.numeric, constant.language, constant.other",
         "settings": {"fontStyle": "", "foreground": r["constant"]}},
        {"scope": "keyword.operator",
         "settings": {"fontStyle": "", "foreground": r["quiet"]}},
        {"scope": "punctuation",
         "settings": {"fontStyle": "", "foreground": r["quiet"]}},
        {"scope": "support.function",
         "settings": {"fontStyle": "", "foreground": r["bold"]}},
        {"scope": "entity.name.tag",
         "settings": {"fontStyle": "", "foreground": r["builtin"]}},
        {"scope": "entity.other.attribute-name",
         "settings": {"fontStyle": "", "foreground": r["quiet"]}},
        {"scope": "markup.heading",
         "settings": {"fontStyle": "", "foreground": r["function"]}},
        {"scope": "markup.bold, markup.italic",
         "settings": {"fontStyle": "", "foreground": r["bold"]}},
        {"scope": "markup.inline.raw",
         "settings": {"fontStyle": "", "foreground": r["constant"]}},
        {"scope": "meta.embedded, source.embedded",
         "settings": {"fontStyle": "", "foreground": p["fg"]}},
    ]

    semantic_token_colors = {
        "function.declaration": {"foreground": r["optional"]},
        "function.defaultLibrary": {"foreground": r["bold"]},
    }

    return {
        "$schema": "vscode://schemas/color-theme",
        "name": name,
        "type": ui_theme,
        "colors": colors,
        "tokenColors": token_colors,
        "semanticTokenColors": semantic_token_colors,
    }


def generate_vscode(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "vscode")
    themes_dir = os.path.join(out, "themes")
    os.makedirs(themes_dir, exist_ok=True)

    package = {
        "name": "nibelung-theme",
        "displayName": "Nibelung",
        "description": "Minimalist color theme with cool grays and subtle blue accents",
        "version": "0.1.0",
        "engines": {"vscode": "^1.60.0"},
        "categories": ["Themes"],
        "contributes": {
            "themes": [
                {"label": "Nibelung", "uiTheme": "vs",
                 "path": "./themes/nibelung-color-theme.json"},
                {"label": "Nibelung Dark", "uiTheme": "vs-dark",
                 "path": "./themes/nibelung-dark-color-theme.json"},
            ]
        },
    }

    _write_json(os.path.join(out, "package.json"), package)

    light_theme = _vscode_theme(
        light_p, roles(light_p), ansi(light_p), "Nibelung", "vs")
    _write_json(os.path.join(themes_dir, "nibelung-color-theme.json"), light_theme)

    dark_theme = _vscode_theme(
        dark_p, roles(dark_p), ansi(dark_p), "Nibelung Dark", "vs-dark")
    _write_json(os.path.join(themes_dir, "nibelung-dark-color-theme.json"), dark_theme)

    print(f"VSCode: wrote {out}")


# ---------------------------------------------------------------------------
# Neovim backend
# ---------------------------------------------------------------------------

def _nvim_hl(group, opts):
    parts = []
    for k, v in opts.items():
        if isinstance(v, bool):
            parts.append(f"{k} = {'true' if v else 'false'}")
        else:
            parts.append(f'{k} = "{v}"')
    return f'hl("{group}", {{{", ".join(parts)}}})'


def _nvim_theme(p, r, a, name, variant):
    lines = [
        'vim.cmd("highlight clear")',
        'if vim.fn.exists("syntax_on") then vim.cmd("syntax reset") end',
        f'vim.g.colors_name = "{name}"',
        f'vim.o.background = "{variant}"',
        "vim.o.termguicolors = true",
        "",
        "local hl = function(group, opts) vim.api.nvim_set_hl(0, group, opts) end",
        "",
        "-- Legacy syntax groups",
    ]

    def hl(group, **opts):
        lines.append(_nvim_hl(group, opts))

    hl("Normal",    fg=p["fg"],       bg=p["bg"],       bold=False, italic=False)
    hl("Comment",   fg=r["comment"],  bg=p["comment-bg"], bold=False, italic=False)
    hl("String",    fg=r["optional"],                   bold=False, italic=False)
    hl("Character", fg=r["optional"],                   bold=False, italic=False)
    hl("Function",  fg=r["bold"],                       bold=False, italic=False)
    hl("Keyword",   fg=r["constant"],                   bold=False, italic=False)
    hl("Type",      fg=r["builtin"],                    bold=False, italic=False)
    hl("Identifier",fg=p["fg"],                         bold=False, italic=False)
    hl("Constant",  fg=r["constant"],                   bold=False, italic=False)
    hl("Number",    fg=r["constant"],                   bold=False, italic=False)
    hl("Boolean",   fg=r["constant"],                   bold=False, italic=False)
    hl("Operator",  fg=r["quiet"],                      bold=False, italic=False)
    hl("PreProc",   fg=r["builtin"],                    bold=False, italic=False)
    hl("Special",   fg=r["constant"],                   bold=False, italic=False)
    hl("Delimiter", fg=r["bold"],                       bold=False, italic=False)
    hl("Statement", fg=r["constant"],                   bold=False, italic=False)
    hl("Title",     fg=r["function"],                   bold=False, italic=False)
    hl("Directory", fg=r["constant"],                   bold=False, italic=False)

    lines.append("")
    lines.append("-- Treesitter groups")

    hl("@keyword",              fg=r["constant"],                   bold=False, italic=False)
    hl("@keyword.return",       fg=r["constant"],                   bold=False, italic=False)
    hl("@keyword.function",     fg=r["constant"],                   bold=False, italic=False)
    hl("@keyword.import",       fg=r["constant"],                   bold=False, italic=False)
    hl("@string",               fg=r["optional"],                   bold=False, italic=False)
    hl("@string.escape",        fg=r["quiet"],                      bold=False, italic=False)
    hl("@string.regexp",        fg=r["constant"],                   bold=False, italic=False)
    hl("@string.documentation", fg=r["optional"],                   bold=False, italic=False)
    hl("@comment",              fg=r["comment"],  bg=p["comment-bg"], bold=False, italic=False)
    hl("@function",             fg=r["bold"],                       bold=False, italic=False)
    hl("@function.call",        fg=r["bold"],                       bold=False, italic=False)
    hl("@function.builtin",     fg=r["bold"],                       bold=False, italic=False)
    hl("@variable",             fg=r["builtin"],                    bold=False, italic=False)
    hl("@variable.builtin",     fg=r["builtin"],                    bold=False, italic=False)
    hl("@variable.parameter",   fg=r["optional"],                   bold=False, italic=False)
    hl("@variable.member",      fg=r["optional"],                   bold=False, italic=False)
    hl("@type",                 fg=r["builtin"],                    bold=False, italic=False)
    hl("@type.builtin",         fg=r["builtin"],                    bold=False, italic=False)
    hl("@constructor",          fg=r["builtin"],                    bold=False, italic=False)
    hl("@module",               fg=r["builtin"],                    bold=False, italic=False)
    hl("@property",             fg=r["optional"],                   bold=False, italic=False)
    hl("@operator",             fg=r["quiet"],                      bold=False, italic=False)
    hl("@number",               fg=r["constant"],                   bold=False, italic=False)
    hl("@boolean",              fg=r["constant"],                   bold=False, italic=False)
    hl("@punctuation.bracket",  fg=r["quiet"],                      bold=False, italic=False)
    hl("@punctuation.delimiter",fg=r["quiet"],                      bold=False, italic=False)
    hl("@constant",             fg=r["constant"],                   bold=False, italic=False)
    hl("@constant.builtin",     fg=r["constant"],                   bold=False, italic=False)
    hl("@markup.heading",       fg=r["function"],                   bold=False, italic=False)
    hl("@markup.strong",        fg=r["bold"],                       bold=False, italic=False)
    hl("@markup.italic",        fg=r["bold"],                       bold=False, italic=False)
    hl("@markup.raw",           fg=r["constant"],                   bold=False, italic=False)
    hl("@markup.link",          fg=p["link"],                       bold=False, italic=False)
    hl("@tag",                  fg=r["builtin"],                    bold=False, italic=False)
    hl("@tag.attribute",        fg=r["quiet"],                      bold=False, italic=False)
    hl("@tag.delimiter",        fg=r["quiet"],                      bold=False, italic=False)

    lines.append("")
    lines.append("-- LSP semantic tokens")

    hl("@lsp.type.function",   fg=r["bold"],                        bold=False, italic=False)
    hl("@lsp.type.variable",   fg=r["builtin"],                     bold=False, italic=False)
    hl("@lsp.type.type",       fg=r["builtin"],                     bold=False, italic=False)
    hl("@lsp.type.keyword",    fg=r["constant"],                    bold=False, italic=False)
    hl("@lsp.type.comment",    fg=r["comment"],  bg=p["comment-bg"], bold=False, italic=False)
    hl("@lsp.type.string",     fg=r["optional"],                    bold=False, italic=False)
    hl("@lsp.type.number",     fg=r["constant"],                    bold=False, italic=False)
    hl("@lsp.type.operator",   fg=r["quiet"],                       bold=False, italic=False)
    hl("@lsp.type.property",   fg=r["optional"],                    bold=False, italic=False)
    hl("@lsp.type.parameter",  fg=r["optional"],                    bold=False, italic=False)
    hl("@lsp.type.namespace",  fg=r["builtin"],                     bold=False, italic=False)
    lines.append(_nvim_hl("@lsp.mod.deprecated", {"strikethrough": True}))

    lines.append("")
    lines.append("-- UI groups")

    hl("Cursor",       fg=p["bg"],       bg=p["fg"],       bold=False, italic=False)
    hl("CursorLine",                     bg=p["level0"],   bold=False, italic=False)
    hl("CursorColumn",                   bg=p["level0"],   bold=False, italic=False)
    hl("ColorColumn",                    bg=p["level0"],   bold=False, italic=False)
    hl("Visual",       fg=p["level1"],   bg=p["emphasis"], bold=False, italic=False)
    hl("Search",       fg=p["level0"],   bg=p["level5"],   bold=False, italic=False)
    hl("IncSearch",    fg=p["level0"],   bg=p["level5"],   bold=False, italic=False)
    hl("MatchParen",   fg=p["level1"],   bg=p["emphasis"], bold=False, italic=False)
    hl("Pmenu",        fg=p["fg"],       bg=p["level0"],   bold=False, italic=False)
    hl("PmenuSel",     fg=p["level1"],   bg=p["emphasis"], bold=False, italic=False)
    hl("PmenuSbar",                      bg=p["level1"],   bold=False, italic=False)
    hl("PmenuThumb",                     bg=p["level3"],   bold=False, italic=False)
    hl("NormalFloat",  fg=p["fg"],       bg=p["level0"],   bold=False, italic=False)
    hl("FloatBorder",  fg=p["level2"],   bg=p["level0"],   bold=False, italic=False)
    hl("StatusLine",   fg=p["level0"],   bg=p["fg"],       bold=False, italic=False)
    hl("StatusLineNC", fg=p["level5"],   bg=p["level0"],   bold=False, italic=False)
    hl("LineNr",       fg=p["fg"],       bg=p["bg"],       bold=False, italic=False)
    hl("CursorLineNr", fg=p["emphasis"], bg=p["bg"],       bold=False, italic=False)
    hl("SignColumn",   fg=p["fg"],       bg=p["bg"],       bold=False, italic=False)
    hl("Folded",       fg=p["level3"],   bg=p["level0"],   bold=False, italic=False)
    hl("FoldColumn",   fg=p["level3"],   bg=p["bg"],       bold=False, italic=False)
    hl("NonText",      fg=p["level2"],                     bold=False, italic=False)
    hl("SpecialKey",   fg=p["level2"],                     bold=False, italic=False)
    hl("Whitespace",   fg=p["level2"],                     bold=False, italic=False)
    hl("Conceal",      fg=p["level3"],                     bold=False, italic=False)
    hl("WinSeparator", fg=p["level1"],                     bold=False, italic=False)
    hl("VertSplit",    fg=p["level1"],                     bold=False, italic=False)
    hl("WildMenu",     fg=p["level1"],   bg=p["emphasis"], bold=False, italic=False)
    hl("TabLine",      fg=p["level3"],   bg=p["level0"],   bold=False, italic=False)
    hl("TabLineFill",                    bg=p["level0"],   bold=False, italic=False)
    hl("TabLineSel",   fg=p["fg"],       bg=p["bg"],       bold=False, italic=False)
    hl("ErrorMsg",     fg=p["level5"],                     bold=False, italic=False)
    hl("WarningMsg",   fg=p["level4"],                     bold=False, italic=False)
    hl("MoreMsg",      fg=p["emphasis"],                   bold=False, italic=False)
    hl("ModeMsg",      fg=p["fg"],                         bold=False, italic=False)
    hl("Question",     fg=p["emphasis"],                   bold=False, italic=False)
    lines.append(_nvim_hl("SpellBad",   {"sp": p["level5"],   "undercurl": True}))
    lines.append(_nvim_hl("SpellCap",   {"sp": p["level4"],   "undercurl": True}))
    lines.append(_nvim_hl("SpellRare",  {"sp": p["emphasis"], "undercurl": True}))
    lines.append(_nvim_hl("SpellLocal", {"sp": p["level3"],   "undercurl": True}))

    lines.append("")
    lines.append("-- Diagnostics")

    hl("DiagnosticError", fg=p["level5"],   bold=False, italic=False)
    hl("DiagnosticWarn",  fg=p["level4"],   bold=False, italic=False)
    hl("DiagnosticInfo",  fg=p["emphasis"], bold=False, italic=False)
    hl("DiagnosticHint",  fg=p["level3"],   bold=False, italic=False)
    lines.append(_nvim_hl("DiagnosticUnderlineError", {"sp": p["level5"],   "underline": True}))
    lines.append(_nvim_hl("DiagnosticUnderlineWarn",  {"sp": p["level4"],   "underline": True}))
    lines.append(_nvim_hl("DiagnosticUnderlineInfo",  {"sp": p["emphasis"], "underline": True}))
    lines.append(_nvim_hl("DiagnosticUnderlineHint",  {"sp": p["level3"],   "underline": True}))

    lines.append("")
    lines.append("-- Diff")

    hl("DiffAdd",    fg=p["rainbow-green"],  bg=p["level1"], bold=False, italic=False)
    hl("DiffDelete", fg=p["rainbow-red"],    bg=p["level1"], bold=False, italic=False)
    hl("DiffChange", fg=p["rainbow-yellow"], bg=p["level1"], bold=False, italic=False)
    hl("DiffText",   fg=p["rainbow-yellow"], bg=p["level2"], bold=False, italic=False)

    lines.append("")
    lines.append("-- Terminal colors")

    ansi_order = [
        "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
        "bright_black", "bright_red", "bright_green", "bright_yellow",
        "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
    ]
    for i, key in enumerate(ansi_order):
        lines.append(f'vim.g.terminal_color_{i} = "{a[key]}"')

    return "\n".join(lines) + "\n"


def generate_neovim(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "neovim", "colors")
    os.makedirs(out, exist_ok=True)

    light_lua = _nvim_theme(light_p, roles(light_p), ansi(light_p), "nibelung", "light")
    with open(os.path.join(out, "nibelung.lua"), "w") as f:
        f.write(light_lua)

    dark_lua = _nvim_theme(dark_p, roles(dark_p), ansi(dark_p), "nibelung-dark", "dark")
    with open(os.path.join(out, "nibelung-dark.lua"), "w") as f:
        f.write(dark_lua)

    print(f"Neovim: wrote {os.path.dirname(out)}")


# ---------------------------------------------------------------------------
# IntelliJ backend
# ---------------------------------------------------------------------------

def icls_color(hex_color):
    return hex_color[1:].upper().zfill(6)


def _icls_attr(parent, name, fg=None, bg=None):
    opt = ET.SubElement(parent, "option", name=name)
    val = ET.SubElement(opt, "value")
    if fg is not None:
        ET.SubElement(val, "option", name="FOREGROUND", value=icls_color(fg))
    if bg is not None:
        ET.SubElement(val, "option", name="BACKGROUND", value=icls_color(bg))
    ET.SubElement(val, "option", name="FONT_TYPE", value="0")


def _icls_scheme(p, r, name, parent_scheme):
    scheme = ET.Element("scheme", name=name, version="142", parent_scheme=parent_scheme)

    colors_el = ET.SubElement(scheme, "colors")
    color_map = {
        "CARET_COLOR":                  p["fg"],
        "CARET_ROW_COLOR":              p["level0"],
        "SELECTION_BACKGROUND":         p["emphasis"],
        "SELECTION_FOREGROUND":         p["level1"],
        "GUTTER_BACKGROUND":            p["bg"],
        "LINE_NUMBERS_COLOR":           p["fg"],
        "LINE_NUMBER_ON_CARET_ROW_COLOR": p["emphasis"],
        "INDENT_GUIDE":                 p["level0"],
        "SELECTED_INDENT_GUIDE":        p["level1"],
        "RIGHT_MARGIN_COLOR":           p["level1"],
        "ADDED_LINES_COLOR":            p["rainbow-green"],
        "MODIFIED_LINES_COLOR":         p["rainbow-yellow"],
        "DELETED_LINES_COLOR":          p["rainbow-red"],
        "FILESTATUS_ADDED":             p["rainbow-green"],
        "FILESTATUS_MODIFIED":          p["rainbow-yellow"],
        "FILESTATUS_DELETED":           p["rainbow-red"],
    }
    for k, v in color_map.items():
        ET.SubElement(colors_el, "option", name=k, value=icls_color(v))

    attrs_el = ET.SubElement(scheme, "attributes")

    _icls_attr(attrs_el, "DEFAULT_KEYWORD",              fg=r["constant"])
    _icls_attr(attrs_el, "DEFAULT_STRING",               fg=r["optional"])
    _icls_attr(attrs_el, "DEFAULT_NUMBER",               fg=r["constant"])
    _icls_attr(attrs_el, "DEFAULT_CONSTANT",             fg=r["constant"])
    _icls_attr(attrs_el, "DEFAULT_LINE_COMMENT",         fg=r["comment"], bg=p["comment-bg"])
    _icls_attr(attrs_el, "DEFAULT_BLOCK_COMMENT",        fg=r["comment"], bg=p["comment-bg"])
    _icls_attr(attrs_el, "DEFAULT_DOC_COMMENT",          fg=r["optional"])
    _icls_attr(attrs_el, "DEFAULT_DOC_COMMENT_TAG",      fg=r["optional"])
    _icls_attr(attrs_el, "DEFAULT_FUNCTION_DECLARATION", fg=r["optional"])
    _icls_attr(attrs_el, "DEFAULT_STATIC_METHOD",        fg=r["bold"])
    _icls_attr(attrs_el, "DEFAULT_INSTANCE_METHOD",      fg=r["bold"])
    _icls_attr(attrs_el, "DEFAULT_IDENTIFIER",           fg=p["fg"])
    _icls_attr(attrs_el, "DEFAULT_PARAMETER",            fg=r["optional"])
    _icls_attr(attrs_el, "DEFAULT_INSTANCE_FIELD",       fg=r["optional"])
    _icls_attr(attrs_el, "DEFAULT_STATIC_FIELD",         fg=r["optional"])
    _icls_attr(attrs_el, "DEFAULT_GLOBAL_VARIABLE",      fg=r["builtin"])
    _icls_attr(attrs_el, "DEFAULT_CLASS_NAME",           fg=r["builtin"])
    _icls_attr(attrs_el, "DEFAULT_INTERFACE_NAME",       fg=r["builtin"])
    _icls_attr(attrs_el, "DEFAULT_OPERATION_SIGN",       fg=r["quiet"])
    _icls_attr(attrs_el, "DEFAULT_BRACES",               fg=r["quiet"])
    _icls_attr(attrs_el, "DEFAULT_BRACKETS",             fg=r["quiet"])
    _icls_attr(attrs_el, "DEFAULT_PARENTHS",             fg=r["quiet"])
    _icls_attr(attrs_el, "DEFAULT_DOT",                  fg=r["quiet"])
    _icls_attr(attrs_el, "DEFAULT_COMMA",                fg=r["quiet"])
    _icls_attr(attrs_el, "DEFAULT_SEMICOLON",            fg=r["quiet"])
    _icls_attr(attrs_el, "DEFAULT_METADATA",             fg=r["builtin"])
    _icls_attr(attrs_el, "DEFAULT_LABEL",                fg=r["constant"])
    _icls_attr(attrs_el, "DIFF_CONFLICT",                fg=p["rainbow-orange"])
    _icls_attr(attrs_el, "DIFF_DELETED",                 fg=p["rainbow-red"])
    _icls_attr(attrs_el, "DIFF_INSERTED",                fg=p["rainbow-green"])
    _icls_attr(attrs_el, "DIFF_MODIFIED",                fg=p["rainbow-yellow"])

    return scheme


def generate_intellij(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "intellij")
    os.makedirs(out, exist_ok=True)

    for p, name, parent_scheme, filename in [
        (light_p, "Nibelung",      "Default", "Nibelung.icls"),
        (dark_p,  "Nibelung Dark", "Darcula", "Nibelung_Dark.icls"),
    ]:
        scheme = _icls_scheme(p, roles(p), name, parent_scheme)
        tree = ET.ElementTree(scheme)
        ET.indent(tree, space="  ")
        path = os.path.join(out, filename)
        with open(path, "w", encoding="utf-8") as f:
            tree.write(f, xml_declaration=True, encoding="unicode")
            f.write("\n")

    print(f"IntelliJ: wrote {out}")


# ---------------------------------------------------------------------------
# Alacritty backend
# ---------------------------------------------------------------------------

def _alacritty_theme(p, a, title):
    al_bg = p["level0"]
    al_cyan = p["accent-bright"]
    al_blue = "#8384DD"
    return f"""\
# {title} theme for Alacritty
# Generated by nibelung-theme/export/generate.py

[colors.primary]
background = "{al_bg}"
foreground = "{p["fg"]}"

[colors.cursor]
cursor = "{p["fg"]}"
text = "{p["bg"]}"

[colors.vi_mode_cursor]
cursor = "{p["emphasis"]}"
text = "{p["bg"]}"

[colors.selection]
background = "{p["accent-subtle"]}"
text = "{p["level6"]}"

[colors.search.matches]
background = "{p["accent-subtle"]}"
foreground = "{p["level6"]}"

[colors.search.focused_match]
background = "{p["emphasis"]}"
foreground = "{p["bg"]}"

[colors.hints.start]
background = "{p["level0"]}"
foreground = "{p["fg"]}"

[colors.hints.end]
background = "{p["level0"]}"
foreground = "{p["level3"]}"

[colors.footer_bar]
background = "{p["level2"]}"
foreground = "{p["level6"]}"

[colors.normal]
black = "{a["black"]}"
red = "{a["red"]}"
green = "{a["green"]}"
yellow = "{a["yellow"]}"
blue = "{al_blue}"
magenta = "{a["magenta"]}"
cyan = "{al_cyan}"
white = "{a["white"]}"

[colors.bright]
black = "{a["bright_black"]}"
red = "{a["bright_red"]}"
green = "{a["bright_green"]}"
yellow = "{a["bright_yellow"]}"
blue = "{a["bright_blue"]}"
magenta = "{a["bright_magenta"]}"
cyan = "{al_cyan}"
white = "{a["bright_white"]}"
"""


def generate_alacritty(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "alacritty")
    os.makedirs(out, exist_ok=True)

    light_toml = _alacritty_theme(light_p, ansi(light_p), "Nibelung")
    with open(os.path.join(out, "nibelung.toml"), "w") as f:
        f.write(light_toml)

    dark_toml = _alacritty_theme(dark_p, ansi(dark_p), "Nibelung Dark")
    with open(os.path.join(out, "nibelung-dark.toml"), "w") as f:
        f.write(dark_toml)

    print(f"Alacritty: wrote {out}")


# ---------------------------------------------------------------------------
# Caelestia backend
# ---------------------------------------------------------------------------

def _caelestia_scheme(p, a, variant_name, light_p=None):
    def m3(c): return c[1:].lower()

    is_dark = (variant_name == "dark")
    lp = light_p if light_p else p  # light palette for Fixed colors (M3: constant across modes)

    colours = {
        "primary_paletteKeyColor": m3(p["emphasis"]),
        "secondary_paletteKeyColor": m3(p["level3"]),
        "tertiary_paletteKeyColor": m3(p["rainbow-magenta"]),
        "neutral_paletteKeyColor": m3(p["fg"]),
        "neutral_variant_paletteKeyColor": m3(p["level4"]),

        "background": m3(p["bg"]),
        "onBackground": m3(p["fg"]),
        "surface": m3(p["bg"]),
        "surfaceDim": m3(p["bg"]) if is_dark else m3(p["level0"]),
        "surfaceBright": m3(p["level2"]) if is_dark else m3(p["bg"]),
        "surfaceContainerLowest": m3(p["bg"]),
        "surfaceContainerLow": m3(_blend(p["bg"], p["level0"])),
        "surfaceContainer": m3(p["level0"]),
        "surfaceContainerHigh": m3(p["level1"]),
        "surfaceContainerHighest": m3(p["level2"]),
        "onSurface": m3(p["fg"]),
        "surfaceVariant": m3(p["level1"]),
        "onSurfaceVariant": m3(p["level5"]) if not is_dark else m3(p["level4"]),
        "inverseSurface": m3(p["fg"]),
        "inverseOnSurface": m3(p["level0"]),
        "surfaceTint": m3(p["emphasis"]),

        "primary": m3(p["emphasis"]),
        "onPrimary": m3(lp["level6"]),
        "primaryContainer": m3(_blend(p["emphasis"], p["bg"], 0.5)),
        "onPrimaryContainer": m3(p["fg"]),
        "inversePrimary": m3(p["accent-light"]),

        "secondary": m3(p["level3"]),
        "onSecondary": m3(p["fg"]),
        "secondaryContainer": m3(_blend(p["level3"], p["bg"], 0.6)),
        "onSecondaryContainer": m3(p["fg"]),

        "tertiary": m3(p["rainbow-magenta"]),
        "onTertiary": m3(lp["level6"]),
        "tertiaryContainer": m3(_blend(p["rainbow-magenta"], p["bg"], 0.7)),
        "onTertiaryContainer": m3(p["fg"]),

        "error": m3(p["rainbow-red"]),
        "onError": m3(lp["level6"]),
        "errorContainer": m3(_blend(p["rainbow-red"], p["bg"], 0.7)),
        "onErrorContainer": m3(p["fg"]),

        "success": m3(p["rainbow-green"]),
        "onSuccess": m3(lp["level6"]),
        "successContainer": m3(_blend(p["rainbow-green"], p["bg"], 0.7)),
        "onSuccessContainer": m3(p["fg"]),

        # Fixed colors (M3: constant across light/dark, always derived from light palette)
        "primaryFixed": m3(_blend(lp["emphasis"], lp["bg"], 0.7)),
        "primaryFixedDim": m3(lp["emphasis"]),
        "onPrimaryFixed": m3(lp["level6"]),
        "onPrimaryFixedVariant": m3(lp["level2"]),

        "secondaryFixed": m3(_blend(lp["level3"], lp["bg"], 0.6)),
        "secondaryFixedDim": m3(lp["level3"]),
        "onSecondaryFixed": m3(lp["level6"]),
        "onSecondaryFixedVariant": m3(lp["level2"]),

        "tertiaryFixed": m3(_blend(lp["rainbow-magenta"], lp["bg"], 0.7)),
        "tertiaryFixedDim": m3(lp["rainbow-magenta"]),
        "onTertiaryFixed": m3(lp["level6"]),
        "onTertiaryFixedVariant": m3(lp["level2"]),

        "outline": m3(p["level3"]),
        "outlineVariant": m3(p["level1"]),

        "shadow": "000000",
        "scrim": "000000",

        "term0": m3(a["black"]),
        "term1": m3(a["red"]),
        "term2": m3(a["green"]),
        "term3": m3(a["yellow"]),
        "term4": m3(a["blue"]),
        "term5": m3(a["magenta"]),
        "term6": m3(a["cyan"]),
        "term7": m3(a["white"]),
        "term8": m3(a["bright_black"]),
        "term9": m3(a["bright_red"]),
        "term10": m3(a["bright_green"]),
        "term11": m3(a["bright_yellow"]),
        "term12": m3(a["bright_blue"]),
        "term13": m3(a["bright_magenta"]),
        "term14": m3(a["bright_cyan"]),
        "term15": m3(a["bright_white"]),

        "rosewater": m3(p["rainbow-orange"]),
        "flamingo": m3(p["rainbow-red"]),
        "pink": m3(p["rainbow-magenta"]),
        "mauve": m3(p["emphasis"]),
        "red": m3(p["rainbow-red"]),
        "maroon": m3(p["rainbow-red"]),
        "peach": m3(p["rainbow-orange"]),
        "yellow": m3(p["rainbow-yellow"]),
        "green": m3(p["rainbow-green"]),
        "teal": m3(p["rainbow-cyan"]),
        "sky": m3(p["rainbow-bluelight"]),
        "sapphire": m3(p["rainbow-blue"]),
        "blue": m3(p["emphasis"]),
        "lavender": m3(p["accent-light"]),

        "klink": m3(p["link"]),
        "klinkSelection": m3(p["link"]),
        "kvisited": m3(p["level4"]),
        "kvisitedSelection": m3(p["level4"]),
        "knegative": m3(p["rainbow-red"]),
        "knegativeSelection": m3(p["rainbow-red"]),
        "kneutral": m3(p["rainbow-yellow"]),
        "kneutralSelection": m3(p["rainbow-yellow"]),
        "kpositive": m3(p["rainbow-green"]),
        "kpositiveSelection": m3(p["rainbow-green"]),

        "text": m3(p["fg"]),
        "subtext1": m3(p["level4"]),
        "subtext0": m3(p["level3"]),
        "overlay2": m3(p["level3"]),
        "overlay1": m3(p["level2"]),
        "overlay0": m3(p["level1"]),
        "surface2": m3(p["level1"]),
        "surface1": m3(p["level0"]),
        "surface0": m3(p["level0"]),
        "base": m3(p["bg"]),
        "mantle": m3(p["bg"]),
        "crust": m3(p["bg"]),
    }

    return {
        "name": "nibelung",
        "flavour": variant_name,
        "mode": variant_name,
        "variant": "tonalspot",
        "colours": colours,
    }


def generate_caelestia(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "caelestia")
    os.makedirs(out, exist_ok=True)

    light_scheme = _caelestia_scheme(light_p, ansi(light_p), "light")
    _write_json(os.path.join(out, "nibelung-scheme.json"), light_scheme)

    dark_scheme = _caelestia_scheme(dark_p, ansi(dark_p), "dark", light_p=light_p)
    _write_json(os.path.join(out, "nibelung-dark-scheme.json"), dark_scheme)

    # Also write .txt format for installation into caelestia scheme directory
    for scheme, mode in [(light_scheme, "light"), (dark_scheme, "dark")]:
        txt_dir = os.path.join(out, "default")
        os.makedirs(txt_dir, exist_ok=True)
        txt_path = os.path.join(txt_dir, f"{mode}.txt")
        with open(txt_path, "w") as f:
            for key, value in scheme["colours"].items():
                f.write(f"{key} {value}\n")

    print(f"Caelestia: wrote {out}")


# ---------------------------------------------------------------------------
# OpenCode backend
# ---------------------------------------------------------------------------

def _opencode_theme(light_p, dark_p):
    defs = {}
    for key, val in light_p.items():
        defs[f"l-{key}"] = val
    for key, val in dark_p.items():
        defs[f"d-{key}"] = val

    def dl(l_key, d_key):
        return {"dark": f"d-{d_key}", "light": f"l-{l_key}"}

    def same(key):
        return dl(key, key)

    theme = {
        "primary":                same("accent-match"),
        "secondary":              same("accent-bright"),
        "accent":                 same("accent-light"),
        "error":                  same("rainbow-red"),
        "warning":                same("rainbow-orange"),
        "success":                same("rainbow-green"),
        "info":                   same("accent-bright"),
        "text":                   same("fg"),
        "textMuted":              same("level3"),
        "background":             same("bg"),
        "backgroundPanel":        same("level0"),
        "backgroundElement":      same("level1"),
        "border":                 same("level2"),
        "borderActive":           same("level3"),
        "borderSubtle":           same("level1"),
        "diffAdded":              same("rainbow-green"),
        "diffRemoved":            same("rainbow-red"),
        "diffContext":            same("level3"),
        "diffHunkHeader":         same("level3"),
        "diffHighlightAdded":     same("rainbow-green"),
        "diffHighlightRemoved":   same("rainbow-red"),
        "diffAddedBg":            same("level0"),
        "diffRemovedBg":          same("level0"),
        "diffContextBg":          same("level0"),
        "diffLineNumber":         same("level2"),
        "diffAddedLineNumberBg":  same("level0"),
        "diffRemovedLineNumberBg":same("level0"),
        "markdownText":           same("fg"),
        "markdownHeading":        same("accent-match"),
        "markdownLink":           same("link"),
        "markdownLinkText":       same("accent-match"),
        "markdownCode":           same("rainbow-green"),
        "markdownBlockQuote":     same("level3"),
        "markdownEmph":           same("accent-bright"),
        "markdownStrong":         same("level5"),
        "markdownHorizontalRule": same("level2"),
        "markdownListItem":       same("accent-match"),
        "markdownListEnumeration":same("accent-light"),
        "markdownImage":          same("accent-match"),
        "markdownImageText":      same("accent-light"),
        "markdownCodeBlock":      same("fg"),
        "syntaxComment":          same("level3"),
        "syntaxKeyword":          same("accent-match"),
        "syntaxFunction":         same("rainbow-blue"),
        "syntaxVariable":         same("rainbow-cyan"),
        "syntaxString":           same("rainbow-green"),
        "syntaxNumber":           same("rainbow-orange"),
        "syntaxType":             same("rainbow-bluelight"),
        "syntaxOperator":         same("level4"),
        "syntaxPunctuation":      same("level3"),
    }

    return {
        "$schema": "https://opencode.ai/theme.json",
        "defs": defs,
        "theme": theme,
    }


def generate_opencode(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "opencode")
    os.makedirs(out, exist_ok=True)
    _write_json(os.path.join(out, "nibelung.json"), _opencode_theme(light_p, dark_p))
    print(f"OpenCode: wrote {out}")


# ---------------------------------------------------------------------------
# Telegram Desktop backend
# ---------------------------------------------------------------------------

def _telegram_palette(p, variant):
    """Generate a .tdesktop-palette text for Telegram Desktop.

    Undefined entries fall back to Telegram's built-in defaults, so the output
    only covers the variables whose mapping to the nibelung palette is meaningful.
    """
    is_dark = (variant == "dark")
    active_fg = p["level1"] if is_dark else p["level6"]

    # Dark mode: emphasis is foreground accent, not background fill.
    # Large areas (bubbles, selected rows, folders) use neutral grays.
    msg_out_bg = _blend(p["level1"], p["accent-subtle"], 0.15) if is_dark else p["accent-subtle"]
    msg_out_bg_sel = _blend(p["level1"], p["accent-subtle"], 0.35) if is_dark else p["accent-light"]
    sel_bg = p["level2"] if is_dark else p["emphasis"]
    sel_fg = p["level6"] if is_dark else active_fg
    sel_secondary = p["level4"] if is_dark else active_fg
    sel_accent = p["emphasis"] if is_dark else active_fg

    lines = []

    def entry(name, value):
        lines.append(f"{name}: {value};")

    # Window base
    entry("windowBg",               p["bg"])
    entry("windowFg",               p["fg"])
    entry("windowBgOver",           p["level0"])
    entry("windowBgRipple",         p["level1"])
    entry("windowFgOver",           "windowFg")
    entry("windowSubTextFg",        p["level3"])
    entry("windowSubTextFgOver",    p["level4"])
    entry("windowBoldFg",           p["level5"])
    entry("windowBoldFgOver",       p["level6"])
    entry("windowBgActive",         p["emphasis"])
    entry("windowFgActive",         active_fg)
    entry("windowActiveTextFg",     p["link"])
    entry("windowShadowFg",         "#000000")
    entry("windowShadowFgFallback", p["level0"])
    entry("shadowFg",               "#00000028")

    # Buttons
    entry("activeButtonBg",              "windowBgActive")
    entry("activeButtonBgOver",          p["accent-bright"])
    entry("activeButtonBgRipple",        p["accent-match"])
    entry("activeButtonFg",              "windowFgActive")
    entry("activeButtonFgOver",          "activeButtonFg")
    entry("activeButtonSecondaryFg",     p["accent-subtle"])
    entry("activeButtonSecondaryFgOver", "activeButtonSecondaryFg")
    entry("activeLineFg",                p["emphasis"])
    entry("activeLineFgError",           p["rainbow-red"])

    entry("lightButtonBg",       "windowBg")
    entry("lightButtonBgOver",   p["level0"])
    entry("lightButtonBgRipple", p["level1"])
    entry("lightButtonFg",       "windowActiveTextFg")
    entry("lightButtonFgOver",   "lightButtonFg")

    entry("attentionButtonFg",       p["rainbow-red"])
    entry("attentionButtonFgOver",   "attentionButtonFg")
    entry("attentionButtonBgOver",   p["level0"])
    entry("attentionButtonBgRipple", p["level1"])

    entry("outlineButtonBg",        "windowBg")
    entry("outlineButtonBgOver",    p["level0"])
    entry("outlineButtonOutlineFg", p["emphasis"])
    entry("outlineButtonBgRipple",  p["level1"])

    # Popup menu
    entry("menuBg",             "windowBg")
    entry("menuBgOver",         "windowBgOver")
    entry("menuBgRipple",       "windowBgRipple")
    entry("menuIconFg",         p["level3"])
    entry("menuIconFgOver",     p["level4"])
    entry("menuSubmenuArrowFg", p["level5"])
    entry("menuFgDisabled",     p["level2"])
    entry("menuSeparatorFg",    p["level1"])

    # Scrollbars
    entry("scrollBarBg",     p["level3"] + "80")
    entry("scrollBarBgOver", p["level4"] + "80")
    entry("scrollBg",        p["level1"] + "80")
    entry("scrollBgOver",    p["level2"] + "80")

    entry("smallCloseIconFg",     p["level3"])
    entry("smallCloseIconFgOver", p["level4"])

    entry("radialFg", "windowFgActive")
    entry("radialBg", "#00000056")

    # Inputs
    entry("placeholderFg",         "windowSubTextFg")
    entry("placeholderFgActive",   p["level3"])
    entry("inputBorderFg",         p["level1"])
    entry("filterInputBorderFg",   p["emphasis"])
    entry("filterInputActiveBg",   "windowBg")
    entry("filterInputInactiveBg", "windowBgOver")

    entry("checkboxFg",       p["level3"])
    entry("botKbBg",          "menuBgOver")
    entry("botKbDownBg",      "menuBgRipple")
    entry("botKbColor",       "windowBoldFgOver")
    entry("sliderBgInactive", p["level2"])
    entry("sliderBgActive",   "windowBgActive")

    # Tooltip
    entry("tooltipBg",       p["level0"])
    entry("tooltipFg",       p["fg"])
    entry("tooltipBorderFg", p["level1"])

    # Window title (Windows only, but declare anyway)
    entry("titleShadow",                  "#00000010")
    entry("titleBg",                      "windowBgOver")
    entry("titleBgActive",                "titleBg")
    entry("titleButtonBg",                "titleBg")
    entry("titleButtonFg",                p["level3"])
    entry("titleButtonBgOver",            p["level1"])
    entry("titleButtonFgOver",            p["level4"])
    entry("titleButtonBgActive",          "titleButtonBg")
    entry("titleButtonFgActive",          "titleButtonFg")
    entry("titleButtonBgActiveOver",      "titleButtonBgOver")
    entry("titleButtonFgActiveOver",      "titleButtonFgOver")
    entry("titleButtonCloseBg",           "titleButtonBg")
    entry("titleButtonCloseFg",           "titleButtonFg")
    entry("titleButtonCloseBgOver",       p["rainbow-red"])
    entry("titleButtonCloseFgOver",       active_fg)
    entry("titleButtonCloseBgActive",     "titleButtonCloseBg")
    entry("titleButtonCloseFgActive",     "titleButtonCloseFg")
    entry("titleButtonCloseBgActiveOver", "titleButtonCloseBgOver")
    entry("titleButtonCloseFgActiveOver", "titleButtonCloseFgOver")
    entry("titleFgActive",                p["level5"])
    entry("titleFg",                      p["level4"])

    entry("trackFg",       p["level2"])
    entry("trackFgActive", p["emphasis"])
    entry("trackFgOver",   p["level3"])

    # Dialog list (left panel)
    entry("dialogsMenuIconFg",     p["level3"])
    entry("dialogsMenuIconFgOver", p["level4"])
    entry("dialogsBg",             "windowBg")
    entry("dialogsNameFg",         p["level6"])
    entry("dialogsChatIconFg",     p["level3"])
    entry("dialogsDateFg",         p["level3"])
    entry("dialogsTextFg",         p["level4"])
    entry("dialogsTextFgService",  "windowActiveTextFg")
    entry("dialogsDraftFg",        p["rainbow-red"])
    entry("dialogsVerifiedIconBg", "windowBgActive")
    entry("dialogsVerifiedIconFg", "windowFgActive")
    entry("dialogsSendingIconFg",  p["level3"])
    entry("dialogsSentIconFg",     p["emphasis"])
    entry("dialogsUnreadBg",       p["emphasis"])
    entry("dialogsUnreadBgMuted",  p["level3"])
    entry("dialogsUnreadFg",       active_fg)

    entry("dialogsBgOver",             p["level0"])
    entry("dialogsNameFgOver",         "dialogsNameFg")
    entry("dialogsChatIconFgOver",     "dialogsChatIconFg")
    entry("dialogsDateFgOver",         "dialogsDateFg")
    entry("dialogsTextFgOver",         "dialogsTextFg")
    entry("dialogsTextFgServiceOver",  "dialogsTextFgService")
    entry("dialogsDraftFgOver",        "dialogsDraftFg")
    entry("dialogsVerifiedIconBgOver", "dialogsVerifiedIconBg")
    entry("dialogsVerifiedIconFgOver", "dialogsVerifiedIconFg")
    entry("dialogsSendingIconFgOver",  "dialogsSendingIconFg")
    entry("dialogsSentIconFgOver",     "dialogsSentIconFg")
    entry("dialogsUnreadBgOver",       "dialogsUnreadBg")
    entry("dialogsUnreadBgMutedOver",  "dialogsUnreadBgMuted")
    entry("dialogsUnreadFgOver",       "dialogsUnreadFg")

    entry("dialogsBgActive",             sel_bg)
    entry("dialogsNameFgActive",         sel_fg)
    entry("dialogsChatIconFgActive",     sel_fg if not is_dark else p["level5"])
    entry("dialogsDateFgActive",         sel_secondary)
    entry("dialogsTextFgActive",         sel_secondary)
    entry("dialogsTextFgServiceActive",  sel_accent)
    entry("dialogsDraftFgActive",        p["rainbow-red"] if is_dark else active_fg)
    entry("dialogsVerifiedIconBgActive", sel_accent)
    entry("dialogsVerifiedIconFgActive", sel_bg if is_dark else p["emphasis"])
    entry("dialogsSendingIconFgActive",  sel_secondary)
    entry("dialogsSentIconFgActive",     sel_accent)
    entry("dialogsUnreadBgActive",       p["emphasis"] if is_dark else active_fg)
    entry("dialogsUnreadBgMutedActive",  p["level3"] if is_dark else p["level2"])
    entry("dialogsUnreadFgActive",       active_fg if is_dark else p["emphasis"])

    entry("dialogsRippleBg",       p["level1"])
    entry("dialogsRippleBgActive", p["level3"] if is_dark else p["accent-match"])
    entry("dialogsForwardBg",      "dialogsBgActive")
    entry("dialogsForwardFg",      "dialogsNameFgActive")

    entry("searchedBarBg",     p["level0"])
    entry("searchedBarBorder", p["level1"])
    entry("searchedBarFg",     p["level4"])

    # History / chat area
    entry("historyTextInFg",          p["fg"])
    entry("historyTextInFgSelected",  p["fg"])
    entry("historyTextOutFg",         p["fg"])
    entry("historyTextOutFgSelected", p["fg"])
    entry("historyCaretFg",           p["fg"])
    entry("historyLinkInFg",          p["link"])
    entry("historyLinkInFgSelected",  p["link"])
    entry("historyLinkOutFg",         p["link"])
    entry("historyLinkOutFgSelected", p["link"])
    entry("historyFileNameInFg",      p["fg"])
    entry("historyFileNameOutFg",     p["fg"])
    entry("historyOutIconFg",         p["emphasis"])
    entry("historyOutIconFgSelected", p["emphasis"])
    entry("historyIconFgInverted",    p["level6"] if is_dark else "windowBg")
    entry("historyCallArrowInFg",     p["rainbow-green"])
    entry("historyCallArrowMissedInFg", p["rainbow-red"])
    entry("historyCallArrowOutFg",    p["rainbow-green"])
    entry("historyUnreadBarBg",       p["level0"])
    entry("historyUnreadBarBorder",   p["level1"])
    entry("historyUnreadBarFg",       p["level4"])

    # Peer colors (8 rotating, used for avatars and names)
    entry("historyPeer1NameFg",    p["rainbow-red"])
    entry("historyPeer1UserpicBg", p["rainbow-red"])
    entry("historyPeer2NameFg",    p["rainbow-green"])
    entry("historyPeer2UserpicBg", p["rainbow-green"])
    entry("historyPeer3NameFg",    p["rainbow-yellow"])
    entry("historyPeer3UserpicBg", p["rainbow-yellow"])
    entry("historyPeer4NameFg",    p["rainbow-blue"])
    entry("historyPeer4UserpicBg", p["rainbow-blue"])
    entry("historyPeer5NameFg",    p["rainbow-orange"])
    entry("historyPeer5UserpicBg", p["rainbow-orange"])
    entry("historyPeer6NameFg",    p["rainbow-cyan"])
    entry("historyPeer6UserpicBg", p["rainbow-cyan"])
    entry("historyPeer7NameFg",    p["rainbow-magenta"])
    entry("historyPeer7UserpicBg", p["rainbow-magenta"])
    entry("historyPeer8NameFg",    p["rainbow-bluelight"])
    entry("historyPeer8UserpicBg", p["rainbow-bluelight"])
    entry("historyPeerArchiveUserpicBg", p["level3"])
    entry("historyPeerSavedMessagesBg",  p["emphasis"])
    entry("historyPeerUserpicFg",        p["level6"] if is_dark else active_fg)

    # Message bubbles
    entry("msgInBg",                 p["level0"])
    entry("msgInBgSelected",         p["level1"] if is_dark else p["accent-subtle"])
    entry("msgOutBg",                msg_out_bg)
    entry("msgOutBgSelected",        msg_out_bg_sel)
    entry("msgSelectOverlay",        p["emphasis"] + "40")
    entry("msgStickerOverlay",       p["emphasis"] + "40")
    entry("msgInServiceFg",          p["emphasis"])
    entry("msgInServiceFgSelected",  p["emphasis"])
    entry("msgOutServiceFg",         p["emphasis"])
    entry("msgOutServiceFgSelected", p["emphasis"])
    entry("msgInShadow",             p["level1"])
    entry("msgInShadowSelected",     p["level1"])
    entry("msgOutShadow",            p["level1"])
    entry("msgOutShadowSelected",    p["level1"])
    entry("msgInDateFg",             p["level4"])
    entry("msgInDateFgSelected",     p["level5"])
    entry("msgOutDateFg",            p["level4"])
    entry("msgOutDateFgSelected",    p["level5"])
    entry("msgServiceFg",            p["fg"] if is_dark else p["level6"])
    entry("msgServiceBg",            p["level0"])
    entry("msgServiceBgSelected",    p["level1"])
    entry("msgInReplyBarColor",      p["emphasis"])
    entry("msgInReplyBarSelColor",   p["emphasis"])
    entry("msgOutReplyBarColor",     p["emphasis"])
    entry("msgOutReplyBarSelColor",  p["emphasis"])
    entry("msgImgReplyBarColor",     p["level6"] if is_dark else active_fg)
    entry("msgInMonoFg",             p["rainbow-green"])
    entry("msgOutMonoFg",            p["rainbow-green"])
    entry("msgDateImgFg",            p["level6"] if is_dark else active_fg)
    entry("msgDateImgBg",            "#00000080" if is_dark else p["level6"] + "80")
    entry("msgDateImgBgOver",        "#000000a0" if is_dark else p["level6"] + "a0")
    entry("msgDateImgBgSelected",    "#000000a0" if is_dark else p["level6"] + "a0")
    entry("msgFileThumbLinkInFg",    p["link"])
    entry("msgFileThumbLinkOutFg",   p["link"])
    entry("msgFileInBg",             p["emphasis"])
    entry("msgFileInBgOver",         p["accent-bright"])
    entry("msgFileInBgSelected",     p["accent-match"])
    entry("msgFileOutBg",            p["emphasis"])
    entry("msgFileOutBgOver",        p["accent-bright"])
    entry("msgFileOutBgSelected",    p["accent-match"])
    entry("msgFile1Bg",              p["rainbow-blue"])
    entry("msgFile1BgDark",          p["rainbow-blue"])
    entry("msgFile1BgOver",          p["rainbow-blue"])
    entry("msgFile1BgSelected",      p["rainbow-blue"])
    entry("msgFile2Bg",              p["rainbow-green"])
    entry("msgFile2BgDark",          p["rainbow-green"])
    entry("msgFile2BgOver",          p["rainbow-green"])
    entry("msgFile2BgSelected",      p["rainbow-green"])
    entry("msgFile3Bg",              p["rainbow-red"])
    entry("msgFile3BgDark",          p["rainbow-red"])
    entry("msgFile3BgOver",          p["rainbow-red"])
    entry("msgFile3BgSelected",      p["rainbow-red"])
    entry("msgFile4Bg",              p["rainbow-yellow"])
    entry("msgFile4BgDark",          p["rainbow-yellow"])
    entry("msgFile4BgOver",          p["rainbow-yellow"])
    entry("msgFile4BgSelected",      p["rainbow-yellow"])
    entry("msgWaveformInActive",     p["emphasis"])
    entry("msgWaveformInInactive",   p["level2"])
    entry("msgWaveformOutActive",    p["emphasis"])
    entry("msgWaveformOutInactive",  p["level2"])
    entry("msgBotKbOverBgAdd",       p["level6"] + "20")
    entry("msgBotKbIconFg",          p["level6"])
    entry("msgBotKbRippleBg",        p["level6"] + "10")
    entry("msgBotKbButtonBg",        p["level0"])

    # Compose area
    entry("historyComposeAreaBg",         "windowBg")
    entry("historyComposeAreaFg",         p["fg"])
    entry("historyComposeAreaFgService",  p["level4"])
    entry("historyComposeIconFg",         p["level3"])
    entry("historyComposeIconFgOver",     p["level4"])
    entry("historySendIconFg",            p["emphasis"])
    entry("historySendIconFgOver",        p["accent-bright"])
    entry("historyPinnedBg",              "windowBg")
    entry("historyReplyBg",               "windowBg")
    entry("historyReplyIconFg",           p["emphasis"])
    entry("historyReplyCancelFg",         p["level3"])
    entry("historyReplyCancelFgOver",     p["level4"])
    entry("historyComposeButtonBg",       "windowBg")
    entry("historyComposeButtonBgOver",   p["level0"])
    entry("historyComposeButtonBgRipple", p["level1"])

    # Overview (media gallery checkmarks)
    entry("overviewCheckBg",       p["bg"] + "60")
    entry("overviewCheckFg",       p["level6"] if is_dark else active_fg)
    entry("overviewCheckFgActive", p["level6"] if is_dark else active_fg)
    entry("overviewCheckedBg",     p["emphasis"])
    entry("overviewCheckedFg",     p["level6"] if is_dark else active_fg)

    # Sidebar (folders)
    entry("sideBarBg",           p["level0"])
    entry("sideBarBgActive",     sel_bg)
    entry("sideBarBgRipple",     p["level1"])
    entry("sideBarTextFg",       p["level4"])
    entry("sideBarTextFgActive", sel_accent)
    entry("sideBarIconFg",       p["level3"])
    entry("sideBarIconFgActive", sel_accent)
    entry("sideBarBadgeBg",      p["emphasis"])
    entry("sideBarBadgeBgMuted", p["level3"])
    entry("sideBarBadgeFg",      active_fg)

    # Intro (login screen)
    entry("introBg",              "windowBg")
    entry("introTitleFg",         p["level6"])
    entry("introDescriptionFg",   p["level4"])
    entry("introErrorFg",         p["rainbow-red"])
    entry("introCoverTopBg",      p["emphasis"])
    entry("introCoverBottomBg",   p["level0"])
    entry("introCoverIconsFg",    p["level1"])
    entry("introCoverPlaneTrace", p["level0"])
    entry("introCoverPlaneInner", p["emphasis"])
    entry("introCoverPlaneOuter", p["accent-match"])
    entry("introCoverPlaneIcon",  p["level6"])

    # Box (modal dialogs)
    entry("boxBg",                     "windowBg")
    entry("boxTextFg",                 p["fg"])
    entry("boxTextFgGood",             p["rainbow-green"])
    entry("boxTextFgError",            p["rainbow-red"])
    entry("boxTitleFg",                p["level6"])
    entry("boxSearchBg",               "windowBg")
    entry("boxSearchCancelIconFg",     p["level3"])
    entry("boxSearchCancelIconFgOver", p["level4"])
    entry("boxTitleAdditionalFg",      p["level3"])
    entry("boxTitleCloseFg",           p["level3"])
    entry("boxTitleCloseFgOver",       p["level4"])
    entry("boxPhotoBg",                p["bg"])
    entry("boxPhotoTextFg",            p["level6"] if is_dark else active_fg)
    entry("boxPhotoCaptionFg",         p["level4"])
    entry("boxDividerBg",              p["level0"])
    entry("boxDividerFg",              p["level4"])

    # Mentions popup
    entry("mentionBg",           p["level0"])
    entry("mentionBgOver",       p["level1"])
    entry("mentionFg",           p["fg"])
    entry("mentionFgOver",       p["fg"])
    entry("mentionFgActive",     p["emphasis"])
    entry("mentionFgOverActive", p["emphasis"])

    # Calls
    entry("callArrowFg",            p["rainbow-green"])
    entry("callArrowMissedFg",      p["rainbow-red"])
    entry("callIconFg",             p["level6"] if is_dark else active_fg)
    entry("callBg",                 p["level6"])
    entry("callNameFg",             p["level6"] if is_dark else active_fg)
    entry("callFingerprintBg",      p["bg"] + "14")
    entry("callMuteRipple",         p["bg"] + "14")
    entry("callAnswerBg",           p["rainbow-green"])
    entry("callAnswerRipple",       p["rainbow-green"])
    entry("callAnswerBgOuter",      p["rainbow-green"] + "50")
    entry("callHangupBg",           p["rainbow-red"])
    entry("callHangupRipple",       p["rainbow-red"])
    entry("callCancelBg",           p["level5"] if is_dark else active_fg)
    entry("callCancelFg",           p["fg"])
    entry("callCancelRipple",       p["level1"])
    entry("callMuteBg",             p["level3"])
    entry("callMuteBgActive",       p["level2"])
    entry("callMuteFg",             p["level6"])
    entry("callMuteFgActive",       p["level5"])
    entry("callMuteRippleBgActive", p["level2"])

    # Media player
    entry("mediaPlayerBg",         "windowBg")
    entry("mediaPlayerActiveFg",   p["emphasis"])
    entry("mediaPlayerInactiveFg", p["level2"])
    entry("mediaPlayerDisabledFg", p["level1"])

    # Import progress
    entry("importHistoryImportBg", "windowBg")
    entry("importIconFg",          p["level6"] if is_dark else active_fg)

    return "\n".join(lines) + "\n"


def generate_telegram(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "telegram")
    os.makedirs(out, exist_ok=True)

    light_palette = _telegram_palette(light_p, "light")
    with open(os.path.join(out, "nibelung.tdesktop-palette"), "w") as f:
        f.write(light_palette)

    dark_palette = _telegram_palette(dark_p, "dark")
    with open(os.path.join(out, "nibelung-dark.tdesktop-palette"), "w") as f:
        f.write(dark_palette)

    print(f"Telegram: wrote {out}")


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

def run_smoke_tests(dist):
    # VSCode light
    with open(f"{dist}/vscode/themes/nibelung-color-theme.json") as f:
        vscode_light = json.load(f)
    assert vscode_light["colors"]["editor.background"] == "#F8F9FA", \
        f"VSCode light bg: {vscode_light['colors']['editor.background']!r}"
    assert vscode_light["colors"]["statusBar.background"] == "#495057", \
        f"VSCode light statusBar: {vscode_light['colors']['statusBar.background']!r}"
    kw_scope = next(t for t in vscode_light["tokenColors"]
                    if "keyword" in str(t.get("scope", "")))
    assert kw_scope["settings"]["foreground"].upper() == "#6C757D", \
        f"VSCode light keyword fg: {kw_scope['settings']['foreground']!r}"

    # VSCode dark
    with open(f"{dist}/vscode/themes/nibelung-dark-color-theme.json") as f:
        vscode_dark = json.load(f)
    assert vscode_dark["colors"]["editor.background"] == "#212529", \
        f"VSCode dark bg: {vscode_dark['colors']['editor.background']!r}"

    # Alacritty light
    with open(f"{dist}/alacritty/nibelung.toml") as f:
        content = f.read()
        assert "#F8F9FA" in content, "Alacritty light: missing bg #F8F9FA"
        assert "#495057" in content, "Alacritty light: missing fg #495057"

    # IntelliJ light
    tree = ET.parse(f"{dist}/intellij/Nibelung.icls")
    scheme = tree.getroot()
    assert scheme.get("name") == "Nibelung", \
        f"IntelliJ name: {scheme.get('name')!r}"
    assert scheme.get("parent_scheme") == "Default", \
        f"IntelliJ parent_scheme: {scheme.get('parent_scheme')!r}"

    # Neovim light
    with open(f"{dist}/neovim/colors/nibelung.lua") as f:
        lua = f.read()
        assert 'vim.g.colors_name = "nibelung"' in lua, \
            "Neovim: missing colors_name assignment"
        assert "#F8F9FA" in lua, "Neovim light: missing bg #F8F9FA"

    # Caelestia light
    with open(f"{dist}/caelestia/nibelung-scheme.json") as f:
        caelestia = json.load(f)
    assert caelestia["name"] == "nibelung", \
        f"Caelestia name: {caelestia['name']!r}"
    assert caelestia["mode"] == "light", \
        f"Caelestia mode: {caelestia['mode']!r}"
    assert caelestia["colours"]["background"] == "f8f9fa", \
        f"Caelestia light bg: {caelestia['colours']['background']!r}"
    assert caelestia["colours"]["primary"] == "9bb1ff", \
        f"Caelestia light primary: {caelestia['colours']['primary']!r}"

    # Caelestia dark
    with open(f"{dist}/caelestia/nibelung-dark-scheme.json") as f:
        caelestia_dark = json.load(f)
    assert caelestia_dark["mode"] == "dark", \
        f"Caelestia dark mode: {caelestia_dark['mode']!r}"
    assert caelestia_dark["colours"]["background"] == "212529", \
        f"Caelestia dark bg: {caelestia_dark['colours']['background']!r}"
    assert caelestia_dark["colours"]["shadow"] == "000000", \
        f"Caelestia dark shadow: {caelestia_dark['colours']['shadow']!r}"

    # OpenCode
    with open(f"{dist}/opencode/nibelung.json") as f:
        opencode = json.load(f)
    assert opencode["$schema"] == "https://opencode.ai/theme.json", \
        f"OpenCode schema: {opencode['$schema']!r}"
    assert opencode["defs"]["l-bg"] == "#F8F9FA", \
        f"OpenCode defs l-bg: {opencode['defs']['l-bg']!r}"
    assert opencode["defs"]["d-bg"] == "#212529", \
        f"OpenCode defs d-bg: {opencode['defs']['d-bg']!r}"
    assert opencode["theme"]["primary"]["dark"] == "d-accent-match", \
        f"OpenCode primary dark: {opencode['theme']['primary']['dark']!r}"
    assert opencode["theme"]["syntaxKeyword"]["light"] == "l-accent-match", \
        f"OpenCode syntaxKeyword light: {opencode['theme']['syntaxKeyword']['light']!r}"

    # Telegram light
    with open(f"{dist}/telegram/nibelung.tdesktop-palette") as f:
        tg_light = f.read()
    assert "windowBg: #F8F9FA;" in tg_light, \
        f"Telegram light windowBg missing or wrong"
    assert "windowFg: #495057;" in tg_light, \
        f"Telegram light windowFg missing or wrong"
    assert "windowBgActive: #9BB1FF;" in tg_light, \
        f"Telegram light accent missing"

    # Telegram dark
    with open(f"{dist}/telegram/nibelung-dark.tdesktop-palette") as f:
        tg_dark = f.read()
    assert "windowBg: #212529;" in tg_dark, \
        f"Telegram dark windowBg missing or wrong"
    assert "windowFg: #CED4DA;" in tg_dark, \
        f"Telegram dark windowFg missing or wrong"

    print("Smoke tests passed")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False))
        f.write("\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate nibelung themes for VSCode, Neovim, IntelliJ, Alacritty, Caelestia, and OpenCode")
    parser.add_argument("--emacs",      default="emacs",
                        help="Path to Emacs binary (default: emacs)")
    parser.add_argument("--output-dir", default="dist",
                        help="Output directory (default: dist)")
    parser.add_argument("--target",     default="all",
                        choices=["vscode", "neovim", "intellij", "alacritty", "caelestia", "opencode", "telegram", "all"],
                        help="Which backend to generate (default: all)")
    parser.add_argument("--smoke-test", metavar="DIST_DIR",
                        help="Run smoke tests against generated files in DIST_DIR")
    args = parser.parse_args()

    if args.smoke_test:
        run_smoke_tests(args.smoke_test)
        return

    light_p, dark_p = extract_palettes(args.emacs)

    generators = {
        "vscode":     generate_vscode,
        "neovim":     generate_neovim,
        "intellij":   generate_intellij,
        "alacritty":  generate_alacritty,
        "caelestia":  generate_caelestia,
        "opencode":   generate_opencode,
        "telegram":   generate_telegram,
    }

    targets = list(generators.keys()) if args.target == "all" else [args.target]
    for target in targets:
        generators[target](light_p, dark_p, args.output_dir)


if __name__ == "__main__":
    main()
