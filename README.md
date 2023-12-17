# hebrew_search_pg
using pgvector to have knn search over a medium-large dataset

you will need to install both postgress and pgvector.


# notes
most systems have the postgres username as postgres if it is diffrent in your system replace it (including the install and uninstall files).
# setup

starting postgress 

'''bash
pg_ctl start
'''

making the db
'''bash 
createdb -h localhost -U postgres hebrew_document_search
'''

'''bash 
python setup.py
'''

# uninstall 
droping the db
'''bash 
dropdb -h localhost -U postgres hebrew_document_search
'''
