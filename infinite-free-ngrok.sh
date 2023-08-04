#!/bin/bash

# Function to run the binary using expect and script
run_ngrok() {
    # Run the binary using expect and script
    expect <<EOF
set timeout $TIMEOUT
spawn ngrok http $NGROK_PORT
expect "offline"
exit 0
EOF
}

# Function to start the ngrok process and capture the forwarding URL
start_ngrok() {
    # Start the ngrok process
    rm ngrok.log
    run_ngrok > ngrok.log &

    # Capture the PID of the ngrok process
    NGROK_PID=$!
    echo "ngrok process started with PID: $NGROK_PID"

    sleep 1
    cat ngrok.log

    echo -e "\nsleeping 6.9 then capturing ngrok url"
    sleep 10 
    
}

parse_ngrok_url(){
    # Extract the forwarding URL from the ngrok output
    NGROK_URL=$(egrep -o 'https://\S+ngrok.io' ngrok.log | tail -n 1)
    echo "ngrok forwarding URL: $NGROK_URL"
}

# Function to stop the ngrok process
stop_ngrok() {
    # Kill the ngrok process using the captured PID
    kill $NGROK_PID
    pkill ngrok
    echo "ngrok process with PID $NGROK_PID stopped"
}


set_twilio_webhook_to_new_ngrok_url(){
            # Set the new sms_url using the ngrok forwarding URL
            NEW_SMS_URL="${NGROK_URL}/sms"

            # Construct the request URL
            REQUEST_URL="https://api.twilio.com/2010-04-01/Accounts/${TWILIO_ACCOUNT_SID}/IncomingPhoneNumbers/${TWILIO_PHONE_NUMBER_SID}.json"

            # Make the API request to update the sms_url
            curl -X POST -u "${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}" \
                -d "SmsUrl=${NEW_SMS_URL}" \
                "${REQUEST_URL}"
}

NGROK_PORT=$1
if test -z "$NGROK_PORT"; then
    NGROK_PORT=6969
fi
TIMEOUT=$2
if test -z "$TIMEOUT"; then
    TIMEOUT=7169
fi

while true; do
    start_ngrok $NGROK_PORT
    parse_ngrok_url
    if test -z "$NGROK_URL"; then
        echo "ngrok URL not found, restarting ngrok"
        stop_ngrok
        continue
    fi
    set_twilio_webhook_to_new_ngrok_url
    sleep $TIMEOUT
    stop_ngrok
done
stop_ngrok

