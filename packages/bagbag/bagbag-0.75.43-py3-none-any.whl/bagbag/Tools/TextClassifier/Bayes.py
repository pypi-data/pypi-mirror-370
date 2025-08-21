from sklearn.naive_bayes import MultinomialNB

from .base import * 

# ZH
#                precision    recall  f1-score   support                                                                                                                                                        
#                                                                                                                                                                                                               
#   _08_Finance       0.88      0.90      0.89       479
#        _10_IT       0.82      0.87      0.84       462
#    _13_Health       0.82      0.90      0.86       446
#    _14_Sports       0.96      1.00      0.98       474
#    _16_Travel       0.89      0.91      0.90       478
# _20_Education       0.84      0.89      0.86       461
#   _22_Recruit       0.92      0.73      0.82       619
#   _23_Culture       0.81      0.82      0.82       483
#  _24_Military       0.94      0.91      0.93       508
# 
#      accuracy                           0.88      4410
#     macro avg       0.88      0.88      0.88      4410
#  weighted avg       0.88      0.88      0.87      4410
# 
# EN
#                           precision    recall  f1-score   support                                                                                                                                             
#                                                                                                                                                                                                               
#              alt.atheism       0.71      0.80      0.75       280
#            comp.graphics       0.72      0.76      0.74       369
#  comp.os.ms-windows.misc       0.73      0.77      0.75       373
# comp.sys.ibm.pc.hardware       0.81      0.64      0.71       499
#    comp.sys.mac.hardware       0.81      0.87      0.84       357
#           comp.windows.x       0.78      0.87      0.82       356
#             misc.forsale       0.78      0.87      0.82       349
#                rec.autos       0.91      0.90      0.91       401
#          rec.motorcycles       0.97      0.92      0.94       419
#       rec.sport.baseball       0.93      0.90      0.92       411
#         rec.sport.hockey       0.99      0.89      0.93       444
#                sci.crypt       0.96      0.78      0.86       487
#          sci.electronics       0.64      0.83      0.72       301
#                  sci.med       0.77      0.93      0.84       329
#                sci.space       0.94      0.84      0.89       442
#   soc.religion.christian       0.96      0.67      0.79       574
#       talk.politics.guns       0.95      0.66      0.78       519
#    talk.politics.mideast       0.95      0.93      0.94       384
#       talk.politics.misc       0.52      0.93      0.67       174
#       talk.religion.misc       0.24      0.95      0.39        64
# 
#                 accuracy                           0.82      7532
#                macro avg       0.80      0.84      0.80      7532
#             weighted avg       0.85      0.82      0.83      7532


class Bayes(baseClassificationClass):
    def __init__(self) -> None:
        super().__init__()
        self.classifierfunc = MultinomialNB

# 用法见SVM