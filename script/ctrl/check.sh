#!/bin/bash

if [ $# -ne 1 ];then
    echo "usage: $0 task_name"
    exit 1
fi
task_name=$1

num=`ps -ef | grep "./task.py $task_name" | grep -v grep | wc -l`
if [ $num -gt 0 ];then
    echo "process ok!"
else
    echo "process not exists!"
fi
