import json

file_path = r"C:\Users\Cymonic\Desktop\Cymonic\HR_BOT\WorkMate\chunks+metadata\leave_policy_3.json"

updated_answer = (
     "Employees are entitled to the following types of leave:\n\n"
     "• Privilege Leave (PL): 18 days per year\n"
     "• Casual Leave (CL): 12 days per year\n"
     "• Sick Leave (SL): 12 days per year\n"
     "• Maternity Leave: 26 weeks\n"
     "• Paternity Leave: 10 working days\n"
     "• Sabbatical Leave: Up to 1 year\n"
     "• Festival & National Holidays: 10 days\n"
     "• Unpaid Leave (LWP): As approved"
 )

with open(file_path, "r", encoding="utf-8") as f:
     chunk = json.load(f)

chunk["answer"] = updated_answer

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(chunk, f, indent=4, ensure_ascii=False)

print("✅ leave_policy_3.json updated successfully")

import json

file_path = r"C:\Users\Cymonic\Desktop\Cymonic\HR_BOT\WorkMate\chunks+metadata\reimbursement_policy_23.json"

updated_answer = (
    "Employees may claim reimbursement for the following expense categories:\n\n"
    "• Travel (Local Conveyance): ₹3,000 per month\n"
    "• Travel (Outstation – Bus/Train): Actuals (Economy class)\n"
    "• Travel (Flight): Actuals (Economy class, prior approval required)\n"
    "• Food & Meals: ₹500 per day\n"
    "• Accommodation: ₹2,500 per night\n"
    "• Mobile / Internet: ₹1,000 per month\n"
    "• Client Entertainment: ₹3,000 per event\n"
    "• Office Supplies: Actuals (approval required)\n"
    "• Training & Certification: Actuals (HR approval required)"
)

with open(file_path, "r", encoding="utf-8") as f:
    chunk = json.load(f)

chunk["answer"] = updated_answer

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(chunk, f, indent=4, ensure_ascii=False)

print("✅ reimbursement_policy_23.json updated successfully")
