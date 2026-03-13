" vim/plugin/rsvp.vim
" RSVP Writing Suite — Vim integration
" =====================================
" Provides commands and quickfix integration for the rsvp-tools suite.
" All commands operate on the current file unless a range or visual
" selection is specified.
"
" Commands:
"   :RSVPEntropy        — entropy scan → quickfix
"   :RSVPFlow           — flow/curvature scan → location list
"   :RSVPBeats          — beat topology map → preview window
"   :RSVPPersona        — character field report → preview window
"   :RSVPPersona NAME   — focus on a single character
"   :RSVPRewrite PASS   — apply a named transform to visual selection
"   :RSVPParse          — parse current file → JSON preview
"   :RSVPStatus         — show field summary in command line
"
" Quickfix integration:
"   rsvp-entropy and rsvp-flow emit Vim quickfix format when called with
"   --fmt quickfix. :RSVPEntropy and :RSVPFlow load these into cexpr so
"   that :cn / :cp / :copen navigate structural issues directly.
"
" Requires: rsvp-tools suite installed; bin/ directory on PATH or
"           g:rsvp_bin_dir set to the absolute path of bin/.

if exists("g:loaded_rsvp")
  finish
endif
let g:loaded_rsvp = 1

" ── Configuration ─────────────────────────────────────────────────────────────

" Set g:rsvp_bin_dir to the bin/ directory of the suite if not on PATH.
" Example: let g:rsvp_bin_dir = '/home/user/rsvp-writing-suite/bin'
if !exists("g:rsvp_bin_dir")
  let g:rsvp_bin_dir = ""
endif

" Entropy threshold for quickfix flagging
if !exists("g:rsvp_entropy_threshold")
  let g:rsvp_entropy_threshold = 4.0
endif

" Flow stagnation threshold
if !exists("g:rsvp_stagnation_threshold")
  let g:rsvp_stagnation_threshold = 0.15
endif

" ── Helpers ───────────────────────────────────────────────────────────────────

function! s:BinPath(tool) abort
  if g:rsvp_bin_dir != ""
    return g:rsvp_bin_dir . "/" . a:tool
  endif
  return a:tool
endfunction

function! s:OpenPreview(content) abort
  " Open content in a horizontal preview window
  silent! pclose
  new
  setlocal buftype=nofile bufhidden=wipe noswapfile nobuflisted
  setlocal filetype=rsvp-report
  call setline(1, split(a:content, "\n"))
  setlocal nomodifiable
  resize 20
  wincmd p
endfunction

" ── Commands ──────────────────────────────────────────────────────────────────

" :RSVPEntropy — load entropy quickfix for current file
command! RSVPEntropy call s:RunEntropy()

function! s:RunEntropy() abort
  let l:file = expand("%")
  let l:cmd = s:BinPath("rsvp-entropy") .
        \ " --fmt quickfix" .
        \ " --threshold " . g:rsvp_entropy_threshold .
        \ " " . shellescape(l:file)
  cexpr system(l:cmd)
  copen
  echo "RSVPEntropy: quickfix loaded (" . l:file . ")"
endfunction


" :RSVPFlow — load flow diagnostics into location list
command! RSVPFlow call s:RunFlow()

function! s:RunFlow() abort
  let l:file = expand("%")
  let l:cmd = s:BinPath("rsvp-flow") .
        \ " --fmt quickfix" .
        \ " --stagnation " . g:rsvp_stagnation_threshold .
        \ " " . shellescape(l:file)
  lexpr system(l:cmd)
  lopen
  echo "RSVPFlow: location list loaded"
endfunction


" :RSVPBeats — show beat topology map in preview window
command! RSVPBeats call s:RunBeats()

function! s:RunBeats() abort
  let l:file = expand("%")
  let l:cmd = s:BinPath("rsvp-beats") . " " . shellescape(l:file)
  let l:output = system(l:cmd)
  call s:OpenPreview(l:output)
  echo "RSVPBeats: topology map loaded"
endfunction


" :RSVPPersona [NAME] — character field report
command! -nargs=? RSVPPersona call s:RunPersona(<q-args>)

function! s:RunPersona(char) abort
  let l:file = expand("%")
  let l:char_flag = a:char != "" ? " --character " . shellescape(a:char) : ""
  let l:cmd = s:BinPath("rsvp-persona") . l:char_flag . " " . shellescape(l:file)
  let l:output = system(l:cmd)
  call s:OpenPreview(l:output)
endfunction


" :RSVPRewrite PASS — apply a transform pass to the visual selection
" Usage: select lines in visual mode, then :RSVPRewrite lamphrodyne_smooth
command! -range -nargs=1 RSVPRewrite call s:RunRewrite(<line1>, <line2>, <q-args>)

function! s:RunRewrite(line1, line2, pass) abort
  let l:lines = getline(a:line1, a:line2)
  let l:text = join(l:lines, "\n")
  let l:cmd = s:BinPath("rsvp-rewrite") .
        \ " --pass " . shellescape(a:pass) .
        \ " --diff"
  let l:annotation = system(l:cmd, l:text)

  " Show annotation in command area; rewrite is piped to a scratch buffer
  let l:cmd2 = s:BinPath("rsvp-rewrite") . " --pass " . shellescape(a:pass)
  let l:result = system(l:cmd2, l:text)

  " Open diff split
  silent! pclose
  new
  setlocal buftype=nofile bufhidden=wipe noswapfile nobuflisted
  call setline(1, split(l:result, "\n"))
  setlocal nomodifiable
  resize 15
  echo "RSVPRewrite [" . a:pass . "]: " . trim(l:annotation)
endfunction


" :RSVPParse — show parse tree for current file
command! RSVPParse call s:RunParse()

function! s:RunParse() abort
  let l:file = expand("%")
  let l:cmd = s:BinPath("rsvp-parse") . " --fmt text " . shellescape(l:file)
  let l:output = system(l:cmd)
  call s:OpenPreview(l:output)
endfunction


" :RSVPStatus — print one-line RSVP field summary to command line
command! RSVPStatus call s:RunStatus()

function! s:RunStatus() abort
  let l:file = expand("%")
  let l:entropy_cmd = s:BinPath("rsvp-entropy") . " --fmt json " . shellescape(l:file)
  let l:json = system(l:entropy_cmd)
  " Extract a rough summary without json parsing in vimscript
  let l:flagged = len(split(l:json, '"flagged": true')) - 1
  let l:total   = len(split(l:json, '"flagged"')) - 1
  echo "RSVP: " . l:flagged . "/" . l:total . " patches flagged  |  " . l:file
endfunction


" ── Autocommands ──────────────────────────────────────────────────────────────

augroup rsvp_auto
  autocmd!
  " Automatically set compiler to rsvp-entropy for fountain files
  autocmd FileType fountain setlocal makeprg=rsvp-entropy\ --fmt\ quickfix\ %
  autocmd FileType fountain setlocal errorformat=%f:%l:%c:%m
augroup END
