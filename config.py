#done
import os

apphost = "resident.cwek9hx2daym.us-east-1.rds.amazonaws.com"
appuser = "admin"
apppass = "adminadmin"
appdb = "resident"
awsbucket = "addresident01"
awsregion ="us-east-1"
adminusername= os.environ.get('adminpassword') or "admin"
adminpassword= os.environ.get('adminpassword')