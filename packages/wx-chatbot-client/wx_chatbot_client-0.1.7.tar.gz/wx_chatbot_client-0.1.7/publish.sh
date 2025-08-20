echo '+ running .......................'

echo '+ step1.          clean.....'
rm -rf dist

echo '+ step2.          build.....'
uv build --package wx-chatbot-client src/wx_chatbot_client || { echo "command failed"; exit 1; }

echo '+ step3.          publish.....'
uvx uv-publish