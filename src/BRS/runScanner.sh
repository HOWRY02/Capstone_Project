cd ./data/scanned_data && scanimage --device 'brother3:net1;dev0' --mode "True Gray" --resolution 1200 --format png --batch=doc_%d.png --brightness "-50" --contrast "30" -x "210" -y "297"
# cd ./data/scanned_data && scanimage --mode "True Gray" --resolution 1200 --format png --batch=doc_%d.png --brightness "-50" --contrast "30" -x "210" -y "297"
