#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
from operator import add

from pyspark.sql import SparkSession


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: accuracy analysis <file>", file=sys.stderr)
        sys.exit(-1)
        
    labelList = []
    #this file defines the mapping from class number to human-readable 
    #text for the Resnet18 model
    with open("/home/cc/assignment3_cloud/Spark/imageclasses.txt", 'r') as file:
        for line in file:
            labelList.append(line)
            
    def isLineCorrect(lineStr):
    
        elements = lineStr.split(" ")
        
        if(elements[2] in labelList[int(elements[1])]):
            return (elements[0], (1,0))
        else:
            return (elements[0], (0,1))
    
    def tupleAdd(t1, t2):
        return ((t1[0] + t2[0]),(t1[1] + t2[1]))


    spark = SparkSession.builder.appName("PythonWordCount").getOrCreate()

    lines = spark.read.text(sys.argv[1]).rdd.map(lambda r: r[0])
    
    counts = (
        lines.map(lambda x: isLineCorrect(x)).reduceByKey(tupleAdd)
    )
    output = counts.collect()
    for producer, count in output:
        print(f"{producer}: correct: {count[0]}, incorrect: {count[1]}")

    spark.stop()
