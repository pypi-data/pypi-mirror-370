# Job and Session startup optimizations

During interactive sessions, there are two main actions where you would interact with Geneva.

* Compute cluster creation
* Job execution

Behind the scenes, Geneva packages your python environment and auto-provisions nodes to execute the jobs.  This can be time consuming, taking on the order of 5mins to complete before any work is done.   The following sections will describe what happens in these steps and how to diagnose and speed up these interactions.

## Compute cluster creation

To execute a Geneva job, you'll need to initialize a compute environment.  Here's the basic steps Geneva takes to instantiate that cluster:

* User requests a cluster 
  * Scan workspace's python path for modules
    * Generate local workspace directory zip 
    * Generate python site-packages directory zip(s)
    * Generate other dirs zip (may include your .venv)
  * Upload zips
  * Provision head node
    * Initialize head node

The requests to create an environment can take 5-10 mins to initiate.  The most time-consuming steps are generating directory zips and uploading them.  AI workloads often require many module packages and can be dependent on specific versions to work.  Common modules required for GPU use to run model inferrence can easily be 5GB-10GB of compressed content.  On GCE for example, this can take ~5mins to zip all this and ~1min to upload all of this data.

To speed this up, Geneva employs caching to help optimize the startup time.  There are a few things you can do to make subsequent runs faster, often times <1 minute:

**Hashing and Caching.**  Geneva generates a hash of each path in the python path that takes into account files and their last modified time.  After the first time a directory zip is created and uploaded, the cached copy is used and no new zip is generated or uploaded.  However, if there are any changes (e.g. new module added or upgraded) a new hash created and the environment's content is zipped and uploaded.  

**Isolate dynamic code and modules.**  If you use a Jupyter notebook environment for your driver, the content of the `.ipynb` file is constantly changing.  This means the hash for the directory that contains the notebook will change, even if the subdirectories do not.  If your notebook is in your home directory, this could pull in large amounts unneeded code and data.  To avoid this you can move your notebook into a subdirectory with no children.  When your notebook is executed it is updated but only the notebook content is resent.  Other path directories are unchanged, have the same hash and can skip zip and ship. 

**Package dependecies into a docker image**.   Geneva has an option to skip the zip and ship of the site-packages.  Enabling this assumes that the default docker image is overriden with a custom image that has the `site-package` content preloaded.

**Pre-provision nodes and pods.**  In your kubernetes configuration,  you can tag specific nodes with `geneva.lancedb.com/ray-head` k8s label.  These nodes should be configured to be on non-spot instances that are always up.  This makes initial kuberay cluster creation quick.

## Job execution

A backfill or materialized view jobs triggers the provisioning of worker nodes that will perform the computations and writes.   A cold start can be slow because several steps must take place before the UDFs can be applied.  However, once nodes and pods are warmed up, the time between submission and execution can be quick.

Here's the basic steps Geneva takes to kick off a Geneva job: 

* User submits job (backfill)
  * plan scans
    * provision worker nodes (vms)
        * load vm
  * Autoscale workers nodes
    * provision worker nodes (vms)
        * load vm
    * schedule ray actors 
        * download docker images 
        * download zips 
    * execute udf
    * orchestrate fragment write.

In practice, planning the initial distributed step scans require loading vm and pod images.  With a cold start, this can take ~5 minutes. 

Here are some steps you can take to pre-warming worker nodes and pods so that exectuion can be more interactive:

**Set worker spec's replicas or min_replicas to a value >0.**  When the kuberay cluster is instantiated this also pre-provision vm's so they are ready for k8s to place pod.    replicas (for initial # of worker nodes), and minWorkers (to keep a pool for nodes always up)

**Make a warmup call.**  Making an initial request to ray will load the pod and zips content to the worker node so that subsequent startups will be fast.  

**Prevent nodes from auto-scaling down.** During cluster creation, you can specifiy `idle_timeout_seconds` option  -- this is the amount of time before an node needs to be idle before it is considered for de-provisioning.  
