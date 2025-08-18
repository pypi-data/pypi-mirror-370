let SessionLoad = 1
if &cp | set nocp | endif
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/devi/tunneltop.git/main/tunneltop
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
if &shortmess =~ 'A'
  set shortmess=aoOA
else
  set shortmess=aoO
endif
badd +181 ~/scripts/.tunneltop.toml
badd +728 ~/devi/tunneltop.git/main/tunneltop/tunneltop.py
badd +535 ~/.vim/bundle/YouCompleteMe/third_party/ycmd/third_party/jedi_deps/jedi/jedi/third_party/typeshed/stdlib/3/os/__init__.pyi
argglobal
%argdel
edit ~/devi/tunneltop.git/main/tunneltop/tunneltop.py
argglobal
balt ~/.vim/bundle/YouCompleteMe/third_party/ycmd/third_party/jedi_deps/jedi/jedi/third_party/typeshed/stdlib/3/os/__init__.pyi
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal nofen
silent! normal! zE
let &fdl = &fdl
let s:l = 815 - ((50 * winheight(0) + 25) / 51)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 815
normal! 05|
tabnext 1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
let &shortmess = s:shortmess_save
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
nohlsearch
let g:this_session = v:this_session
let g:this_obsession = v:this_session
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
