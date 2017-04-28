#!/bin/sh

for((i=0;i<=10000;i++))
do
  nohup python temp.py 1>out.1 2>err.1 &
  sleep 1800
done
