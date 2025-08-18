import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from xai_easy import explain_model, explain_instance, select_top_features

def test_explain_and_local():
    data = load_iris(as_frame=True)
    X, y = data.data, data.target
    clf = RandomForestClassifier(random_state=0).fit(X, y)
    gdf = explain_model(clf, X, y, top_n=3)
    assert not gdf.empty
    ldf = explain_instance(clf, X, X.iloc[0].values)
    assert len(ldf) == X.shape[1]

def test_select_top_features():
    import numpy as np
    X = np.random.RandomState(0).rand(100, 1000)
    y = np.random.randint(0,2,size=100)
    idx, names = select_top_features(X, y, task='classification', k=20)
    assert len(idx) == 20
