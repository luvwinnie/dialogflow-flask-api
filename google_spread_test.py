import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('asiaquest-intern-leow-3e0b0d31061a.json', scope)
gc = gspread.authorize(credentials)
worksheet = gc.open('weekly_report').sheet1
cell = worksheet.acell('E19') # or .cell(1, 2)

# wks.update_acell('A1', 'Hello World!')
print(cell.value)