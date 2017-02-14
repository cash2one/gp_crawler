#!/bin/bash

if [ $# -ne 1 ];then
    echo "usage: $0 task_name"
    exit 1
fi
task_name=$1
task_dir="../../data/task"
stop_flag="${task_dir}/${task_name}.stop"

touch ${stop_flag}
echo "stop message has been sent!"

cnt=0
while [ 1 ];do
    num=`ps -ef | grep "./task.py $task_name" | grep -v grep | wc -l`
    if [ $num -eq 0 ];then
        echo "process stop ok!"
        break
    else
        echo "stopping..."
        sleep 1
    fi
    cnt=$((cnt+1))
    if [ $cnt -gt 5 ];then
        echo "process is stopping, please wait a minute!"
        break
    fi
done


