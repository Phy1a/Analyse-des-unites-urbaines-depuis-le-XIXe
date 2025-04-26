dep_dico2 = { # only Corsica, code on the used website for GET requests
                "2A" : "84", "2B" : "92"
                }

for year in range(1931,1875,-5):
    for dep in dep_dico2:
        print(dep, dep_dico2[dep])