#!/bin/bash



git config --global --add safe.directory /app
echo "CHECKING GIT STATUS"
git status
echo "END CHECKING GIT STATUS"
echo "RUNNING LS"
ls
echo "END RUNNING LS"

# Check if the requirements file has been cloned yet, if not sleep for 5 seconds and try again
while [ ! -f /app/$CODE_DIR/$ENTRYPOINT ]
do
    echo "REQUIREMENTS FILE NOT FOUND, SLEEPING FOR 5 SECONDS"
    echo "LOOKING IN DIRECTORY:  /app/$CODE_DIR/$ENTRYPOINT"
    sleep 5
done
pip install -r /app/$CODE_DIR/requirements.txt


DIR_TO_WATCH=/app/$CODE_DIR/
cd /app/

while true; do
  # Start your server in the background
  streamlit run /app/$CODE_DIR/$ENTRYPOINT --server.port=80 --server.address=0.0.0.0 --server.baseUrlPath=$STREAMLIT_BASE_URL_PATH --server.fileWatcherType=none &
  SERVER_PID=$!

  # Wait for changes in the directory
  inotifywait -r -e modify,create,delete,move $DIR_TO_WATCH

  # Kill the server after detecting changes
  kill $SERVER_PID

  # Wait for a moment before restarting the server
  sleep 1
done