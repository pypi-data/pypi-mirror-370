# workday/parsers/worker_parsers.py

from typing import Any, Dict, List, Optional
from decimal import Decimal
from ..utils import extract_by_type, first, ensure_list

def parse_personal_data(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the personal information of the worker.
    """
    personal = worker_data.get("Personal_Data", {}) or {}
    name_data = personal.get("Name_Data", {}) or {}
    legal = name_data.get("Legal_Name_Data", {}).get("Name_Detail_Data", {}) or {}
    preferred = name_data.get("Preferred_Name_Data", {}).get("Name_Detail_Data", {}) or {}

    # Names
    first_name            = legal.get("First_Name")
    middle_name           = legal.get("Middle_Name")
    last_name             = legal.get("Last_Name")
    formatted_name        = legal.get("Formatted_Name")
    reporting_name        = legal.get("Reporting_Name")
    pref_formatted_name   = preferred.get("Formatted_Name")
    pref_reporting_name   = preferred.get("Reporting_Name")

    # Pronouns
    pronoun_id = None
    pron_refs = personal.get("Pronoun_Reference", []) or []
    if pron_refs:
        for entry in ensure_list(pron_refs[0].get("ID")):
            if entry.get("type") == "Pronoun_ID":
                pronoun_id = entry.get("_value_1")
                break

    # Demographics & birth_date
    birth_date                       = None
    gender                           = None
    ethnicity                        = None
    hispanic_or_latino               = None
    hispanic_or_latino_visual_survey = None

    personal_info_nodes = personal.get("Personal_Information_Data", []) or []
    if personal_info_nodes:
        # Birth date
        bd = personal_info_nodes[0].get("Birth_Date")
        birth_date = str(bd) if bd else None

        # Search for gender, ethnicity, hispanic flags
        for info in personal_info_nodes:
            for country_info in ensure_list(info.get("Personal_Information_For_Country_Data")):
                # ignoramos valores nulos o no‐dict
                if not isinstance(country_info, dict):
                    continue
                # Gender
                try_g = _extract_gender(country_info)
                if try_g and not gender:
                    gender = try_g
                # Ethnicity
                try_e = _extract_ethnicity(country_info)
                if try_e and not ethnicity:
                    ethnicity = try_e
                # Hispanic flags
                for cp in ensure_list(country_info.get("Country_Personal_Information_Data", [])):
                    if not isinstance(cp, dict):
                        continue
                    his = cp.get("Hispanic_or_Latino")
                    if his is not None and hispanic_or_latino is None:
                        hispanic_or_latino = bool(his)
                    hisv = cp.get("Hispanic_or_Latino_Visual_Survey")
                    if hisv is not None and hispanic_or_latino_visual_survey is None:
                        hispanic_or_latino_visual_survey = bool(hisv)

                if all(v is not None for v in [gender, ethnicity, hispanic_or_latino, hispanic_or_latino_visual_survey]):
                    break
            if all(v is not None for v in [gender, ethnicity, hispanic_or_latino, hispanic_or_latino_visual_survey]):
                break

    # Tobacco use
    tobacco_use = None
    tu = personal.get("Tobacco_Use")
    if tu is not None:
        tobacco_use = bool(tu)

    return {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "formatted_name": formatted_name,
        "reporting_name": reporting_name,
        "pref_formatted_name": pref_formatted_name,
        "pref_reporting_name": pref_reporting_name,
        "pronoun_id": pronoun_id,
        "birth_date": birth_date,
        "gender": gender,
        "hispanic_or_latino": hispanic_or_latino,
        "hispanic_or_latino_visual_survey": hispanic_or_latino_visual_survey,
        "ethnicity": ethnicity,
        "tobacco_use": tobacco_use,
    }

def parse_contact_data(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the contact information (email, address, phone) of the worker.
    """
    contact = worker_data.get("Personal_Data", {}).get("Contact_Data", {}) or {}

    # Emails
    email_entries = contact.get("Email_Address_Data", []) or []
    emails        = [e.get("Email_Address") for e in email_entries if e.get("Email_Address")]
    email         = emails[0] if emails else None

    email_usage_public = None
    email_id           = None
    if email_entries:
        usage = ensure_list(email_entries[0].get("Usage_Data"))
        if usage:
            email_usage_public = bool(usage[0].get("Public"))
        email_id = email_entries[0].get("ID")

    # Address
    addr_entries                  = contact.get("Address_Data", []) or []
    addr                          = addr_entries[0] if addr_entries else {}
    address                       = addr.get("Formatted_Address")
    if address and "NO STREET ADDRESS" in address:
        address = None
    address_effective_date        = addr.get("Effective_Date")
    address_format_type           = addr.get("Address_Format_Type")
    defaulted_business_site_address = addr.get("Defaulted_Business_Site_Address")
    if defaulted_business_site_address is not None:
        defaulted_business_site_address = bool(defaulted_business_site_address)

    aline                         = first(addr.get("Address_Line_Data", []))
    address_line                  = aline.get("_value_1") or aline.get("#text")
    address_line_descriptor       = aline.get("Descriptor")
    municipality                  = addr.get("Municipality")
    country_region_descriptor     = addr.get("Country_Region_Descriptor")
    postal_code                   = addr.get("Postal_Code")
    addr_usage                    = ensure_list(addr.get("Usage_Data"))
    address_usage_public          = bool(addr_usage[0].get("Public")) if addr_usage else None
    address_number_of_days        = addr.get("Number_of_Days")
    address_id                    = addr.get("Address_ID")

    # Country and State
    country = None
    state_code = None
    country_ref = addr.get("Country_Reference", {}) or {}
    for c in ensure_list(country_ref.get("ID")):
        if c.get("type") == "ISO_3166-1_Alpha-2_Code":
            country = c.get("_value_1")
            break
    
    # Extract state code from Country_Region_Reference
    country_region_ref = addr.get("Country_Region_Reference", {}) or {}
    for cr in ensure_list(country_region_ref.get("ID")):
        if cr.get("type") == "ISO_3166-2_Code":
            state_code = cr.get("_value_1")
            break
    


    # Phone
    phone_entries             = contact.get("Phone_Data", []) or []
    p                         = phone_entries[0] if phone_entries else {}
    phone                     = p.get("E164_Formatted_Phone")
    phone_area_code           = p.get("Area_Code")
    phone_number_wo_area      = p.get("Phone_Number_Without_Area_Code")
    phone_traditional         = p.get("Workday_Traditional_Formatted_Phone")
    phone_national            = p.get("National_Formatted_Phone")
    phone_international       = p.get("International_Formatted_Phone")
    phone_tenant              = p.get("Tenant_Formatted_Phone")

    # Device type
    dev_ref = p.get("Phone_Device_Type_Reference", {}) or {}
    phone_device_type_id = None
    for entry in ensure_list(dev_ref.get("ID")):
        if entry.get("type") == "Phone_Device_Type_ID":
            phone_device_type_id = entry.get("_value_1")
            break

    ph_usage           = ensure_list(p.get("Usage_Data"))
    phone_usage_public = bool(ph_usage[0].get("Public")) if ph_usage else None
    phone_id           = p.get("ID")

    return {
        "email": email,
        "emails": emails or None,
        "email_usage_public": email_usage_public,
        "email_id": email_id,
        "address": address,
        "address_effective_date": str(address_effective_date) if address_effective_date else None,
        "address_format_type": address_format_type,
        "defaulted_business_site_address": defaulted_business_site_address,
        "address_line": address_line,
        "address_line_descriptor": address_line_descriptor,
        "municipality": municipality,
        "country_region_descriptor": country_region_descriptor,
        "postal_code": postal_code,
        "address_usage_public": address_usage_public,
        "address_number_of_days": address_number_of_days,
        "address_id": address_id,
        "country_code": country,
        "state_code": state_code,
        "phone": phone,
        "phone_area_code": phone_area_code,
        "phone_number_wo_area": phone_number_wo_area,
        "phone_traditional": phone_traditional,
        "phone_national": phone_national,
        "phone_international": phone_international,
        "phone_tenant": phone_tenant,
        "phone_device_type_id": phone_device_type_id,
        "phone_usage_public": phone_usage_public,
        "phone_id": phone_id,
    }


def parse_worker_organization_data(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse worker organization information from worker data"""
    organization_data = worker_data.get("Organization_Data", {}) or {}
    worker_orgs = organization_data.get("Worker_Organization_Data", []) or []
    
    organizations = []
    primary_org = None
    company_org = None
    cost_center_org = None
    pay_group_org = None
    supervisory_org = None
    
    for org in worker_orgs:
        org_ref = org.get("Organization_Reference", {}) or {}
        org_data = org.get("Organization_Data", {}) or {}
        
        # Extract organization IDs
        org_ids = org_ref.get("ID", []) or []
        org_ref_id = extract_by_type(org_ids, "Organization_Reference_ID")
        company_id = extract_by_type(org_ids, "Company_Reference_ID")
        cost_center_id = extract_by_type(org_ids, "Cost_Center_Reference_ID")
        custom_org_id = extract_by_type(org_ids, "Custom_Organization_Reference_ID")
        
        # Organization details
        org_name = org_data.get("Organization_Name")
        org_code = org_data.get("Organization_Code")
        
        # Organization type
        org_type_ref = org_data.get("Organization_Type_Reference", {}) or {}
        org_type_ids = org_type_ref.get("ID", []) or []
        org_type = extract_by_type(org_type_ids, "Organization_Type_ID")
        
        # Organization subtype
        org_subtype_ref = org_data.get("Organization_Subtype_Reference", {}) or {}
        org_subtype_ids = org_subtype_ref.get("ID", []) or []
        org_subtype = extract_by_type(org_subtype_ids, "Organization_Subtype_ID")
        
        # Used in assignments
        used_in_assignments = org_data.get("Used_in_Change_Organization_Assignments", "0") == "1"
        
        org_info = {
            "organization_reference_id": org_ref_id,
            "organization_name": org_name,
            "organization_code": org_code,
            "organization_type": org_type,
            "organization_subtype": org_subtype,
            "company_id": company_id,
            "cost_center_id": cost_center_id,
            "custom_organization_id": custom_org_id,
            "used_in_assignments": used_in_assignments,
        }
        
        organizations.append(org_info)
        
        # Identify specific organization types
        if org_type == "Company" and org_subtype == "Company":
            company_org = org_info
        elif org_type == "Cost_Center" and org_subtype == "Cost_Center":
            cost_center_org = org_info
        elif org_type == "Pay_Group" and org_subtype == "Pay_Group":
            pay_group_org = org_info
        elif org_type == "Supervisory" and org_subtype == "Department":
            supervisory_org = org_info
        
        # Set primary organization (first one or most relevant)
        if not primary_org:
            primary_org = org_info
    
    return {
        "organizations": organizations,
        "primary_organization_id": primary_org.get("organization_reference_id") if primary_org else None,
        "primary_organization_name": primary_org.get("organization_name") if primary_org else None,
        "primary_organization_type": primary_org.get("organization_type") if primary_org else None,
        "primary_organization_code": primary_org.get("organization_code") if primary_org else None,
        "company_id": company_org.get("organization_reference_id") if company_org else None,
        "company_name": company_org.get("organization_name") if company_org else None,
        "cost_center_id": cost_center_org.get("organization_reference_id") if cost_center_org else None,
        "cost_center_name": cost_center_org.get("organization_name") if cost_center_org else None,
        "pay_group_id": pay_group_org.get("organization_reference_id") if pay_group_org else None,
        "pay_group_name": pay_group_org.get("organization_name") if pay_group_org else None,
        "supervisory_organization_id": supervisory_org.get("organization_reference_id") if supervisory_org else None,
        "supervisory_organization_name": supervisory_org.get("organization_name") if supervisory_org else None,
    }

def parse_compensation_data(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the compensation details of the worker.

    Extracts:
      - wage (float)
      - compensation_effective_date (str)
      - compensation_guidelines (package / grade / profile IDs)
      - salary_and_hourly (list of elements)
      - compensation_summary (nested summary)
      - reason_references (mapping of reason type → ID)
    """
    compensation = worker_data.get("Compensation_Data", {}) or {}

    # — Salary / hourly nodes —
    salary_nodes = ensure_list(compensation.get("Salary_and_Hourly_Data"))
    wage = next(
        (float(s.get("Amount")) for s in salary_nodes if s and s.get("Amount") is not None),
        None
    )
    salary_and_hourly = _parse_salary_nodes(salary_nodes)

    # — Compensation guidelines —
    guidelines_nodes = compensation.get("Compensation_Guidelines_Data", []) or []
    if guidelines_nodes:
        g0 = guidelines_nodes[0] or {}
        compensation_guidelines = {
            "package": extract_by_type(
                g0.get("Compensation_Package_Reference", {}).get("ID", []),
                "Compensation_Package_ID"
            ),
            "grade": extract_by_type(
                g0.get("Compensation_Grade_Reference", {}).get("ID", []),
                "Compensation_Grade_ID"
            ),
            "profile": extract_by_type(
                g0.get("Compensation_Grade_Profile_Reference", {}).get("ID", []),
                "Compensation_Grade_Profile_ID"
            ),
        }
    else:
        compensation_guidelines = {"package": None, "grade": None, "profile": None}

    # — Reason references (requerido por el modelo) —
    reason_refs: Dict[str, str] = {}
    for node in ensure_list(compensation.get("Reason_Reference")):
        for entry in ensure_list(node.get("ID")):
            t = entry.get("type")
            v = entry.get("_value_1")
            if t and v:
                reason_refs[t] = v

    # — Build and return —
    return {
        "wage": wage,
        "compensation_effective_date": (
            str(compensation.get("Compensation_Effective_Date"))
            if compensation.get("Compensation_Effective_Date") else None
        ),
        "compensation_guidelines": compensation_guidelines,
        "salary_and_hourly": salary_and_hourly,
        "compensation_summary": _parse_compensation_summary(compensation),
        "reason_references": reason_refs or None,
    }

def parse_identification_data(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse identification details (national ID, license, custom IDs).
    """
    # Identification_Data está dentro de Personal_Data
    personal_data = worker_data.get("Personal_Data", {}) or {}
    ident = personal_data.get("Identification_Data", {}) or {}

    # National ID
    nat_list   = ident.get("National_ID", []) or []
    nat0       = nat_list[0] if nat_list else {}
    nid_data   = nat0.get("National_ID_Data", {}) or {}
    national_id = nid_data.get("ID")
    national_id_type_code = extract_by_type(
        nid_data.get("ID_Type_Reference", {}).get("ID", []),
        "National_ID_Type_Code"
    )
    nshr = first(nat0.get("National_ID_Shared_Reference", {})).get("ID", []) or []
    national_id_shared_reference = extract_by_type(
        nshr,
        "National_Identifier_Reference_ID"
    )

    # License
    lic_list  = ident.get("License_ID", []) or []
    license_data = first(lic_list).get("License_ID_Data", {}) or {}
    license_id = license_data.get("ID")
    
    # License Type ID
    id_type_ref = license_data.get("ID_Type_Reference", {}) or {}
    license_type_id = extract_by_type(
        id_type_ref.get("ID", []) or [],
        "License_ID_Type_ID"
    )
    
    # License State Code
    country_region_ref = license_data.get("Country_Region_Reference", {}) or {}
    license_state_code = extract_by_type(
        country_region_ref.get("ID", []) or [],
        "ISO_3166-2_Code"
    )
    
    license_issued_date = license_data.get("Issued_Date")
    license_expiration_date = license_data.get("Expiration_Date")

    # Custom IDs
    custom_ids       = {}
    custom_shared    = {}
    associate_oid    = None
    adp_payroll_id   = None
    adp_payroll_group = None
    old_corporate_email = None
    
    for cid in ident.get("Custom_ID", []) or []:
        data  = cid.get("Custom_ID_Data", {}) or {}
        cv    = data.get("ID")
        
        id_type_ref = data.get("ID_Type_Reference", {}) or {}
        id_list = id_type_ref.get("ID", []) or []
        
        ctype = extract_by_type(id_list, "Custom_ID_Type_ID")
        
        if ctype:
            custom_ids[ctype] = cv
            # Extract specific Custom IDs
            if ctype == "Associate OID":
                associate_oid = cv
            elif ctype == "ADP Payroll ID":
                adp_payroll_id = cv
            elif ctype == "ADP Payroll Group":
                adp_payroll_group = cv
            elif ctype == "Old Corporate Email":
                old_corporate_email = cv
            shared_ids = first(cid.get("Custom_ID_Shared_Reference", {})).get("ID", []) or []
            sref = extract_by_type(shared_ids, "Custom_Identifier_Reference_ID")
            if sref:
                custom_shared[ctype] = sref

    return {
        "national_id": national_id,
        "national_id_type_code": national_id_type_code,
        "national_id_shared_reference": national_id_shared_reference,
        "license_id": license_id,
        "license_type_id": license_type_id,
        "license_state_code": license_state_code,
        "license_issued_date": str(license_issued_date) if license_issued_date else None,
        "license_expiration_date": str(license_expiration_date) if license_expiration_date else None,
        "custom_ids": custom_ids or None,
        "custom_id_shared_references": custom_shared or None,
        "associate_oid": associate_oid,
        "adp_payroll_id": adp_payroll_id,
        "adp_payroll_group": adp_payroll_group,
        "old_corporate_email": old_corporate_email,
    }

def parse_benefits_and_roles(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse benefit enrollments, roles, and worker documents.
    """
    # Benefits
    ben_section         = worker_data.get("Benefit_Enrollment_Data", {}) or {}
    benefit_enrollments = [
        b.get("Benefit_Enrollment_Type")
        for b in ben_section.get("Benefit_Enrollment", [])
        if b and b.get("Benefit_Enrollment_Type")
    ] or None

    # Roles
    roles_section = worker_data.get("Roles_Data", {}) or {}
    roles         = [
        r.get("Role_Data", {}).get("Role_Name")
        for r in roles_section.get("Role", [])
        if r and r.get("Role_Data", {}).get("Role_Name")
    ] or None

    # Documents
    docs_section      = worker_data.get("Worker_Documents_Data", {}) or {}
    worker_documents  = [
        d.get("Worker_Document_Data", {}).get("Document_Reference")
        for d in docs_section.get("Worker_Document", [])
        if d and d.get("Worker_Document_Data", {}).get("Document_Reference")
    ] or None

    return {
        "benefit_enrollments": benefit_enrollments,
        "roles": roles,
        "worker_documents": worker_documents,
    }


def parse_employment_data(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse employment-related details (position, hours, job profile).
    """

    employment = worker_data.get("Employment_Data", {}) or {}
    wjd_list   = ensure_list(employment.get("Worker_Job_Data"))
    wjd        = wjd_list[0] if wjd_list else {}
    pos        = wjd.get("Position_Data", {}) or {}

    # Identificadores & títulos
    # position_id     = extract_by_type(
    #     pos.get("Position_Reference", {}).get("ID", []),
    #     "Position_ID"
    # )
    position_id = extract_by_type(pos.get("Position_Reference",{}).get("ID",[]), "Position_ID") or pos.get("Position_ID")

    position_title  = pos.get("Position_Title")
    business_title  = pos.get("Business_Title")

    # Fechas
    start_date          = pos.get("Start_Date")
    end_employment_date = pos.get("End_Employment_Date")

    # Tipos & clasificaciones
    wt_ref = pos.get("Worker_Type_Reference") or {}
    worker_type = extract_by_type(wt_ref.get("ID", []), "Employee_Type_ID")

    pt_ref = pos.get("Position_Time_Type_Reference") or {}
    position_time_type = extract_by_type(pt_ref.get("ID", []), "Position_Time_Type_ID")

    pr_ref = pos.get("Pay_Rate_Type_Reference") or {}
    pay_rate_type = extract_by_type(pr_ref.get("ID", []), "Pay_Rate_Type_ID")

    # Horas & exención
    job_exempt                      = pos.get("Job_Exempt")
    scheduled_weekly_hours          = float(pos.get("Scheduled_Weekly_Hours")) if pos.get("Scheduled_Weekly_Hours") is not None else None
    default_weekly_hours            = float(pos.get("Default_Weekly_Hours"))   if pos.get("Default_Weekly_Hours")   is not None else None
    full_time_equivalent_percentage = float(pos.get("Full_Time_Equivalent_Percentage")) if pos.get("Full_Time_Equivalent_Percentage") is not None else None

    # Job Profile & Management Level
    jps = pos.get("Job_Profile_Summary_Data") or {}

    # Job Profile
    jpr = jps.get("Job_Profile_Reference") or {}
    job_profile_id   = extract_by_type(jpr.get("ID", []), "Job_Profile_ID")
    job_profile_name = jps.get("Job_Profile_Name")

    # Management Level
    mlr = jps.get("Management_Level_Reference") or {}
    management_level = extract_by_type(mlr.get("ID", []), "Management_Level_ID")


    # Job Family (pueden venir varias referencias)
    families = []
    for fam in ensure_list(jps.get("Job_Family_Reference", [])):
        fam_id = extract_by_type(fam.get("ID", []), "Job_Family_ID")
        if fam_id:
            families.append(fam_id)

    return {
        "position_id": position_id,
        "position_title": position_title,
        "business_title": business_title,
        "start_date": start_date,
        "end_employment_date": end_employment_date,
        "worker_type": worker_type,
        "position_time_type": position_time_type,
        "pay_rate_type": pay_rate_type,
        "job_exempt": job_exempt,
        "scheduled_weekly_hours": scheduled_weekly_hours,
        "default_weekly_hours": default_weekly_hours,
        "full_time_equivalent_percentage": full_time_equivalent_percentage,
        "job_profile_id": job_profile_id,
        "job_profile_name": job_profile_name,
        "management_level": management_level,
        "job_family": families or None,
    }


from typing import Any, Dict
from ..utils import extract_by_type

def parse_worker_status(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse worker status details (active, hire/termination dates, eligibility),
    asegurando no romper si algún _Reference es None.
    """
    employment = worker_data.get("Employment_Data", {}) or {}
    status     = employment.get("Worker_Status_Data", {}) or {}

    # — Campos básicos —
    active             = status.get("Active")
    active_status_date = status.get("Active_Status_Date")
    hire_date          = status.get("Hire_Date")
    original_hire_date = status.get("Original_Hire_Date")
    first_day_of_work  = status.get("First_Day_of_Work")
    seniority_date     = status.get("Seniority_Date")
    terminated         = status.get("Terminated")
    termination_date   = status.get("Termination_Date")
    pay_through_date   = status.get("Pay_Through_Date")

    # — Razón y categoría de terminación —
    ptr_ref = status.get("Primary_Termination_Reason_Reference") or {}
    term_id_list = ptr_ref.get("ID") or []
    termination_reason = extract_by_type(term_id_list, "Event_Classification_Subcategory_ID")

    ptc_ref = status.get("Primary_Termination_Category_Reference") or {}
    cat_id_list = ptc_ref.get("ID") or []
    termination_category = extract_by_type(cat_id_list, "Termination_Category_ID")

    termination_involuntary = status.get("Termination_Involuntary")

    # — Elegibilidad —
    eh_ref = status.get("Eligible_for_Hire_Reference") or {}
    eh_id_list = eh_ref.get("ID") or []
    eligible_for_hire = extract_by_type(eh_id_list, "Yes_No_Type_ID") == "Yes"

    regrettable_termination = status.get("Regrettable_Termination")

    erh_ref = status.get("Eligible_for_Rehire_on_Latest_Termination_Reference") or {}
    erh_id_list = erh_ref.get("ID") or []
    eligible_for_rehire = extract_by_type(erh_id_list, "Yes_No_Type_ID") == "Yes"

    termination_last_day_of_work = status.get("Termination_Last_Day_of_Work")

    return {
        "active": active,
        "active_status_date": active_status_date,
        "hire_date": hire_date,
        "original_hire_date": original_hire_date,
        "first_day_of_work": first_day_of_work,
        "seniority_date": seniority_date,
        "terminated": terminated,
        "termination_date": termination_date,
        "pay_through_date": pay_through_date,
        "termination_reason": termination_reason,
        "termination_category": termination_category,
        "termination_involuntary": termination_involuntary,
        "eligible_for_hire": eligible_for_hire,
        "regrettable_termination": regrettable_termination,
        "eligible_for_rehire": eligible_for_rehire,
        "termination_last_day_of_work": termination_last_day_of_work,
    }

def parse_business_site(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse business site summary data.
    """
    employment = worker_data.get("Employment_Data", {}) or {}
    wjd_list   = ensure_list(employment.get("Worker_Job_Data"))
    wjd        = wjd_list[0] if wjd_list else {}
    pos        = wjd.get("Position_Data", {}) or {}

    bs = pos.get("Business_Site_Summary_Data", {}) or {}
    business_site_name        = bs.get("Name")
    business_site_location_id = extract_by_type(
        bs.get("Location_Reference", {}).get("ID", []),
        "Location_ID"
    )
    # El Address_Data completo lo guardamos tal cual
    bs_address_list = ensure_list(bs.get("Address_Data", []))
    business_site_address = bs_address_list[0] if bs_address_list else None

    return {
        "business_site_name": business_site_name,
        "business_site_location_id": business_site_location_id,
        "business_site_address": business_site_address,
    }

def parse_management_chain_data(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse management chain data from Worker_Management_Chain_Data.
    """
    management_data = worker_data.get("Management_Chain_Data", {}) or {}
    
    # Supervisory Management Chain
    supervisory_chain = management_data.get("Worker_Supervisory_Management_Chain_Data", {}) or {}
    management_chain_data = supervisory_chain.get("Management_Chain_Data", [])
    
    management_chain = []
    direct_manager_id = None
    direct_manager_name = None
    
    if isinstance(management_chain_data, list):
        for level in management_chain_data:
            if isinstance(level, dict):
                # Extract organization info
                org_ref = level.get("Organization_Reference", {}) or {}
                org_ids = org_ref.get("ID", [])
                organization_id = extract_by_type(org_ids, "Organization_Reference_ID")
                organization_name = org_ref.get("Descriptor")
                
                # Extract manager info from Manager_Reference
                manager_ref = level.get("Manager_Reference", [])
                if isinstance(manager_ref, list) and manager_ref:
                    manager_ref = manager_ref[0]  # Take first manager reference
                
                manager_id = None
                manager_name = None
                
                if isinstance(manager_ref, dict):
                    manager_ids = manager_ref.get("ID", [])
                    manager_id = extract_by_type(manager_ids, "Employee_ID")
                    manager_name = manager_ref.get("Descriptor")
                
                # Extract manager name from Manager field (which has Worker_Descriptor)
                manager_data = level.get("Manager", [])
                if isinstance(manager_data, list) and manager_data:
                    manager_item = manager_data[0]
                    if isinstance(manager_item, dict):
                        # Get the name from Worker_Descriptor
                        manager_name = manager_item.get("Worker_Descriptor")
                
                # If this is the first level (direct manager), store it separately
                if direct_manager_id is None:
                    direct_manager_id = manager_id
                    direct_manager_name = manager_name
                
                # Add to management chain
                management_chain.append({
                    "organization_id": organization_id,
                    "organization_name": organization_name,
                    "manager_id": manager_id,
                    "manager_name": manager_name
                })
    
    # Matrix Management Chain
    matrix_chain = management_data.get("Worker_Matrix_Management_Chain_Data", {}) or {}
    matrix_management_chain_data = matrix_chain.get("Management_Chain_Data", [])
    
    matrix_management_chain = []
    
    if isinstance(matrix_management_chain_data, list):
        for level in matrix_management_chain_data:
            if isinstance(level, dict):
                # Extract organization info
                org_ref = level.get("Organization_Reference", {}) or {}
                org_ids = org_ref.get("ID", [])
                organization_id = extract_by_type(org_ids, "Organization_Reference_ID")
                organization_name = org_ref.get("Descriptor")
                
                # Extract manager info from Manager_Reference
                manager_ref = level.get("Manager_Reference", [])
                if isinstance(manager_ref, list) and manager_ref:
                    manager_ref = manager_ref[0]  # Take first manager reference
                
                manager_id = None
                manager_name = None
                
                if isinstance(manager_ref, dict):
                    manager_ids = manager_ref.get("ID", [])
                    manager_id = extract_by_type(manager_ids, "Employee_ID")
                    manager_name = manager_ref.get("Descriptor")
                
                # Extract manager name from Manager field (which has Worker_Descriptor)
                manager_data = level.get("Manager", [])
                if isinstance(manager_data, list) and manager_data:
                    manager_item = manager_data[0]
                    if isinstance(manager_item, dict):
                        # Get the name from Worker_Descriptor
                        manager_name = manager_item.get("Worker_Descriptor")
                
                # Add to matrix management chain
                matrix_management_chain.append({
                    "organization_id": organization_id,
                    "organization_name": organization_name,
                    "manager_id": manager_id,
                    "manager_name": manager_name
                })
    
    return {
        "management_chain": management_chain,
        "direct_manager_id": direct_manager_id,
        "direct_manager_name": direct_manager_name,
        "matrix_management_chain": matrix_management_chain,
    }

def parse_position_management_chain_data(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse management chain data from Position_Management_Chains_Data.
    This is different from Worker_Management_Chain_Data and contains the actual management chain.
    """
    employment = worker_data.get("Employment_Data", {}) or {}
    wjd_list = ensure_list(employment.get("Worker_Job_Data"))
    wjd = wjd_list[0] if wjd_list else {}
    pos = wjd.get("Position_Data", {}) or {}
    
    # Get Position Management Chains Data
    position_management_chains = pos.get("Position_Management_Chains_Data", {}) or {}
    
    # Supervisory Management Chain
    supervisory_chain = position_management_chains.get("Position_Supervisory_Management_Chain_Data", {}) or {}
    management_chain_data = supervisory_chain.get("Management_Chain_Data", [])
    
    management_chain = []
    direct_manager_id = None
    direct_manager_name = None
    
    if isinstance(management_chain_data, list):
        for level in management_chain_data:
            if isinstance(level, dict):
                # Extract organization info
                org_ref = level.get("Organization_Reference", {}) or {}
                org_ids = org_ref.get("ID", [])
                organization_id = extract_by_type(org_ids, "Organization_Reference_ID")
                organization_name = org_ref.get("Descriptor")
                
                # Extract manager info from Manager_Reference
                manager_ref = level.get("Manager_Reference", [])
                if isinstance(manager_ref, list) and manager_ref:
                    manager_ref = manager_ref[0]  # Take first manager reference
                
                manager_id = None
                manager_name = None
                
                if isinstance(manager_ref, dict):
                    manager_ids = manager_ref.get("ID", [])
                    manager_id = extract_by_type(manager_ids, "Employee_ID")
                    manager_name = manager_ref.get("Descriptor")
                
                # Extract manager name from Manager field (which has Worker_Descriptor)
                manager_data = level.get("Manager", [])
                if isinstance(manager_data, list) and manager_data:
                    manager_item = manager_data[0]
                    if isinstance(manager_item, dict):
                        # Get the name from Worker_Descriptor
                        manager_name = manager_item.get("Worker_Descriptor")
                
                # If this is the first level (direct manager), store it separately
                if direct_manager_id is None:
                    direct_manager_id = manager_id
                    direct_manager_name = manager_name
                
                # Add to management chain
                management_chain.append({
                    "organization_id": organization_id,
                    "organization_name": organization_name,
                    "manager_id": manager_id,
                    "manager_name": manager_name
                })
    
    # Matrix Management Chain
    matrix_chain = position_management_chains.get("Position_Matrix_Management_Chain_Data", {}) or {}
    matrix_management_chain_data = matrix_chain.get("Management_Chain_Data", [])
    
    matrix_management_chain = []
    
    if isinstance(matrix_management_chain_data, list):
        for level in matrix_management_chain_data:
            if isinstance(level, dict):
                # Extract organization info
                org_ref = level.get("Organization_Reference", {}) or {}
                org_ids = org_ref.get("ID", [])
                organization_id = extract_by_type(org_ids, "Organization_Reference_ID")
                organization_name = org_ref.get("Descriptor")
                
                # Extract manager info from Manager_Reference
                manager_ref = level.get("Manager_Reference", [])
                if isinstance(manager_ref, list) and manager_ref:
                    manager_ref = manager_ref[0]  # Take first manager reference
                
                manager_id = None
                manager_name = None
                
                if isinstance(manager_ref, dict):
                    manager_ids = manager_ref.get("ID", [])
                    manager_id = extract_by_type(manager_ids, "Employee_ID")
                    manager_name = manager_ref.get("Descriptor")
                
                # Extract manager name from Manager field (which has Worker_Descriptor)
                manager_data = level.get("Manager", [])
                if isinstance(manager_data, list) and manager_data:
                    manager_item = manager_data[0]
                    if isinstance(manager_item, dict):
                        # Get the name from Worker_Descriptor
                        manager_name = manager_item.get("Worker_Descriptor")
                
                # Add to matrix management chain
                matrix_management_chain.append({
                    "organization_id": organization_id,
                    "organization_name": organization_name,
                    "manager_id": manager_id,
                    "manager_name": manager_name
                })
    
    return {
        "management_chain": management_chain,
        "direct_manager_id": direct_manager_id,
        "direct_manager_name": direct_manager_name,
        "matrix_management_chain": matrix_management_chain,
    }

def parse_payroll_and_tax_data(worker_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse payroll and tax related data from Position_Data.
    """
    employment = worker_data.get("Employment_Data", {}) or {}
    wjd_list = ensure_list(employment.get("Worker_Job_Data"))
    wjd = wjd_list[0] if wjd_list else {}
    pos = wjd.get("Position_Data", {}) or {}
    
    # Federal Withholding FEIN
    federal_withholding_fein = pos.get("Federal_Withholding_FEIN")
    
    # Workers Compensation Code
    workers_compensation_code = None
    wc_data = pos.get("Worker_Compensation_Code_Data", [])
    if isinstance(wc_data, list) and wc_data:
        wc_item = wc_data[0]
        if isinstance(wc_item, dict):
            workers_compensation_code = wc_item.get("Workers_Compensation_Code")
    
    # Payroll Interface Processing Data
    payroll_frequency = None
    payroll_data = pos.get("Payroll_Interface_Processing_Data", {}) or {}
    freq_ref = payroll_data.get("Frequency_Reference", {}) or {}
    freq_ids = freq_ref.get("ID", [])
    payroll_frequency = extract_by_type(freq_ids, "Frequency_ID")
    
    # Manager as of last detected manager change
    last_detected_manager_id = None
    last_detected_manager_name = None
    manager_refs = pos.get("Manager_as_of_last_detected_manager_change_Reference", [])
    if isinstance(manager_refs, list) and manager_refs:
        manager_ref = manager_refs[0]
        if isinstance(manager_ref, dict):
            manager_ids = manager_ref.get("ID", [])
            last_detected_manager_id = extract_by_type(manager_ids, "Employee_ID")
            last_detected_manager_name = manager_ref.get("Descriptor")
    
    return {
        "federal_withholding_fein": federal_withholding_fein,
        "workers_compensation_code": workers_compensation_code,
        "payroll_frequency": payroll_frequency,
        "last_detected_manager_id": last_detected_manager_id,
        "last_detected_manager_name": last_detected_manager_name,
    }
# ———————————————————————————————————————————————————————————————————
# Internal helpers for compensation
# ———————————————————————————————————————————————————————————————————

def _parse_salary_nodes(salary_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for s in salary_nodes:
        if not s:
            continue

        plan_id = extract_by_type(
            s.get("Compensation_Plan_Reference", {}).get("ID", []),
            "Compensation_Plan_ID"
        )
        elem_id = extract_by_type(
            s.get("Compensation_Element_Reference", {}).get("ID", []),
            "Compensation_Element_ID"
        )
        curr_id = extract_by_type(
            s.get("Currency_Reference", {}).get("ID", []),
            "Currency_ID"
        )
        freq_id = extract_by_type(
            s.get("Frequency_Reference", {}).get("ID", []),
            "Frequency_ID"
        )

        eff = s.get("Assignment_Effective_Date")

        result.append({
            "plan":                      plan_id,
            "element":                   elem_id,
            "amount":                    s.get("Amount"),
            "currency":                  curr_id,
            "frequency":                 freq_id,
            "assignment_effective_date": str(eff) if eff else None,
        })
    return result


def _get_summary_section(comp_section: Dict[str, Any], key: str) -> Dict[str, Any]:
    """
    Extrae una sección de resumen asegurándose de:
      - Si viene como lista, tomar el primer elemento.
      - Si viene anidada bajo la misma clave, bajar un nivel.
    """
    sec = comp_section.get(key) or {}
    # si es lista, tomar primer elemento
    if isinstance(sec, list):
        sec = sec[0] if sec else {}
    # si es dict y contiene la misma clave, desanidar
    if isinstance(sec, dict) and key in sec:
        inner = sec[key]
        if isinstance(inner, list):
            sec = inner[0] if inner else {}
        elif isinstance(inner, dict):
            sec = inner
    return sec or {}

from typing import Any, Dict, Optional
from ..utils import extract_by_type

def _parse_compensation_summary(comp_section: Dict[str, Any]) -> Dict[str, Any]:
    """
    Devuelve los resúmenes de compensación en un dict con claves:
    employee, annualized, pay_group, annualized_reporting, hourly
    """
    def _parse_summary(sd: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Si sd es None o un dict vacío -> no hay summary
        if not sd:
            return None

        # Currency: protege Currency_Reference == None
        curr_ref = sd.get("Currency_Reference") or {}
        curr_ids = curr_ref.get("ID") or []
        currency = extract_by_type(curr_ids, "Currency_ID")

        # Frequency: protege Frequency_Reference == None
        freq_ref = sd.get("Frequency_Reference") or {}
        freq_ids = freq_ref.get("ID") or []
        frequency = extract_by_type(freq_ids, "Frequency_ID")

        return {
            "total_base_pay":              sd.get("Total_Base_Pay"),
            "total_salary_and_allowances": sd.get("Total_Salary_and_Allowances"),
            "primary_compensation_basis":  sd.get("Primary_Compensation_Basis"),
            "currency":                    currency,
            "frequency":                   frequency,
        }

    return {
        "employee":             _parse_summary(_get_summary_section(comp_section, "Employee_Compensation_Summary_Data")),
        "annualized":           _parse_summary(_get_summary_section(comp_section, "Annualized_Summary_Data")),
        "pay_group":            _parse_summary(_get_summary_section(comp_section, "Summary_Data_in_Pay_Group_Frequency")),
        "annualized_reporting": _parse_summary(_get_summary_section(comp_section, "Annualized_in_Reporting_Currency_Summary_Data")),
        "hourly":               _parse_summary(_get_summary_section(comp_section, "Summary_Data_in_Hourly_Frequency")),
    }

def _extract_gender(country_info: Dict[str, Any]) -> Optional[str]:

    if not isinstance(country_info, dict):
        return None
    for cp in ensure_list(country_info.get("Country_Personal_Information_Data")):
        if not isinstance(cp, dict):
            continue
        gender_ref = cp.get("Gender_Reference", {}) or {}
        for gid in ensure_list(gender_ref.get("ID")):
            if gid.get("type") == "Gender_Code":
                return gid.get("_value_1")
    return None

def _extract_ethnicity(country_info: Dict[str, Any]) -> Optional[str]:

    if not isinstance(country_info, dict):
        return None
    for cp in ensure_list(country_info.get("Country_Personal_Information_Data")):
        if not isinstance(cp, dict):
            continue
        for eth_ref in ensure_list(cp.get("Ethnicity_Reference")):
            if not isinstance(eth_ref, dict):
                continue
            for eid in ensure_list(eth_ref.get("ID")):
                if eid.get("type") == "Ethnicity_ID":
                    return eid.get("_value_1")
    return None

__all__ = [
    "parse_personal_data",
    "parse_contact_data",
    "parse_worker_organization_data",
    "parse_compensation_data",
    "parse_identification_data",
    "parse_benefits_and_roles",
    "parse_employment_data",
    "parse_worker_status",
    "parse_business_site",
    "parse_management_chain_data",
    "parse_position_management_chain_data",
    "parse_payroll_and_tax_data",
]
