from mignonFramework import MicroServiceByNodeJS


service =  MicroServiceByNodeJS(True)


@service.evalJS("test")
def helloT(a, b):
    return ""


print(helloT(1, 2))