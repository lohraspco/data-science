1. Setup Azure ML
   * Get Azure Subscription
   * Create Azure Machine Learning Resource
    * Create Compute
2. Open in VSCode
   * When compute is started, open it in VSCode (you will need to login into Azure) 
   * in VSCode cmd az login --tenant TENANT_ID
3. Create pipeliens using SDK V2 and MLFlow
    * MLFlow: </b>
    ```sql az ml workspace show --query mlflow_tracking_uri```

This is an example of how to run single and parallel azure jobs.

The error messages in Azure Python SDK V2 are not that helpful.