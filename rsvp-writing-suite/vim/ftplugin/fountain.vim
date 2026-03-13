" vim/ftplugin/fountain.vim
" Filetype settings and RSVP key mappings for Fountain screenplays
" ================================================================
"
" Assumes the rsvp plugin is loaded (vim/plugin/rsvp.vim).
" Place this file in ~/.vim/ftplugin/ or add vim/ to runtimepath.
"
" Local mappings (buffer-local, <LocalLeader> prefix):
"
"   <LocalLeader>e   — RSVPEntropy: entropy scan → quickfix
"   <LocalLeader>f   — RSVPFlow: flow scan → location list
"   <LocalLeader>b   — RSVPBeats: topology map preview
"   <LocalLeader>p   — RSVPPersona: character field report
"   <LocalLeader>r   — RSVPParse: parse tree preview
"   <LocalLeader>s   — RSVPStatus: one-line field summary
"   <LocalLeader>m   — :make (rsvp-entropy quickfix, same as RSVPEntropy)
"
" Scene navigation:
"   ]] / [[          — jump to next / previous scene heading
"
" Fold method: scene headings become fold markers when foldmethod=expr

if exists("b:did_ftplugin_rsvp_fountain")
  finish
endif
let b:did_ftplugin_rsvp_fountain = 1

setlocal textwidth=72
setlocal wrap
setlocal linebreak
setlocal spell
setlocal foldmethod=expr
setlocal foldexpr=FountainFoldLevel(v:lnum)

" ── Scene folding ─────────────────────────────────────────────────────────────

function! FountainFoldLevel(lnum) abort
  let l:line = getline(a:lnum)
  if l:line =~# '^\(INT\|EXT\|INT\./EXT\|I/E\)[\. ]'
    return ">1"
  endif
  return "="
endfunction


" ── Scene navigation ──────────────────────────────────────────────────────────

" Jump forward to next scene heading
nnoremap <buffer> ]] :call search('^\(INT\|EXT\|INT\./EXT\|I/E\)[\. ]', 'W')<CR>

" Jump backward to previous scene heading
nnoremap <buffer> [[ :call search('^\(INT\|EXT\|INT\./EXT\|I/E\)[\. ]', 'bW')<CR>


" ── RSVP key mappings ─────────────────────────────────────────────────────────

nnoremap <buffer> <LocalLeader>e :RSVPEntropy<CR>
nnoremap <buffer> <LocalLeader>f :RSVPFlow<CR>
nnoremap <buffer> <LocalLeader>b :RSVPBeats<CR>
nnoremap <buffer> <LocalLeader>p :RSVPPersona<CR>
nnoremap <buffer> <LocalLeader>r :RSVPParse<CR>
nnoremap <buffer> <LocalLeader>s :RSVPStatus<CR>
nnoremap <buffer> <LocalLeader>m :make<CR>

" Rewrite transforms on visual selection
xnoremap <buffer> <LocalLeader>rl :RSVPRewrite redundancy_reduce<CR>
xnoremap <buffer> <LocalLeader>rs :RSVPRewrite lamphrodyne_smooth<CR>
xnoremap <buffer> <LocalLeader>rt :RSVPRewrite torsion_sharpen<CR>
xnoremap <buffer> <LocalLeader>re :RSVPRewrite entropy_bleed_reduce<CR>


" ── Syntax hints ─────────────────────────────────────────────────────────────
" Minimal syntax highlighting if no fountain.vim syntax file is present.
" A full syntax plugin is recommended (e.g. vim-fountain).

if !exists("b:current_syntax")
  syntax match fountainScene     /^\(INT\|EXT\|INT\./EXT\|I/E\).*/
  syntax match fountainCharacter /^[A-Z][A-Z0-9 \-']\+\s*$/
  syntax match fountainTransition /^\(FADE\|CUT\|SMASH\).*/
  syntax match fountainNote      /\[\[.*\]\]/

  highlight fountainScene     ctermfg=Yellow   guifg=#d4b400
  highlight fountainCharacter ctermfg=Cyan     guifg=#5fd7ff
  highlight fountainTransition ctermfg=Magenta guifg=#d78700
  highlight fountainNote      ctermfg=Green    guifg=#87af87

  let b:current_syntax = "fountain"
endif
