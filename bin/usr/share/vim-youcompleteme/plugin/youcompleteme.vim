" Copyright (C) 2011, 2012  Google Inc.
"
" This file is part of YouCompleteMe.
"
" YouCompleteMe is free software: you can redistribute it and/or modify
" it under the terms of the GNU General Public License as published by
" the Free Software Foundation, either version 3 of the License, or
" (at your option) any later version.
"
" YouCompleteMe is distributed in the hope that it will be useful,
" but WITHOUT ANY WARRANTY; without even the implied warranty of
" MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
" GNU General Public License for more details.
"
" You should have received a copy of the GNU General Public License
" along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

" This is basic vim plugin boilerplate
let s:save_cpo = &cpo
set cpo&vim

function! s:restore_cpo()
  let &cpo = s:save_cpo
  unlet s:save_cpo
endfunction

" NOTE: The minimum supported version is 8.1.2269, but neovim always reports as
" v:version 800, but will largely work.
let s:is_neovim = has( 'nvim' )

if exists( "g:loaded_youcompleteme" )
  call s:restore_cpo()
  finish
elseif ( v:version < 801 || (v:version == 801 && !has( 'patch2269' )) ) &&
      \ !s:is_neovim
  echohl WarningMsg |
        \ echomsg "YouCompleteMe unavailable: requires Vim 8.1.2269+." |
        \ echohl None
  call s:restore_cpo()
  finish
elseif !has( 'timers' )
  echohl WarningMsg |
        \ echomsg "YouCompleteMe unavailable: requires Vim compiled with " .
        \ "the timers feature." |
        \ echohl None
  call s:restore_cpo()
  finish
elseif !has( 'python3_compiled' )
  echohl WarningMsg |
        \ echomsg "YouCompleteMe unavailable: requires Vim compiled with " .
        \ "Python (3.6.0+) support." |
        \ echohl None
  call s:restore_cpo()
  finish
" These calls try to load the Python 3 libraries when Vim is
" compiled dynamically against them. Since only one can be loaded at a time on
" some platforms, we first check if Python 3 is available.
elseif !has( 'python3' )
  echohl WarningMsg |
        \ echomsg "YouCompleteMe unavailable: unable to load Python." |
        \ echohl None
  call s:restore_cpo()
  finish
elseif &encoding !~? 'utf-\?8'
  echohl WarningMsg |
        \ echomsg "YouCompleteMe unavailable: requires UTF-8 encoding. " .
        \ "Put the line 'set encoding=utf-8' in your vimrc." |
        \ echohl None
  call s:restore_cpo()
  finish
endif

let g:loaded_youcompleteme = 1

"
" List of YCM options.
"
let g:ycm_filetype_whitelist =
      \ get( g:, 'ycm_filetype_whitelist', { "*": 1 } )

let g:ycm_filetype_blacklist =
      \ get( g:, 'ycm_filetype_blacklist', {
      \   'tagbar': 1,
      \   'notes': 1,
      \   'markdown': 1,
      \   'netrw': 1,
      \   'unite': 1,
      \   'text': 1,
      \   'vimwiki': 1,
      \   'pandoc': 1,
      \   'infolog': 1,
      \   'leaderf': 1,
      \   'mail': 1
      \ } )

" Blacklist empty buffers unless explicity whitelisted; workaround for
" https://github.com/ycm-core/YouCompleteMe/issues/3781
if !has_key( g:ycm_filetype_whitelist, 'ycm_nofiletype' )
  let g:ycm_filetype_blacklist[ 'ycm_nofiletype' ] = 1
endif

let g:ycm_open_loclist_on_ycm_diags =
      \ get( g:, 'ycm_open_loclist_on_ycm_diags', 1 )

let g:ycm_add_preview_to_completeopt =
      \ get( g:, 'ycm_add_preview_to_completeopt', 0 )

let g:ycm_autoclose_preview_window_after_completion =
      \ get( g:, 'ycm_autoclose_preview_window_after_completion', 0 )

let g:ycm_autoclose_preview_window_after_insertion =
      \ get( g:, 'ycm_autoclose_preview_window_after_insertion', 0 )

let g:ycm_key_list_select_completion =
      \ get( g:, 'ycm_key_list_select_completion', ['<TAB>', '<Down>'] )

let g:ycm_key_list_previous_completion =
      \ get( g:, 'ycm_key_list_previous_completion', ['<S-TAB>', '<Up>'] )

let g:ycm_key_list_stop_completion =
      \ get( g:, 'ycm_key_list_stop_completion', ['<C-y>'] )

let g:ycm_key_invoke_completion =
      \ get( g:, 'ycm_key_invoke_completion', '<C-Space>' )

let g:ycm_key_detailed_diagnostics =
      \ get( g:, 'ycm_key_detailed_diagnostics', '<leader>d' )

let g:ycm_cache_omnifunc =
      \ get( g:, 'ycm_cache_omnifunc', 1 )

let g:ycm_log_level =
      \ get( g:, 'ycm_log_level',
      \ get( g:, 'ycm_server_log_level', 'info' ) )

let g:ycm_keep_logfiles =
      \ get( g:, 'ycm_keep_logfiles',
      \ get( g:, 'ycm_server_keep_logfiles', 0 ) )

let g:ycm_extra_conf_vim_data =
      \ get( g:, 'ycm_extra_conf_vim_data', [] )

let g:ycm_server_python_interpreter =
      \ get( g:, 'ycm_server_python_interpreter',
      \ get( g:, 'ycm_path_to_python_interpreter', '' ) )

let g:ycm_show_diagnostics_ui =
      \ get( g:, 'ycm_show_diagnostics_ui', 1 )

let g:ycm_enable_diagnostic_signs =
      \ get( g:, 'ycm_enable_diagnostic_signs',
      \ get( g:, 'syntastic_enable_signs', 1 ) )

let g:ycm_enable_diagnostic_highlighting =
      \ get( g:, 'ycm_enable_diagnostic_highlighting',
      \ get( g:, 'syntastic_enable_highlighting', 1 ) )

let g:ycm_echo_current_diagnostic =
      \ get( g:, 'ycm_echo_current_diagnostic',
      \ get( g:, 'syntastic_echo_current_error', 1 ) )

let g:ycm_filter_diagnostics =
      \ get( g:, 'ycm_filter_diagnostics', {} )

let g:ycm_always_populate_location_list =
      \ get( g:, 'ycm_always_populate_location_list',
      \ get( g:, 'syntastic_always_populate_loc_list', 0 ) )

let g:ycm_error_symbol =
      \ get( g:, 'ycm_error_symbol',
      \ get( g:, 'syntastic_error_symbol', '>>' ) )

let g:ycm_warning_symbol =
      \ get( g:, 'ycm_warning_symbol',
      \ get( g:, 'syntastic_warning_symbol', '>>' ) )

let g:ycm_complete_in_comments =
      \ get( g:, 'ycm_complete_in_comments', 0 )

let g:ycm_complete_in_strings =
      \ get( g:, 'ycm_complete_in_strings', 1 )

let g:ycm_collect_identifiers_from_tags_files =
      \ get( g:, 'ycm_collect_identifiers_from_tags_files', 0 )

let g:ycm_seed_identifiers_with_syntax =
      \ get( g:, 'ycm_seed_identifiers_with_syntax', 0 )

let g:ycm_goto_buffer_command =
      \ get( g:, 'ycm_goto_buffer_command', 'same-buffer' )

let g:ycm_disable_for_files_larger_than_kb =
      \ get( g:, 'ycm_disable_for_files_larger_than_kb', 1000 )

let g:ycm_auto_hover =
      \ get( g:, 'ycm_auto_hover', 'CursorHold' )

"
" List of ycmd options.
" Beware: We (Debian) load the defaults directly from ycmd
" instead of embedding the values here as upstream does.
"
if exists( '*json_decode' )
  let s:option_file = '/usr/lib/ycmd/ycmd/default_settings.json'
  if filereadable( s:option_file )
    let s:default_options = json_decode( join( readfile( s:option_file ) ) )
    for key in keys( s:default_options )
      if ! has_key( g:, 'ycm_' . key )
        let g:[ 'ycm_' . key ] = s:default_options[ key ]
      endif
    endfor
    unlet key
  endif
endif

if has( 'vim_starting' ) " Loading at startup.
  " We defer loading until after VimEnter to allow the gui to fork (see
  " `:h gui-fork`) and avoid a deadlock situation, as explained here:
  " https://github.com/Valloric/YouCompleteMe/pull/2473#issuecomment-267716136
  augroup youcompletemeStart
    autocmd!
    autocmd VimEnter * call youcompleteme#Enable()
  augroup END
else " Manual loading with :packadd.
  call youcompleteme#Enable()
endif

" This is basic vim plugin boilerplate
call s:restore_cpo()
