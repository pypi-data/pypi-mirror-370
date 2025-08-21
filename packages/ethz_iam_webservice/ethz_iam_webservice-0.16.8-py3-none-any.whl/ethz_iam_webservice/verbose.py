# display messages when in a interactive context (IPython or Jupyter)

VERBOSE = False

try:
    get_ipython() # noqa: F821
except Exception:
    VERBOSE = False
else:
    VERBOSE = True
