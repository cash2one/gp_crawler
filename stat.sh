cwd=`pwd`

d=`date +"%Y%m%d"`
#d="20160518"
cd log
echo "RetCode"
awk -F 'RetCode' '{print $2}' appstat_advert.log.$d.* | awk -F ',' '{print $1}' | sort | uniq -c

echo
echo
echo "RetCode = 0 and NewVersionCode != 0"
awk -F ',' '{if($11=="RetCode[0]" && $21!="NewVersionCode[0]" && $12=="CompatibleCode[1]"){print $0}}' appstat_advert.log.$d.* | wc -l
awk -F ',' '{if($11=="RetCode[0]" && $21!="NewVersionCode[0]"){print $0}}' appstat_advert.log.$d.* | wc -l

echo "RetCode = 0 and NewVersionCode = 0"
awk -F ',' '{if($11=="RetCode[0]" && $21=="NewVersionCode[0]"){print $0}}' appstat_advert.log.$d.* | wc -l
