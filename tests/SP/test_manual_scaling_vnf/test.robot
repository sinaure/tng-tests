*** Settings ***
Documentation     Test suite for uploading a package to the SP platform
Library           tnglib

*** Variables ***
${HOST}                http://int-sp-ath.5gtango.eu   #  the name of SP we want to use
${READY}       READY
${FILE_SOURCE_DIR}     ./packages   # to be modified and added accordingly if package is not on the same folder as test
${FILE_NAME}           eu.5gtango.test-ns-nsid1v.0.1.tgo    # The package to be uploaded and tested


*** Test Cases ***
Setting the SP Path
    Set SP Path     ${HOST}
    ${result} =     Sp Health Check
    Should Be True   ${result}
Upload the Package
    ${result} =     Upload Package      ${FILE_SOURCE_DIR}/${FILE_NAME}
    Should Be True     ${result[0]}
    ${service} =     Map Package On Service      ${result[1]}
    Should Be True     ${service[0]}
    Set Suite Variable     ${SERVICE_UUID}  ${service[1]}
    Log     ${SERVICE_UUID}
Deploying Service
    ${init} =   Service Instantiate     ${SERVICE_UUID}
    Log     ${init}
    Set Suite Variable     ${REQUEST}  ${init[1]}
    Log     ${REQUEST}
Wait For Ready
    Wait until Keyword Succeeds     3 min   5 sec   Check Status
    Set SIU
Scaling out VNF
###Scaling OUT code will go here once ready
Wait For Ready
    Wait until Keyword Succeeds     3 min   5 sec   Check Status
    Set SIU
Scaling in VNF
###Scaling IN code will go here once ready
Wait For Ready
    Wait until Keyword Succeeds     3 min   5 sec   Check Status
    Set SIU        
Terminate Service
    ${ter} =    Service Terminate   ${TERMINATE}
    Log     ${ter}
    Set Suite Variable     ${TERM_REQ}  ${ter[1]}
    Wait until Keyword Succeeds     2 min   5 sec   Check Terminate
Clean the Packages
    Remove all Packages


*** Keywords ***
Check Status
    ${status} =     Get Request     ${REQUEST}
    Should Be Equal    ${READY}  ${status[1]['status']}
Set SIU
    ${status} =     Get Request     ${REQUEST}
    Set Suite Variable     ${TERMINATE}    ${status[1]['instance_uuid']}
Check Terminate
    ${status} =     Get Request     ${TERM_REQ}
    Should Be Equal    ${READY}  ${status[1]['status']}
