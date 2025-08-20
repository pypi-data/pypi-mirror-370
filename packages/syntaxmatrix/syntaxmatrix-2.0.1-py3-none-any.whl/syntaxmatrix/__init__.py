from .core import SyntaxMUI

_app_instance = SyntaxMUI()

run = _app_instance.run
text_input = _app_instance.text_input
button = _app_instance.button
file_uploader = _app_instance.file_uploader
set_ui_mode = _app_instance.set_ui_mode
set_theme = _app_instance.set_theme
enable_theme_toggle = _app_instance.enable_theme_toggle
disable_theme_toggle = _app_instance.disable_theme_toggle
get_text_input_value = _app_instance.get_text_input_value
clear_text_input_value = _app_instance.clear_text_input_value
get_file_upload_value = _app_instance.get_file_upload_value
get_chat_history = _app_instance.get_chat_history
set_chat_history = _app_instance.set_chat_history
clear_chat_history = _app_instance.clear_chat_history
write = _app_instance.write
markdown = _app_instance.markdown
latex = _app_instance.latex
error = _app_instance.error
success = _app_instance.success
info = _app_instance.info
warning = _app_instance.warning
# plt_plot = _app_instance.plt_plot
# plotly_plot = _app_instance.plotly_plot

set_user_icon = _app_instance.set_user_icon
set_bot_icon = _app_instance.set_bot_icon
set_favicon = _app_instance.set_favicon
set_project_title = _app_instance.set_project_title
set_site_title = _app_instance.set_site_title
set_site_logo = _app_instance.set_site_logo
list_ui_modes = _app_instance.list_ui_modes
list_themes = _app_instance.list_themes
load_sys_chunks = _app_instance.load_sys_chunks

get_session_id = _app_instance.get_session_id
add_user_chunks = _app_instance.add_user_chunks
get_user_chunks = _app_instance.get_user_chunks
clear_user_chunks = _app_instance.clear_user_chunks
stream_write = _app_instance.stream_write
set_plottings = _app_instance.set_plottings
dropdown = _app_instance.dropdown
get_widget_value = _app_instance.get_widget_value

save_embed_model = _app_instance.save_embed_model
load_embed_model = _app_instance.load_embed_model
delete_embed_key = _app_instance.delete_embed_key
set_prompt_profile = _app_instance.set_prompt_profile
set_prompt_instructions = _app_instance.set_prompt_instructions
set_website_description = _app_instance.set_website_description
smiv_index = _app_instance.smiv_index
smpv_search  = _app_instance.smpv_search
process_query = _app_instance.process_query
embed_query = _app_instance.embed_query

app = _app_instance.app