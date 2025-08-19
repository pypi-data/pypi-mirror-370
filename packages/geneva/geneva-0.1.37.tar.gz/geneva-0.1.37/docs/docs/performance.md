# Tuning Geneva distributed performance

When Geneva runs in distributed mode, jobs are deployed against a kubernetes kuberay instance that dynamically provisions a Ray cluster.  Jobs execution time depends on suffcient cpu/gpu resources for *computation* and sufficient *write bandwidth* to store the output values.  Tuning the performance of a job boils down to configuring the table or cluster resources.

## Scaling computation resoures

Geneva jobs can split and schedule computational work into smalller batches that are assigned to *tasks* which are distributed across the cluster.  As each task completes, each writes its output into a checkpoint file.  If a job is interurupted or run again, Geneva will look to see if a checkpoint for the computation is already present and if not will kick off computations.  

Usually computation capacity is the bottleneck for job execution.  To complete all of a job's tasks more quickly, you just need to increase the amount of CPU/GPU resources available.

### GKE node pools

GKE + kuberay can autoscale the amount of VM nodes on demand.  Limitations on the amount of resources provisioned is configured via [nodepools](https://cloud.google.com/kubernetes-engine/docs/how-to/node-pools#scale-node-pool).  Node pools can be managed to scale vertically (type of machine) or horizontally (# of nodes)

Properly applying kubernetes labels to the nodepool machines allow you to control resources for different jobs in your cluster.
 
TODO: include more detailes on node labels instructions

TODO: pod specific node pool for job's workers.

### ray_cluster resource definitions

TODO

### Options on `Table.backfill(..)`

The `Table.backfill(..) ` method has several optional arguments to tune performance.  To saturate the CPUs in the cluster, the main arguments to change are `concurrency` which controls the number of task processes and `intra_applier_concurrency` which controls the number of task threads per task process.

`commit_granularity` controls how frequently fragments are committed so that partical results can be come visible to table readers.  

Setting `batch_size` smaller introduces finer-grained checkpoints and can help provide more frequent proof of life as a job is being executed.  This is useful if the computation on your data is expensive.

::: geneva.table.Table.backfill
    options:
      annotations_path: brief
      show_source: false


## Balancing write bandwidth

While computation can be broken down to small tasks, new Lance column data for each fragment must be written out in a serialized fashion.  Each fragment has a writer that waits for checkpointed results to arrive, sequences them, and then serially write out the new datafile.  

Writers can be a bottleneck if a lance dataset has a small number of fragments, espcially if the amount of data being written out is comparatively large.  Maximizing parallel write throughput can be achieved by having more fragments than nodes in the cluster. 

### Symptom: Computation tasks complete but writers seem to hang

Certain jobs that take a small data set and expand it may appear as if the writer has frozen.  

An example is table that contains a list of URLs pointing to large media files.  This list is relatively small (&lt; 100MB) and can fit into a single fragment.  A UDF that downloads will fetch all the data and then attempt to write all of it out through the single writer.  This single writer then can be responsible for serially writing out 500+GB of data to a single file!

To mitigate this, you can load your initial table so that there will be multipe fragments.  Each fragment with new outputs can be written in parallel with higher write throughput.
