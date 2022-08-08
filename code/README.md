# Project Build Process

If you want to walk through the workflow manually to build and understand how the project works, follow the steps below. There is a lot more detail and explanation/comments in each of the files/notebooks so its worth looking into those. We will focus our attention on working within CML, using all it has to offer, while glossing over the details that are simply standard data science. We trust that you are familiar with typical data science workflows and do not need detailed explanations of the code.

### 0 - Bootstrap

There are a couple of steps needed at the start to configure the Project and Workspace settings so each step will run successfully. You **must** run the project bootstrap before running other steps.

Open the file `0_bootstrap.py` in a normal workbench Python3 session. You only need a 1 CPU / 2 GB instance. Then **Run > Run All Lines**

### 2 - Data Analysis

This is a Jupyter Notebook that does some basic data exploration and visualization. It is here to show how this would be part of the data science workflow.

Open a Jupyter Notebook session (rather than a work bench): Python3, 2 CPU, 8 GB and open the `2_data_analysis.ipynb` file. 

At the top of the page click **Cells > Run All**.

### 3 - Data Processing

Open `3_data_processing.py` in a Workbench session: Python3, 4 CPU, 12 GB. Run the file.

### 5 - Model Train

If you want to train a new model, use the **[Jobs](https://docs.cloudera.com/machine-learning/cloud/jobs-pipelines/topics/ml-creating-a-job.html)** feature for ad-hoc, recurring, or dependent jobs to run specific scripts. To run the model training process as a job, create a new job by going to the Project window and clicking _Jobs > New Job_ and entering the following settings:

* **Name** : Train Model

* **Script** : 5_model_train.py

* **Arguments** : _Leave blank_

* **Kernel** : Python 3

* **Schedule** : Manual

* **Engine Profile** : 4 vCPU / 8 GiB

  The rest can be left as is. Once the job has been created, click **Run** to start a manual run for that job.

### 6 - Model Serve

The **[Models](https://docs.cloudera.com/machine-learning/cloud/models/topics/ml-creating-and-deploying-a-model.html)** feature is used to deploy a machine learning model into production for real-time prediction. To deploy the model that was trained in the previous step: from  to the Project page, click **Models > New Model** and create a new model with the following details:

* **Name**: Flight Delay Prediction Model
* **Description**: This model API endpoint predicts flight delays
* **File**: 6_model_serve.py
* **Function**: predict_cancelled
* **Kernel**: Python 3
* **Engine Profile**: 1vCPU / 2 GiB Memory

### 7 - Application

The next step is to deploy the Flask application with the **[Applications](https://docs.cloudera.com/machine-learning/cloud/applications/topics/ml-applications.html)** feature in CML. For this project it is used to deploy a web based application that interacts with the underlying model created in the previous step.

Go to the **Applications** section and select "New Application" with the following:

* **Name**: Airline Delay Prediction App
* **Subdomain**: delay-app
* **Script**: 7_application.py
* **Kernel**: Python 3
* **Engine Profile**: 1vCPU / 2 GiB Memory
* **Set Environment Variables**: Enter `SHTM_ACCESS_KEY` as the *Name* and the Access Key you copied from the Model Settings page as the *Value*. Click Add.

Then click "Create Application". After the Application deploys, click on the blue-arrow next to the name to launch the application in a new window.