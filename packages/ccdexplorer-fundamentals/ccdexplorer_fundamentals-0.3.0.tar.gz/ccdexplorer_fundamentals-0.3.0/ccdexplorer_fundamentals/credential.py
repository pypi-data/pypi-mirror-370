from enum import Enum
from ccdexplorer_fundamentals.GRPCClient.CCD_Types import *  # noqa: F403


class CredentialElement(Enum):
    firstName = "First Name"
    lastName = "Last Name"
    sex = "Sex"
    dob = "Date of Birth"
    countryOfResidence = "Country of Residence"
    nationality = "Nationatility"
    idDocType = "Identity Document Type"
    idDocNo = "Identity Document Number"
    idDocIssuer = "Identity Document Issuer"
    idDocIssuedAt = "ID Valid from"
    idDocExpiresAt = "ID Valid to"
    nationalIdNo = "National ID number"
    taxIdNo = "Tax ID number"
    lei = "Legal Entity ID"
    legalName = "Legal Name"
    legalJurisdictionCountry = "Legal Jurisdiction Country"
    businessNumber = "Business Number"
    registrationAuthority = "Registration Authority"


class CredentialDocType(Enum):
    na = "0"
    Passport = "1"
    National_ID_Card = "2"
    Driving_License = "3"
    Immigration_Card = "4"


class Credentials:
    """
    This class processes credential information as retrieved from the node.
    """

    def __init__(self):
        pass

    def determine_id_providers(self, ac):
        """
        Input to this method is the output from the node.
        """
        credentials = []
        for key_policy, v in ac.items():
            v: CCD_AccountCredential  # noqa: F405
            if v.initial:
                v = v.initial
                normal = False
            elif v.normal:
                v = v.normal
                normal = True

            c = {
                "ip_identity": v.ip_id,
                "created_at": v.policy.created_at,
                "valid_to": v.policy.valid_to,
            }
            if normal:
                c.update({"cred_id": v.cred_id})

            if len(v.policy.attributes.keys()) > 0:
                policy_attributes = []
                for key_policy, commitmentAttribute in v.policy.attributes.items():
                    value = commitmentAttribute
                    policy_attributes.append(
                        {"key": CredentialElement[key_policy].value, "value": value}
                    )
                c.update({"policy_attributes": policy_attributes})
            if normal:
                if len(v.commitments.attributes.keys()) > 0:
                    commitment_attributes = []
                    for (
                        key_commitment,
                        commitmentAttribute,
                    ) in v.commitments.attributes.items():
                        value = commitmentAttribute
                        commitment_attributes.append(
                            CredentialElement[key_commitment].value
                        )
                    c.update({"commitment_attributes": commitment_attributes})
            credentials.append(c)
        return credentials


class Identity:
    def __init__(self, account_info: CCD_AccountInfo):  # noqa: F405
        if account_info:
            self.credentials = Credentials().determine_id_providers(
                account_info.credentials
            )
            self.threshold = account_info.threshold
        else:
            self.credentials = []
            self.threshold = 0
