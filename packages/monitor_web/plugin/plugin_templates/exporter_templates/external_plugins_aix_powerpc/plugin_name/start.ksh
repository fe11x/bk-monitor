#!/bin/ksh

export LC_ALL=C
export LANG=C

. ./parse_yaml.ksh
create_variables etc/env.yaml
mkdir -p $(dirname ${BK_PLUGIN_PID_PATH})
mkdir -p ${BK_PLUGIN_LOG_PATH}

log_filepath=${BK_PLUGIN_LOG_PATH}/{{ plugin_id }}.log

./{{ plugin_id }} ${BK_CMD_ARGS} > ${log_filepath} 2>&1 &

pid=$!

echo "process tried to start, pid: ${pid}"

echo "checking process status..."
# wait process start successfully
sleep 2

ps aux | awk '{print $2}'| grep -w ${pid}

ret=$?

if [ ${ret} -ne 0 ]; then
  echo "process exited too quickly, pid: ${pid}"
  echo "process log: "
  cat ${log_filepath}
  exit 1
else
  echo "process started successfully, pid: ${pid}"
  echo ${pid} > ${BK_PLUGIN_PID_PATH}
  exit 0
fi
