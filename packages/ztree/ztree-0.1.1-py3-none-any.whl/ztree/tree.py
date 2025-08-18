from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np
import pandas as pd
import jpype
from jpype import JClass
from .jvm_manager import start_jvm  

class ZTree(BaseEstimator, ClassifierMixin):

    def __init__(
        self,
        z_thresh=0.5,
        java_class="subway.PyZTree",
        mode=0,  # 0 = classification, 1 = regression
        feature_names=None
    ):
        start_jvm()
        self.z_thresh = z_thresh
        if not (0.0 <= z_thresh <= 3):
            raise ValueError("z_thresh must be between 0.0 and 3")
        self.java_class = java_class
        self.mode = mode
        self.tree = None
        self.feature_names = feature_names
        self.PyZTree = jpype.JClass(java_class)
        self.ArrayList = jpype.JClass("java.util.ArrayList")
        self.JIntArray = jpype.JArray(jpype.JInt)
        self.JFloatArray = jpype.JArray(jpype.JFloat)
        self.JBooleanArray = jpype.JArray(jpype.JBoolean)


    def fit(self, X, y):
        JStringArray = jpype.JArray(jpype.JString)
        JIntArray = jpype.JArray(jpype.JInt)
        JFloatArray = jpype.JArray(jpype.JFloat)

        if isinstance(y, (pd.Series, pd.DataFrame)):
            y = y.to_numpy().flatten()
        if y.dtype.kind in {'U', 'S', 'O'} or len(np.unique(y)) == 2:
            self.mode = 0 
        else:
            self.mode = 1

        if isinstance(X, pd.DataFrame) and self.feature_names is not None:
            self.feature_names = X.columns.tolist()
            X = X.to_numpy()
        elif self.feature_names is not None:
            pass 
        else:
            feature_names = [f"feat_{i}" for i in range(X.shape[1])]
        feature_names = self.feature_names
        feature_types = []
        for idx in range(len(feature_names)):
            col = X[:, idx]
            if isinstance(col[0], (int, float, np.integer, np.floating)):
                feature_types.append(1) 
            else:
                feature_types.append(-1)
        java_feature_names = JStringArray(feature_names)
        java_feature_types = JIntArray(feature_types)

        object_x = ZTree.numpy_to_jobject(X)

        y = y.astype(np.float32).tolist()
        java_y = JFloatArray(y)
        
        pytree = self.PyZTree(self.mode, 5, 10)
        tree = pytree.fit(java_feature_names, java_feature_types, object_x, java_y, self.z_thresh)
        self.tree = tree
        

    def predict(self, X, decision_threshold="argmax"):
        if self.tree is None:
           raise RuntimeError("Model is not trained. Call `.fit()` first.")
        Xj = ZTree.numpy_to_jobject(X)
        if self.mode == 0:
            proba = self.predict_proba(X) 
            if decision_threshold == "argmax" or decision_threshold is None:
                return np.argmax(proba, axis=1).astype(np.int32)
            else:
                thr = float(decision_threshold)
                return (proba[:, 1] >= thr).astype(np.int32)
        else:
            preds_java = self.tree.predict(Xj, self.z_thresh)
            return np.asarray(list(preds_java), dtype=np.float32)


    def predict_proba(self, X):
        if self.mode != 0:
            raise AttributeError("predict_proba is only available for classification tasks")
        if self.tree is None:
            raise RuntimeError("Model is not trained. Call `.fit()` first.")
        X = ZTree.numpy_to_jobject(X)
        probs_java = self.tree.predict(X, self.z_thresh)
        probs = np.array(list(probs_java), dtype=np.float32)
        return np.column_stack([1.0 - probs, probs])
    
    
    def search_optimal_z_thresh(self, X, y):
        JStringArray = jpype.JArray(jpype.JString)
        JIntArray = jpype.JArray(jpype.JInt)
        JFloatArray = jpype.JArray(jpype.JFloat)

        if isinstance(y, (pd.Series, pd.DataFrame)):
            y = y.to_numpy().flatten()
        if y.dtype.kind in {'U', 'S', 'O'} or len(np.unique(y)) == 2:
            self.mode = 0 
        else:
            self.mode = 1

        if isinstance(X, pd.DataFrame) and self.feature_names is not None:
            self.feature_names = X.columns.tolist()
            X = X.to_numpy()
        elif self.feature_names is not None:
            pass 
        else:
            feature_names = [f"feat_{i}" for i in range(X.shape[1])]
        feature_names = self.feature_names
        feature_types = []
        for idx in range(len(feature_names)):
            col = X[:, idx]
            if isinstance(col[0], (int, float, np.integer, np.floating)):
                feature_types.append(1) 
            else:
                feature_types.append(-1)
        java_feature_names = JStringArray(feature_names)
        java_feature_types = JIntArray(feature_types)

        object_x = ZTree.numpy_to_jobject(X)

        y = y.astype(np.float32).tolist()
        java_y = JFloatArray(y)

        pytree = self.PyZTree(self.mode, 5, 10)
        z = pytree.searchZ(java_feature_names, java_feature_types, object_x, java_y)
        return float(z)
    
    def fit_optimal(self, X, y):
        JStringArray = jpype.JArray(jpype.JString)
        JIntArray = jpype.JArray(jpype.JInt)
        JFloatArray = jpype.JArray(jpype.JFloat)

        if isinstance(y, (pd.Series, pd.DataFrame)):
            y = y.to_numpy().flatten()
        if y.dtype.kind in {'U', 'S', 'O'} or len(np.unique(y)) == 2:
            self.mode = 0 
        else:
            self.mode = 1

        if isinstance(X, pd.DataFrame) and self.feature_names is not None:
            self.feature_names = X.columns.tolist()
            X = X.to_numpy()
        elif self.feature_names is not None:
            pass 
        else:
            feature_names = [f"feat_{i}" for i in range(X.shape[1])]
        feature_names = self.feature_names
        feature_types = []
        for idx in range(len(feature_names)):
            col = X[:, idx]
            if isinstance(col[0], (int, float, np.integer, np.floating)):
                feature_types.append(1) 
            else:
                feature_types.append(-1)
        java_feature_names = JStringArray(feature_names)
        java_feature_types = JIntArray(feature_types)

        object_x = ZTree.numpy_to_jobject(X)

        y = y.astype(np.float32).tolist()
        java_y = JFloatArray(y)
        
        pytree = self.PyZTree(self.mode, 5, 10)
        tree = pytree.fitOptimal(java_feature_names, java_feature_types, object_x, java_y)
        self.tree = tree


    def print_tree(self):
        if self.tree is None:
            raise RuntimeError("Model is not trained. Call `.fit()` first.")
        self.tree.print_(0, 0)

    @staticmethod
    def numpy_to_jobject(np_array):
        import jpype
        rows, cols = np_array.shape
        JObject = jpype.JClass("java.lang.Object")
        JString = jpype.JClass("java.lang.String")
        JFloat = jpype.JClass("java.lang.Float")
        ObjectArray = jpype.JArray(jpype.JArray(JObject))(rows)
        for i in range(rows):
            inner_array = jpype.JArray(JObject)(cols)
            for j in range(cols):
                val = np_array[i, j]
                if isinstance(val, (int, float, np.integer, np.floating)):
                    inner_array[j] = JFloat(float(val))
                else:
                    inner_array[j] = JString(str(val))
            ObjectArray[i] = inner_array
        return ObjectArray