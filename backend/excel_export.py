import pandas as pd

def export_logs_to_excel(logs):
    data = [{"UID": log.uid, "Action": log.action, "Date": log.date, "Time": log.time} for log in logs]
    df = pd.DataFrame(data)
    output = df.to_excel(index=False, engine='openpyxl')
    return output
