# total = 0
# for i in range(5):
#     total = total + i
# print(total)

name = input("Enter your name: ")
age = int(input("Enter your age: "))

if age >= 18:
    status = "Adult"
else:
    status = "Minor"

print(f"Hello {name}")
