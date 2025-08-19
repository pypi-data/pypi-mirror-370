# Auth

Types:

```python
from web_recruitment_sdk.types import Authorization, Role, AuthListRolesResponse
```

Methods:

- <code title="get /auth/roles">client.auth.<a href="./src/web_recruitment_sdk/resources/auth.py">list_roles</a>() -> <a href="./src/web_recruitment_sdk/types/auth_list_roles_response.py">AuthListRolesResponse</a></code>
- <code title="patch /auth/users/{user_id}">client.auth.<a href="./src/web_recruitment_sdk/resources/auth.py">update_user_authorization</a>(user_id, \*\*<a href="src/web_recruitment_sdk/types/auth_update_user_authorization_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/authorization.py">Authorization</a></code>

# Admin

Types:

```python
from web_recruitment_sdk.types import AdminListAccountsResponse
```

Methods:

- <code title="get /admin/accounts">client.admin.<a href="./src/web_recruitment_sdk/resources/admin/admin.py">list_accounts</a>() -> <a href="./src/web_recruitment_sdk/types/admin_list_accounts_response.py">AdminListAccountsResponse</a></code>

## Users

Types:

```python
from web_recruitment_sdk.types.admin import UserWithAccount, UserListResponse
```

Methods:

- <code title="get /admin/users/{user_id}">client.admin.users.<a href="./src/web_recruitment_sdk/resources/admin/users.py">retrieve</a>(user_id) -> <a href="./src/web_recruitment_sdk/types/admin/user_with_account.py">UserWithAccount</a></code>
- <code title="get /admin/users">client.admin.users.<a href="./src/web_recruitment_sdk/resources/admin/users.py">list</a>(\*\*<a href="src/web_recruitment_sdk/types/admin/user_list_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/admin/user_list_response.py">UserListResponse</a></code>
- <code title="delete /admin/users/{user_id}">client.admin.users.<a href="./src/web_recruitment_sdk/resources/admin/users.py">delete</a>(user_id) -> None</code>
- <code title="post /admin/users">client.admin.users.<a href="./src/web_recruitment_sdk/resources/admin/users.py">invite</a>(\*\*<a href="src/web_recruitment_sdk/types/admin/user_invite_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/admin/user_with_account.py">UserWithAccount</a></code>
- <code title="get /admin/users/me">client.admin.users.<a href="./src/web_recruitment_sdk/resources/admin/users.py">retrieve_current</a>() -> <a href="./src/web_recruitment_sdk/types/admin/user_with_account.py">UserWithAccount</a></code>
- <code title="patch /admin/users/me/tenant">client.admin.users.<a href="./src/web_recruitment_sdk/resources/admin/users.py">update_tenant</a>(\*\*<a href="src/web_recruitment_sdk/types/admin/user_update_tenant_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/admin/user_with_account.py">UserWithAccount</a></code>

# Patients

Types:

```python
from web_recruitment_sdk.types import (
    PatientRead,
    PatientUpdate,
    PatientListResponse,
    PatientGetByProtocolResponse,
    PatientGetExportsResponse,
    PatientGetProtocolMatchesResponse,
    PatientImportCsvResponse,
)
```

Methods:

- <code title="get /patients/{patient_id}">client.patients.<a href="./src/web_recruitment_sdk/resources/patients/patients.py">retrieve</a>(patient_id) -> <a href="./src/web_recruitment_sdk/types/patient_read.py">PatientRead</a></code>
- <code title="patch /patients/{patient_id}">client.patients.<a href="./src/web_recruitment_sdk/resources/patients/patients.py">update</a>(patient_id, \*\*<a href="src/web_recruitment_sdk/types/patient_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/patient_read.py">PatientRead</a></code>
- <code title="get /patients">client.patients.<a href="./src/web_recruitment_sdk/resources/patients/patients.py">list</a>(\*\*<a href="src/web_recruitment_sdk/types/patient_list_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/patient_list_response.py">PatientListResponse</a></code>
- <code title="get /patients/protocol/{protocol_id}">client.patients.<a href="./src/web_recruitment_sdk/resources/patients/patients.py">get_by_protocol</a>(protocol_id, \*\*<a href="src/web_recruitment_sdk/types/patient_get_by_protocol_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/patient_get_by_protocol_response.py">PatientGetByProtocolResponse</a></code>
- <code title="get /patients/{patient_id}/exports">client.patients.<a href="./src/web_recruitment_sdk/resources/patients/patients.py">get_exports</a>(patient_id) -> <a href="./src/web_recruitment_sdk/types/patient_get_exports_response.py">PatientGetExportsResponse</a></code>
- <code title="get /patients/{patient_id}/protocol-matches">client.patients.<a href="./src/web_recruitment_sdk/resources/patients/patients.py">get_protocol_matches</a>(patient_id) -> <a href="./src/web_recruitment_sdk/types/patient_get_protocol_matches_response.py">PatientGetProtocolMatchesResponse</a></code>
- <code title="post /patients/import-csv">client.patients.<a href="./src/web_recruitment_sdk/resources/patients/patients.py">import_csv</a>(\*\*<a href="src/web_recruitment_sdk/types/patient_import_csv_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/patient_import_csv_response.py">PatientImportCsvResponse</a></code>

## Notes

Types:

```python
from web_recruitment_sdk.types.patients import NoteRead, NoteListResponse
```

Methods:

- <code title="post /patients/{patient_id}/notes">client.patients.notes.<a href="./src/web_recruitment_sdk/resources/patients/notes.py">create</a>(path_patient_id, \*\*<a href="src/web_recruitment_sdk/types/patients/note_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/patients/note_read.py">NoteRead</a></code>
- <code title="get /patients/{patient_id}/notes">client.patients.notes.<a href="./src/web_recruitment_sdk/resources/patients/notes.py">list</a>(patient_id) -> <a href="./src/web_recruitment_sdk/types/patients/note_list_response.py">NoteListResponse</a></code>
- <code title="delete /patients/{patient_id}/notes/{note_id}">client.patients.notes.<a href="./src/web_recruitment_sdk/resources/patients/notes.py">delete</a>(note_id, \*, patient_id) -> None</code>

# PatientsByExternalID

Methods:

- <code title="get /patients_by_external_id/{external_id}">client.patients_by_external_id.<a href="./src/web_recruitment_sdk/resources/patients_by_external_id.py">retrieve</a>(external_id) -> <a href="./src/web_recruitment_sdk/types/patient_read.py">PatientRead</a></code>

# ProtocolParsing

Types:

```python
from web_recruitment_sdk.types import (
    ProtocolRead,
    ProtocolStatus,
    ProtocolParsingGetStatusesResponse,
)
```

Methods:

- <code title="get /protocol-parsing">client.protocol_parsing.<a href="./src/web_recruitment_sdk/resources/protocol_parsing.py">get_statuses</a>(\*\*<a href="src/web_recruitment_sdk/types/protocol_parsing_get_statuses_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/protocol_parsing_get_statuses_response.py">ProtocolParsingGetStatusesResponse</a></code>
- <code title="post /protocol-parsing">client.protocol_parsing.<a href="./src/web_recruitment_sdk/resources/protocol_parsing.py">upload</a>(\*\*<a href="src/web_recruitment_sdk/types/protocol_parsing_upload_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/protocol_read.py">ProtocolRead</a></code>

# MatchingJobs

Methods:

- <code title="post /matching_jobs/protocols/{protocol_id}">client.matching_jobs.<a href="./src/web_recruitment_sdk/resources/matching_jobs.py">start_protocol_matching_job</a>(protocol_id) -> <a href="./src/web_recruitment_sdk/types/protocol_read.py">ProtocolRead</a></code>

# CustomSearches

Types:

```python
from web_recruitment_sdk.types import (
    CustomSearchRead,
    FunnelStats,
    PatientMatch,
    CustomSearchListResponse,
    CustomSearchGetCriteriaInstancesResponse,
    CustomSearchRetrieveMatchesResponse,
    CustomSearchRetrieveSitesResponse,
)
```

Methods:

- <code title="post /custom-searches">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">create</a>(\*\*<a href="src/web_recruitment_sdk/types/custom_search_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_search_read.py">CustomSearchRead</a></code>
- <code title="get /custom-searches/{custom_search_id}">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">retrieve</a>(custom_search_id) -> <a href="./src/web_recruitment_sdk/types/custom_search_read.py">CustomSearchRead</a></code>
- <code title="patch /custom-searches/{custom_search_id}">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">update</a>(custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_search_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_search_read.py">CustomSearchRead</a></code>
- <code title="get /custom-searches">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">list</a>() -> <a href="./src/web_recruitment_sdk/types/custom_search_list_response.py">CustomSearchListResponse</a></code>
- <code title="delete /custom-searches/{custom_search_id}">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">delete</a>(custom_search_id) -> None</code>
- <code title="get /custom-searches/{custom_search_id}/criteria_instances">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">get_criteria_instances</a>(custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_search_get_criteria_instances_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_search_get_criteria_instances_response.py">CustomSearchGetCriteriaInstancesResponse</a></code>
- <code title="patch /v2/custom-searches/{custom_search_id}">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">patch</a>(custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_search_patch_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_search_read.py">CustomSearchRead</a></code>
- <code title="get /custom-searches/{custom_search_id}/funnel">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">retrieve_funnel</a>(custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_search_retrieve_funnel_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/funnel_stats.py">FunnelStats</a></code>
- <code title="get /custom-searches/{custom_search_id}/matches">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">retrieve_matches</a>(custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_search_retrieve_matches_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_search_retrieve_matches_response.py">CustomSearchRetrieveMatchesResponse</a></code>
- <code title="get /custom-searches/{custom_search_id}/sites">client.custom_searches.<a href="./src/web_recruitment_sdk/resources/custom_searches/custom_searches.py">retrieve_sites</a>(custom_search_id) -> <a href="./src/web_recruitment_sdk/types/custom_search_retrieve_sites_response.py">CustomSearchRetrieveSitesResponse</a></code>

## Criteria

Types:

```python
from web_recruitment_sdk.types.custom_searches import (
    CriteriaCreate,
    CriteriaRead,
    CriteriaStatus,
    CriterionRetrieveResponse,
    CriterionGetMatchingProgressResponse,
)
```

Methods:

- <code title="post /custom-searches/{custom_search_id}/criteria">client.custom_searches.criteria.<a href="./src/web_recruitment_sdk/resources/custom_searches/criteria.py">create</a>(path_custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_searches/criterion_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_searches/criteria_read.py">CriteriaRead</a></code>
- <code title="get /custom-searches/{custom_search_id}/criteria">client.custom_searches.criteria.<a href="./src/web_recruitment_sdk/resources/custom_searches/criteria.py">retrieve</a>(custom_search_id) -> <a href="./src/web_recruitment_sdk/types/custom_searches/criterion_retrieve_response.py">CriterionRetrieveResponse</a></code>
- <code title="put /custom-searches/{custom_search_id}/criteria/{criterion_id}">client.custom_searches.criteria.<a href="./src/web_recruitment_sdk/resources/custom_searches/criteria.py">update</a>(criterion_id, \*, path_custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_searches/criterion_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_searches/criteria_read.py">CriteriaRead</a></code>
- <code title="delete /custom-searches/{custom_search_id}/criteria/{criterion_id}">client.custom_searches.criteria.<a href="./src/web_recruitment_sdk/resources/custom_searches/criteria.py">delete</a>(criterion_id, \*, custom_search_id) -> None</code>
- <code title="get /custom-searches/{custom_search_id}/criteria/matching-progress">client.custom_searches.criteria.<a href="./src/web_recruitment_sdk/resources/custom_searches/criteria.py">get_matching_progress</a>(custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_searches/criterion_get_matching_progress_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_searches/criterion_get_matching_progress_response.py">CriterionGetMatchingProgressResponse</a></code>

## UserCriteria

Types:

```python
from web_recruitment_sdk.types.custom_searches import (
    UserProtocolCriteriaFilterUpdate,
    UserCriterionRetrieveResponse,
    UserCriterionUpdateResponse,
)
```

Methods:

- <code title="get /custom-searches/{custom_search_id}/user-criteria">client.custom_searches.user_criteria.<a href="./src/web_recruitment_sdk/resources/custom_searches/user_criteria.py">retrieve</a>(custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_searches/user_criterion_retrieve_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_searches/user_criterion_retrieve_response.py">UserCriterionRetrieveResponse</a></code>
- <code title="put /custom-searches/{custom_search_id}/user-criteria">client.custom_searches.user_criteria.<a href="./src/web_recruitment_sdk/resources/custom_searches/user_criteria.py">update</a>(custom_search_id, \*\*<a href="src/web_recruitment_sdk/types/custom_searches/user_criterion_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_searches/user_criterion_update_response.py">UserCriterionUpdateResponse</a></code>

# CustomCriteria

Types:

```python
from web_recruitment_sdk.types import CriteriaType, CustomCriterionListResponse
```

Methods:

- <code title="get /custom-criteria">client.custom_criteria.<a href="./src/web_recruitment_sdk/resources/custom_criteria.py">list</a>(\*\*<a href="src/web_recruitment_sdk/types/custom_criterion_list_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_criterion_list_response.py">CustomCriterionListResponse</a></code>

# Criteria

Methods:

- <code title="post /criteria">client.criteria.<a href="./src/web_recruitment_sdk/resources/criteria.py">create</a>(\*\*<a href="src/web_recruitment_sdk/types/criterion_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_searches/criteria_read.py">CriteriaRead</a></code>
- <code title="get /criteria/{criteria_id}">client.criteria.<a href="./src/web_recruitment_sdk/resources/criteria.py">retrieve</a>(criteria_id) -> <a href="./src/web_recruitment_sdk/types/custom_searches/criteria_read.py">CriteriaRead</a></code>
- <code title="put /criteria/{criterion_id}">client.criteria.<a href="./src/web_recruitment_sdk/resources/criteria.py">update</a>(criterion_id, \*\*<a href="src/web_recruitment_sdk/types/criterion_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_searches/criteria_read.py">CriteriaRead</a></code>

# Appointments

Types:

```python
from web_recruitment_sdk.types import Appointment, AppointmentListResponse
```

Methods:

- <code title="get /appointments/{trially_appointment_id}">client.appointments.<a href="./src/web_recruitment_sdk/resources/appointments.py">retrieve</a>(trially_appointment_id) -> <a href="./src/web_recruitment_sdk/types/appointment.py">Appointment</a></code>
- <code title="get /appointments">client.appointments.<a href="./src/web_recruitment_sdk/resources/appointments.py">list</a>(\*\*<a href="src/web_recruitment_sdk/types/appointment_list_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/appointment_list_response.py">AppointmentListResponse</a></code>

# Sites

Types:

```python
from web_recruitment_sdk.types import SiteRead, SiteListResponse
```

Methods:

- <code title="get /sites/{site_id}">client.sites.<a href="./src/web_recruitment_sdk/resources/sites.py">retrieve</a>(site_id) -> <a href="./src/web_recruitment_sdk/types/site_read.py">SiteRead</a></code>
- <code title="get /sites">client.sites.<a href="./src/web_recruitment_sdk/resources/sites.py">list</a>() -> <a href="./src/web_recruitment_sdk/types/site_list_response.py">SiteListResponse</a></code>

# Crio

Types:

```python
from web_recruitment_sdk.types import CrioListSitesResponse
```

Methods:

- <code title="get /crio/sites">client.crio.<a href="./src/web_recruitment_sdk/resources/crio.py">list_sites</a>(\*\*<a href="src/web_recruitment_sdk/types/crio_list_sites_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/crio_list_sites_response.py">CrioListSitesResponse</a></code>

# Health

Methods:

- <code title="get /health">client.health.<a href="./src/web_recruitment_sdk/resources/health.py">check</a>() -> object</code>

# System

Types:

```python
from web_recruitment_sdk.types import (
    CriteriaInstanceAnswer,
    CriteriaInstanceCreate,
    ExportStatus,
    SystemCreateCriteriaInstanceResponse,
    SystemCreateEntitySearchIndexResponse,
    SystemGetConnectionPoolStatusResponse,
    SystemGetPatientMatchDataResponse,
    SystemPatchPatientExportResponse,
    SystemSearchEntitiesResponse,
    SystemUpdateAccountResponse,
)
```

Methods:

- <code title="post /system/{tenant_db_name}/patient-match-data/bulk-search">client.system.<a href="./src/web_recruitment_sdk/resources/system/system.py">bulk_search_patient_match_data</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system_bulk_search_patient_match_data_params.py">params</a>) -> object</code>
- <code title="post /system/{tenant_db_name}/criteria_instances">client.system.<a href="./src/web_recruitment_sdk/resources/system/system.py">create_criteria_instance</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system_create_criteria_instance_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system_create_criteria_instance_response.py">SystemCreateCriteriaInstanceResponse</a></code>
- <code title="post /system/{tenant_db_name}/entity-search/index">client.system.<a href="./src/web_recruitment_sdk/resources/system/system.py">create_entity_search_index</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system_create_entity_search_index_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system_create_entity_search_index_response.py">SystemCreateEntitySearchIndexResponse</a></code>
- <code title="get /system/{db_name}/connection-pool-status">client.system.<a href="./src/web_recruitment_sdk/resources/system/system.py">get_connection_pool_status</a>(db_name) -> str</code>
- <code title="post /system/{tenant_db_name}/patient-match-data">client.system.<a href="./src/web_recruitment_sdk/resources/system/system.py">get_patient_match_data</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system_get_patient_match_data_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system_get_patient_match_data_response.py">SystemGetPatientMatchDataResponse</a></code>
- <code title="patch /system/{tenant_db_name}/patient-ctms-exports/{patient_ctms_export_id}">client.system.<a href="./src/web_recruitment_sdk/resources/system/system.py">patch_patient_export</a>(patient_ctms_export_id, \*, tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system_patch_patient_export_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system_patch_patient_export_response.py">SystemPatchPatientExportResponse</a></code>
- <code title="get /system/ping">client.system.<a href="./src/web_recruitment_sdk/resources/system/system.py">ping</a>() -> object</code>
- <code title="post /system/{tenant_db_name}/entity-search">client.system.<a href="./src/web_recruitment_sdk/resources/system/system.py">search_entities</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system_search_entities_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system_search_entities_response.py">SystemSearchEntitiesResponse</a></code>
- <code title="patch /system/{tenant_db_name}/account">client.system.<a href="./src/web_recruitment_sdk/resources/system/system.py">update_account</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system_update_account_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system_update_account_response.py">SystemUpdateAccountResponse</a></code>

## Protocols

Types:

```python
from web_recruitment_sdk.types.system import ProtocolListResponse, ProtocolGetCriteriaResponse
```

Methods:

- <code title="get /system/{tenant_db_name}/protocols/{protocol_id}">client.system.protocols.<a href="./src/web_recruitment_sdk/resources/system/protocols/protocols.py">retrieve</a>(protocol_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/protocol_read.py">ProtocolRead</a></code>
- <code title="get /system/{tenant_db_name}/protocols">client.system.protocols.<a href="./src/web_recruitment_sdk/resources/system/protocols/protocols.py">list</a>(tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/protocol_list_response.py">ProtocolListResponse</a></code>
- <code title="get /system/{tenant_db_name}/protocols/{protocol_id}/criteria">client.system.protocols.<a href="./src/web_recruitment_sdk/resources/system/protocols/protocols.py">get_criteria</a>(protocol_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/protocol_get_criteria_response.py">ProtocolGetCriteriaResponse</a></code>
- <code title="post /system/{tenant_db_name}/protocols/refresh-patient-matches">client.system.protocols.<a href="./src/web_recruitment_sdk/resources/system/protocols/protocols.py">refresh_patient_matches</a>(tenant_db_name) -> object</code>

### MatchingJobs

Methods:

- <code title="post /system/{tenant_db_name}/protocols/{protocol_id}/matching_jobs">client.system.protocols.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/protocols/matching_jobs.py">create</a>(protocol_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/protocol_read.py">ProtocolRead</a></code>
- <code title="delete /system/{tenant_db_name}/protocols/{protocol_id}/matching_jobs">client.system.protocols.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/protocols/matching_jobs.py">delete</a>(protocol_id, \*, tenant_db_name) -> object</code>

## Criteria

Types:

```python
from web_recruitment_sdk.types.system import (
    CriterionListResponse,
    CriterionGetPatientsToMatchResponse,
)
```

Methods:

- <code title="get /system/{tenant_db_name}/criteria">client.system.criteria.<a href="./src/web_recruitment_sdk/resources/system/criteria/criteria.py">list</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/criterion_list_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/criterion_list_response.py">CriterionListResponse</a></code>
- <code title="get /system/{tenant_db_name}/criteria/{criteria_id}/patients-to-match">client.system.criteria.<a href="./src/web_recruitment_sdk/resources/system/criteria/criteria.py">get_patients_to_match</a>(criteria_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/criterion_get_patients_to_match_response.py">CriterionGetPatientsToMatchResponse</a></code>

### MatchingJobs

Methods:

- <code title="post /system/{tenant_db_name}/criteria/{criterion_id}/matching_jobs">client.system.criteria.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/criteria/matching_jobs.py">create</a>(criterion_id, \*, tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/criteria/matching_job_create_params.py">params</a>) -> object</code>
- <code title="delete /system/{tenant_db_name}/criteria/{criterion_id}/matching_jobs">client.system.criteria.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/criteria/matching_jobs.py">delete</a>(criterion_id, \*, tenant_db_name) -> object</code>

## ProtocolParsing

Methods:

- <code title="post /system/{tenant_db_name}/protocol-parsing/{job_id}/error">client.system.protocol_parsing.<a href="./src/web_recruitment_sdk/resources/system/protocol_parsing.py">set_error</a>(job_id, \*, tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/protocol_parsing_set_error_params.py">params</a>) -> object</code>
- <code title="post /system/{tenant_db_name}/protocol-parsing/{job_id}/success">client.system.protocol_parsing.<a href="./src/web_recruitment_sdk/resources/system/protocol_parsing.py">set_success</a>(job_id, \*, tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/protocol_parsing_set_success_params.py">params</a>) -> object</code>

## Sites

Types:

```python
from web_recruitment_sdk.types.system import SiteCreate, SiteListResponse
```

Methods:

- <code title="post /system/{tenant_db_name}/sites">client.system.sites.<a href="./src/web_recruitment_sdk/resources/system/sites/sites.py">create</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/site_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/site_read.py">SiteRead</a></code>
- <code title="get /system/{tenant_db_name}/sites/{site_id}">client.system.sites.<a href="./src/web_recruitment_sdk/resources/system/sites/sites.py">retrieve</a>(site_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/site_read.py">SiteRead</a></code>
- <code title="patch /system/{tenant_db_name}/sites/{site_id}">client.system.sites.<a href="./src/web_recruitment_sdk/resources/system/sites/sites.py">update</a>(site_id, \*, tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/site_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/site_read.py">SiteRead</a></code>
- <code title="get /system/{tenant_db_name}/sites">client.system.sites.<a href="./src/web_recruitment_sdk/resources/system/sites/sites.py">list</a>(tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/site_list_response.py">SiteListResponse</a></code>
- <code title="delete /system/{tenant_db_name}/sites/{site_id}">client.system.sites.<a href="./src/web_recruitment_sdk/resources/system/sites/sites.py">delete</a>(site_id, \*, tenant_db_name) -> object</code>

### Trially

Types:

```python
from web_recruitment_sdk.types.system.sites import (
    TriallyGetActiveCustomSearchesResponse,
    TriallyGetActiveProtocolsResponse,
)
```

Methods:

- <code title="get /system/{tenant_db_name}/sites/trially/{trially_site_id}/custom-searches">client.system.sites.trially.<a href="./src/web_recruitment_sdk/resources/system/sites/trially.py">get_active_custom_searches</a>(trially_site_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/sites/trially_get_active_custom_searches_response.py">TriallyGetActiveCustomSearchesResponse</a></code>
- <code title="get /system/{tenant_db_name}/sites/trially/{trially_site_id}/protocols">client.system.sites.trially.<a href="./src/web_recruitment_sdk/resources/system/sites/trially.py">get_active_protocols</a>(trially_site_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/sites/trially_get_active_protocols_response.py">TriallyGetActiveProtocolsResponse</a></code>

## Patients

Types:

```python
from web_recruitment_sdk.types.system import PatientCreate
```

Methods:

- <code title="post /system/{tenant_db_name}/patients">client.system.patients.<a href="./src/web_recruitment_sdk/resources/system/patients/patients.py">create</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patient_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/patient_read.py">PatientRead</a></code>
- <code title="patch /system/{tenant_db_name}/patients/{patient_id}">client.system.patients.<a href="./src/web_recruitment_sdk/resources/system/patients/patients.py">update</a>(patient_id, \*, tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patient_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/patient_read.py">PatientRead</a></code>

### Bulk

Types:

```python
from web_recruitment_sdk.types.system.patients import BulkInsertResult
```

Methods:

- <code title="put /system/{tenant_db_name}/patients/bulk/appointments">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">create_appointments</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_create_appointments_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/allergies">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_allergies</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_allergies_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/conditions">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_conditions</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_conditions_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/patient_demographics">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_demographics</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_demographics_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/patient_entity">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_entity</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_entity_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/entity_search">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_entity_search</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_entity_search_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/patient_history">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_history</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_history_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/lab_results">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_lab_results</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_lab_results_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/medications">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_medications</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_medications_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/procedures">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_procedures</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_procedures_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk/patient_vitals">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">update_vitals</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_update_vitals_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>
- <code title="put /system/{tenant_db_name}/patients/bulk">client.system.patients.bulk.<a href="./src/web_recruitment_sdk/resources/system/patients/bulk.py">upsert</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/patients/bulk_upsert_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>

## Appointments

Types:

```python
from web_recruitment_sdk.types.system import AppointmentListResponse
```

Methods:

- <code title="get /system/{tenant_db_name}/appointments">client.system.appointments.<a href="./src/web_recruitment_sdk/resources/system/appointments.py">list</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/appointment_list_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/appointment_list_response.py">AppointmentListResponse</a></code>
- <code title="delete /system/{tenant_db_name}/appointments/{trially_appointment_id}">client.system.appointments.<a href="./src/web_recruitment_sdk/resources/system/appointments.py">delete</a>(trially_appointment_id, \*, tenant_db_name) -> None</code>

## Bulk

Methods:

- <code title="put /system/{tenant_db_name}/bulk/criteria_instances">client.system.bulk.<a href="./src/web_recruitment_sdk/resources/system/bulk.py">update_criteria_instances</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/bulk_update_criteria_instances_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/patients/bulk_insert_result.py">BulkInsertResult</a></code>

## MatchingJobs

Types:

```python
from web_recruitment_sdk.types.system import ExternalJobStatus, MatchingJobRead, MatchingTaskRead
```

Methods:

- <code title="get /system/{tenant_db_name}/matching_jobs/{matching_job_id}">client.system.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/matching_jobs.py">retrieve</a>(matching_job_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/matching_job_read.py">MatchingJobRead</a></code>
- <code title="post /system/{tenant_db_name}/matching_jobs/{matching_job_id}/cancel">client.system.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/matching_jobs.py">cancel</a>(matching_job_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/matching_job_read.py">MatchingJobRead</a></code>
- <code title="post /system/{tenant_db_name}/matching_jobs/complete_task">client.system.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/matching_jobs.py">complete_task</a>(path_tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/matching_job_complete_task_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/matching_task_read.py">MatchingTaskRead</a></code>
- <code title="post /system/{tenant_db_name}/matching_jobs/error_task">client.system.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/matching_jobs.py">error_task</a>(path_tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/matching_job_error_task_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/matching_task_read.py">MatchingTaskRead</a></code>
- <code title="post /system/{tenant_db_name}/matching_jobs/process">client.system.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/matching_jobs.py">process</a>(path_tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/matching_job_process_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/matching_job_read.py">MatchingJobRead</a></code>
- <code title="post /system/{tenant_db_name}/matching_jobs/start_all">client.system.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/matching_jobs.py">start_all</a>(tenant_db_name) -> object</code>

## Cache

Methods:

- <code title="get /system/{tenant_db_name}/cache/clear">client.system.cache.<a href="./src/web_recruitment_sdk/resources/system/cache.py">clear</a>(tenant_db_name) -> object</code>

## CustomSearches

Types:

```python
from web_recruitment_sdk.types.system import (
    CustomSearchListResponse,
    CustomSearchRetrieveCriteriaResponse,
)
```

Methods:

- <code title="get /system/{tenant_db_name}/custom-searches">client.system.custom_searches.<a href="./src/web_recruitment_sdk/resources/system/custom_searches/custom_searches.py">list</a>(tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/custom_search_list_response.py">CustomSearchListResponse</a></code>
- <code title="post /system/{tenant_db_name}/custom-searches/refresh-patient-matches">client.system.custom_searches.<a href="./src/web_recruitment_sdk/resources/system/custom_searches/custom_searches.py">refresh_patient_matches</a>(tenant_db_name) -> object</code>
- <code title="get /system/{tenant_db_name}/custom-searches/{custom_search_id}/criteria">client.system.custom_searches.<a href="./src/web_recruitment_sdk/resources/system/custom_searches/custom_searches.py">retrieve_criteria</a>(custom_search_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/system/custom_search_retrieve_criteria_response.py">CustomSearchRetrieveCriteriaResponse</a></code>

### MatchingJobs

Methods:

- <code title="post /system/{tenant_db_name}/custom-searches/{custom_search_id}/matching_jobs">client.system.custom_searches.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/custom_searches/matching_jobs.py">create</a>(custom_search_id, \*, tenant_db_name) -> <a href="./src/web_recruitment_sdk/types/custom_search_read.py">CustomSearchRead</a></code>
- <code title="delete /system/{tenant_db_name}/custom-searches/{custom_search_id}/matching_jobs">client.system.custom_searches.matching_jobs.<a href="./src/web_recruitment_sdk/resources/system/custom_searches/matching_jobs.py">delete</a>(custom_search_id, \*, tenant_db_name) -> object</code>

## Carequality

### Documents

Methods:

- <code title="post /system/{tenant_db_name}/carequality/documents/uploaded">client.system.carequality.documents.<a href="./src/web_recruitment_sdk/resources/system/carequality/documents.py">confirm_upload</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/carequality/document_confirm_upload_params.py">params</a>) -> object</code>

## Outreach

### Task

Types:

```python
from web_recruitment_sdk.types.system.outreach import TaskStartHandlerResponse
```

Methods:

- <code title="post /system/{tenant_db_name}/outreach/task/start">client.system.outreach.task.<a href="./src/web_recruitment_sdk/resources/system/outreach/task.py">start_handler</a>(tenant_db_name, \*\*<a href="src/web_recruitment_sdk/types/system/outreach/task_start_handler_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/system/outreach/task_start_handler_response.py">TaskStartHandlerResponse</a></code>

# FeatureFlags

Types:

```python
from web_recruitment_sdk.types import FeatureFlagRetrieveResponse
```

Methods:

- <code title="get /feature-flags/{flag_key}">client.feature_flags.<a href="./src/web_recruitment_sdk/resources/feature_flags.py">retrieve</a>(flag_key) -> <a href="./src/web_recruitment_sdk/types/feature_flag_retrieve_response.py">FeatureFlagRetrieveResponse</a></code>

# Dashboards

Types:

```python
from web_recruitment_sdk.types import ChartResponse
```

Methods:

- <code title="get /dashboards/age-distribution">client.dashboards.<a href="./src/web_recruitment_sdk/resources/dashboards.py">get_age_distribution</a>(\*\*<a href="src/web_recruitment_sdk/types/dashboard_get_age_distribution_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/chart_response.py">ChartResponse</a></code>
- <code title="get /dashboards/ethnic-distribution">client.dashboards.<a href="./src/web_recruitment_sdk/resources/dashboards.py">get_ethnic_distribution</a>(\*\*<a href="src/web_recruitment_sdk/types/dashboard_get_ethnic_distribution_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/chart_response.py">ChartResponse</a></code>
- <code title="get /dashboards/gender-distribution">client.dashboards.<a href="./src/web_recruitment_sdk/resources/dashboards.py">get_gender_distribution</a>(\*\*<a href="src/web_recruitment_sdk/types/dashboard_get_gender_distribution_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/chart_response.py">ChartResponse</a></code>
- <code title="get /dashboards/race-distribution">client.dashboards.<a href="./src/web_recruitment_sdk/resources/dashboards.py">get_race_distribution</a>(\*\*<a href="src/web_recruitment_sdk/types/dashboard_get_race_distribution_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/chart_response.py">ChartResponse</a></code>
- <code title="get /dashboards/conditions">client.dashboards.<a href="./src/web_recruitment_sdk/resources/dashboards.py">get_top_conditions</a>(\*\*<a href="src/web_recruitment_sdk/types/dashboard_get_top_conditions_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/chart_response.py">ChartResponse</a></code>
- <code title="get /dashboards/medications">client.dashboards.<a href="./src/web_recruitment_sdk/resources/dashboards.py">get_top_medications</a>(\*\*<a href="src/web_recruitment_sdk/types/dashboard_get_top_medications_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/chart_response.py">ChartResponse</a></code>
- <code title="get /dashboards/procedures">client.dashboards.<a href="./src/web_recruitment_sdk/resources/dashboards.py">get_top_procedures</a>(\*\*<a href="src/web_recruitment_sdk/types/dashboard_get_top_procedures_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/chart_response.py">ChartResponse</a></code>

# Protocols

Types:

```python
from web_recruitment_sdk.types import (
    ProtocolParsingRead,
    ProtocolParsingStatus,
    ProtocolListResponse,
    ProtocolGetCriteriaInstancesResponse,
    ProtocolGetMatchesResponse,
)
```

Methods:

- <code title="get /protocols/{protocol_id}">client.protocols.<a href="./src/web_recruitment_sdk/resources/protocols/protocols.py">retrieve</a>(protocol_id) -> <a href="./src/web_recruitment_sdk/types/protocol_read.py">ProtocolRead</a></code>
- <code title="patch /protocols/{protocol_id}">client.protocols.<a href="./src/web_recruitment_sdk/resources/protocols/protocols.py">update</a>(protocol_id, \*\*<a href="src/web_recruitment_sdk/types/protocol_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/protocol_read.py">ProtocolRead</a></code>
- <code title="get /protocols">client.protocols.<a href="./src/web_recruitment_sdk/resources/protocols/protocols.py">list</a>() -> <a href="./src/web_recruitment_sdk/types/protocol_list_response.py">ProtocolListResponse</a></code>
- <code title="delete /protocols/{protocol_id}">client.protocols.<a href="./src/web_recruitment_sdk/resources/protocols/protocols.py">delete</a>(protocol_id) -> None</code>
- <code title="get /protocols/{protocol_id}/criteria_instances">client.protocols.<a href="./src/web_recruitment_sdk/resources/protocols/protocols.py">get_criteria_instances</a>(protocol_id, \*\*<a href="src/web_recruitment_sdk/types/protocol_get_criteria_instances_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/protocol_get_criteria_instances_response.py">ProtocolGetCriteriaInstancesResponse</a></code>
- <code title="get /protocols/{protocol_id}/funnel">client.protocols.<a href="./src/web_recruitment_sdk/resources/protocols/protocols.py">get_funnel</a>(protocol_id, \*\*<a href="src/web_recruitment_sdk/types/protocol_get_funnel_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/funnel_stats.py">FunnelStats</a></code>
- <code title="get /protocols/{protocol_id}/matches">client.protocols.<a href="./src/web_recruitment_sdk/resources/protocols/protocols.py">get_matches</a>(protocol_id, \*\*<a href="src/web_recruitment_sdk/types/protocol_get_matches_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/protocol_get_matches_response.py">ProtocolGetMatchesResponse</a></code>
- <code title="get /protocols/{protocol_id}/protocol-parsing">client.protocols.<a href="./src/web_recruitment_sdk/resources/protocols/protocols.py">get_parsing_status</a>(protocol_id) -> <a href="./src/web_recruitment_sdk/types/protocol_parsing_read.py">ProtocolParsingRead</a></code>
- <code title="post /protocols/{protocol_id}/ready">client.protocols.<a href="./src/web_recruitment_sdk/resources/protocols/protocols.py">set_ready</a>(protocol_id) -> <a href="./src/web_recruitment_sdk/types/protocol_read.py">ProtocolRead</a></code>

## Sites

Types:

```python
from web_recruitment_sdk.types.protocols import SiteCreateResponse, SiteListResponse
```

Methods:

- <code title="post /protocols/{protocol_id}/sites/{site_id}">client.protocols.sites.<a href="./src/web_recruitment_sdk/resources/protocols/sites.py">create</a>(site_id, \*, protocol_id) -> <a href="./src/web_recruitment_sdk/types/protocols/site_create_response.py">SiteCreateResponse</a></code>
- <code title="get /protocols/{protocol_id}/sites">client.protocols.sites.<a href="./src/web_recruitment_sdk/resources/protocols/sites.py">list</a>(protocol_id) -> <a href="./src/web_recruitment_sdk/types/protocols/site_list_response.py">SiteListResponse</a></code>
- <code title="delete /protocols/{protocol_id}/sites/{site_id}">client.protocols.sites.<a href="./src/web_recruitment_sdk/resources/protocols/sites.py">delete</a>(site_id, \*, protocol_id) -> None</code>

## Criteria

Types:

```python
from web_recruitment_sdk.types.protocols import (
    CriterionListResponse,
    CriterionGetMatchingProgressResponse,
)
```

Methods:

- <code title="post /protocols/{protocol_id}/criteria">client.protocols.criteria.<a href="./src/web_recruitment_sdk/resources/protocols/criteria.py">create</a>(path_protocol_id, \*\*<a href="src/web_recruitment_sdk/types/protocols/criterion_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_searches/criteria_read.py">CriteriaRead</a></code>
- <code title="put /protocols/{protocol_id}/criteria/{criterion_id}">client.protocols.criteria.<a href="./src/web_recruitment_sdk/resources/protocols/criteria.py">update</a>(criterion_id, \*, path_protocol_id, \*\*<a href="src/web_recruitment_sdk/types/protocols/criterion_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/custom_searches/criteria_read.py">CriteriaRead</a></code>
- <code title="get /protocols/{protocol_id}/criteria">client.protocols.criteria.<a href="./src/web_recruitment_sdk/resources/protocols/criteria.py">list</a>(protocol_id) -> <a href="./src/web_recruitment_sdk/types/protocols/criterion_list_response.py">CriterionListResponse</a></code>
- <code title="delete /protocols/{protocol_id}/criteria/{criterion_id}">client.protocols.criteria.<a href="./src/web_recruitment_sdk/resources/protocols/criteria.py">delete</a>(criterion_id, \*, protocol_id) -> None</code>
- <code title="get /protocols/{protocol_id}/criteria/matching-progress">client.protocols.criteria.<a href="./src/web_recruitment_sdk/resources/protocols/criteria.py">get_matching_progress</a>(protocol_id, \*\*<a href="src/web_recruitment_sdk/types/protocols/criterion_get_matching_progress_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/protocols/criterion_get_matching_progress_response.py">CriterionGetMatchingProgressResponse</a></code>

## UserCriteria

Types:

```python
from web_recruitment_sdk.types.protocols import (
    UserCriterionUpdateResponse,
    UserCriterionListResponse,
)
```

Methods:

- <code title="put /protocols/{protocol_id}/user-criteria">client.protocols.user_criteria.<a href="./src/web_recruitment_sdk/resources/protocols/user_criteria.py">update</a>(protocol_id, \*\*<a href="src/web_recruitment_sdk/types/protocols/user_criterion_update_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/protocols/user_criterion_update_response.py">UserCriterionUpdateResponse</a></code>
- <code title="get /protocols/{protocol_id}/user-criteria">client.protocols.user_criteria.<a href="./src/web_recruitment_sdk/resources/protocols/user_criteria.py">list</a>(protocol_id, \*\*<a href="src/web_recruitment_sdk/types/protocols/user_criterion_list_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/protocols/user_criterion_list_response.py">UserCriterionListResponse</a></code>

# ExportJobs

Types:

```python
from web_recruitment_sdk.types import (
    ExportJobCreateResponse,
    ExportJobListResponse,
    ExportJobRetrievePatientsResponse,
)
```

Methods:

- <code title="post /export-job/sites/{site_id}">client.export_jobs.<a href="./src/web_recruitment_sdk/resources/export_jobs.py">create</a>(site_id, \*\*<a href="src/web_recruitment_sdk/types/export_job_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/export_job_create_response.py">ExportJobCreateResponse</a></code>
- <code title="get /export-jobs">client.export_jobs.<a href="./src/web_recruitment_sdk/resources/export_jobs.py">list</a>() -> <a href="./src/web_recruitment_sdk/types/export_job_list_response.py">ExportJobListResponse</a></code>
- <code title="get /export-jobs/{export_job_id}/patients">client.export_jobs.<a href="./src/web_recruitment_sdk/resources/export_jobs.py">retrieve_patients</a>(export_job_id) -> <a href="./src/web_recruitment_sdk/types/export_job_retrieve_patients_response.py">ExportJobRetrievePatientsResponse</a></code>

# External

## Carequality

Types:

```python
from web_recruitment_sdk.types.external import CarequalityHealthCheckResponse
```

Methods:

- <code title="get /external/carequality/health">client.external.carequality.<a href="./src/web_recruitment_sdk/resources/external/carequality/carequality.py">health_check</a>() -> <a href="./src/web_recruitment_sdk/types/external/carequality_health_check_response.py">CarequalityHealthCheckResponse</a></code>

### Patients

Types:

```python
from web_recruitment_sdk.types.external.carequality import (
    PatientRetrieveResponse,
    PatientSearchResponse,
)
```

Methods:

- <code title="get /external/carequality/patients/{carequality_patient_id}">client.external.carequality.patients.<a href="./src/web_recruitment_sdk/resources/external/carequality/patients.py">retrieve</a>(carequality_patient_id) -> <a href="./src/web_recruitment_sdk/types/external/carequality/patient_retrieve_response.py">PatientRetrieveResponse</a></code>
- <code title="post /external/carequality/patients/search">client.external.carequality.patients.<a href="./src/web_recruitment_sdk/resources/external/carequality/patients.py">search</a>(\*\*<a href="src/web_recruitment_sdk/types/external/carequality/patient_search_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/external/carequality/patient_search_response.py">PatientSearchResponse</a></code>

### Documents

Types:

```python
from web_recruitment_sdk.types.external.carequality import DocumentGenerateUploadURLResponse
```

Methods:

- <code title="post /external/carequality/documents/upload-url">client.external.carequality.documents.<a href="./src/web_recruitment_sdk/resources/external/carequality/documents.py">generate_upload_url</a>(\*\*<a href="src/web_recruitment_sdk/types/external/carequality/document_generate_upload_url_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/external/carequality/document_generate_upload_url_response.py">DocumentGenerateUploadURLResponse</a></code>

# Outreach

Types:

```python
from web_recruitment_sdk.types import OutreachTriggerCallResponse
```

Methods:

- <code title="post /outreach/make-call">client.outreach.<a href="./src/web_recruitment_sdk/resources/outreach/outreach.py">trigger_call</a>(\*\*<a href="src/web_recruitment_sdk/types/outreach_trigger_call_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/outreach_trigger_call_response.py">OutreachTriggerCallResponse</a></code>

## Campaigns

Types:

```python
from web_recruitment_sdk.types.outreach import (
    CampaignCreateResponse,
    CampaignListResponse,
    CampaignPauseResponse,
    CampaignStartResponse,
)
```

Methods:

- <code title="post /outreach/campaigns">client.outreach.campaigns.<a href="./src/web_recruitment_sdk/resources/outreach/campaigns/campaigns.py">create</a>(\*\*<a href="src/web_recruitment_sdk/types/outreach/campaign_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/outreach/campaign_create_response.py">CampaignCreateResponse</a></code>
- <code title="get /outreach/campaigns">client.outreach.campaigns.<a href="./src/web_recruitment_sdk/resources/outreach/campaigns/campaigns.py">list</a>() -> <a href="./src/web_recruitment_sdk/types/outreach/campaign_list_response.py">CampaignListResponse</a></code>
- <code title="post /outreach/campaigns/{campaign_id}/pause">client.outreach.campaigns.<a href="./src/web_recruitment_sdk/resources/outreach/campaigns/campaigns.py">pause</a>(campaign_id) -> <a href="./src/web_recruitment_sdk/types/outreach/campaign_pause_response.py">CampaignPauseResponse</a></code>
- <code title="post /outreach/campaigns/{campaign_id}/start">client.outreach.campaigns.<a href="./src/web_recruitment_sdk/resources/outreach/campaigns/campaigns.py">start</a>(campaign_id) -> <a href="./src/web_recruitment_sdk/types/outreach/campaign_start_response.py">CampaignStartResponse</a></code>

### Patients

Types:

```python
from web_recruitment_sdk.types.outreach.campaigns import PatientListResponse
```

Methods:

- <code title="get /outreach/campaigns/{campaign_id}/patients">client.outreach.campaigns.patients.<a href="./src/web_recruitment_sdk/resources/outreach/campaigns/patients/patients.py">list</a>(campaign_id) -> <a href="./src/web_recruitment_sdk/types/outreach/campaigns/patient_list_response.py">PatientListResponse</a></code>

#### Actions

Types:

```python
from web_recruitment_sdk.types.outreach.campaigns.patients import (
    ActionCreateResponse,
    ActionListResponse,
)
```

Methods:

- <code title="post /outreach/campaigns/{campaign_id}/patients/{patient_id}/actions">client.outreach.campaigns.patients.actions.<a href="./src/web_recruitment_sdk/resources/outreach/campaigns/patients/actions.py">create</a>(patient_id, \*, campaign_id, \*\*<a href="src/web_recruitment_sdk/types/outreach/campaigns/patients/action_create_params.py">params</a>) -> <a href="./src/web_recruitment_sdk/types/outreach/campaigns/patients/action_create_response.py">ActionCreateResponse</a></code>
- <code title="get /outreach/campaigns/{campaign_id}/patients/{patient_id}/actions">client.outreach.campaigns.patients.actions.<a href="./src/web_recruitment_sdk/resources/outreach/campaigns/patients/actions.py">list</a>(patient_id, \*, campaign_id) -> <a href="./src/web_recruitment_sdk/types/outreach/campaigns/patients/action_list_response.py">ActionListResponse</a></code>

# Webhooks

Types:

```python
from web_recruitment_sdk.types import WebhookLogPayloadResponse
```

Methods:

- <code title="post /webhooks/log">client.webhooks.<a href="./src/web_recruitment_sdk/resources/webhooks/webhooks.py">log_payload</a>() -> <a href="./src/web_recruitment_sdk/types/webhook_log_payload_response.py">WebhookLogPayloadResponse</a></code>

## Carequality

### Documents

Methods:

- <code title="post /webhooks/carequality/documents/uploaded">client.webhooks.carequality.documents.<a href="./src/web_recruitment_sdk/resources/webhooks/carequality/documents.py">confirm_upload</a>(\*\*<a href="src/web_recruitment_sdk/types/webhooks/carequality/document_confirm_upload_params.py">params</a>) -> object</code>
