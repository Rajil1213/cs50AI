import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])

    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []
    # for converting months (strings) to corresponding ints 
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_num = enumerate(months)
    month = {k: v for v, k in month_num}

    with open(filename, "r") as raw:

        # returns an OrderedDict object for iterating
        reader = csv.DictReader(raw)
        for each_row in reader:
            
            # initializing an empty list and
            # append values to it after typecasting
            row = []
            row.append(int(each_row["Administrative"]))
            row.append(float(each_row["Administrative_Duration"]))
            row.append(int(each_row["Informational"]))
            row.append(float(each_row["Informational_Duration"]))
            row.append(int(each_row["ProductRelated"]))
            row.append(float(each_row["ProductRelated_Duration"]))
            row.append(float(each_row["BounceRates"]))
            row.append(float(each_row["ExitRates"]))
            row.append(float(each_row["PageValues"]))
            row.append(float(each_row["SpecialDay"]))
            row.append(int(month[each_row["Month"]]))
            row.append(int(each_row["OperatingSystems"]))
            row.append(int(each_row["Browser"]))
            row.append(int(each_row["Region"]))
            row.append(int(each_row["TrafficType"]))
            row.append(int(each_row["VisitorType"] == 'Returning_Visitor'))
            row.append(int(each_row["Weekend"] == 'TRUE'))
            evidence.append(row)
            
            # append the corresponding label
            labels.append(int(each_row["Revenue"] == 'TRUE'))

    return evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    
    # sklearn's K-Nearest Neighbor Classifier
    # considering 1 neighbor and then, training (fit-ing)
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    
    # total test set size
    size = len(labels)
    # total negative examples
    negatives = 0
    # total positive examples
    positives = 0
    # no. of positives identified as positives
    true_positives = 0
    # no. of negatives identified as negatives
    true_negatives = 0

    for i in range(size):

        if labels[i] == 0:
            negatives += 1
            if labels[i] == predictions[i]:
                true_negatives += 1
        else:
            positives += 1
            if labels[i] == predictions[i]:
                true_positives += 1

    # True Positive Rate        
    sensitivity = true_positives / positives

    # True Negative Rate
    specificity = true_negatives / negatives    
    
    return sensitivity, specificity


if __name__ == "__main__":
    main()
