# ExcelCSVParseHelper

A lightweight Python library to help parse, manipulate, and automate workflows between CSV and Excel files.

## Features

- Insert numerical or string data into Excel cells
- Automatically reopen or close Excel files
- Parse, clean, and filter CSV datasets
- Read ranges from Excel sheets
- Split lists into positives/negatives for further processing

## Installation

```bash
pip install ExcelCSVParseHelper

```
requires windows-only packages psutil and pywin32 for full functionality [automatic close and open of excel files] 

## Example Usage

```python
from ExcelCSVParseHelper import *

insert_data_to_excel("myfile.xlsx", {"A1": 100, "B2": 200}, sheet_arg="Sheet1")

df = prepare_source(base_path="data.csv", sep=",", columns_to_drop=[0, 2])


more advanced use cases are also supported like for example via use of a 'staging' function in the following manner:

def run(
    date,
    idea1_base_path,
    idea1_postfix = "_results_ide1.csv",
    idea1_sep = ";",
    ida1_columns_to_keep = [1, 2],
    idea1_prefix_list = ["A", "B"], 
    idea1_column_list = ["One", "Two"],
    idea1_start_int= 1,
    idea1_include_header= True,
    raw_path = None
):
    
   
    
    postfix= idea1_postfix
    base_path= idea1_base_path
    sep= idea1_sep
    columns_to_keep= ida1_columns_to_keep
    
    return_dict= {}
    
    prefix_list= ida1_prefix_list
    column_list= ida1_column_list
    
    for i in range(len(prefix_list)):
        return_dict = set_source(
            file_path= raw_path,
            prefix_letter=prefix_list[i],
            column_target=column_list[i],
            date_target=f"{date}",
            start_int= idea1_start_int,
            header=column_list[i],
            postfix=postfix,
            base_path=base_path,
            sep=sep,
            white_list=True,
            columns_to_keep=columns_to_keep,
            infer=False,
            
            header_start= 213,
            range_of_interest_start=0,
            range_of_interest_end=96,
            include_header= idea1_include_header
        )
        
        fp  = return_dict["file_path"]
        
        
        
        close_excel_file_if_open(return_dict["file_path"])
        
        insert_data_to_excel(
            return_dict["file_path"],
            return_dict["column_insert"],
            sheet_arg= "data",
        )

or

def run_2(
    date,
    two_base_path,
    two_colums_to_drop=[
        "UsrName",
        "TmZn",
        "INFO",
        "Self",
    ],
    two_postfix="-two.csv",
    two_sep=";",
    two_prefix_list=["B", "C", "D", "E", "F"], #do których kolumn będzie wstawione
    two_column_list=["1", "2" , "3", "4", "5"],
    two_start_int= 1,
    two_include_header= True,
    raw_path = None
    
):
    
    

    postfix = two_postfix
    base_path= two_base_path
    sep = two_sep
    columns_to_drop = two_colums_to_drop

    return_dict = {}

    prefix_list = two_prefix_list
    column_list = two_column_list


    for i in range(len(prefix_list)):
        return_dict = set_source(
            file_path= raw_path,
            prefix_letter=prefix_list[i],
            column_target=column_list[i],
            date_target=f"{date}",
            start_int= two_start_int,
            header=column_list[i],
            postfix=postfix,
            base_path=base_path,
            sep=sep,
            columns_to_drop=columns_to_drop,
            white_list=False,
            columns_to_keep=None,
            infer=True,
            header_start=None,
            range_of_interest_start=None,
            range_of_interest_end=None,
            include_header= two_include_header
        )

        fp  = return_dict["file_path"]
        
       


        close_excel_file_if_open(return_dict["file_path"])

        insert_data_to_excel(
            return_dict["file_path"],
            return_dict["column_insert"],
            sheet_arg= "Dane",
        )
```
