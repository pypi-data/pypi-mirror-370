# Apheris CLI

The [Apheris](http://www.apheris.com) Command Line Interface (CLI) is a tool for Machine Learning Engineers and Data Scientists to define Federated computations, launch them and get the results through the Apheris product.

The CLI provides both terminal and Python interfaces to interact with the Apheris 3.0 platform. It can be used to create, activate and deactivate Compute Specs, and to submit and monitor compute jobs.

We recommend installing the CLI in a fresh virtual environment.

For a full guide to the CLI, please see the [Apheris CLI documentation](https://www.apheris.com/docs/data-science-and-ml/apheris-cli-hello-world.html).

## Quickstart: Python API

```python
import apheris

# Login to apheris
>>> apheris.login()
Logging in to your company account...
Apheris:
Authenticating with Apheris Cloud Platform...
Please continue the authorization process in your browser.

Login was successful

# List the datasets to which you have access
>>> apheris.list_datasets()
+-----+---------------------------------------------------------+--------------+---------------------------+
| idx |                        dataset_id                       | organization |       data custodian      |
+-----+---------------------------------------------------------+--------------+---------------------------+
|  0  |          cancer-medical-images_gateway-2_org-2          |    Org 2     |        Orsino Hoek        |
|  1  |          pneumonia-x-ray-images_gateway-2_org-2         |    Org 2     |        Orsino Hoek        |
|  2  |            covid-19-patients_gateway-1_org-1            |    Org 1     |      Agathe McFarland     |
|  3  | medical-decathlon-task004-hippocampus-a_gateway-1_org-1 |    Org 1     |      Agathe McFarland     |
|  4  | medical-decathlon-task004-hippocampus-b_gateway-2_org-2 |    Org 2     |        Orsino Hoek        |
| ... |                           ...                           |     ...      |            ...            |
+-----+---------------------------------------------------------+--------------+---------------------------+

# List models available to you
>>> apheris.list_models()
+-----+---------------------------+-------------------------------------+
|  id |            name           |               version               |
+-----+---------------------------+-------------------------------------+
|  0  |       apheris-nnunet      |                u.v.w                |
|  1  |     apheris-statistics    |                x.y.z                |
| ... |            ...            |                 ...                 |
+-----+---------------------------+-------------------------------------+

# List compuutations
>>> apheris.list_compute_specs()
+--------------------------------------+---------------------+------------------------------+
| ID                                   | Created             | Activation Status            |
+--------------------------------------+---------------------+------------------------------+
| f20eba74-28d2-4458-aedb-72a983cb2a33 | 2025-05-20 13:37:59 | inactive.awaiting_activation |
| 29d542ed-d273-4176-8e3f-dfc70311cf32 | 2025-05-20 13:38:44 | inactive.shutdown            |
| c4e3f12a-0b20-4475-9611-79846dcb23b6 | 2025-05-21 07:40:53 | inactive.shutdown            |
| aae7bf0e-0568-4441-8d85-fdabc6343a4d | 2025-05-21 07:48:57 | inactive.shutdown            |
| 67b76354-aae3-48cc-810a-fd79c1040cc3 | 2025-05-21 07:50:05 | inactive.shutdown            |
| 70829d63-bb77-4ff0-a1a9-90273aa38792 | 2025-05-23 06:16:36 | inactive.shutdown            |
| 41994296-be34-487c-893c-d183f7baeb99 | 2025-05-23 06:52:50 | inactive.shutdown            |
| f1589f63-cfc9-4b1a-b985-ee959121c765 | 2025-05-23 07:17:11 | inactive.shutdown            |
| 3640fed9-f1d3-43f8-9b6b-5cde345a5ed5 | 2025-05-26 11:56:14 | inactive.awaiting_activation |
| defe5013-2c73-4eb9-be52-1ae7aed841ff | 2025-05-26 12:00:59 | active.running               |
+--------------------------------------+---------------------+------------------------------+

# Run a job in Apheris
>>> from aphcli.api import job
>>> job.run(
...    datasets=[
...     "medical-decathlon-task004-hippocampus-a_gateway-1_org-1",
...     "medical-decathlon-task004-hippocampus-b_gateway-2_org-2"
...    ],
...    payload={"mode": "training", "model_configuration": "2d", "dataset_id": 4, "num_rounds": 1},
...    model="apheris-nnunet",
...    version="x.y.z"
...)
Job(duration='0:00:00', id=UUID('f77d5dc7-a2e7-4a2a-827d-49a2131b1ffe'), status='submitted', created_at=datetime.datetime(2025, 7, 8, 17, 17, 6, 897476), compute_spec_id=UUID('defe5013-2c73-4eb9-be52-1ae7aed841ff'))

# Logout of Apheris
>>> apheris.logout()
Logging out from Apheris Cloud Platform session
Successfully logged out
```

##  Quickstart: CLI

Logging into Apheris:

```console
$ apheris login
Logging in to your company account...
Apheris:
Authenticating with Apheris Cloud Platform...
Please continue the authorization process in your browser.

Login was successful
You are logged in:
 e-mail:  your.name@your-company.com
 organization: your_organisation
 environment: your_environment
```

You can check your current login status.

```console
$ apheris login status
You are logged in:
 e-mail:  your.name@your-company.com
 organization: your_organisation
 environment: your_environment
```

When you are done with your work, it is recommended to log out.

```console
$ apheris logout
Logging out from Apheris Cloud Platform session
Logging out from Apheris Compute environments session
Successfully logged out
```

You can see the datasets to which you've been given access using the `datasets` command:

```console
$ apheris datasets list
+-----+---------------------------------------------------------+--------------+---------------------------+
| idx |                        dataset_id                       | organization |       data custodian      |
+-----+---------------------------------------------------------+--------------+---------------------------+
|  0  |          cancer-medical-images_gateway-2_org-2          |    Org 2     |        Orsino Hoek        |
|  1  |          pneumonia-x-ray-images_gateway-2_org-2         |    Org 2     |        Orsino Hoek        |
|  2  |            covid-19-patients_gateway-1_org-1            |    Org 1     |      Agathe McFarland     |
|  3  | medical-decathlon-task004-hippocampus-a_gateway-1_org-1 |    Org 1     |      Agathe McFarland     |
|  4  | medical-decathlon-task004-hippocampus-b_gateway-2_org-2 |    Org 2     |        Orsino Hoek        |
| ... |                           ...                           |     ...      |            ...            |
+-----+---------------------------------------------------------+--------------+---------------------------+
```

And you can see models using the `models` command:

```console
$ apheris models list
+-----+---------------------------+-------------------------------------+
|  id |            name           |               version               |
+-----+---------------------------+-------------------------------------+
|  0  |       apheris-nnunet      |                u.v.w                |
|  1  |     apheris-statistics    |                x.y.z                |
| ... |            ...            |                 ...                 |
+-----+---------------------------+-------------------------------------+
```

You can schedule a job on Apheris using the `job` command:

```console
$ apheris job schedule \
--dataset_ids medical-decathlon-task004-hippocampus-a_gateway-1_org-1,medical-decathlon-task004-hippocampus-b_gateway-2_org-2 \
--model_id apheris-nnunet \
--model_version x.y.z \
--payload '{"mode": "training", "model_configuration": "2d", "dataset_id": 4, "num_rounds": 1}'
About to schedule job with parameters:
Dataset IDs: medical-decathlon-task004-hippocampus-a_gateway-1_org-1,medical-decathlon-task004-hippocampus-b_gateway-2_org-2
Model: apheris-nnunet:x.y.z
Payload: {"mode": "training", "model_configuration": "2d", "dataset_id": 4, "num_rounds": 1}
Resources:
  Client: 1.0 CPU, 0 GPU, 2000 MB memory
  Server: 1.0 CPU, 0 GPU, 2000 MB memory

Do you want to proceed? (y/N)
:y

The job was submitted! The job ID is d6f7b657-8b30-4636-8f4c-2d96678095ba
```

Check the status of a job:

```console
$ apheris job status

Using the cached `compute_spec_id` defe5013-2c73-4eb9-be52-1ae7aed841ff [2025-07-08 17:17:06].
Using the cached `job_id` f77d5dc7-a2e7-4a2a-827d-49a2131b1ffe [stored 2025-07-08 17:36:26].

status: running
```

Once a job is complete, you can download the results:

```console
$ apheris job download-results /path/to/store/results

Using the cached `compute_spec_id` defe5013-2c73-4eb9-be52-1ae7aed841ff [2025-07-08 17:17:06].
Using the cached `job_id` f77d5dc7-a2e7-4a2a-827d-49a2131b1ffe [stored 2025-07-08 17:36:26].

Successfully downloaded job outputs to /path/to/store/results
```
