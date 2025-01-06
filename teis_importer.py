import csv
import random
import time
import pandas as pd
import numpy as np
import math

from dhis2 import Api
from dhis2 import RequestException, setup_logger, logger

from Utils import project_utils

# login credentials for the dhis2 api
url = 'https://hmis.moh.gov.rw/idsr'
# url = 'https://online.hisprwanda.org/idsrvpd'
username = ''
password = ''

# org_unit_id = 'Hjw70Lodtf2'
upload_user = ''
file_name = 'afp_cleaned_2.csv'

change_date = True

# DHIS2 API connection
api = Api(url, username, password)

# setup the logger
setup_logger()


def make_new_patientID(year):
    response_id = ''
    try:
        response_id = api.get('trackedEntityAttributes/XuuupMIvUeK/generate')
    except:
        logger.error('Failed generate the uid')
    unique_id = response_id.json()
    unique_id = unique_id.get('value')

    patient_id_new = str('A809/RW'+year+'/' + unique_id)
    return patient_id_new


def upload_dhis2_tracked_entity_instances():
    counter = 0
    chunk_size = 2500  # dividing a large file in small chunks for efficiency
    file_chunks = pd.read_csv(file_name, chunksize=chunk_size)
    for chunk in file_chunks:
        start = time.time()
        for row in chunk.values:
            counter = counter + 1
            patient_id = ''
            try:
                # attributes
                date_registered = '01/01/1990' if str(row[15]) == 'nan' else str(row[15])
                disease = 'Acute Flaccid Paralysis'
                reporting_during_outbreak = ''
                outbreak_code = ''
                epid_number = '' if str(row[0]) == 'nan' else str(row[0])
                date_sample_received = '' if str(row[42]) == 'nan' else str(row[42])
                patient_id = make_new_patientID(year=date_sample_received.split('-')[0][-2:])
                org_unit_id = '' if str(row[6]) == 'nan' else str(row[6])
                parent_names = '' if str(row[10]) == 'nan' else str(row[10]).split("/")
                parent_names_father = '' if len(parent_names) < 1 else parent_names[0]
                parent_names_mother = '' if len(parent_names) < 2 else parent_names[1]
                dob = '' if str(row[11]) == 'nan' else str(row[11])
                patient_names = '-' if str(row[12]) == 'nan' else str(row[12]).split(" ")
                first_name = patient_names[0]
                last_name = '-' if len(patient_names) < 2 else patient_names[1]
                age_in_years = '' if str(row[13]) == 'nan' else str(int(float(row[13])))
                age_in_months = '' if str(row[14]) == 'nan' else str(int(float(row[14])))
                sex = 'Detected' if str(row[15]) == 'Positive' else 'Not Detected'
                province_of_residence = '' if str(row[120]) == 'nan' else '0' + str(row[120])
                district_of_residence = '' if str(row[119]) == 'nan' else '0' + str(row[119])
                sector_of_residence = ''
                village_of_residence = ''
                phone = ''
                occupation = ''
                national_id = ''
                case_classification = 'Suspected case'
                parent_phone = ''

                # data elements

                # DIAGNOSTIC & CLINICAL INFORMATION STAGE

                system_gen_outcome = '' if str(row[44]) == 'nan' else str(row[44])
                date_of_symptoms_onset = date_sample_received if str(row[29]) == 'nan' else str(row[29])
                specimen_collected = 'Yes'
                date_seen_at_HF = date_sample_received if str(row[17]) == 'nan' else str(row[17])
                date_of_admission = date_sample_received if str(row[26]) == 'nan' else str(row[26])
                in_patient_out_patient = 'No' if date_of_admission == '' else 'Yes'
                any_injection_given_before = 'No'
                provisional_diagnosis = '-'
                if str(row[34]) == 'nan':
                    was_true_afp = 'No'
                elif str(int(float(row[34]))) == '1':
                    was_true_afp = 'Yes'
                else:
                    was_true_afp = 'No'

                immunocompromised = 'No'

                # vaccination
                total_doses = '' if str(row[35]) == 'nan' else str(int(float(row[35])))
                been_vaccinated = 'Yes' if total_doses != '' else 'No'
                date_of_dose_given_at_birth = '' if str(row[36]) == 'nan' else str(row[36])
                first_dose = '' if str(row[37]) == 'nan' else str(row[37])
                second_dose = '' if str(row[38]) == 'nan' else str(row[38])
                third_dose = '' if str(row[39]) == 'nan' else str(row[39])
                date_of_last_vaccination = '' if str(row[39]) == 'nan' else str(row[39])
                total_opv_sia = '-' if str(row[76]) == 'nan' else str(int(float(row[76])))
                total_opv_ri = '-' if str(row[77]) == 'nan' else str(int(float(row[77])))
                total_ipv_ri_sia = '-' if str(row[78]) == 'nan' else str(int(float(row[78])))
                date_total_ipv_ri_sia = ''

                # symptoms
                fever_at_on_set = 'Yes' if str(row[30]) != 'nan' else 'No'
                asymmetrical = 'Yes' if str(row[32]) != 'nan' else 'No'
                flaccid_sudden_paralysis = 'Yes' if str(row[33]) != 'nan' else 'No'
                site_left_arm = 'No'
                site_left_leg = 'No'
                site_right_arm = 'No'
                site_right_leg = 'No'
                sensitive_to_pain = 'Yes' if str(row[93]) != 'nan' else 'No'
                progression_in_3_days = 'Yes' if str(row[31]) != 'nan' else 'No'

                # notification
                date_notified_district = date_sample_received if str(row[17]) == 'nan' else str(row[17])
                name_of_person_completing_form = '-'
                date_case_investigated = date_sample_received if str(row[18]) == 'nan' else str(row[18])
                date_onset_rash = date_sample_received
                name_of_person_completing_investigation = '-'
                contact_of_person_completing_investigation = '-'

                # followup
                date_followup_examination = date_sample_received if str(row[66]) == 'nan' else str(row[66])

                # history of travel
                history_of_travel = 'No'

                # LAB REQUEST STAGE
                lab_request_id = patient_id
                sample_type = 'STOOL'
                lab_name = ''
                date_sample_sent_to_lab = '' if str(row[44]) == 'nan' else str(row[44])
                date_1st_stool_collected = '' if str(row[42]) == 'nan' else str(row[42])
                date_2nd_stool_collected = '' if str(row[43]) == 'nan' else str(row[43])
                purpose_of_testing = 'Confirmation of Diagnosis'

                # TRACKING STAGE
                tracking_lab_level = 'District'
                specimen_id = patient_id
                lis_code = ''
                if str((row[45])) == 'nan':
                    specimen_condition = 'Inadequate'
                elif str((row[45])) == 'poor':
                    specimen_condition = 'Inadequate'
                elif str(int(float(row[45]))) == '1':
                    specimen_condition = 'Adequate'
                else:
                    specimen_condition = 'Inadequate'

                # LAB RESULTS STAGE
                specimen_id = patient_id
                status_of_sample = specimen_condition
                w1 = 'No'
                w2 = 'No'
                w3 = 'No'
                discordant_sabin = ''
                npent_result = ''
                nev_result = ''
                date_final_cell_culture_results = '' if str(row[46]) == 'nan' else str(row[46])
                date_lab_result_sent_to_national_lab = ''  # TODO ask RBC ladies these variables
                date_lab_result_received_at_national_lab = ''  # TODO ask RBC ladies these variables

                if str(row[48]) == '1-Suspected Poliovirus':
                    final_cell_culture_result = 'Suspected Poliovirus'
                elif str(row[48]) == '2-Negative':
                    final_cell_culture_result = 'Negative'
                elif str(row[48]) == '3-NPENT':
                    final_cell_culture_result = 'NPENT'
                elif str(row[48]) == '4-Suspected Poliovirus + NPENT':
                    final_cell_culture_result = 'Suspected Poliovirus + NPENT'
                else:
                    final_cell_culture_result = ''

                # FINAL CLASSIFICATION STAGE
                if str((row[70])) == 'nan':
                    final_classification = 'Not an AFP'
                elif str(int(float(row[70]))) == '1':
                    final_classification = 'Confirmed WPV'
                elif str(int(float(row[70]))) == '2':
                    final_classification = 'Compatible'
                elif str(int(float(row[70]))) == '3':
                    final_classification = 'Discarded'
                elif str(int(float(row[70]))) == '6':
                    final_classification = 'Not an AFP'
                else:
                    final_classification = 'Not an AFP'

                enrollment_and_incident_date = date_seen_at_HF if date_seen_at_HF != '' else date_sample_received

                tei_data = {
                    "trackedEntityType": "j9TllKXZ3jb",
                    "orgUnit": org_unit_id,
                    "storedBy": upload_user,
                    "attributes": [
                        {
                            "attribute": "XuuupMIvUeK",
                            "value": patient_id.split('/')[2]
                        },
                        {
                            "attribute": "FfbxJbJ8rEB",
                            "value": patient_id
                        },
                        {
                            "attribute": "mfClmvRjS9V",
                            "value": epid_number
                        },
                        {
                            "attribute": "uOTHyxNv2W4",
                            "value": disease
                        },
                        {
                            "attribute": "qkQCA6ieVyu",
                            "value": reporting_during_outbreak
                        },
                        {
                            "attribute": "rK06rQeRu6V",
                            "value": outbreak_code
                        },
                        {
                            "attribute": "e9BrRZAicPE",
                            "value": first_name
                        },
                        {
                            "attribute": "G2LApJMOSck",
                            "value": last_name
                        },
                        {
                            "attribute": "Rq4qM2wKYFL",
                            "value": sex
                        },
                        {
                            "attribute": "A31FfrjPqyp",
                            "value": dob
                        },
                        {
                            "attribute": "VKBJi5N8mFm",
                            "value": age_in_years
                        },
                        {
                            "attribute": "vyCxLpUme4C",
                            "value": age_in_months
                        },
                        {
                            "attribute": "E7u9XdW24SP",
                            "value": phone
                        },
                        {
                            "attribute": "oUqWGeHjj5C",
                            "value": national_id
                        },
                        {
                            "attribute": "vM43jtv7MZ7",
                            "value": province_of_residence
                        },
                        {
                            "attribute": "ZCq6pNXVswA",
                            "value": district_of_residence
                        },
                        {
                            "attribute": "VkDFlme97C9",
                            "value": sector_of_residence
                        },
                        {
                            "attribute": "iO0Y20xJQe5",
                            "value": village_of_residence
                        },
                        {
                            "attribute": "xgDYh5XLSHW",
                            "value": occupation
                        },
                        {
                            "attribute": "bt06ynPCyFd",
                            "value": case_classification
                        },
                        {
                            "attribute": "adJ527HOTea",
                            "value": date_of_symptoms_onset
                        },
                        {
                            "attribute": "cLXIqrougUP",
                            "value": parent_names_father
                        },
                        {
                            "attribute": "aEydrg1MxNW",
                            "value": parent_names_mother
                        },
                        {
                            "attribute": "kKBhH8pQW8p",
                            "value": parent_phone
                        }
                    ],
                    "enrollments": [
                        {
                            "orgUnit": org_unit_id,  #
                            "program": 'U86iDWxDek8',
                            "enrollmentDate": enrollment_and_incident_date,
                            "incidentDate": enrollment_and_incident_date,
                            "events": [
                                # DIAGNOSTIC & CLINICAL INFORMATION STAGE
                                {
                                    "program": "U86iDWxDek8",
                                    "orgUnit": org_unit_id,
                                    "eventDate": enrollment_and_incident_date,
                                    "status": "COMPLETED",
                                    "storedBy": upload_user,
                                    "programStage": "CklnXjJgfxT",
                                    "dataValues": [
                                        {
                                            "dataElement": "ydCJveAOQsv",
                                            "value": date_of_symptoms_onset
                                        },
                                        {
                                            "dataElement": "oD3vbGPqWt8",
                                            "value": date_seen_at_HF
                                        },
                                        {
                                            "dataElement": "SYlEh4KgLna",
                                            "value": specimen_collected
                                        },
                                        {
                                            "dataElement": "jNmaI44NAsm",
                                            "value": in_patient_out_patient
                                        },
                                        {
                                            "dataElement": "hQ8mCCIC1C1",
                                            "value": any_injection_given_before
                                        },
                                        {
                                            "dataElement": "H1xx3BkfDBa",
                                            "value": provisional_diagnosis
                                        },
                                        {
                                            "dataElement": "WDWjVKuoonN",
                                            "value": was_true_afp
                                        },
                                        {
                                            "dataElement": "VVoYhn1UG8u",
                                            "value": immunocompromised
                                        },
                                        {
                                            "dataElement": "BHGG89rIIcP",
                                            "value": been_vaccinated
                                        },
                                        {
                                            "dataElement": "AzQwExWosJz",
                                            "value": total_doses
                                        },
                                        {
                                            "dataElement": "tj9iS3V92em",
                                            "value": date_of_dose_given_at_birth
                                        },
                                        {
                                            "dataElement": "KhieS2gxN3k",
                                            "value": first_dose
                                        },
                                        {
                                            "dataElement": "h3OlaksuV4u",
                                            "value": second_dose
                                        },
                                        {
                                            "dataElement": "HEO3xQXmXrV",
                                            "value": third_dose
                                        },
                                        {
                                            "dataElement": "lMXqMH3ri9O",
                                            "value": date_of_last_vaccination
                                        },
                                        {
                                            "dataElement": "O8u0OszYM9t",
                                            "value": total_opv_sia
                                        },
                                        {
                                            "dataElement": "ezvCIvsRWC5",
                                            "value": total_opv_ri
                                        },
                                        {
                                            "dataElement": "vNNdyjDJCL3",
                                            "value": total_ipv_ri_sia
                                        },
                                        {
                                            "dataElement": "yHLJDYvB212",
                                            "value": date_total_ipv_ri_sia
                                        },
                                        {
                                            "dataElement": "SZ0QGv76Gfp",
                                            "value": fever_at_on_set
                                        },
                                        {
                                            "dataElement": "N9xuT56rb1j",
                                            "value": asymmetrical
                                        },
                                        {
                                            "dataElement": "cEo2JtUtVFk",
                                            "value": flaccid_sudden_paralysis
                                        },
                                        {
                                            "dataElement": "gFHjABcZxp0",
                                            "value": site_left_arm
                                        },
                                        {
                                            "dataElement": "juA8VYMP1iY",
                                            "value": site_right_arm
                                        },
                                        {
                                            "dataElement": "RsFBo33mtgK",
                                            "value": site_left_leg
                                        },
                                        {
                                            "dataElement": "ubV1SnsqC2i",
                                            "value": site_right_leg
                                        },
                                        {
                                            "dataElement": "mYIKXVygnEh",
                                            "value": sensitive_to_pain
                                        },
                                        {
                                            "dataElement": "ArLraYnjWSA",
                                            "value": progression_in_3_days
                                        },
                                        {
                                            "dataElement": "uM6WlqEUudp",
                                            "value": date_notified_district
                                        },
                                        {
                                            "dataElement": "sZtmP5ZH7Vp",
                                            "value": name_of_person_completing_form
                                        },
                                        {
                                            "dataElement": "sPOfaKnhQ3p",
                                            "value": date_case_investigated
                                        },
                                        {
                                            "dataElement": "ONiFzSQDuQO",
                                            "value": date_onset_rash
                                        },
                                        {
                                            "dataElement": "E0I5RZshCcI",
                                            "value": name_of_person_completing_investigation
                                        },
                                        {
                                            "dataElement": "mFYiHoEwK3Z",
                                            "value": contact_of_person_completing_investigation
                                        },
                                        {
                                            "dataElement": "sUMhQfPzrzN",
                                            "value": date_followup_examination
                                        },
                                        {
                                            "dataElement": "WJTIZE8cYcY",
                                            "value": history_of_travel
                                        }
                                    ]
                                },
                                # LABORATORY REQUEST STAGE
                                {
                                    "program": "U86iDWxDek8",
                                    "orgUnit": org_unit_id,
                                    "eventDate": enrollment_and_incident_date,
                                    "status": "COMPLETED",
                                    "storedBy": upload_user,
                                    "programStage": "psOOCKL60wb",
                                    "dataValues": [
                                        {
                                            "dataElement": "mWiDKXqfYeL",
                                            "value": lab_request_id
                                        },
                                        {
                                            "dataElement": "CCq1S9gyocG",
                                            "value": purpose_of_testing
                                        },
                                        {
                                            "dataElement": "GzIo6aEN7Mc",
                                            "value": date_sample_sent_to_lab
                                        },
                                        {
                                            "dataElement": "t3tYFQxrL5V",
                                            "value": sample_type
                                        },
                                        {
                                            "dataElement": "SIYwWhJ0Urv",
                                            "value": date_1st_stool_collected
                                        },
                                        {
                                            "dataElement": "ZMUOakxQZrL",
                                            "value": date_2nd_stool_collected
                                        }
                                    ]
                                },
                                # SPECIMEN TRACKING STAGE
                                {
                                    "program": "U86iDWxDek8",
                                    "orgUnit": org_unit_id,
                                    "eventDate": enrollment_and_incident_date,
                                    "status": "COMPLETED",
                                    "storedBy": upload_user,
                                    "programStage": "j4vmqHk4lZx",
                                    "dataValues": [
                                        {
                                            "dataElement": "lvM0cPM5aXW",
                                            "value": tracking_lab_level
                                        },
                                        {
                                            "dataElement": "lgbCSpMa9uW",
                                            "value": specimen_id
                                        },
                                        {
                                            "dataElement": "Dvm1i4JUqJL",
                                            "value": lis_code
                                        },
                                        {
                                            "dataElement": "ul1GflrNFHZ",
                                            "value": specimen_condition
                                        }
                                    ]
                                },
                                # LAB RESULTS STAGE
                                {
                                    "program": "U86iDWxDek8",
                                    "orgUnit": org_unit_id,
                                    "eventDate": enrollment_and_incident_date,
                                    "status": "COMPLETED",
                                    "storedBy": upload_user,
                                    "programStage": "cYEsxIe5jxL",
                                    "dataValues": [
                                        {
                                            "dataElement": "mWiDKXqfYeL",
                                            "value": lab_request_id
                                        },
                                        {
                                            "dataElement": "RTn5sMw0TaR",
                                            "value": date_sample_received
                                        },
                                        {
                                            "dataElement": "yZmadWo2sSf",
                                            "value": status_of_sample
                                        },
                                        {
                                            "dataElement": "V9uSaI6rekY",
                                            "value": w1
                                        },
                                        {
                                            "dataElement": "ZHCRlzamo0S",
                                            "value": w2
                                        },
                                        {
                                            "dataElement": "hOHuZIbGcaH",
                                            "value": w3
                                        },
                                        {
                                            "dataElement": "zUWyPmnsL2U",
                                            "value": final_cell_culture_result
                                        },
                                        {
                                            "dataElement": "uQiapN4OCBk",
                                            "value": date_final_cell_culture_results
                                        }
                                    ]
                                },
                                # FINAL CLASSIFICATION STAGE
                                {
                                    "program": "U86iDWxDek8",
                                    "orgUnit": org_unit_id,
                                    "eventDate": enrollment_and_incident_date,
                                    "status": "COMPLETED",
                                    "storedBy": upload_user,
                                    "programStage": "shBKILekMiy",
                                    "dataValues": [
                                        {
                                            "dataElement": "CljPbtjuMPE",
                                            "value": final_classification
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }

                response_post = api.post('trackedEntityInstances', json=tei_data)
                teid = response_post.headers._store['location'][1].split('/')[-1]

                logger.info("#### {} Created TEI : {} - TEI id: {}".format(counter, patient_id, teid))
                try:
                    with open('succeded_AFP_imports.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(teid)
                except:
                    logger.error("### Failed to write row to file, with IO error:")
            except:
                logger.error('Failed to import TEI: {} '.format(patient_id))
                try:
                    with open('failed_AFP_imports.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(row)
                except:
                    logger.error("### Failed to write row to file, with IO error:")
        end = time.time()
        print("\n**********************************************\n*** Time taken to import Teis : ", (end - start),
              " Seconds or " + str((end - start) / 60) + " Minutes\n**********************************************")


if __name__ == '__main__':
    upload_dhis2_tracked_entity_instances()
