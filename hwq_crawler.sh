for pkg in `cat $1`
do
    python script/main.py --pack_name="$pkg" --task_type=1 --task_name="advert"
done
