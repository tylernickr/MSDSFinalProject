import pymysql
from decimal import Decimal
from subprocess import run
from math import log2

if __name__ == '__main__':

    db = pymysql.connect("localhost", "nick", "", "github")
    c = db.cursor()
    c.execute('select id from project p left join project_languages l on p.id = l.projectID where l.projectID is null limit 1')
    results = c.fetchall()
    c.close()
    while len(results) > 0:
        projectid = results[0][0]
        print(projectid)
        sql = 'select SUBSTRING_INDEX(file,\'.\',-1), count(distinct file) ' \
              'from commit c join file_modification f ' \
              'on c.hash = f.hash ' \
              'where projectID = \'' + projectid + '\' ' \
              'group by 1 order by 2 desc limit 1'
        c = db.cursor()
        c.execute(sql)
        query_res = c.fetchall()
        c.close()

        try:
            project_language = query_res[0][0]
        except:
            project_language = ''

        with open('project_languages.dat', 'w') as languages_file:
            print(projectid + ": " + str(project_language))
            print(projectid + "\t" + str(project_language), file=languages_file)

        run(['mysqlimport', '-u' + 'nick', '-p' + '', '--local', 'github', 'project_languages.dat'])
        run(['rm', 'project_languages.dat'])

        sql = 'select id ' \
              'from project p left join project_languages l ' \
              'on p.id = l.projectID ' \
              'where l.projectID is null limit 1'
        c = db.cursor()
        c.execute(sql)
        results = c.fetchall()
        c.close()
