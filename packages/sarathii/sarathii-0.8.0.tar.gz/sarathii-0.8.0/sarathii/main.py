def full_detail():
	def full_name():
		print("NAME:VIJAYASARATHI.A")
	def dob():
		print("DOB:02/MAY/2004")
	def age():
		from datetime import date
		birthyear=2004
		currentyear=date.today().year
		age=currentyear-birthyear
		print(f"AGE:{age}")
	def degree():
		print("DEGREE:B.TECH-AI&DS")
	def fan():
		print("THALAPATHY VIJAY")
