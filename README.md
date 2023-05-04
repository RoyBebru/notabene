# NotaBene

The program is an address book that runs in a command-line mode in terminal window.


To run program use command

    $ pip3 install .
    $ nb

The command prompt looks like this:

    (101(17(1((C>

or

    (101(17(1((@>

where:
  - **101** means amount of all records;
  - **17** means amount records in **MATCH set**;
  - **1** means amount records in **MATCH subset** of **MATCH set**;
  - **C** means that address book is not modified yet;
  - **@** means that address book is modified and must be saved to file.

Most commands work with 2 sets: **MATCH set** and **MATCH subset**. **MATCH set** is formed by the **show** or **all** command. The **search** command selects **MATCH subset** from **MATCH set** based on a regular expression. **change** and **delete** commands are worked with **MATCH subset**. Each command has an Ukrainian synonym and can be shortened while ambiguity is absent. So, command **search** can be entered as **sea** or **se**, but not **s** because other command **show** has first letter **s**.

Application support the following commands:
  - **all**|**всі** - select to **MATCH set**/**subset** all record:
    ```
    (0(0(0((C> all
    (93(93(93((C>
    ```
  - **show**|**покажи**|**показати**|**дивись**|**дивися**|**дивитись**|**дивитися** - select records to **MATCH set** and print them page by page.
  Selection can be made by
    - name,
    - part of name,
    - phone number,
    - part of phone number.
  - **search**|**see**|**шукати**|**шукай**|**пошук**|**знайти**|**знайди** - select records in **MATCH set** to **MATCH subset** by simple regular expression with metasymbols like it is for files
    - '\*' matches any zero or more characters,
    - '\?' matches any one character,
    - '[string]' matches exactly one character that is a member of the string 'string'.
    For example:
    ```
    (112(112(112((C> show лен
    #1 Name: Людмила Цибуленко
       Phone: 729-72-47
       Birthday: 08.07.1988 (+99 days left)

    #2 Name: Христина Вакуленко
       Phone: +38 037 907-94-48

    #3 Name: Мілена Щириця
       Phone: 086 446 24 04
       Phone: 008-39-47
       Phone: +38 037 222-69-92
    (112(3(3((C> search [29]?47
    #1 Name: Людмила Цибуленко
       Phone: 729-72-47
       Birthday: 08.07.1988 (+99 days left)

    #3 Name: Мілена Щириця
       Phone: 086 446 24 04
       Phone: 008-39-47
       Phone: +38 037 222-69-92
    (112(3(2((C> 
    ```
    **MATCH set** defines numbering of records in form "**\#\<num\>**". It is convinient to use numbering in the **search** regular expression. For example,
    ```
    (112(3(2((C> search #3
    #3 Name: Мілена Щириця
       Phone: 086 446 24 04
       Phone: 008-39-47
       Phone: +38 037 222-69-92
    (112(3(1((C> 
    ```
  - **add**|**додати**|**додай** - add to address book new record or field:
    ```
    (93(93(93((C> add Мар'яна Архипівна Вандер-Вілька
    (94(94(1((@> show
    #94 Name: Мар'яна Архипівна Вандер-Вілька
    (94(94(1((@> add phone +38 (099) 730-99-90
    (94(94(1((@> show
    #94 Name: Мар'яна Архипівна Вандер-Вілька
        Phone: +38 (099) 730-99-90
    (94(94(1((@>
    ```
    Name can be up to 3 words with "'" and "-" symbols.

    There exists the following fields:
      - **phone**: phone number, for example, 11-351, +380(050) 123-77-11, 12121212121. Any record can have some **phone** fields or none.
      - **address**: any string without requirements. Any record can have some **phone** fields or none.
      - **birthday**: birthday in format DD.MM.YY or DDD.MM.YYYYY. If it is present the days that left to near birthday will be displayed in output. Field can be absent or present not more than 1 time.  
      - **comment**: any string without requirements. Any record can have some **phone** fields or none.
    - **delete**|**видалити** - deletes all records in **MATCH subset** or fields within these records. For example:
    Delete  **MATCH set** records:
    ```
    (94(94(1((C> del
    (93(93(93((@>
    ```
    Delete record in **MATCH set** with name "Мар'яна":
    ```
    (112(112(112((@> Додати Мар'яна Архипівна Вандер-Вілька
    (113(113(1((@> add Вандер-Вілька Мар'яна
    (114(114(1((@> sh Вандер
    #1 Name: Мар'яна Архипівна Вандер-Вілька

    #2 Name: Вандер-Вілька Мар'яна
    (114(2(2((@> del Архипів
    (113(1(1((@> sh
    #1 Name: Вандер-Вілька Мар'яна
    (113(1(1((@> 
    ```
    To delete not first field in record can be used number in the end of field name. So, to delete 2nd field "Phone" can be used command "del phone2":
    ```
    (112(112(112((C> sh Ром
    #1 Name: Роман Голик
       Phone: 034 962-24-35
       Address: провулок Спортивний, буд. 18 кв. 55, Шепетівка, 05681

    #2 Name: Софія Романчук
       Phone: 054 164 46 43
       Phone: 081 520 27 37
       Phone: 013 877-51-53
       Address: площа Окружна, буд. 32, Почаїв, 68326
    (112(2(2((C> del phone2
    (112(2(2((@> sh
    #1 Name: Роман Голик
       Phone: 034 962-24-35
       Address: провулок Спортивний, буд. 18 кв. 55, Шепетівка, 05681

    #2 Name: Софія Романчук
       Phone: 054 164 46 43
       Phone: 013 877-51-53
       Address: площа Окружна, буд. 32, Почаїв, 68326
    (112(2(2((@> 
    ```
  - **change**|**змінити** - changes record name or field. **MATCH subset** must contain only one record to rename it:
    ```
    (112(112(112((C> sh Софія Романчук
    #1 Name: Софія Романчук
       Phone: 054 164 46 43
       Phone: 013 877-51-53
       Address: площа Окружна, буд. 32, Почаїв, 68326
    (112(1(1((C> change Соломія Романчук
    (112(1(1((@> sh
    #1 Name: Соломія Романчук
       Phone: 054 164 46 43
       Phone: 013 877-51-53
       Address: площа Окружна, буд. 32, Почаїв, 68326
    (112(1(1((@> 
    ```
    It is possible to change fields within many records in **MATCH subset**.
    
    To change not first field in record can be used number in the end of field name. So, to change 2nd field "Phone" can be used command "change phone2":
    ```
    (112(2(2((C> sh лен
    #1 Name: Людмила Цибуленко
       Phone: 729-72-47
       Birthday: 08.07.1988 (+99 days left)

    #2 Name: Христина Вакуленко
       Phone: +38 037 907-94-48

    #3 Name: Мілена Щириця
       Phone: 086 446 24 04
       Phone: 008-39-47
       Phone: +38 037 222-69-92
    (112(3(3((C> change phone2 (096) 777-77-777
    (112(3(3((@> sh
    #1 Name: Людмила Цибуленко
       Phone: 729-72-47
       Birthday: 08.07.1988 (+99 days left)

    #2 Name: Христина Вакуленко
       Phone: +38 037 907-94-48

    #3 Name: Мілена Щириця
       Phone: 086 446 24 04
       Phone: (096) 777-77-777
       Phone: +38 037 222-69-92
    (112(3(3((@> 
    ```
  - **\?**|**help**|**допоможи**|**допомога** - prints short instruction
  - **.**|**exit**|**quit**|**bye**|**вийди**|**вийти**|**вихід** - save modifications and exit from application
  - **CTRL+C** - exit from program without saving modification
