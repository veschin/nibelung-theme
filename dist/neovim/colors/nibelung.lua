vim.cmd("highlight clear")
if vim.fn.exists("syntax_on") then vim.cmd("syntax reset") end
vim.g.colors_name = "nibelung"
vim.o.background = "light"
vim.o.termguicolors = true

local hl = function(group, opts) vim.api.nvim_set_hl(0, group, opts) end

-- Legacy syntax groups
hl("Normal", {fg = "#495057", bg = "#F8F9FA", bold = false, italic = false})
hl("Comment", {fg = "#ADB5BD", bg = "#E9ECEF", bold = false, italic = false})
hl("String", {fg = "#ADB5BD", bold = false, italic = false})
hl("Character", {fg = "#ADB5BD", bold = false, italic = false})
hl("Function", {fg = "#9BB1FF", bold = false, italic = false})
hl("Keyword", {fg = "#6C757D", bold = false, italic = false})
hl("Type", {fg = "#ADB5BD", bold = false, italic = false})
hl("Identifier", {fg = "#495057", bold = false, italic = false})
hl("Constant", {fg = "#6C757D", bold = false, italic = false})
hl("Number", {fg = "#6C757D", bold = false, italic = false})
hl("Boolean", {fg = "#6C757D", bold = false, italic = false})
hl("Operator", {fg = "#CED4DA", bold = false, italic = false})
hl("PreProc", {fg = "#ADB5BD", bold = false, italic = false})
hl("Special", {fg = "#6C757D", bold = false, italic = false})
hl("Delimiter", {fg = "#9BB1FF", bold = false, italic = false})
hl("Statement", {fg = "#6C757D", bold = false, italic = false})
hl("Title", {fg = "#343A40", bold = false, italic = false})
hl("Directory", {fg = "#6C757D", bold = false, italic = false})

-- Treesitter groups
hl("@keyword", {fg = "#6C757D", bold = false, italic = false})
hl("@keyword.return", {fg = "#6C757D", bold = false, italic = false})
hl("@keyword.function", {fg = "#6C757D", bold = false, italic = false})
hl("@keyword.import", {fg = "#6C757D", bold = false, italic = false})
hl("@string", {fg = "#ADB5BD", bold = false, italic = false})
hl("@string.escape", {fg = "#CED4DA", bold = false, italic = false})
hl("@string.regexp", {fg = "#6C757D", bold = false, italic = false})
hl("@string.documentation", {fg = "#ADB5BD", bold = false, italic = false})
hl("@comment", {fg = "#ADB5BD", bg = "#E9ECEF", bold = false, italic = false})
hl("@function", {fg = "#9BB1FF", bold = false, italic = false})
hl("@function.call", {fg = "#9BB1FF", bold = false, italic = false})
hl("@function.builtin", {fg = "#9BB1FF", bold = false, italic = false})
hl("@variable", {fg = "#ADB5BD", bold = false, italic = false})
hl("@variable.builtin", {fg = "#ADB5BD", bold = false, italic = false})
hl("@variable.parameter", {fg = "#ADB5BD", bold = false, italic = false})
hl("@variable.member", {fg = "#ADB5BD", bold = false, italic = false})
hl("@type", {fg = "#ADB5BD", bold = false, italic = false})
hl("@type.builtin", {fg = "#ADB5BD", bold = false, italic = false})
hl("@constructor", {fg = "#ADB5BD", bold = false, italic = false})
hl("@module", {fg = "#ADB5BD", bold = false, italic = false})
hl("@property", {fg = "#ADB5BD", bold = false, italic = false})
hl("@operator", {fg = "#CED4DA", bold = false, italic = false})
hl("@number", {fg = "#6C757D", bold = false, italic = false})
hl("@boolean", {fg = "#6C757D", bold = false, italic = false})
hl("@punctuation.bracket", {fg = "#CED4DA", bold = false, italic = false})
hl("@punctuation.delimiter", {fg = "#CED4DA", bold = false, italic = false})
hl("@constant", {fg = "#6C757D", bold = false, italic = false})
hl("@constant.builtin", {fg = "#6C757D", bold = false, italic = false})
hl("@markup.heading", {fg = "#343A40", bold = false, italic = false})
hl("@markup.strong", {fg = "#9BB1FF", bold = false, italic = false})
hl("@markup.italic", {fg = "#9BB1FF", bold = false, italic = false})
hl("@markup.raw", {fg = "#6C757D", bold = false, italic = false})
hl("@markup.link", {fg = "#9BB1FF", bold = false, italic = false})
hl("@tag", {fg = "#ADB5BD", bold = false, italic = false})
hl("@tag.attribute", {fg = "#CED4DA", bold = false, italic = false})
hl("@tag.delimiter", {fg = "#CED4DA", bold = false, italic = false})

-- LSP semantic tokens
hl("@lsp.type.function", {fg = "#9BB1FF", bold = false, italic = false})
hl("@lsp.type.variable", {fg = "#ADB5BD", bold = false, italic = false})
hl("@lsp.type.type", {fg = "#ADB5BD", bold = false, italic = false})
hl("@lsp.type.keyword", {fg = "#6C757D", bold = false, italic = false})
hl("@lsp.type.comment", {fg = "#ADB5BD", bg = "#E9ECEF", bold = false, italic = false})
hl("@lsp.type.string", {fg = "#ADB5BD", bold = false, italic = false})
hl("@lsp.type.number", {fg = "#6C757D", bold = false, italic = false})
hl("@lsp.type.operator", {fg = "#CED4DA", bold = false, italic = false})
hl("@lsp.type.property", {fg = "#ADB5BD", bold = false, italic = false})
hl("@lsp.type.parameter", {fg = "#ADB5BD", bold = false, italic = false})
hl("@lsp.type.namespace", {fg = "#ADB5BD", bold = false, italic = false})
hl("@lsp.mod.deprecated", {strikethrough = true})

-- UI groups
hl("Cursor", {fg = "#F8F9FA", bg = "#495057", bold = false, italic = false})
hl("CursorLine", {bg = "#E9ECEF", bold = false, italic = false})
hl("CursorColumn", {bg = "#E9ECEF", bold = false, italic = false})
hl("ColorColumn", {bg = "#E9ECEF", bold = false, italic = false})
hl("Visual", {fg = "#DEE2E6", bg = "#9BB1FF", bold = false, italic = false})
hl("Search", {fg = "#E9ECEF", bg = "#343A40", bold = false, italic = false})
hl("IncSearch", {fg = "#E9ECEF", bg = "#343A40", bold = false, italic = false})
hl("MatchParen", {fg = "#DEE2E6", bg = "#9BB1FF", bold = false, italic = false})
hl("Pmenu", {fg = "#495057", bg = "#E9ECEF", bold = false, italic = false})
hl("PmenuSel", {fg = "#DEE2E6", bg = "#9BB1FF", bold = false, italic = false})
hl("PmenuSbar", {bg = "#DEE2E6", bold = false, italic = false})
hl("PmenuThumb", {bg = "#ADB5BD", bold = false, italic = false})
hl("NormalFloat", {fg = "#495057", bg = "#E9ECEF", bold = false, italic = false})
hl("FloatBorder", {fg = "#CED4DA", bg = "#E9ECEF", bold = false, italic = false})
hl("StatusLine", {fg = "#E9ECEF", bg = "#495057", bold = false, italic = false})
hl("StatusLineNC", {fg = "#343A40", bg = "#E9ECEF", bold = false, italic = false})
hl("LineNr", {fg = "#495057", bg = "#F8F9FA", bold = false, italic = false})
hl("CursorLineNr", {fg = "#9BB1FF", bg = "#F8F9FA", bold = false, italic = false})
hl("SignColumn", {fg = "#495057", bg = "#F8F9FA", bold = false, italic = false})
hl("Folded", {fg = "#ADB5BD", bg = "#E9ECEF", bold = false, italic = false})
hl("FoldColumn", {fg = "#ADB5BD", bg = "#F8F9FA", bold = false, italic = false})
hl("NonText", {fg = "#CED4DA", bold = false, italic = false})
hl("SpecialKey", {fg = "#CED4DA", bold = false, italic = false})
hl("Whitespace", {fg = "#CED4DA", bold = false, italic = false})
hl("Conceal", {fg = "#ADB5BD", bold = false, italic = false})
hl("WinSeparator", {fg = "#DEE2E6", bold = false, italic = false})
hl("VertSplit", {fg = "#DEE2E6", bold = false, italic = false})
hl("WildMenu", {fg = "#DEE2E6", bg = "#9BB1FF", bold = false, italic = false})
hl("TabLine", {fg = "#ADB5BD", bg = "#E9ECEF", bold = false, italic = false})
hl("TabLineFill", {bg = "#E9ECEF", bold = false, italic = false})
hl("TabLineSel", {fg = "#495057", bg = "#F8F9FA", bold = false, italic = false})
hl("ErrorMsg", {fg = "#343A40", bold = false, italic = false})
hl("WarningMsg", {fg = "#6C757D", bold = false, italic = false})
hl("MoreMsg", {fg = "#9BB1FF", bold = false, italic = false})
hl("ModeMsg", {fg = "#495057", bold = false, italic = false})
hl("Question", {fg = "#9BB1FF", bold = false, italic = false})
hl("SpellBad", {sp = "#343A40", undercurl = true})
hl("SpellCap", {sp = "#6C757D", undercurl = true})
hl("SpellRare", {sp = "#9BB1FF", undercurl = true})
hl("SpellLocal", {sp = "#ADB5BD", undercurl = true})

-- Diagnostics
hl("DiagnosticError", {fg = "#343A40", bold = false, italic = false})
hl("DiagnosticWarn", {fg = "#6C757D", bold = false, italic = false})
hl("DiagnosticInfo", {fg = "#9BB1FF", bold = false, italic = false})
hl("DiagnosticHint", {fg = "#ADB5BD", bold = false, italic = false})
hl("DiagnosticUnderlineError", {sp = "#343A40", underline = true})
hl("DiagnosticUnderlineWarn", {sp = "#6C757D", underline = true})
hl("DiagnosticUnderlineInfo", {sp = "#9BB1FF", underline = true})
hl("DiagnosticUnderlineHint", {sp = "#ADB5BD", underline = true})

-- Diff
hl("DiffAdd", {fg = "#8FBF9F", bg = "#DEE2E6", bold = false, italic = false})
hl("DiffDelete", {fg = "#E08E8E", bg = "#DEE2E6", bold = false, italic = false})
hl("DiffChange", {fg = "#C9C97D", bg = "#DEE2E6", bold = false, italic = false})
hl("DiffText", {fg = "#C9C97D", bg = "#CED4DA", bold = false, italic = false})

-- Terminal colors
vim.g.terminal_color_0 = "#DEE2E6"
vim.g.terminal_color_1 = "#E08E8E"
vim.g.terminal_color_2 = "#8FBF9F"
vim.g.terminal_color_3 = "#C9C97D"
vim.g.terminal_color_4 = "#7B8CDE"
vim.g.terminal_color_5 = "#C99BC9"
vim.g.terminal_color_6 = "#7EB8B8"
vim.g.terminal_color_7 = "#6C757D"
vim.g.terminal_color_8 = "#ADB5BD"
vim.g.terminal_color_9 = "#E08E8E"
vim.g.terminal_color_10 = "#8FBF9F"
vim.g.terminal_color_11 = "#C9C97D"
vim.g.terminal_color_12 = "#8BA3D7"
vim.g.terminal_color_13 = "#C99BC9"
vim.g.terminal_color_14 = "#7EB8B8"
vim.g.terminal_color_15 = "#212529"
