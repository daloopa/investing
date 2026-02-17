---
title: Supported Calendar Period Formats
url: https://docs.daloopa.com/docs/supported-calendar-period-formats
path: /docs/supported-calendar-period-formats
---

# Supported Calendar Period Formats

# Supported Calendar Period Formats

## 

List of calendar period formats that excel addin supports:

**Notation:**

`X - number`

`Q - Q`

`FY - FY`

`| - or`

`Y - 1 digit of the year`

`E - estimate suffix`

`A - actual suffix`

`[ ] - optional element`

`( ) - required element`

* * *

**Supported:**

  * Any date format from Excel, CELL has to be formatted as a valid DATE type in excel
  * every date is subtracted by 45days and converted to the classic format
  * while using this type for calendar period format, FY is not supported, conversion only from Q1 to Q4



* * *

In all formats below; lowercase or uppercase doesn’t matter. Both are supported.

**Classic format:**

`2021Q1, 2021Q2, 2021Q3, 2021Q4, 2021FY`

`YYYYQX`

**Pattern 1**

`(XQ | FY | F)["-" | "'" | "_" |":" | whitespace](YY | YYYY)[whitespace]["E" | "A"]`

`(QX | FY | F)["-" | "'" | "_" |":" | whitespace](YY | YYYY)[whitespace]["E" | "A"]`

_Examples:_

`2Q22`

`2Q 22`

`2Q-22`

`2Q'22`

`2Q:22`

`2Q2022`

`2Q 2022`

`2Q-2022`

`2Q'2022`

`2Q:2022`

`2Q_2022`

`Q2 22`

`Q2-22`

`Q2'22`

`Q2:22`

`Q2_22`

`Q2 2022`

`Q2-2022`

`Q2'2022`

`Q2:2022`

`Q2_2022`

**Pattern 2**

`YY[whitespace]["E" | "A"]`

`YYYY[whitespace]["E" | "A"]`

`YYYY["-" | "'" | ":" | whitespace](QX | XQ | FY)[whitespace]["E" | "A"]`

`YY["-" | "'" | ":" | whitespace](QX | XQ | FY)[whitespace]["E" | "A"]`

_Examples:_

`22` converted to 2022FY

`2022` converted to 2022FY

`2022Q1`

`2022 Q1`

`2022-Q1`

`2022'Q1`

`2022:Q1`

`2022_Q1`

`22Q1`

`22 Q1`

`22-Q1`

`22'Q1`

`22:Q1`

`2022 1Q`

`2022-1Q`

`2022'1Q`

`2022:1Q`

`2022_1Q`

`22 1Q`

`22-1Q`

`22'1Q`

`22:1Q`

`22_1Q`

 __Updated 9 months ago

* * *

[Settings](/docs/settings)[Update your existing models](/docs/update-your-existing-models)

Ask AI

