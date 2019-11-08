
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/evaluation.ipynb

# Evaluation metrics for vulnerability detection - Accuracy, Precision, Recall
def eval_vuln(mdl, tst):
    tps, tns, fps, fns = 0, 0, 0, 0
    print("Hello World")
    for inpt, lbl in zip(tst["query"], tst["res"]):
        print(lbl)
        pred = mdl.predict(inpt, 1, temperature=0.75)
        if lbl == "yes":
            if pred == lbl:
                tps += 1
            else: fns += 1
        else:
            if pred == lbl:
                tns += 1
            else: fps += 1

    acc   = (tps + tns) / len(tst)
    prec  = tps / (tps + fps)
    recal = tps / (tps + fns)

    return acc, prec, recal