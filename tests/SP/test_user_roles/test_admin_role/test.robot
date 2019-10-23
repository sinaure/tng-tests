*** Settings ***
Documentation   Test the User Management Admin Role
Library         tnglib
Library         Collections
Library         DateTime
Library         json

*** Variables ***
${SP_HOST}                http://pre-int-sp-ath.5gtango.eu  #  the name of SP we want to use
${READY}       READY

*** Test Cases ***
Setting the SP Path
	#From date to obtain GrayLogs
    ${from_date} =   Get Current Date
    Set Global Variable  ${from_date}
	
    Set SP Path     ${SP_HOST}
    ${result} =     Sp Health Check
    Should Be True  ${result}

Initial Admin Login
    ${initial_admin_token}=      Update Token      username=tango   password=admin
    Should Be True  ${initial_admin_token[0]}
    Set Suite Variable     ${initial_admin_token[1]}
	Set Global Variable  ${initial_admin_token[1]}
    Should Be True  ${initial_admin_token[0]}

Register a new user with admin role
    # Check if logged in user has admin role
    ${result} =      User Info         username=tango
    ${json_resp} = 	Set Variable	${result[1]}
    ${role_root}=    Get From Dictionary    ${json_resp}    role
    ${role}=    Get From Dictionary    ${role_root}    role
    # if user is admin continue to creation of admin user
    Run keyword If 	"${role}" == "admin" 	Register User

Logout Initial Admin User
    ${result}=      Logout User      token=${initial_admin_token[1]}
    Should be True      ${result[0]}

Check if token exists
    ${token}=      Get Token
    Run keyword If 	${token[0]} == True 	Check Valid Token
    Run keyword If 	${token[0]} == False 	Login

Obtain Packages
    ${packages}=      Get Packages
    Should be True      ${packages[0]}

Obtain Services
    ${services}=     get Service Descriptors
    Should be True      ${services[0]}

Obtain SLA Templates
    ${templates}=      get Sla Templates
    Should be True      ${templates[0]}

Obtain SLA Agreements
    ${agreements}=      Get Agreements      nsi_uuid=None
    Should be True      ${agreements[0]}

Obtain Policies
    ${policies}=      Get Policies
    Should be True      ${policies[0]}

Logout User
    ${result}=      Logout User      token=${valid_token[1]}
    Should be True      ${result[0]}

Delete user
    ${result}=      Delete User   username=${username}
    Should be True      ${result[0]}

Obtain GrayLogs
    ${to_date} =  Get Current Date
    Set Suite Variable  ${param_file}   True
    Get Logs  ${from_date}  ${to_date}  ${SP_HOST}  ${param_file}
	
*** Keywords ***
Check Status
    ${status} =     Get Request     ${REQUEST}
    Should Be Equal    ${READY}  ${status[1]['status']}

Check Valid Token
    ${valid_token}=    Is Token Valid
    # if token is still valid pass it to the headers
    if ${valid_token[0]} == True
        # pass token into headers
        add token to header(${valid_token[1]})
        Set Suite Variable     ${valid_token[1]}
	    Set Global Variable  ${valid_token[1]}
        Should Be True  ${valid_token[0]}
    # if token is not still valid attempt a new login
    else:
        Login
Login
    ${valid_token}=      Update Token      username=tango_test   password=admin_test
    Should Be True  ${valid_token[0]}
    Set Suite Variable     ${valid_token[1]}
	Set Global Variable  ${valid_token[1]}
    Should Be True  ${valid_token[0]}

Register User
    ${result} =      Register         username=tango_test   password=admin_test   name=tango_test   email=tango@tango.com   role=admin
    ${json_resp} = 	Set Variable	${result[1]}
    ${username}=    Get From Dictionary    ${json_resp}    username
    Set Suite Variable     ${username}
	Set Global Variable  ${username}
    Should Be True  ${result[0]}