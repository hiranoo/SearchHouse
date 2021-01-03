# Before executing
1. rewrite BASE_PATH in modules/base_path.py depending on your environment

2. enable PYTHONPATH: modules/*

# Flow
1. fetch data from suumo -- ./data/fetched/*_date.csv
2. update data to be latest -- ./data/latest/*.csv
3. select some data from latest data -- DataFrame
4. add data to the selected data, refering detail link -- DataFrame
5. select favorite data from 4's data -- ./data/selected/selected.csv
6. send favorite data (choose all or new) -- ./data/sending/*.csv


