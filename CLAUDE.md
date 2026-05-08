# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Nibelung is a minimalistic Emacs color theme with light (`nibelung`) and dark (`nibelung-dark`) variants. Comments are treated as first-class citizens with their own background highlighting.

## Commands

```bash
make test          # Run all tests (compile + load + face validation)
make test-compile  # Byte-compile all .el files with strict warnings
make test-load     # Load both theme variants in headless Emacs
make test-faces    # Validate all registered faces exist
make clean         # Remove .elc files
```

## Architecture

Four files, strict dependency order:

1. **nibelung-palettes.el** — Two color palettes (`nibelung-light-palette`, `nibelung-dark-palette`) as property lists. All colors defined here.
2. **nibelung-theme-base.el** — `nibelung-theme-create` function: extracts palette colors into local variables, defines semantic face groups (bold, comment, string, etc.), then applies 600+ face definitions via `custom-theme-set-faces`.
3. **nibelung-theme.el** — Light theme entry point. Requires base + palettes, calls `nibelung-theme-create` with light palette.
4. **nibelung-dark-theme.el** — Dark theme entry point. Same pattern, dark palette.

### Key patterns

- **Palette indirection**: Faces never hardcode colors. Everything references palette keys (`:bg`, `:fg`, `:level0`–`:level6`, `:accent-*`, `:emphasis`, etc.), enabling both variants from one codebase.
- **Semantic let-bindings**: `nibelung-theme-base.el` creates ~58 intermediate face definitions (e.g., `bold`, `comment`, `builtin`) that are reused across 600+ face assignments for consistency.
- **Quasiquote interpolation**: Face specs use `` `((t ...)) `` with `,variable` unquoting to inject palette-derived colors.

### Adding a new face

1. Identify the correct semantic group in `nibelung-theme-base.el`
2. Use existing let-bound variables (e.g., `fg`, `bg`, `emphasis`, `level3`) — don't hardcode hex colors
3. Run `make test` to verify compilation and face registration

### Adding/modifying palette colors

Edit `nibelung-palettes.el`. Both light and dark palettes must have matching keys. Then update `nibelung-theme-base.el` to extract and use the new key.

## Supported packages

40+ packages have explicit face definitions including: Magit, Org Mode, Dired/Diredfl/Dirvish, Company/Corfu, Vertico/Consult, Tree-sitter, Eglot/LSP, Evil, Rainbow Delimiters, Doom Modeline, Markdown, Flymake/Flycheck, Treemacs, Hydra, Dape, and full ANSI terminal colors.
