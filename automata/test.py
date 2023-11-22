import httpx
from selectolax.parser import HTMLParser
from icecream import ic
from pydantic import BaseModel
from rich.table import Table
from rich.console import Console


student_num = int(input("input student name: "))


cookies = {
    "cal_getYearsTree": "%5B0%2C%5B0%2C0%2C0%2C0%5D%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%5D%7C20222",
    "c_cal_periodGroupCode": "COURSES",
    "act_accountTree": "%5B0%2C0%2C0%2C0%5D%7Cundefined",
    "c_rpt_selectedSemester": "ALL",
    "WPU_lang": "ar",
    "c_act_ledger_accountId": "519.115",
    "c_act_ledger_currencyId": "284",
    "c_act_ledger_lastMatching": "N",
    "PHPSESSID": "6rjf7n78sn4c6kusqo7v310s3g",
}

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "Referer": "http://edu/RAS/?sc=434",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

###############################################

payload_get_student_id = {
    "cmd": "getStudentsAutocomplete",
    "q": student_num,
    "limit": "20",
}

res = httpx.post(
    "http://edu/RAS/app/_fin/sta/views/scripts/_sta_global_ajax.php",
    headers=headers,
    cookies=cookies,
    data=payload_get_student_id,
)

student_id = res.json()["data"][0]["STUDENT_ID"]
student_name = res.json()["data"][0]["STUDENT_NAME_SL"]

#####################################################

payload_set_id = {
    "cmd": "setStudentId",
    "studentId": student_id,
}


res = httpx.post(
    "http://edu/RAS/app/_FIN/STA/views/scripts/_sta_global_ajax.php",
    headers=headers,
    cookies=cookies,
    data=payload_set_id,
)

#####################################################

payload_get_transactions = {
    "cmd": "getAjaxPage",
    "page": "student_account_transactions.php",
}

res = httpx.post(
    "http://edu/RAS/app/gen/php/ajax_content.php?",
    headers=headers,
    cookies=cookies,
    data=payload_get_transactions,
)

#######################################

parser = HTMLParser(res.content)
table = parser.css_first("table#student_transactions > tbody")
rows = table.css("tr")


class Transaction(BaseModel):
    debit: int
    credit: int
    balance: int
    activedate: str
    semester: str


transactions = []

for row in rows:
    cells = row.css("td.txtC span")
    for cell in cells:
        transaction = Transaction(**cell.attributes).model_dump()
        transactions.append(transaction)

console = Console()
table = Table(title=f"Student Transactions {student_name}", show_lines=True)
headers = list(transactions[0].keys())

[table.add_column(header, justify="center", max_width=30) for header in headers]

for trans in transactions:
    row = [f"{cell}" if type(cell) != int else f"{cell:,}" for cell in trans.values()]
    table.add_row(*row)

console.print(table)
