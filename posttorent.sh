#! /bin/bash
# posttorrent.sh by Killemov
{
  # Log file, file where we tell what events have been processed.
  LOG_FILE=/var/log/posttorrent.log
  # Username for transmission remote.
  TR_USERNAME=""
  # Password for transmission remote.
  TR_PASSWORD=""
  # Get current time.
  NOW=$(date +%Y-%m-%d\ %H:%M:%S)

  ENCODED_TR_TORRENT_NAME = $(echo "${TR_TORRENT_NAME}" | base64)
  
  mv "${TR_TORRENT_DIR}/${TR_TORRENT_NAME}" "${TR_TORRENT_DIR}/$ENCODED_TR_TORRENT_NAME" 
  # Source directory, should not be changed.
  SRC_DIR="${TR_TORRENT_DIR}/$ENCODED_TR_TORRENT_NAME"
  # Directory to store the un-compressed files in..
  DEST_DIR="${TR_TORRENT_DIR}/$ENCODED_TR_TORRENT_NAME/"
  # This parameter string could be passed from Transmission in the future.
  TR_TORRENT_PARAMETER="EXTRACT SLEEP1h"

  if [ -e "$SRC_DIR/keep" ]; then
    TR_TORRENT_PARAMETER="$TR_TORRENT_PARAMETER KEEP"
  fi

  if [ -e "$SRC_DIR/exit" ]; then
    TR_TORRENT_PARAMETER="EXIT"
  fi

  # Actual processing starts here.
  if [[ "$TR_TORRENT_PARAMETER" =~ "EXIT" ]]; then
    echo $NOW "Exiting $TR_TORRENT_NAME" >> $LOG_FILE
    exit 0
  fi

  if [[ "$TR_TORRENT_PARAMETER" =~ "EXTRACT" ]]; then
    cd $TR_TORRENT_DIR
    if [ -d "$SRC_DIR" ]; then
      IFS=$'\n'
      unset RAR_FILES i
      for RAR_FILE in $( find "$SRC_DIR" -type f -iname "*.rar" ); do
        if [[ $RAR_FILE =~ .*part.*.rar ]]; then
          if [[ $RAR_FILE =~ .*part0*1.rar ]]; then
            RAR_FILES[i++]=$RAR_FILE
          fi
        else
          RAR_FILES[i++]=$RAR_FILE
        fi
      done
      unset IFS

      if [ ${#RAR_FILES} -gt 0 ]; then
        for RAR_FILE in "${RAR_FILES[@]}"; do
          unrar x -inul "$RAR_FILE" "$DEST_DIR"
          if [ $? -gt 0 ]; then
            echo $NOW "Error unrarring $TR_TORRENT_NAME" >> $LOG_FILE
            transmission-remote -n $TR_USERNAME:$TR_PASSWORD -t $TR_TORRENT_HASH --verify --start
            exit 0
          fi
        done
        if [[ ! "$TR_TORRENT_PARAMETER" =~ "KEEP" ]]; then
          SLEEP=$(expr match "$TR_TORRENT_PARAMETER" '.*SLEEP\([0-9a-zA-Z]*\)')
          if [ ${#SLEEP} -gt 0 ]; then
            sleep $SLEEP
          fi
          transmission-remote -n $TR_USERNAME:$TR_PASSWORD -t $TR_TORRENT_HASH --remove-and-delete
        fi
        echo $NOW "Unrarred $TR_TORRENT_NAME" >> $LOG_FILE
      fi
    fi
  fi
  mv "${TR_TORRENT_DIR}/$ENCODED_TR_TORRENT_NAME" "${TR_TORRENT_DIR}/${TR_TORRENT_NAME}" 
} &