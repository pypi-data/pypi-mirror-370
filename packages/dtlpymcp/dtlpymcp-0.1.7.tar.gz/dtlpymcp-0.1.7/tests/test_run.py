from dtlpymcp.proxy import main
import dtlpy as dl
import os
dl.setenv('rc')
if dl.token_expired():
    dl.login()
os.environ["DATALOOP_API_KEY"] = dl.token()
main()







