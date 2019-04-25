from os import walk, path, mkdir
from subprocess import run
from codecs import open
from sys import argv, exit

COMMIT_DATA_DIR = 'commit_data/'
MOD_FILES_DIR = 'modified_files_data/'
DB_FILES_ROOT = 'db_files/'

if __name__ == '__main__':
    arg1 = argv[1]
    arg2 = argv[2]

    if not path.exists(DB_FILES_ROOT):
        mkdir(DB_FILES_ROOT)

    with open(DB_FILES_ROOT + 'project.dat', 'w') as project_file:
        with open(DB_FILES_ROOT + 'github_user.dat', 'w') as user_file:
            with open(DB_FILES_ROOT + 'commit.dat', 'w') as commit_file:
                for root, dir, files in walk(COMMIT_DATA_DIR):
                    for file in files:
                        fileparts = file.split('#####')
                        name = fileparts[1].split('.csv')[0]
                        id = file.split('.csv')[0]
                        print(id + '\t' + name, file=project_file)
                        print(root + '/' + file)
                        for line in open(root + '/' + file, "r", encoding='utf-8', errors="ignore"):
                            try:
                                fields = line[:-1].split(",|,")
                                hash = fields[0]
                                authorName = fields[1]
                                authorEmail = fields[2]
                                authorTime = fields[3]
                                committerName = fields[4]
                                committerEmail = fields[5]
                                committerTime = fields[6]
                                subject = fields[7]
                            except IndexError:
                                print(line)
                            print('\t'.join([authorEmail, authorName]), file=user_file)
                            print('\t'.join([committerEmail, committerName]), file=user_file)
                            print('\t'.join([hash, id, authorEmail, authorTime, committerEmail, committerTime, subject]), file=commit_file)

    with open(DB_FILES_ROOT + 'file_modification.dat', 'w') as mod_file:
        for root, dir, files in walk(MOD_FILES_DIR):
            for file in files:
                for line in open(root + '/' + file):
                    fields = line[:-1].split(',,')
                    hash = fields[0]
                    added = fields[1]
                    deleted = fields[2]
                    filename = fields[3]
                    print('\t'.join([hash, filename, added, deleted]), file=mod_file)

    run(['mysqlimport', '-u' + arg1, '-p' + arg2, '--local', 'github', DB_FILES_ROOT + 'project.dat'])
    run(['mysqlimport', '-u' + arg1, '-p' + arg2, '--local', 'github', DB_FILES_ROOT + 'github_user.dat'])
    run(['mysqlimport', '-u' + arg1, '-p' + arg2, '--local', 'github', DB_FILES_ROOT + 'commit.dat'])
    run(['mysqlimport', '-u' + arg1, '-p' + arg2, '--local', 'github', DB_FILES_ROOT + 'file_modification.dat'])
