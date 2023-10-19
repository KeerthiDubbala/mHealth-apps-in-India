#!/bin/zsh

# mkdir data/master_json
# mkdir data/master_json/app_individual_jsons
# mkdir data/master_json/temporary_bookkeeping
# touch data/master_json/temporary_bookkeeping/apps_queried.txt

N=5
for n in {0..$N}; do
    python crawl_appid_list_parallel.py -f Medical_apps_2021.txt -g HealthFitness_apps_2021.txt -s $n &
done