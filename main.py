import ast


with open("sample.py", "r") as file:
    code = file.read()

tree = ast.parse(code)

#print(tree)

print(ast.dump(tree, indent=4))