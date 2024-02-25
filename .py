import os
def patch_path(path):
    path = os.path.normpath(path)
    path = path.replace("//","/")
    return path + "/"
print(patch_path("//dev/core"))
# random.randint()