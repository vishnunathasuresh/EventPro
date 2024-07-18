# EventPro
---
![image](./assets/icon-square-rounded-border.png)
## Purpose and Scope

- The software is built on python and streamlit framework to serve the needs of easy and efficient conduction of School Youth Festivals in schools.
- The project is used to maintain and update an **sqlite database** to effectively keep record of the student list entered as a csv and use it for::

    - **Records of Participants**
    - **Preparation of Judgement Sheets**
    - **Judge Events and Tabulate Results**
    - **Generate Reports on Various Categories and Events**
    - **Generate a printable certificate file to enable digitalized Certificate Creation**
  

## Dependencies 
```
streamlit
streamlit-authenticator
streamlit-autorefresh
pandas
```
## Databases Schema
```
STUDENT (
    [ADMISSSION_NUMBER], 
    STUDENT_NAME,
    CLASS,
    DIVISION,
    HOUSE,
    CATEGORY,
)
```

```
PARTICIPANT (
    [ADMISSION_NUMBER, EVENT_NAME],
    JUDGE1,
    .
    .
    .
    TOTAL_MARKS,
    RANK, 
    GRADE,
    DISQUALIFIED,
    REMARKS
)
```
```
GRADE_MARKS (
    [GRADE], MIN_MARKS
)
```
```
CLASS_CATEGORY (
    [CLASS], CATEGORY
)
```
```
EVENT_NAME ([EVENT_NAME])
```

```
PARAMETER (
    DATABASENAME,
    MAX_MARKS_FOR_EACH_JUDGE,
    MIN_MARKS_FOR_PRIZE,
    TOTAL_MARKS,
    RESULTS_READY,
    MAXIMUM_EVENTS_FOR_PARTICIPANTS
)
```
## Execution
```
Run the start-server.bat file in the root directory.
```
or
```
streamlit run main.py
```

## Port Information

```
Port Number : 8501
```