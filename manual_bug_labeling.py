import pymysql
from subprocess import run
from random import choices
from string import digits, ascii_letters

if __name__ == '__main__':
    db = pymysql.connect("localhost", "nick", "", "github")
    i = 0
    while i < 10:
        c = db.cursor()
        hash40 = ''.join(choices(ascii_letters + digits, k=40))
        c.execute('SELECT hash, subject FROM commit ORDER BY rand() LIMIT 5')
        rows = [{'hash': x[0], 'message': x[1]} for x in c.fetchall()]
        with open('bug_labels.dat', 'w') as bcp_file:
            for row in rows:
                print(row['message'])
                response = input("bug?: ")
                if response.lower() == 'y':
                    response = 'y'
                else:
                    response = 'n'
                print(row['hash'] + '\t' + response + ',', file=bcp_file)

        run(['mysqlimport', '-u' + 'nick', '-p' + '', '--local', 'github', 'bug_labels.dat'])
        run(['rm', 'bug_labels.dat'])

        i += 1
