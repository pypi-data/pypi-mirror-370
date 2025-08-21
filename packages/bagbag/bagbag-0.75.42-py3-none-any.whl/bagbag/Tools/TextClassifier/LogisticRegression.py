from sklearn.linear_model import LogisticRegression as logisticregression

from .base import * 

# ZH
#                precision    recall  f1-score   support                                                                                                                                                        
#                                                                                                                                                                                                               
#   _08_Finance       0.87      0.93      0.90       459
#        _10_IT       0.87      0.86      0.87       496
#    _13_Health       0.91      0.90      0.91       492
#    _14_Sports       0.97      0.99      0.98       479
#    _16_Travel       0.91      0.93      0.92       476
# _20_Education       0.86      0.91      0.89       465
#   _22_Recruit       0.89      0.88      0.89       493
#   _23_Culture       0.89      0.78      0.83       557
#  _24_Military       0.96      0.95      0.95       493
# 
#      accuracy                           0.90      4410
#     macro avg       0.90      0.91      0.90      4410
#  weighted avg       0.90      0.90      0.90      4410
# 
# EN
#                           precision    recall  f1-score   support                                                                                                                                             
#                                                                                                                                                                                                               
#              alt.atheism       0.73      0.81      0.77       287
#            comp.graphics       0.79      0.68      0.73       449
#  comp.os.ms-windows.misc       0.77      0.76      0.76       400
# comp.sys.ibm.pc.hardware       0.74      0.71      0.72       409
#    comp.sys.mac.hardware       0.82      0.82      0.82       387
#           comp.windows.x       0.75      0.82      0.78       358
#             misc.forsale       0.85      0.80      0.82       417
#                rec.autos       0.89      0.90      0.90       392
#          rec.motorcycles       0.95      0.95      0.95       401
#       rec.sport.baseball       0.93      0.90      0.92       412
#         rec.sport.hockey       0.95      0.95      0.95       403
#                sci.crypt       0.91      0.96      0.94       377
#          sci.electronics       0.77      0.73      0.75       419
#                  sci.med       0.86      0.89      0.87       383
#                sci.space       0.92      0.89      0.90       407
#   soc.religion.christian       0.93      0.81      0.87       459
#       talk.politics.guns       0.90      0.74      0.81       444
#    talk.politics.mideast       0.88      0.97      0.92       339
#       talk.politics.misc       0.60      0.80      0.68       231
#       talk.religion.misc       0.51      0.80      0.62       158
# 
#                 accuracy                           0.83      7532
#                macro avg       0.82      0.83      0.82      7532
#             weighted avg       0.84      0.83      0.83      7532

class LogisticRegression(baseClassificationClass):
    def __init__(self) -> None:
        super().__init__()
        self.classifierfunc = logisticregression
