" vim/ftplugin/markdown.vim
" RSVP key mappings for prose and Markdown documents
" ===================================================

if exists("b:did_ftplugin_rsvp_markdown")
  finish
endif
let b:did_ftplugin_rsvp_markdown = 1

" ── RSVP key mappings ─────────────────────────────────────────────────────────

nnoremap <buffer> <LocalLeader>e :RSVPEntropy<CR>
nnoremap <buffer> <LocalLeader>f :RSVPFlow<CR>
nnoremap <buffer> <LocalLeader>b :RSVPBeats<CR>
nnoremap <buffer> <LocalLeader>s :RSVPStatus<CR>

" Rewrite transforms on visual selection
xnoremap <buffer> <LocalLeader>rl :RSVPRewrite redundancy_reduce<CR>
xnoremap <buffer> <LocalLeader>rs :RSVPRewrite lamphrodyne_smooth<CR>
xnoremap <buffer> <LocalLeader>re :RSVPRewrite entropy_bleed_reduce<CR>

" Section navigation
nnoremap <buffer> ]] :call search('^#\+\s', 'W')<CR>
nnoremap <buffer> [[ :call search('^#\+\s', 'bW')<CR>
