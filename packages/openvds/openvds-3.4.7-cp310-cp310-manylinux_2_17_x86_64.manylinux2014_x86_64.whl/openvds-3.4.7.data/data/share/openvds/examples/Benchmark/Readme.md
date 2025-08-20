This is a tool used to benchmark HueSpace and OpenVDS to see the performance
characteristics when deployed on cloud instances.

The idea is that this folder is copied to the host. Then a HueSpace binary is
pleaced in the same folder under the folder name HueSpace. Then load the
environment variables and run the script by pointing to a vds using the command line arguments --uri and --connection.

Enabling GPU can be done with the --gpu command line option and testing OpenVDS can be done by adding --openvds.

This script has many been used targeting a Bonaventure import using lossless VDS.

In the NetApp deployment the following script was used to run the benchmark
`run_benchmark.sh`:
```
set -e
uri='s3://osdu-test-bucket-1/bonaventure_ll'
connection='EndpointOverride=https://osdu-bluware.storage.lumen.com:10443'
source set_env.sh
python3 benchmark.py --uri $uri --connection $connection --openvds
python3 benchmark.py --uri $uri --connection $connection
python3 benchmark.py --uri $uri --connection $connection --gpu
```
