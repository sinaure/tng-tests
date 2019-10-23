|||||
| :--- | :--- | :--- | :--- |
| __Test Case Name__ | | test_service_migration_state_os | |
| __Test Purpose__ | | Test the stateful migration of a VNF| |
| __Configuration__ | | A NS composed by one VNF is deployed with the Service Platform| |
| __Test Tool__ | | Robot Framework, using Tnglib | |
| __Metric__ | | Boolean (success or not) | |
| __References__ | |  | |
| __Applicability__ | | Variations of this test case can be performed to test it for different VNFs and multi-VNF services  | |
| __Pre-test conditions__ | | A running Service Platform| |
| __Test sequence__ | Step | Description | Result |
| | 1 | Service Package On-Boarding | Service Package is on-boarded in the SP|
| | 2 | Deploy Network Service | Network Service is deployed in the SP |
| | 3 | Check Network Service instantiation correctness | Confirm that the NS was deployed without errors |
| | 4 | Generate state | The VNF has altered state |
| | 5 | Migrate the VNF | The VNF is migrated from one openstack to the other |
| | 6 | Check VNF migration correctness | Confirm that the migration was executed without errors |
| | 7 | Check if state was migrated to new VNF | The altered state is there or not |
| | 8 | Terminate Network Service | Delete the NS deployed |
| __Test Verdict__ | | Network Service's VNF was migrated succesfully | |
| __Additional resources__ | | | |

