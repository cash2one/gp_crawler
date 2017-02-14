#!/bin/bash

if [ $# -eq 0 ];then
    echo "usage: $0 task_name [action]"
    exit 1
elif [ $# -eq 1 ];then
    task_name=$1
    action="start"
else
    task_name=$1
    action=$2
fi

num=`ps -ef | grep "./task.py $task_name " | grep -v grep | wc -l`
if [ $num -gt 0 ];then
    echo "process already exists!"
    exit 1
fi

cd ../task
nohup ./task.py "$task_name" "$action" 1>>"../../log/task_$task_name.log" 2>&1 &

sleep 1
num=`ps -ef | grep "./task.py $task_name" | grep -v grep | wc -l`
if [ $num -gt 0 ];then
    echo "start ok!"
else
    echo "program exit!"
fi


