# How to use
1. rewrite BASE_PATH in modules/base_path.py depending on your environment

2. enable PYTHONPATH: modules/*

3. execute main.py

# Tips
1. if you don't need all data, you can select data not included in the previously selected data:

   rewrite 'all' as 'new' in main.py
   
## To change searching conditions
1. change url in url_list.txt
1. change filter functions in select_data.py
1. change columns in main.py 

# Flow
1. fetch data from suumo -- ./data/fetched/*_date.csv
2. update data to be latest -- ./data/latest/*.csv
3. select some data from latest data -- DataFrame
4. add data to the selected data, refering detail link -- DataFrame
5. select favorite data from 4's data -- ./data/selected/selected.csv
6. send favorite data (choose all or new) -- ./data/sending/*.csv


