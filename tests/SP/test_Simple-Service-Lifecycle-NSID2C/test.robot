*** Settings ***
Documentation     Test suite for uploading a package to the SP platform
Library           tnglib
Library         Collections
Library         DateTime

*** Variables ***
${HOST}                http://pre-int-sp-ath.5gtango.eu   #  the name of SP we want to use
${READY}       READY
${FILE_SOURCE_DIR}     ./packages   # to be modified and added accordingly if package is not on the same folder as test
${FILE_NAME}           eu.5gtango.test-ns-nsid2c.0.1.tgo    # The package to be uploaded and tested
${NS_PACKAGE_SHORT_NAME}	test-ns-nsid2c

*** Test Cases ***
Setting the SP Path
	    #From date to obtain GrayLogs
    ${from_date} =   Get Current Date
    Set Global Variable  ${from_date}
    
    Set SP Path     ${HOST}
    ${result} =     Sp Health Check
    Should Be True   ${result}
    
Clean the Packages
    @{PACKAGES} =   Get Packages
    FOR     ${PACKAGE}  IN  @{PACKAGES[1]}
        Run Keyword If     '${PACKAGE['name']}'== '${NS_PACKAGE_SHORT_NAME}'    Remove Package      ${PACKAGE['package_uuid']}
    END  
    
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
Terminate Service
    ${ter} =    Service Terminate   ${TERMINATE}
    Log     ${ter}
    Set Suite Variable     ${TERM_REQ}  ${ter[1]}
    Wait until Keyword Succeeds     2 min   5 sec   Check Terminate
    
Obtain GrayLogs
    ${to_date} =  Get Current Date
    Set Suite Variable  ${param_file}   True
    Get Logs  ${from_date}  ${to_date}  ${HOST}  ${param_file}


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
