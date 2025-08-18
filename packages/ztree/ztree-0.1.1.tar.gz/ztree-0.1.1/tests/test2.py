import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import zipfile
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import roc_auc_score
from ztree.tree import ZTree
from ztree.jvm_manager import stop_jvm


# test for regression
'''
csv_path = r"C:\\Users\\ericr\\Downloads\\bike sharing hour.csv"
datafile = pd.read_csv(csv_path, skiprows=1)
col_names = ["instant", "dteday", "season", "year", "month", "hour", "holiday", "weekday",
             "workday", "weathersit", "temp", "atemp", "humidity", "windspeed",
             "casual", "registered", "count"]
datafile.columns = col_names
label_cols = ["season", "month", "hour", "weekday", "weathersit"]
le_dict = {}
for col in label_cols:
    le = LabelEncoder()
    datafile[col] = le.fit_transform(datafile[col])
    le_dict[col] = le
datafile = datafile.drop(columns=["instant", "casual", "registered", "dteday"])
col_names.remove("instant")
col_names.remove("casual")
col_names.remove("registered")
col_names.remove("dteday")
X = datafile.drop(columns=["count"])
col_names = list(X.columns)
y = datafile["count"]
X = X.values
y = y.values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.83, random_state=42)
dt = ZTree(feature_names=col_names)
dt.fit_optimal(X_train, y_train)
y_pred = dt.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print("RMSE:", rmse)
'''

# test for classification
'''
zip_path = "C:/Users/ericr/Downloads/adult.zip"
with zipfile.ZipFile(zip_path, 'r') as z:
    with z.open("adult.data") as f1:
        df1 = pd.read_csv(f1, header=None, sep=",", skipinitialspace=True)
    with z.open("adult.test") as f2:
        df2 = pd.read_csv(f2, header=None, sep=",", skipinitialspace=True, skiprows=1)
datafile = pd.concat([df1, df2], ignore_index=True)
col_names = ["age", "workclass", "fnlwgt", "education", "education-num", "marital-status", "occupation", "relationship",
             "race", "sex", "capital-gain", "capital-loss",  "hours-per-week", "native-country", "income"]
datafile.columns = col_names
datafile['income'] = datafile['income'].apply(lambda x: 1 if x in {'>50K', '>50K.'} else 0)
datafile = datafile.drop(columns=["fnlwgt"])
col_names.remove("fnlwgt")
#categorical_cols = datafile.select_dtypes(include=['object', 'category']).columns
#datafile = pd.get_dummies(datafile, columns=categorical_cols, drop_first=True, dummy_na=True)
X = datafile.drop(columns=["income"])
for col in X.select_dtypes(include=['object', 'category']).columns:
    X[col] = X[col].astype(str)  # Force all categorical columns to string
col_names = list(X.columns)
y = datafile["income"]
X = X.values
y = y.values
y = y.astype("int64")

def read_indices(file, X, y):
    data = []
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                indices = list(map(int, line.split('\t')))
                features = X[indices]
                labels = y[indices]
                data.append(np.column_stack((features, labels)))
    return data

def test_output(training_file, testing_file, X, y):
    train_data = read_indices(training_file, X, y)
    test_data = read_indices(testing_file, X, y)
    for i, (train, test) in enumerate(zip(train_data, test_data)):
        X_train = train[:, :-1]
        y_train = train[:, -1]
        y_train = y_train.astype(int)
        X_test = test[:, :-1]
        y_test = test[:, -1]
        y_test = y_test.astype(int)
        dt = ZTree(feature_names=col_names)
        z = dt.search_optimal_z_thresh(X_train, y_train)
        print(z)
        dt.fit_optimal(X_train, y_train)
        y_pred = dt.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_pred)
        print(f"{auc:.6f}")
        break

training_file0 = "C:/Users/ericr/Documents/train_data3000.txt"
testing_file0 = "C:/Users/ericr/Documents/test_data3000.txt"

test_output(training_file0, testing_file0, X, y)

stop_jvm()
'''