#!/usr/bin/env python3
"""Nibelung theme generator -- exports palettes from Emacs and generates themes
for VSCode, Zed, Neovim, IntelliJ IDEA, Alacritty, Caelestia/Quickshell,
OpenCode, Pi, and OMP."""

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


def _agent_colors():
    """Shared Pi/OMP color-token -> palette-key map (51 tokens).

    OMP (Oh My Pi) is the Pi successor and reuses Pi's token set verbatim;
    the OMP backend extends this map with python-mode and status-line tokens.
    Values are palette var names resolved against ``vars`` at load time.
    """
    return {
        # Core UI
        "accent": "emphasis",
        "border": "level2",
        "borderAccent": "accent-bright",
        "borderMuted": "level1",
        "success": "rainbow-green",
        "error": "rainbow-red",
        "warning": "rainbow-orange",
        "muted": "level4",
        "dim": "level3",
        "text": "fg",
        "thinkingText": "level4",

        # Backgrounds and content
        "selectedBg": "accent-subtle",
        "userMessageBg": "level0",
        "userMessageText": "fg",
        "customMessageBg": "custom-message-bg",
        "customMessageText": "fg",
        "customMessageLabel": "rainbow-magenta",
        "toolPendingBg": "level0",
        "toolSuccessBg": "tool-success-bg",
        "toolErrorBg": "tool-error-bg",
        "toolTitle": "emphasis",
        "toolOutput": "fg",

        # Markdown
        # Pi/OMP render headings with bold (+underline for h1). To make them
        # visually distinct from body text in a terminal (where Nibelung's
        # bg is not guaranteed), we use level6 — the farthest from fg in
        # the grayscale range.
        "mdHeading": "level6",
        "mdLink": "link",
        "mdLinkUrl": "level3",
        "mdCode": "level3",
        "mdCodeBlock": "fg",
        "mdCodeBlockBorder": "level2",
        "mdQuote": "level3",
        "mdQuoteBorder": "level2",
        "mdHr": "level2",
        "mdListBullet": "level4",

        # Tool diffs
        "toolDiffAdded": "rainbow-green",
        "toolDiffRemoved": "rainbow-red",
        "toolDiffContext": "level3",

        # Syntax highlighting — follows Nibelung's semantic roles (see roles()
        # above). The seven-level grayscale is the backbone: level2 (quiet)
        # for operators/punctuation, level3 for comments/strings/types,
        # level4 for keywords/numbers/variables. Only function names get the
        # emphasis blue. Pi/OMP lack per-element backgrounds, so the Emacs
        # comment-bg distinction is lost; comments share level3 with strings.
        "syntaxComment": "level3",
        "syntaxKeyword": "level4",
        "syntaxFunction": "emphasis",
        "syntaxVariable": "level4",
        "syntaxString": "level3",
        "syntaxNumber": "level4",
        "syntaxType": "level3",
        "syntaxOperator": "level2",
        "syntaxPunctuation": "level2",

        # Thinking-level editor borders
        "thinkingOff": "level1",
        "thinkingMinimal": "level2",
        "thinkingLow": "level3",
        "thinkingMedium": "accent-light",
        "thinkingHigh": "accent-bright",
        "thinkingXhigh": "accent-match",

        "bashMode": "rainbow-green",
    }


# ---------------------------------------------------------------------------
# VSCode backend
# ---------------------------------------------------------------------------


def _vscode_theme(p, r, a, name, ui_theme):
    colors = {
        "editor.background":                     p["bg"],
        "editor.foreground":                     p["fg"],
        "editorCursor.foreground":               p["fg"],
        "editor.selectionBackground":            p["accent-subtle"],
        "editor.lineHighlightBackground":        p["level0"],
        "editor.findMatchBackground":            p["level5"] + "80",
        "editor.findMatchHighlightBackground":   p["level4"] + "40",
        "editorLineNumber.foreground":           p["fg"],
        "editorLineNumber.activeForeground":     p["emphasis"],
        "editorIndentGuide.background":          p["level0"],
        "editorIndentGuide.activeBackground":    p["level1"],
        "editorBracketMatch.background":         p["emphasis"] + "40",
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
        "list.activeSelectionBackground":        p["emphasis"] + "40",
        "list.hoverBackground":                  p["level0"] + "80",
        "list.focusBackground":                  p["level0"],
        "panel.background":                      p["level0"],
        "panel.border":                          p["level1"],
        "scrollbarSlider.background":            p["level2"] + "60",
        "scrollbarSlider.hoverBackground":       p["level3"] + "60",
        "diffEditor.insertedTextBackground":     p["rainbow-green"] + "20",
        "diffEditor.removedTextBackground":      p["rainbow-red"] + "20",
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
    # NOTE: VSCode tokenColors do not support per-scope backgroundColor.
    # Comment background highlighting (the Emacs theme's signature feature)
    # cannot be reproduced here. IntelliJ and Neovim support it.
    _token_roles = {
        "comment": "comment",
        "comment.block.documentation": "optional",
        "keyword, keyword.control, keyword.other": "constant",
        "storage.type, storage.modifier": "builtin",
        "string, string.quoted.single, string.quoted.double": "optional",
        "string.regexp": "constant",
        "entity.name.function": "bold",
        "entity.name.function.definition": "optional",
        "entity.name.type, entity.name.class, support.class, entity.other.inherited-class": "builtin",
        "variable, variable.other.readwrite": "builtin",
        "variable.parameter": "optional",
        "variable.language": "builtin",
        "variable.other.property": "optional",
        "constant.numeric, constant.language, constant.other": "constant",
        "keyword.operator": "quiet",
        "punctuation": "quiet",
        "support.function": "bold",
        "entity.name.tag": "builtin",
        "entity.other.attribute-name": "quiet",
        "markup.heading": "function",
        "markup.bold, markup.italic": "bold",
        "markup.inline.raw": "constant",
    }
    token_colors = [
        {"scope": s, "settings": {"fontStyle": "", "foreground": r[rname]}}
        for s, rname in _token_roles.items()
    ]
    # meta.embedded uses fg directly, not a role
    token_colors.append(
        {"scope": "meta.embedded, source.embedded",
         "settings": {"fontStyle": "", "foreground": p["fg"]}},
    )

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
        opts.setdefault("bold", False)
        opts.setdefault("italic", False)
        lines.append(_nvim_hl(group, opts))

    hl("Normal",    fg=p["fg"],       bg=p["bg"])
    hl("Comment",   fg=r["comment"],  bg=p["comment-bg"])
    hl("String",    fg=r["optional"])
    hl("Character", fg=r["optional"])
    hl("Function",  fg=r["bold"])
    hl("Keyword",   fg=r["constant"])
    hl("Type",      fg=r["builtin"])
    hl("Identifier",fg=p["fg"])
    hl("Constant",  fg=r["constant"])
    hl("Number",    fg=r["constant"])
    hl("Boolean",   fg=r["constant"])
    hl("Operator",  fg=r["quiet"])
    hl("PreProc",   fg=r["builtin"])
    hl("Special",   fg=r["constant"])
    hl("Delimiter", fg=r["bold"])
    hl("Statement", fg=r["constant"])
    hl("Title",     fg=r["function"])
    hl("Directory", fg=r["constant"])

    lines.append("")
    lines.append("-- Treesitter groups")

    hl("@keyword",              fg=r["constant"])
    hl("@keyword.return",       fg=r["constant"])
    hl("@keyword.function",     fg=r["constant"])
    hl("@keyword.import",       fg=r["constant"])
    hl("@string",               fg=r["optional"])
    hl("@string.escape",        fg=r["quiet"])
    hl("@string.regexp",        fg=r["constant"])
    hl("@string.documentation", fg=r["optional"])
    hl("@comment",              fg=r["comment"],  bg=p["comment-bg"])
    hl("@function",             fg=r["bold"])
    hl("@function.call",        fg=r["bold"])
    hl("@function.builtin",     fg=r["bold"])
    hl("@variable",             fg=r["builtin"])
    hl("@variable.builtin",     fg=r["builtin"])
    hl("@variable.parameter",   fg=r["optional"])
    hl("@variable.member",      fg=r["optional"])
    hl("@type",                 fg=r["builtin"])
    hl("@type.builtin",         fg=r["builtin"])
    hl("@constructor",          fg=r["builtin"])
    hl("@module",               fg=r["builtin"])
    hl("@property",             fg=r["optional"])
    hl("@operator",             fg=r["quiet"])
    hl("@number",               fg=r["constant"])
    hl("@boolean",              fg=r["constant"])
    hl("@punctuation.bracket",  fg=r["quiet"])
    hl("@punctuation.delimiter",fg=r["quiet"])
    hl("@constant",             fg=r["constant"])
    hl("@constant.builtin",     fg=r["constant"])
    hl("@markup.heading",       fg=r["function"])
    hl("@markup.strong",        fg=r["bold"])
    hl("@markup.italic",        fg=r["bold"])
    hl("@markup.raw",           fg=r["constant"])
    hl("@markup.link",          fg=p["link"])
    hl("@tag",                  fg=r["builtin"])
    hl("@tag.attribute",        fg=r["quiet"])
    hl("@tag.delimiter",        fg=r["quiet"])

    lines.append("")
    lines.append("-- LSP semantic tokens")

    hl("@lsp.type.function",   fg=r["bold"])
    hl("@lsp.type.variable",   fg=r["builtin"])
    hl("@lsp.type.type",       fg=r["builtin"])
    hl("@lsp.type.keyword",    fg=r["constant"])
    hl("@lsp.type.comment",    fg=r["comment"],  bg=p["comment-bg"])
    hl("@lsp.type.string",     fg=r["optional"])
    hl("@lsp.type.number",     fg=r["constant"])
    hl("@lsp.type.operator",   fg=r["quiet"])
    hl("@lsp.type.property",   fg=r["optional"])
    hl("@lsp.type.parameter",  fg=r["optional"])
    hl("@lsp.type.namespace",  fg=r["builtin"])
    lines.append(_nvim_hl("@lsp.mod.deprecated", {"strikethrough": True}))

    lines.append("")
    lines.append("-- UI groups")

    hl("Cursor",       fg=p["bg"],       bg=p["fg"])
    hl("CursorLine",                     bg=p["level0"])
    hl("CursorColumn",                   bg=p["level0"])
    hl("ColorColumn",                    bg=p["level0"])
    hl("Visual",       fg=p["level1"],   bg=p["emphasis"])
    hl("Search",       fg=p["level0"],   bg=p["level5"])
    hl("IncSearch",    fg=p["level0"],   bg=p["level5"])
    hl("MatchParen",   fg=p["level1"],   bg=p["emphasis"])
    hl("Pmenu",        fg=p["fg"],       bg=p["level0"])
    hl("PmenuSel",     fg=p["level1"],   bg=p["emphasis"])
    hl("PmenuSbar",                      bg=p["level1"])
    hl("PmenuThumb",                     bg=p["level3"])
    hl("NormalFloat",  fg=p["fg"],       bg=p["level0"])
    hl("FloatBorder",  fg=p["level2"],   bg=p["level0"])
    hl("StatusLine",   fg=p["level0"],   bg=p["fg"])
    hl("StatusLineNC", fg=p["level5"],   bg=p["level0"])
    hl("LineNr",       fg=p["fg"],       bg=p["bg"])
    hl("CursorLineNr", fg=p["emphasis"], bg=p["bg"])
    hl("SignColumn",   fg=p["fg"],       bg=p["bg"])
    hl("Folded",       fg=p["level3"],   bg=p["level0"])
    hl("FoldColumn",   fg=p["level3"],   bg=p["bg"])
    hl("NonText",      fg=p["level2"])
    hl("SpecialKey",   fg=p["level2"])
    hl("Whitespace",   fg=p["level2"])
    hl("Conceal",      fg=p["level3"])
    hl("WinSeparator", fg=p["level1"])
    hl("VertSplit",    fg=p["level1"])
    hl("WildMenu",     fg=p["level1"],   bg=p["emphasis"])
    hl("TabLine",      fg=p["level3"],   bg=p["level0"])
    hl("TabLineFill",                    bg=p["level0"])
    hl("TabLineSel",   fg=p["fg"],       bg=p["bg"])
    hl("ErrorMsg",     fg=p["level5"])
    hl("WarningMsg",   fg=p["level4"])
    hl("MoreMsg",      fg=p["emphasis"])
    hl("ModeMsg",      fg=p["fg"])
    hl("Question",     fg=p["emphasis"])
    lines.append(_nvim_hl("SpellBad",   {"sp": p["level5"],   "undercurl": True}))
    lines.append(_nvim_hl("SpellCap",   {"sp": p["level4"],   "undercurl": True}))
    lines.append(_nvim_hl("SpellRare",  {"sp": p["emphasis"], "undercurl": True}))
    lines.append(_nvim_hl("SpellLocal", {"sp": p["level3"],   "undercurl": True}))

    lines.append("")
    lines.append("-- Diagnostics")

    hl("DiagnosticError", fg=p["level5"])
    hl("DiagnosticWarn",  fg=p["level4"])
    hl("DiagnosticInfo",  fg=p["emphasis"])
    hl("DiagnosticHint",  fg=p["level3"])
    lines.append(_nvim_hl("DiagnosticUnderlineError", {"sp": p["level5"],   "underline": True}))
    lines.append(_nvim_hl("DiagnosticUnderlineWarn",  {"sp": p["level4"],   "underline": True}))
    lines.append(_nvim_hl("DiagnosticUnderlineInfo",  {"sp": p["emphasis"], "underline": True}))
    lines.append(_nvim_hl("DiagnosticUnderlineHint",  {"sp": p["level3"],   "underline": True}))

    lines.append("")
    lines.append("-- Diff")

    hl("DiffAdd",    fg=p["rainbow-green"],  bg=p["level1"])
    hl("DiffDelete", fg=p["rainbow-red"],    bg=p["level1"])
    hl("DiffChange", fg=p["rainbow-yellow"], bg=p["level1"])
    hl("DiffText",   fg=p["rainbow-yellow"], bg=p["level2"])

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
# Pi backend
# ---------------------------------------------------------------------------

PI_THEME_SCHEMA = "https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/src/modes/interactive/theme/theme-schema.json"


def _pi_theme(p, name, variant):
    is_dark = (variant == "dark")

    vars_ = dict(sorted(p.items()))
    vars_.update({
        "custom-message-bg": _blend(p["level0"], p["rainbow-magenta"], 0.12),
        "tool-success-bg": _blend(p["bg"], p["rainbow-green"], 0.14 if is_dark else 0.16),
        "tool-error-bg": _blend(p["bg"], p["rainbow-red"], 0.14 if is_dark else 0.16),
        "export-info-bg": _blend(p["level0"], p["accent-subtle"], 0.35),
    })

    colors = _agent_colors()

    return {
        "$schema": PI_THEME_SCHEMA,
        "name": name,
        "vars": vars_,
        "colors": colors,
        "export": {
            "pageBg": "bg",
            "cardBg": "level0",
            "infoBg": "export-info-bg",
        },
    }


def generate_pi(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "pi", "themes")
    os.makedirs(out, exist_ok=True)

    _write_json(os.path.join(out, "nibelung.json"),
                _pi_theme(light_p, "nibelung", "light"))
    _write_json(os.path.join(out, "nibelung-dark.json"),
                _pi_theme(dark_p, "nibelung-dark", "dark"))

    print(f"Pi: wrote {os.path.dirname(out)}")

# ---------------------------------------------------------------------------
# OMP backend
# ---------------------------------------------------------------------------

OMP_THEME_SCHEMA = "https://raw.githubusercontent.com/can1357/oh-my-pi/main/packages/coding-agent/src/modes/theme/theme-schema.json"


def _omp_theme(p, name, variant):
    is_dark = (variant == "dark")

    vars_ = dict(sorted(p.items()))
    vars_.update({
        "custom-message-bg": _blend(p["level0"], p["rainbow-magenta"], 0.12),
        "tool-success-bg": _blend(p["bg"], p["rainbow-green"], 0.14 if is_dark else 0.16),
        "tool-error-bg": _blend(p["bg"], p["rainbow-red"], 0.14 if is_dark else 0.16),
        "export-info-bg": _blend(p["level0"], p["accent-subtle"], 0.35),
    })

    # OMP extends Pi's 51 tokens (see _agent_colors) with python mode
    # and a 14-token status line. Override two agent-colors defaults
    # (bashMode, customMessageLabel) from rainbow to accent blue so the
    # OMP variant stays within Nibelung's grayscale+blue palette.
    # Rainbow is reserved for semantic states: git status, diffs, errors.
    colors = _agent_colors()
    colors.update({
        "bashMode": "accent-bright",
        "customMessageLabel": "accent-bright",

        # Modes
        "pythonMode": "accent-bright",

        # Status line — informational segments ride the grayscale ramp;
        # only git states carry semantic rainbow.
        "statusLineBg":        "level1",
        "statusLineSep":       "level2",
        "statusLineModel":     "level5",
        "statusLinePath":      "accent-bright",
        "statusLineGitClean":  "rainbow-green",
        "statusLineGitDirty":  "rainbow-orange",
        "statusLineContext":   "level5",
        "statusLineSpend":     "level5",
        "statusLineStaged":    "rainbow-green",
        "statusLineDirty":     "rainbow-orange",
        "statusLineUntracked": "rainbow-red",
        "statusLineOutput":    "level5",
        "statusLineCost":      "level4",
        "statusLineSubagents": "emphasis",
    })

    return {
        "$schema": OMP_THEME_SCHEMA,
        "name": name,
        "vars": vars_,
        "colors": colors,
        "export": {
            "pageBg": "bg",
            "cardBg": "level0",
            "infoBg": "export-info-bg",
        },
    }


def generate_omp(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "omp", "themes")
    os.makedirs(out, exist_ok=True)

    _write_json(os.path.join(out, "nibelung.json"),
                _omp_theme(light_p, "nibelung", "light"))
    _write_json(os.path.join(out, "nibelung-dark.json"),
                _omp_theme(dark_p, "nibelung-dark", "dark"))

    print(f"OMP: wrote {os.path.dirname(out)}")


# Helpers
# ---------------------------------------------------------------------------
# Zed backend
# ---------------------------------------------------------------------------

ZED_SCHEMA = "https://zed.dev/schema/themes/v0.2.0.json"


def _zed_hl(color, bg=None, weight=None, style=None):
    entry = {"color": color, "font_style": style, "font_weight": weight}
    if bg is not None:
        entry["background_color"] = bg
    return entry


def _zed_syntax(p, r):
    """Zed syntax tokens -> Nibelung semantic roles.

    Unlike VSCode, Zed highlight styles accept ``background_color``, so the
    Emacs theme's signature comment background survives the port.
    """
    cbg = p["comment-bg"]
    syntax = {}

    def add(tokens, color, bg=None, weight=None, style=None):
        for token in tokens:
            syntax[token] = _zed_hl(color, bg, weight, style)

    # Comments — the only tokens with their own background
    add(["comment"], r["comment"], bg=cbg)
    add(["comment.doc", "comment.documentation", "predoc"], r["optional"], bg=cbg)
    add(["comment.hint", "comment.note"], p["emphasis"], bg=cbg)
    add(["comment.todo"], p["rainbow-yellow"], bg=cbg, weight=700)
    add(["comment.warning"], p["rainbow-orange"], bg=cbg)
    add(["comment.error"], p["rainbow-red"], bg=cbg)

    # Keywords and operators
    add(["keyword", "keyword.conditional", "keyword.conditional.ternary",
         "keyword.coroutine", "keyword.debug", "keyword.exception",
         "keyword.export", "keyword.function", "keyword.import",
         "keyword.operator", "keyword.repeat", "keyword.return"],
        r["constant"])
    add(["keyword.modifier", "keyword.type", "keyword.directive",
         "keyword.directive.define", "preproc"], r["builtin"])
    add(["operator"], r["quiet"])
    add(["punctuation", "punctuation.bracket", "punctuation.delimiter",
         "punctuation.special"], r["quiet"])
    add(["punctuation.list_marker"], r["constant"])

    # Literals
    add(["string", "string.doc", "string.documentation", "character"],
        r["optional"])
    add(["string.escape", "character.special"], r["quiet"])
    add(["string.regex", "string.regexp", "string.special",
         "string.special.path", "string.special.symbol", "symbol"],
        r["constant"])
    add(["string.special.url", "link_uri"], p["link"])
    add(["number", "number.float", "float", "boolean", "constant",
         "constant.builtin", "constant.macro"], r["constant"])

    # Functions
    add(["function", "function.call", "function.builtin", "function.method",
         "function.method.call", "function.macro"], r["bold"])
    add(["function.decorator", "attribute"], r["quiet"])

    # Types, variables, modules
    add(["type", "type.builtin", "type.class.definition", "type.definition",
         "type.interface", "type.super", "enum", "variant", "constructor",
         "concept", "parent", "label", "module", "namespace"], r["builtin"])
    add(["variable", "variable.builtin", "variable.special", "primary",
         "embedded"], r["builtin"])
    add(["parameter", "variable.parameter", "property", "variable.member",
         "field"], r["optional"])

    # Markup
    add(["title"], r["function"], weight=700)
    add(["emphasis"], r["bold"], style="italic")
    add(["emphasis.strong"], r["bold"], weight=700)
    add(["text.literal"], r["constant"])
    add(["link_text"], p["link"])
    add(["tag", "tag.doctype"], r["builtin"])
    add(["tag.attribute", "tag.delimiter"], r["quiet"])

    # Diffs
    add(["diff.plus"], p["rainbow-green"])
    add(["diff.minus"], p["rainbow-red"])

    return dict(sorted(syntax.items()))


def _zed_style(p, r, a):
    def status(color):
        """A status color plus its tinted background and border."""
        return color, _blend(p["bg"], color, 0.12), _blend(p["bg"], color, 0.40)

    error, error_bg, error_bd = status(p["level5"])
    warning, warning_bg, warning_bd = status(p["level4"])
    info, info_bg, info_bd = status(p["emphasis"])
    hint, hint_bg, hint_bd = status(p["level3"])
    created, created_bg, created_bd = status(p["rainbow-green"])
    modified, modified_bg, modified_bd = status(p["rainbow-yellow"])
    deleted, deleted_bg, deleted_bd = status(p["rainbow-red"])
    conflict, conflict_bg, conflict_bd = status(p["rainbow-orange"])
    renamed, renamed_bg, renamed_bd = status(p["rainbow-blue"])
    ignored, ignored_bg, ignored_bd = status(p["level3"])

    style = {
        "accents": [p["emphasis"], p["rainbow-green"], p["rainbow-magenta"],
                    p["rainbow-orange"], p["rainbow-cyan"], p["rainbow-red"]],
        "background.appearance": "opaque",

        # Chrome
        "background":                    p["bg"],
        "surface.background":            p["level0"],
        "elevated_surface.background":   p["level0"],
        "border":                        p["level2"],
        "border.variant":                p["level1"],
        "border.focused":                p["emphasis"],
        "border.selected":               p["emphasis"],
        "border.transparent":            p["level2"] + "00",
        "border.disabled":               p["level1"],
        "element.background":            p["level0"],
        "element.hover":                 p["level1"],
        "element.active":                p["level2"],
        "element.selected":              p["accent-subtle"],
        "element.disabled":              p["level1"],
        "drop_target.background":        p["accent-subtle"] + "80",
        "ghost_element.background":      None,
        "ghost_element.hover":           p["level0"] + "80",
        "ghost_element.active":          p["level1"],
        "ghost_element.selected":        p["accent-subtle"],
        "ghost_element.disabled":        p["level0"],

        "text":                          p["fg"],
        "text.muted":                    p["level4"],
        "text.placeholder":              p["level3"],
        "text.disabled":                 p["level3"],
        "text.accent":                   p["emphasis"],
        "icon":                          p["fg"],
        "icon.muted":                    p["level4"],
        "icon.disabled":                 p["level3"],
        "icon.placeholder":              p["level3"],
        "icon.accent":                   p["emphasis"],

        "status_bar.background":         p["bg"],
        "title_bar.background":          p["bg"],
        "title_bar.inactive_background": p["level0"],
        "toolbar.background":            p["bg"],
        "tab_bar.background":            p["level0"],
        "tab.inactive_background":       p["level0"],
        "tab.active_background":         p["bg"],
        "search.match_background":       p["accent-light"] + "66",

        "panel.background":              p["level0"],
        "panel.focused_border":          p["emphasis"],
        "panel.indent_guide":            p["level1"],
        "panel.indent_guide_active":     p["level2"],
        "panel.indent_guide_hover":      p["level2"],
        "pane.focused_border":           p["emphasis"],
        "pane_group.border":             p["level1"],

        "scrollbar.thumb.background":       p["level2"] + "60",
        "scrollbar.thumb.hover_background": p["level3"] + "60",
        "scrollbar.thumb.border":           p["level1"],
        "scrollbar.track.background":       p["bg"] + "00",
        "scrollbar.track.border":           p["level0"],

        # Editor
        "editor.foreground":                p["fg"],
        "editor.background":                p["bg"],
        "editor.gutter.background":         p["bg"],
        "editor.subheader.background":      p["level0"],
        "editor.active_line.background":    p["level0"],
        "editor.highlighted_line.background": p["level1"],
        "editor.line_number":               p["level3"],
        "editor.active_line_number":        p["emphasis"],
        "editor.invisible":                 p["level2"],
        "editor.wrap_guide":                p["level1"],
        "editor.active_wrap_guide":         p["level2"],
        "editor.indent_guide":              p["level0"],
        "editor.indent_guide_active":       p["level2"],
        "editor.document_highlight.read_background":    p["emphasis"] + "20",
        "editor.document_highlight.write_background":   p["emphasis"] + "30",
        "editor.document_highlight.bracket_background": p["emphasis"] + "40",

        # Terminal
        "terminal.background":        p["bg"],
        "terminal.foreground":        p["fg"],
        "terminal.ansi.background":   p["bg"],
        "terminal.bright_foreground": p["level6"],
        "terminal.dim_foreground":    p["level3"],

        "link_text.hover": p["link"],

        # Status / diagnostics
        "error": error, "error.background": error_bg, "error.border": error_bd,
        "warning": warning, "warning.background": warning_bg, "warning.border": warning_bd,
        "info": info, "info.background": info_bg, "info.border": info_bd,
        "hint": hint, "hint.background": hint_bg, "hint.border": hint_bd,
        "success": created, "success.background": created_bg, "success.border": created_bd,
        "created": created, "created.background": created_bg, "created.border": created_bd,
        "modified": modified, "modified.background": modified_bg, "modified.border": modified_bd,
        "deleted": deleted, "deleted.background": deleted_bg, "deleted.border": deleted_bd,
        "conflict": conflict, "conflict.background": conflict_bg, "conflict.border": conflict_bd,
        "renamed": renamed, "renamed.background": renamed_bg, "renamed.border": renamed_bd,
        "ignored": ignored, "ignored.background": ignored_bg, "ignored.border": ignored_bd,
        "hidden": p["level3"], "hidden.background": p["level0"], "hidden.border": p["level1"],
        "predictive": p["level3"], "predictive.background": p["level0"], "predictive.border": p["level1"],
        "unreachable": p["level3"], "unreachable.background": p["level0"], "unreachable.border": p["level1"],

        # Git decorations (newer Zed; falls back to created/modified/deleted)
        "version_control.added":              created,
        "version_control.added_background":   created_bg,
        "version_control.modified":           modified,
        "version_control.modified_background": modified_bg,
        "version_control.deleted":            deleted,
        "version_control.deleted_background": deleted_bg,
        "version_control.conflict":           conflict,
        "version_control.conflict_background": conflict_bg,
        "version_control.renamed":            renamed,
        "version_control.ignored":            ignored,

        "players": [
            {"cursor": c, "background": c, "selection": c + "3d"}
            for c in (p["emphasis"], p["rainbow-green"], p["rainbow-magenta"],
                      p["rainbow-orange"], p["rainbow-cyan"], p["rainbow-red"],
                      p["rainbow-bluelight"], p["rainbow-yellow"])
        ],
        "syntax": _zed_syntax(p, r),
    }

    ansi_names = ["black", "red", "green", "yellow", "blue", "magenta",
                  "cyan", "white"]
    for name in ansi_names:
        style[f"terminal.ansi.{name}"] = a[name]
        style[f"terminal.ansi.bright_{name}"] = a[f"bright_{name}"]
        # Zed has no dim ANSI slot in the Emacs palette; fade toward the bg.
        style[f"terminal.ansi.dim_{name}"] = _blend(a[name], p["bg"], 0.35)

    return style


def generate_zed(light_p, dark_p, output_dir):
    out = os.path.join(output_dir, "zed")
    themes_dir = os.path.join(out, "themes")
    os.makedirs(themes_dir, exist_ok=True)

    family = {
        "$schema": ZED_SCHEMA,
        "name": "Nibelung",
        "author": "veschin",
        "themes": [
            {"name": "Nibelung", "appearance": "light",
             "style": _zed_style(light_p, roles(light_p), ansi(light_p))},
            {"name": "Nibelung Dark", "appearance": "dark",
             "style": _zed_style(dark_p, roles(dark_p), ansi(dark_p))},
        ],
    }
    # sort_keys would scramble the theme list order; keep source order here.
    with open(os.path.join(themes_dir, "nibelung.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(family, indent=2, ensure_ascii=False))
        f.write("\n")

    manifest = "\n".join([
        'id = "nibelung"',
        'name = "Nibelung"',
        'description = "Minimalist color theme with cool grays and subtle blue accents"',
        'version = "0.1.0"',
        'schema_version = 1',
        'authors = ["veschin"]',
        'repository = "https://github.com/veschin/nibelung-theme"',
        "",
    ])
    with open(os.path.join(out, "extension.toml"), "w", encoding="utf-8") as f:
        f.write(manifest)

    print(f"Zed: wrote {out}")


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
        description="Generate nibelung themes for VSCode, Zed, Neovim, IntelliJ, Alacritty, Caelestia, OpenCode, Pi, and OMP")
    parser.add_argument("--emacs",      default="emacs",
                        help="Path to Emacs binary (default: emacs)")
    parser.add_argument("--output-dir", default="dist",
                        help="Output directory (default: dist)")
    parser.add_argument("--target",     default="all",
                        choices=["vscode", "zed", "neovim", "intellij", "alacritty", "caelestia", "opencode", "pi", "omp", "all"],
                        help="Which backend to generate (default: all)")
    args = parser.parse_args()

    light_p, dark_p = extract_palettes(args.emacs)

    generators = {
        "vscode":     generate_vscode,
        "zed":        generate_zed,
        "neovim":     generate_neovim,
        "intellij":   generate_intellij,
        "alacritty":  generate_alacritty,
        "caelestia":  generate_caelestia,
        "opencode":   generate_opencode,
        "pi":         generate_pi,
        "omp":         generate_omp,
    }

    targets = list(generators.keys()) if args.target == "all" else [args.target]
    for target in targets:
        generators[target](light_p, dark_p, args.output_dir)


if __name__ == "__main__":
    main()
