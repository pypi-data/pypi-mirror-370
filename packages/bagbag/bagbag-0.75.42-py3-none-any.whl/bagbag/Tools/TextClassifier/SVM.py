from sklearn.linear_model import SGDClassifier

from .base import * 

# ZH
#                precision    recall  f1-score   support                                                                                                                                                        
#                                                                                                                                                                                                               
#   _08_Finance       0.87      0.94      0.90       453
#        _10_IT       0.87      0.89      0.88       476
#    _13_Health       0.92      0.91      0.92       496
#    _14_Sports       0.99      0.99      0.99       490
#    _16_Travel       0.93      0.92      0.93       496
# _20_Education       0.88      0.91      0.90       474
#   _22_Recruit       0.93      0.89      0.91       514
#   _23_Culture       0.88      0.85      0.87       511
#  _24_Military       0.97      0.95      0.96       500
# 
#      accuracy                           0.92      4410
#     macro avg       0.92      0.92      0.92      4410
#  weighted avg       0.92      0.92      0.92      4410
# 
# EN
#                           precision    recall  f1-score   support                                                                                                                                             
#                                                                                                                                                                                                               
#              alt.atheism       0.77      0.82      0.79       299
#            comp.graphics       0.78      0.76      0.77       401
#  comp.os.ms-windows.misc       0.76      0.76      0.76       394
# comp.sys.ibm.pc.hardware       0.76      0.72      0.74       410
#    comp.sys.mac.hardware       0.85      0.83      0.84       391
#           comp.windows.x       0.76      0.87      0.81       344
#             misc.forsale       0.91      0.82      0.86       434
#                rec.autos       0.88      0.93      0.91       377
#          rec.motorcycles       0.95      0.95      0.95       399
#       rec.sport.baseball       0.95      0.91      0.93       416
#         rec.sport.hockey       0.98      0.95      0.96       413
#                sci.crypt       0.95      0.93      0.94       407
#          sci.electronics       0.74      0.80      0.77       367
#                  sci.med       0.89      0.91      0.90       390
#                sci.space       0.95      0.89      0.92       418
#   soc.religion.christian       0.93      0.84      0.89       442
#       talk.politics.guns       0.94      0.74      0.83       458
#    talk.politics.mideast       0.90      0.97      0.94       349
#       talk.politics.misc       0.61      0.85      0.71       220
#       talk.religion.misc       0.61      0.75      0.67       203
# 
#                 accuracy                           0.85      7532
#                macro avg       0.84      0.85      0.84      7532
#             weighted avg       0.86      0.85      0.85      7532

class SVM(baseClassificationClass):
    def __init__(self) -> None:
        super().__init__()
        self.classifierfunc = SGDClassifier

if __name__ == "__main__":
    from bagbag import * 

    traindatadir = Os.Getenv("HOME") + '/data/train'
    testdatadir = Os.Getenv("HOME") + '/data/test'

    tc = Tools.TextClassifier.SVM()

    # # ipdb.set_trace()

    for label in Tools.ProgressBar(Os.ListDir(traindatadir)):
        fdir = Os.Path.Join(traindatadir, label)
        for fname in Tools.ProgressBar(Os.ListDir(fdir)):
            fpath = Os.Path.Join(fdir, fname)
            text = open(fpath, encoding='gbk', errors='ignore').read()
            tc.Add(label, text)

    Lg.Trace("training")
    tc.Train()

    tc.Save("tc.obj")

    del(tc)

    ts = Tools.TextClassifier.SVM()
    ts.Load("tc.obj")

    ay = []
    py = []
    for label in Tools.ProgressBar(Os.ListDir(testdatadir)):
        fdir = Os.Path.Join(testdatadir, label)
        for fname in Tools.ProgressBar(Os.ListDir(fdir)):
            fpath = Os.Path.Join(fdir, fname)
            text = open(fpath, encoding='gbk', errors='ignore').read()
            # tc.Add(label, text)

            ay.append(label)
            py.append(ts.Predict(text))

    print(ts.Report(py, ay))
        

