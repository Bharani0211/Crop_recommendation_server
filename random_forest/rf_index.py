def random_forest_algorithm(link):
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier

    data = pd.read_csv("FinalData.csv")
    x = np.array(data.iloc[:,0:-1])
    y= np.array(data.iloc[:,-1])

    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.5, random_state=1)
    clf=RandomForestClassifier(n_estimators=100)
    clf.fit(X_train,y_train)

    url=link
    file_id=url.split('/')[-2]
    dwn_url='https://drive.google.com/uc?id=' + file_id
    test_data = pd.read_csv(dwn_url)
    test_data = np.array(test_data)
    y_pred = clf.predict(test_data)

    output = []
    for x in y_pred:
        if x not in output:
            output.append(x)

    cnt=[]
    for i in range(0,len(output)):
        count=0
        for j in range(0,len(y_pred)):
            if output[i]==y_pred[j]:
                count+=1
        cnt.append(count)
    percentage=[]

    ln=len(y_pred)
    p_large=0
    index=0
    for i in range(0,len(cnt)):
        percentage.append((cnt[i]/ln)*100)
        #   print(percentage[i])
        if p_large<percentage[i]:
            p_large=percentage[i]
            index=i
    return({'Crop':output[index], 'Percentage':"{:.2f}".format(percentage[index])})