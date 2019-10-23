|||||
| ---------------------- | ------ | ------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| __Test Case Name__ | | __Multiple Parallel Probes__ \cite{github.multiple.parallel.probes} | |
| __Test Purpose__ | | To ensure that multiple probes can be running in parallel | |
| __Configuration__ | | The TD will be based on the PING and NETCAT test, but using multiple instances/probes sections with no dependencies to execute all probes in parallel. | |
| __Test Tool__ | | Robot Framework | |
| __Metric__ | | No metric (ping and netcat test) | |
| __References__ | | https://github.com/sonata-nfv/tng-vnv-executor/ | |
| __Applicability__ | | Variations of this test case can be performed modifying the TD: To define two probes sections with different names but using the same probe. Using the same probe but setting the instances to 2 | |
| __Pre-test conditions__ | | The packages that contain the NS and Tests will be created before the test execution| |
| __Test sequence__ | Step | Description | Result |
| | 1 | Service Package On-Boarding | Service Package is on-boarded in VnV catalogue |
| | 2 | Test Package On-Boarding | Test Package is on-boarded in VnV catalogue |
| | 3 | Check Service Instantiation | Service instance is up and running |
| | 4 | Check Test Execution | VnV launches and executes the test |
| | 5 | Check Test Completion | VnV test execution is completed |
| | 6 | Check Stored Results | The test results are stored in the test results repository |
| | 7 | Check No Running Instances In SP | After the test, the instantiated service must be deleted from Service Platform |  
| __Test Verdict__ | | The results will show content from the probes | |
| __Additional resources__ | | | |
