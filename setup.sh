# mkdir -p ~/.streamlit/

# echo "\
# [general]\n\
# email = \"muddasir.manage@gmail.com\"\n\
# " > ~/.streamlit/credentials.toml

# echo "\
# [server]\n\
# headless = true\n\
# enableCORS=false\n\
# port = $PORT\n\
# " > ~/.streamlit/config.toml

mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"muddasir.manage@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
maxUploadSize = 1\n\
" > ~/.streamlit/config.toml
