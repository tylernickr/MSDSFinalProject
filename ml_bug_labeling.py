import pymysql
import re
import numpy as np
from subprocess import run
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.svm import SVC


def clean_message(txt):
    txt = txt.lower()
    txt = re.sub('[^0-9a-zA-Z]+', ' ', txt)
    return txt


def label_actual_commits(model, db, word_index_list):
    c = db.cursor()
    c.execute('select c.hash, c.subject from commit c left join commit_bug_labels l on c.hash = l.hash where l.isBug is null limit 5000')
    results = [(x[0], x[1]) for x in c.fetchall()]
    while len(results) > 0:
        hashes = [x[0] for x in results]
        messages = [clean_message(x[1]) for x in results]
        tokenized_messages = [word_tokenize(x) for x in messages]
        tokenized_messages = [[y for y in x if y not in stopwords] for x in tokenized_messages]

        wc_vectors = []
        for message in tokenized_messages:
            word_counts = {}
            for word in message:
                try:
                    word_counts[word] += 1
                except KeyError:
                    word_counts[word] = 1

            word_count_vector = []
            for word in word_index_list:
                try:
                    word_count_vector.append(word_counts[word])
                except KeyError:
                    word_count_vector.append(0)

            wc_vectors.append(np.array(word_count_vector))
        print(len(wc_vectors))
        wc_vectors = np.array(wc_vectors)
        print("Predicting...")
        predictions = ["y" if x == 1 else "n" for x in model.predict(wc_vectors)]
        print("Finished Predictions")

        with open("commit_bug_labels.dat", "w") as upload_file:
            for i in range(0, len(predictions)):
                print(hashes[i] + "\t" + predictions[i], file=upload_file)
            run(['mysqlimport', '-u' + 'nick', '-p' + '', '--local', 'github', 'commit_bug_labels.dat'])
        run(['rm', 'commit_bug_labels.dat'])

        c.execute('select c.hash, c.subject from commit c left join commit_bug_labels l on c.hash = l.hash where l.isBug is null limit 5000')
        results = [(x[0], x[1]) for x in c.fetchall()]



def run_x_validation(raw_data, folds):
    overall_predictions = []
    overall_labels = []

    fold_size = round(len(raw_data) / folds)
    for i in range(0, folds):
        labels = [x[0] for x in raw_data]
        messages = [clean_message(x[1]) for x in raw_data]
        tokenized_messages = [word_tokenize(x) for x in messages]
        tokenized_messages = [[y for y in x if y not in stopwords] for x in tokenized_messages]

        test_start_index = fold_size * i
        test_end_index = fold_size * (i + 1)

        training_messages = tokenized_messages[:test_start_index] + tokenized_messages[test_end_index:]
        test_messages = tokenized_messages[test_start_index:test_end_index]

        training_labels = labels[:test_start_index] + labels[test_end_index:]
        test_labels = labels[test_start_index:test_end_index]

        training_wc_vectors = []
        word_index_list = []
        for message in training_messages:
            for word in message:
                if word not in word_index_list:
                    word_index_list.append(word)

        for message in training_messages:
            word_counts = {}
            for word in message:
                try:
                    word_counts[word] += 1
                except KeyError:
                    word_counts[word] = 1

            word_count_vector = []
            for word in word_index_list:
                try:
                    word_count_vector.append(word_counts[word])
                except KeyError:
                    word_count_vector.append(0)

            training_wc_vectors.append(np.array(word_count_vector))
        training_wc_vectors = np.array(training_wc_vectors)

        test_wc_vectors = []
        for message in test_messages:
            word_counts = {}
            for word in message:
                try:
                    word_counts[word] += 1
                except KeyError:
                    word_counts[word] = 1

            word_count_vector = []
            for word in word_index_list:
                try:
                    word_count_vector.append(word_counts[word])
                except KeyError:
                    word_count_vector.append(0)

            test_wc_vectors.append(np.array(word_count_vector))
        test_wc_vectors = np.array(test_wc_vectors)

        clf = SVC(gamma='scale')
        clf.fit(training_wc_vectors, training_labels)
        predictions = clf.predict(test_wc_vectors)
        overall_predictions = np.concatenate((overall_predictions, predictions), 0)
        overall_labels = np.concatenate((overall_labels, test_labels), 0)
        print("Done with fold: " + str(i))

    results_matrix = np.array([[0, 0], [0, 0]])
    for i in range(0, len(overall_predictions)):
        predicted = int(overall_predictions[i])
        actual = int(overall_labels[i])

        results_matrix[predicted, actual] += 1

    clf = SVC(gamma='scale')
    all_wc_vectors = np.concatenate((training_wc_vectors, test_wc_vectors), 0)
    all_labels = np.concatenate((training_labels, test_labels))
    clf.fit(all_wc_vectors, all_labels)

    return results_matrix, clf, word_index_list


if __name__ == '__main__':
    stopwords = set(stopwords.words('english'))

    db = pymysql.connect("localhost", "nick", "", "github")
    i = 0
    c = db.cursor()
    c.execute('select b.isBug, c.subject from bug_labels b join commit c on b.hash = c.hash')
    raw_data = c.fetchall()
    c.close()
    raw_data = [(1 if x[0] == "y" else 0, x[1]) for x in raw_data]

    results, model, word_index_list = run_x_validation(raw_data, 10)
    confusion_matrix = results / results.sum(0)
    print("\t\t\tActual")
    print("Predicted\tNot Bug\t Bug")
    print("Not Bug\t\t" + str(round(confusion_matrix[0, 0], 2)) + "\t" + str(round(confusion_matrix[0, 1], 2)))
    print("Bug\t\t\t" + str(round(confusion_matrix[1, 0], 2)) + "\t" + str(round(confusion_matrix[1, 1], 2)))

    label_actual_commits(model, db, word_index_list)