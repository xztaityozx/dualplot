import dual
import sys
import pulp

print("please input primal problem")
pp = "".join(sys.stdin.readlines())
DEBUG = True


def debug(obj):
    if not DEBUG:
        return

    src = str(obj)
    sys.stderr.write("\u001b[32mdebug:\u001b[39m")
    for line in src.splitlines():
        sys.stderr.write("\t"+line)
        sys.stderr.write("\n")

    sys.stderr.flush()


def tryParseInt(s: str):
    try:
        int(s)
        return True
    except ValueError:
        return False


def parseVariable(model: str):
    var = []
    for line in model.splitlines():
        for element in line.split():
            if tryParseInt(element):
                continue
            if any([element in ["+", "-", "<", ">", "<=", ">=", "="]]):
                continue
            var.append(element)

    # var = set(var)

    return var


model = dual.dual(pp)


model=model.replace("^T", "")
model=model.replace("I", "1")


debug(model)

var = parseVariable(model)
problem = pulp.LpProblem() if var.pop(
) == "min" else pulp.LpProblem(sense=pulp.LpMaximize)


debug(var)

lpVarList = {}
for v in var:
    if v == "max" or v == "min":
        continue
    lpVarList[v] = pulp.LpVariable(v, lowBound=0)

debug(lpVarList)

for line in model.splitlines():
    element = line.split()
    debug(element)
    if element[0] == "min" or element[0] == "max":
        upper = int(element[1]) * lpVarList[element[2]]
        lower = int(element[4]) * lpVarList[element[5]]
        problem += (upper + lower) if element[3] == "+" else (upper - lower)
    elif len(element) == 3:
        state = lpVarList[element[0]]
        if element[1] == "<":
            problem += state < int(element[2])
        elif element[1] == "<=":
            problem += state <= int(element[2])
        elif element[1] == ">":
            problem += state > int(element[2])
        else:
            problem += state >= int(element[2])
    else:
        upper = int(element[0]) * lpVarList[element[1]]
        lower = int(element[3]) * lpVarList[element[4]]
        state = (upper + lower) if element[2] == "+" else (upper - lower)
        if element[5] == "<":
            problem += state < int(element[6])
        elif element[5] == "<=":
            problem += state <= int(element[6])
        elif element[5] == ">":
            problem += state > int(element[6])
        else:
            problem += state >= int(element[6])


problem.solve()
for k in lpVarList:
    print(k, pulp.value(lpVarList[k]))
