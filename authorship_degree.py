import pymysql
from decimal import Decimal
from subprocess import run
from math import log2

if __name__ == '__main__':

    db = pymysql.connect("localhost", "nick", ".", "github")
    c = db.cursor()
    c.execute('select id from project p left join authorship_score a on p.id = a.projectID where a.authorshipScore is null limit 1')
    results = c.fetchall()
    while len(results) > 0:
        projectid = results[0][0]
        print(projectid)
        c.execute('select c.author, sum(f.added + f.deleted) from commit c join file_modification f on c.hash = f.hash where c.projectID = \'' + projectid + '\' group by c.author')
        author_changes = [x for x in c.fetchall() if x[1] != 0]
        total_changes = sum([x[1] for x in author_changes])

        probabilities = [x[1] / total_changes for x in author_changes]
        entropies = [x * Decimal(log2(x)) for x in probabilities]
        authorship_score = round(-1 * sum(entropies), 4)

        with open('authorship_score.dat', 'w') as author_file:
            print(projectid + ": " + str(authorship_score))
            print(projectid + "\t" + str(authorship_score), file=author_file)

        run(['mysqlimport', '-u' + 'nick', '-p' + '00Tracker.', '--local', 'github', 'authorship_score.dat'])
        run(['rm', 'authorship_score.dat'])

        c.execute('select id from project p left join authorship_score a on p.id = a.projectID where a.authorshipScore is null limit 1')
        results = c.fetchall()


