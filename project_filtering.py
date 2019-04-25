import pymysql

if __name__ == '__main__':
    db = pymysql.connect("localhost", "nick", "", "github")

    # # REMOVE common non-code document types from the database
    excluded_file_types = ['.md}',
                           '.doc',
                           '.docx',
                           '.odt',
                           '.pdf',
                           '.txt',
                           '.md',
                           '.csv',
                           '.dat',
                           '.log',
                           '.ppt',
                           '.xls',
                           '.xlsx',
                           '.rtf',
                           '."',
                           '.conf',
                           '.gif',
                           '.gitignore',
                           '.ini',
                           '.jpg',
                           '.json',
                           '.markdown',
                           '.md"',
                           '.mdown',
                           '.pdf"',
                           '.pdf}',
                           '.png',
                           '.png"',
                           '.properties',
                           '.txt}',
                           '.jpeg',
                           '.jpg"',
                           '.png}',
                           '.svg',
                           '.test',
                           '.tex',
                           '.ttf',
                           '.xml',
                           '.yml']

    for file_type in excluded_file_types:
        c = db.cursor()
        print("Deleting: " + file_type)
        sql = 'delete from file_modification where lower(file) like \'%' + file_type + '\''
        c.execute(sql)
        c.fetchall()
        print("Finished: " + file_type)


    # # REMOVE projects with less than 50 distinct files
    c = db.cursor()
    sql = 'select c.projectID, count(distinct m.file) ' \
          'from commit c join file_modification m ' \
          'on c.hash = m.hash group by c.projectID ' \
          'having count(distinct m.file) < 50'
    c.execute(sql)
    projects = [x[0] for x in c.fetchall()]

    for project in projects:
        sql = 'delete m from file_modification m join commit c ' \
              'on m.hash = c.hash ' \
              'where c.projectID = \'' + project + '\''
        print("Deleting: " + project)
        c.execute(sql)
        print("Finished")

    # CLEANUP other tables
    c = db.cursor()
    sql = 'delete c ' \
          'from commit c left join file_modification m ' \
          'on c.hash = m.hash ' \
          'where m.hash is null'
    c.execute(sql)
    c.fetchall()

    c = db.cursor()
    sql = 'delete p ' \
          'from project p left join commit c ' \
          'on p.id = c.projectID ' \
          'where c.hash is null'
    c.execute(sql)
    c.fetchall()

