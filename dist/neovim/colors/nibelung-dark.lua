vim.cmd("highlight clear")
if vim.fn.exists("syntax_on") then vim.cmd("syntax reset") end
vim.g.colors_name = "nibelung-dark"
vim.o.background = "dark"
vim.o.termguicolors = true

local hl = function(group, opts) vim.api.nvim_set_hl(0, group, opts) end

-- Legacy syntax groups
hl("Normal", {fg = "#CED4DA", bg = "#212529", bold = false, italic = false})
hl("Comment", {fg = "#6C757D", bg = "#2B3035", bold = false, italic = false})
hl("String", {fg = "#6C757D", bold = false, italic = false})
hl("Character", {fg = "#6C757D", bold = false, italic = false})
hl("Function", {fg = "#9BB1FF", bold = false, italic = false})
hl("Keyword", {fg = "#ADB5BD", bold = false, italic = false})
hl("Type", {fg = "#6C757D", bold = false, italic = false})
hl("Identifier", {fg = "#CED4DA", bold = false, italic = false})
hl("Constant", {fg = "#ADB5BD", bold = false, italic = false})
hl("Number", {fg = "#ADB5BD", bold = false, italic = false})
hl("Boolean", {fg = "#ADB5BD", bold = false, italic = false})
hl("Operator", {fg = "#495057", bold = false, italic = false})
hl("PreProc", {fg = "#6C757D", bold = false, italic = false})
hl("Special", {fg = "#ADB5BD", bold = false, italic = false})
hl("Delimiter", {fg = "#9BB1FF", bold = false, italic = false})
hl("Statement", {fg = "#ADB5BD", bold = false, italic = false})
hl("Title", {fg = "#DEE2E6", bold = false, italic = false})
hl("Directory", {fg = "#ADB5BD", bold = false, italic = false})

-- Treesitter groups
hl("@keyword", {fg = "#ADB5BD", bold = false, italic = false})
hl("@keyword.return", {fg = "#ADB5BD", bold = false, italic = false})
hl("@keyword.function", {fg = "#ADB5BD", bold = false, italic = false})
hl("@keyword.import", {fg = "#ADB5BD", bold = false, italic = false})
hl("@string", {fg = "#6C757D", bold = false, italic = false})
hl("@string.escape", {fg = "#495057", bold = false, italic = false})
hl("@string.regexp", {fg = "#ADB5BD", bold = false, italic = false})
hl("@string.documentation", {fg = "#6C757D", bold = false, italic = false})
hl("@comment", {fg = "#6C757D", bg = "#2B3035", bold = false, italic = false})
hl("@function", {fg = "#9BB1FF", bold = false, italic = false})
hl("@function.call", {fg = "#9BB1FF", bold = false, italic = false})
hl("@function.builtin", {fg = "#9BB1FF", bold = false, italic = false})
hl("@variable", {fg = "#6C757D", bold = false, italic = false})
hl("@variable.builtin", {fg = "#6C757D", bold = false, italic = false})
hl("@variable.parameter", {fg = "#6C757D", bold = false, italic = false})
hl("@variable.member", {fg = "#6C757D", bold = false, italic = false})
hl("@type", {fg = "#6C757D", bold = false, italic = false})
hl("@type.builtin", {fg = "#6C757D", bold = false, italic = false})
hl("@constructor", {fg = "#6C757D", bold = false, italic = false})
hl("@module", {fg = "#6C757D", bold = false, italic = false})
hl("@property", {fg = "#6C757D", bold = false, italic = false})
hl("@operator", {fg = "#495057", bold = false, italic = false})
hl("@number", {fg = "#ADB5BD", bold = false, italic = false})
hl("@boolean", {fg = "#ADB5BD", bold = false, italic = false})
hl("@punctuation.bracket", {fg = "#495057", bold = false, italic = false})
hl("@punctuation.delimiter", {fg = "#495057", bold = false, italic = false})
hl("@constant", {fg = "#ADB5BD", bold = false, italic = false})
hl("@constant.builtin", {fg = "#ADB5BD", bold = false, italic = false})
hl("@markup.heading", {fg = "#DEE2E6", bold = false, italic = false})
hl("@markup.strong", {fg = "#9BB1FF", bold = false, italic = false})
hl("@markup.italic", {fg = "#9BB1FF", bold = false, italic = false})
hl("@markup.raw", {fg = "#ADB5BD", bold = false, italic = false})
hl("@markup.link", {fg = "#9BB1FF", bold = false, italic = false})
hl("@tag", {fg = "#6C757D", bold = false, italic = false})
hl("@tag.attribute", {fg = "#495057", bold = false, italic = false})
hl("@tag.delimiter", {fg = "#495057", bold = false, italic = false})

-- LSP semantic tokens
hl("@lsp.type.function", {fg = "#9BB1FF", bold = false, italic = false})
hl("@lsp.type.variable", {fg = "#6C757D", bold = false, italic = false})
hl("@lsp.type.type", {fg = "#6C757D", bold = false, italic = false})
hl("@lsp.type.keyword", {fg = "#ADB5BD", bold = false, italic = false})
hl("@lsp.type.comment", {fg = "#6C757D", bg = "#2B3035", bold = false, italic = false})
hl("@lsp.type.string", {fg = "#6C757D", bold = false, italic = false})
hl("@lsp.type.number", {fg = "#ADB5BD", bold = false, italic = false})
hl("@lsp.type.operator", {fg = "#495057", bold = false, italic = false})
hl("@lsp.type.property", {fg = "#6C757D", bold = false, italic = false})
hl("@lsp.type.parameter", {fg = "#6C757D", bold = false, italic = false})
hl("@lsp.type.namespace", {fg = "#6C757D", bold = false, italic = false})
hl("@lsp.mod.deprecated", {strikethrough = true})

-- UI groups
hl("Cursor", {fg = "#212529", bg = "#CED4DA", bold = false, italic = false})
hl("CursorLine", {bg = "#2B3035", bold = false, italic = false})
hl("CursorColumn", {bg = "#2B3035", bold = false, italic = false})
hl("ColorColumn", {bg = "#2B3035", bold = false, italic = false})
hl("Visual", {fg = "#343A40", bg = "#9BB1FF", bold = false, italic = false})
hl("Search", {fg = "#2B3035", bg = "#DEE2E6", bold = false, italic = false})
hl("IncSearch", {fg = "#2B3035", bg = "#DEE2E6", bold = false, italic = false})
hl("MatchParen", {fg = "#343A40", bg = "#9BB1FF", bold = false, italic = false})
hl("Pmenu", {fg = "#CED4DA", bg = "#2B3035", bold = false, italic = false})
hl("PmenuSel", {fg = "#343A40", bg = "#9BB1FF", bold = false, italic = false})
hl("PmenuSbar", {bg = "#343A40", bold = false, italic = false})
hl("PmenuThumb", {bg = "#6C757D", bold = false, italic = false})
hl("NormalFloat", {fg = "#CED4DA", bg = "#2B3035", bold = false, italic = false})
hl("FloatBorder", {fg = "#495057", bg = "#2B3035", bold = false, italic = false})
hl("StatusLine", {fg = "#2B3035", bg = "#CED4DA", bold = false, italic = false})
hl("StatusLineNC", {fg = "#DEE2E6", bg = "#2B3035", bold = false, italic = false})
hl("LineNr", {fg = "#CED4DA", bg = "#212529", bold = false, italic = false})
hl("CursorLineNr", {fg = "#9BB1FF", bg = "#212529", bold = false, italic = false})
hl("SignColumn", {fg = "#CED4DA", bg = "#212529", bold = false, italic = false})
hl("Folded", {fg = "#6C757D", bg = "#2B3035", bold = false, italic = false})
hl("FoldColumn", {fg = "#6C757D", bg = "#212529", bold = false, italic = false})
hl("NonText", {fg = "#495057", bold = false, italic = false})
hl("SpecialKey", {fg = "#495057", bold = false, italic = false})
hl("Whitespace", {fg = "#495057", bold = false, italic = false})
hl("Conceal", {fg = "#6C757D", bold = false, italic = false})
hl("WinSeparator", {fg = "#343A40", bold = false, italic = false})
hl("VertSplit", {fg = "#343A40", bold = false, italic = false})
hl("WildMenu", {fg = "#343A40", bg = "#9BB1FF", bold = false, italic = false})
hl("TabLine", {fg = "#6C757D", bg = "#2B3035", bold = false, italic = false})
hl("TabLineFill", {bg = "#2B3035", bold = false, italic = false})
hl("TabLineSel", {fg = "#CED4DA", bg = "#212529", bold = false, italic = false})
hl("ErrorMsg", {fg = "#DEE2E6", bold = false, italic = false})
hl("WarningMsg", {fg = "#ADB5BD", bold = false, italic = false})
hl("MoreMsg", {fg = "#9BB1FF", bold = false, italic = false})
hl("ModeMsg", {fg = "#CED4DA", bold = false, italic = false})
hl("Question", {fg = "#9BB1FF", bold = false, italic = false})
hl("SpellBad", {sp = "#DEE2E6", undercurl = true})
hl("SpellCap", {sp = "#ADB5BD", undercurl = true})
hl("SpellRare", {sp = "#9BB1FF", undercurl = true})
hl("SpellLocal", {sp = "#6C757D", undercurl = true})

-- Diagnostics
hl("DiagnosticError", {fg = "#DEE2E6", bold = false, italic = false})
hl("DiagnosticWarn", {fg = "#ADB5BD", bold = false, italic = false})
hl("DiagnosticInfo", {fg = "#9BB1FF", bold = false, italic = false})
hl("DiagnosticHint", {fg = "#6C757D", bold = false, italic = false})
hl("DiagnosticUnderlineError", {sp = "#DEE2E6", underline = true})
hl("DiagnosticUnderlineWarn", {sp = "#ADB5BD", underline = true})
hl("DiagnosticUnderlineInfo", {sp = "#9BB1FF", underline = true})
hl("DiagnosticUnderlineHint", {sp = "#6C757D", underline = true})

-- Diff
hl("DiffAdd", {fg = "#CAFFBF", bg = "#343A40", bold = false, italic = false})
hl("DiffDelete", {fg = "#FFADAD", bg = "#343A40", bold = false, italic = false})
hl("DiffChange", {fg = "#FDFFB6", bg = "#343A40", bold = false, italic = false})
hl("DiffText", {fg = "#FDFFB6", bg = "#495057", bold = false, italic = false})

-- Terminal colors
vim.g.terminal_color_0 = "#343A40"
vim.g.terminal_color_1 = "#FFADAD"
vim.g.terminal_color_2 = "#CAFFBF"
vim.g.terminal_color_3 = "#FDFFB6"
vim.g.terminal_color_4 = "#9FA0FF"
vim.g.terminal_color_5 = "#FFC6FF"
vim.g.terminal_color_6 = "#9BF6FF"
vim.g.terminal_color_7 = "#ADB5BD"
vim.g.terminal_color_8 = "#6C757D"
vim.g.terminal_color_9 = "#FFADAD"
vim.g.terminal_color_10 = "#CAFFBF"
vim.g.terminal_color_11 = "#FDFFB6"
vim.g.terminal_color_12 = "#A0C4FF"
vim.g.terminal_color_13 = "#FFC6FF"
vim.g.terminal_color_14 = "#9BF6FF"
vim.g.terminal_color_15 = "#F8F9FA"
