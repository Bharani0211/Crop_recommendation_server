def decision_tree_algorithm(link):
    import pandas
    import numpy
    from sklearn.tree import DecisionTreeClassifier

    df = pandas.read_csv("FinalData.csv")
    # print(df)

    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

    x = df[features]
    y = df['label']

    dtree = DecisionTreeClassifier()
    dtree = dtree.fit(x, y)

    # data = pandas.read_csv("test_data_or_rice.csv")
    # data = numpy.array(data)
    # y_pred=dtree.predict(data)

    url=link
    file_id=url.split('/')[-2]
    dwn_url='https://drive.google.com/uc?id=' + file_id
    test_data = pandas.read_csv(dwn_url)
    test_data = numpy.array(test_data)
    y_pred=dtree.predict(test_data)

    output = []
    for x in y_pred:
        if x not in output:
            output.append(x)
    # print(output)

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