# Triton Model Operator

В цьому репозиторії я хочу створити прототип системи, який буде підтримувати GitOps підхід для розгортання моделей Nvidia Triton на Kubernetes.
В практичних термінах це буде означати, що перелік моделей, що розгорнуті в Triton будуть зберігатись у вигляді конфігураційних файлів в git репозиторії і буде еволюціонувати, як код. 
Завдання ж пропотипу забезпечити розгортання цих моделей в Nvidia Triton і відповідне управління їх життєвим циклом.

# RENAME to model-deployment-operator



## References

1. [How to check what branches a commit belongs to](https://stackoverflow.com/questions/7131703/how-to-know-which-branch-a-git-log-commit-belongs-to)


## Research
1. How to create CRD from pydantic model:
   * https://github.com/nolar/kopf/issues/524
   * https://github.com/asteven/kopf_resources/blob/master/kopf_resources/registry.py