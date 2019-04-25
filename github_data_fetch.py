from subprocess import run
from os import getcwd, path, chdir, mkdir
from contextlib import contextmanager
from sys import argv

GIT_ROOT = 'https://github.com/'
CLONE_ROOT = 'clones/'
COMMIT_DATA_DIR = 'commit_data/'
MOD_FILES_ROOT = 'modified_files_data/'

@contextmanager
def cd(newdir):
    # Credit cdunn2001 stackoverflow.com
    prevdir = getcwd()
    chdir(path.expanduser(newdir))
    try:
        yield
    finally:
        chdir(prevdir)


def cloneProject(repoOwner, project):
    gitURL = GIT_ROOT + repoOwner + '/' + project + '.git'
    cloneDir = CLONE_ROOT + project
    run(['git', 'clone', gitURL, cloneDir])


def cleanupProject(project):
    cloneDir = CLONE_ROOT + project
    run(['rm', '-rf', cloneDir])


def getCommitMetadata(repoOwner, project):
    cloneDir = CLONE_ROOT + project
    with open(COMMIT_DATA_DIR + repoOwner + '#####' + project + '.csv', 'w') as ouputFile:
        with cd(cloneDir):
            run(['git', 'log', '--pretty=format:%H,|,%an,|,%ae,|,%ad,|,%cn,|,%ce,|,%ct,|,%s'], stdout=ouputFile)


def getModifiedFiles(project):
    cloneDir = CLONE_ROOT + project
    with open(MOD_FILES_ROOT + project + '.csv', 'w') as outputFile:
        with cd(cloneDir):
            with open('temporary.f', 'w') as tmpFile:
                run(['git', 'log', '--pretty=format:🐱%n%H', '--numstat'], stdout=tmpFile)
            for line in open('temporary.f'):
                line = line[:-1]
                if line == '🐱':
                    commithash = ''
                elif line.strip() == '':
                    continue
                elif commithash == '':
                    commithash = line
                else:
                    added, deleted, modpath = line.split(maxsplit=2)
                    print(commithash + ',,' + str(added) + ',,' + str(deleted) + ',,' + modpath, file=outputFile)


def processProject(repo_owner, project):
    print('Repo Owner: ' + repo_owner + '; Project: ' + project)
    cloneProject(repo_owner, project)
    try:
        getCommitMetadata(repoOwner, project)
        getModifiedFiles(project)
        cleanupProject(project)
    except:
        retry_list.append((repo_owner, project))
        cleanupProject(project)


if __name__ == '__main__':
    repo_list = argv[1]
    projects = []
    retry_list = []
    run(['rm', '-rf', CLONE_ROOT])
    mkdir(CLONE_ROOT)
    run(['rm', '-rf', COMMIT_DATA_DIR])
    mkdir(COMMIT_DATA_DIR)
    run(['rm', '-rf', MOD_FILES_ROOT])
    mkdir(MOD_FILES_ROOT)
    for line in open(repo_list):
        repoOwner, project = line[:-1].split('/')
        projects.append((repoOwner, project))

        processProject(repoOwner, project)

    for repoOwner, project in list(retry_list):
        processProject(repoOwner, project)

