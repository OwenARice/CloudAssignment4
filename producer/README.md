Code for the image producer and its latency-recording subtask.

Instructions for use:
 - drop this directory wherever you want
 - update the IP addresses and topic names at the top of "dispatchProducer.py"
 - run "python dispatchProducer.py"
 - latencies will be recorded in "e2elatency.csv"

So you want to run the broker and producer?
 - ssh into VM3
 - run ./zookeeperStart.sh in its top-level directory
 - open another terminal and ssh into VM3
 - run ./brokerStart.sh in its top-level directory
 - open another terminal and ssh into VM1
 - run ./startProducing.sh in its top-level directory
 - NOTE: you may have to wait a minute between starting zookeeper and the broker
