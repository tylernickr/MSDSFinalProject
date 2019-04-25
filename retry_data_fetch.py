import pymysql

if __name__ == '__main__':
    attempted = []
    for line in open('1000_repositories.txt', 'r'):
        attempted.append(line[:-1])
    print(attempted)
    print(len(attempted))

    db = pymysql.connect("localhost", "nick", "00Tracker.", "github")
    c = db.cursor()
    c.execute('select distinct projectID from commit')

    successful = []
    for row in c.fetchall():
        successful.append(row[0].strip().replace('#####', '/'))
    print(successful)
    print(len(successful))

    not_in = [x for x in attempted if x not in successful]

    with open("retry_repos.txt", 'w') as new_file:
        for repo in not_in:
            print(repo, file=new_file)
            