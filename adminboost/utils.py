
def import_from_string(path):
    """
    Utility function to dynamically load a class specified by a string,
    e.g. 'path.to.my.Class'.
    """
    module_name, klass = path.rsplit('.', 1)
    module = __import__(module_name, fromlist=[klass])
    return getattr(module, klass)