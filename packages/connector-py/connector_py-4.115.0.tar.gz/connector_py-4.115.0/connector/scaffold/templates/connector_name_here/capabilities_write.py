from connector.generated import (
    ActivateAccountRequest,
    ActivateAccountResponse,
    AssignEntitlementRequest,
    AssignEntitlementResponse,
    CreateAccountResponse,
    DeactivateAccountRequest,
    DeactivateAccountResponse,
    DowngradeLicenseRequest,
    DowngradeLicenseResponse,
    DeleteAccountRequest,
    DeleteAccountResponse,
    ReleaseResourcesRequest,
    ReleaseResourcesResponse,
    TransferDataRequest,
    TransferDataResponse,
    UnassignEntitlementRequest,
    UnassignEntitlementResponse,
)
from connector.integration import CustomRequest

from {name}.dto.user import CreateAccount


async def assign_entitlement(args: AssignEntitlementRequest) -> AssignEntitlementResponse:
    raise NotImplementedError


async def unassign_entitlement(
    args: UnassignEntitlementRequest,
) -> UnassignEntitlementResponse:
    raise NotImplementedError


async def create_account(
    args: CustomRequest[CreateAccount],
) -> CreateAccountResponse:
    raise NotImplementedError


async def delete_account(
    args: DeleteAccountRequest,
) -> DeleteAccountResponse:
    raise NotImplementedError


async def activate_account(
    args: ActivateAccountRequest,
) -> ActivateAccountResponse:
    raise NotImplementedError


async def deactivate_account(
    args: DeactivateAccountRequest,
) -> DeactivateAccountResponse:
    raise NotImplementedError

async def transfer_data(
    args: TransferDataRequest,
) -> TransferDataResponse:
    raise NotImplementedError

async def downgrade_license(
    args: DowngradeLicenseRequest,
) -> DowngradeLicenseResponse:
    raise NotImplementedError

async def release_resources(
    args: ReleaseResourcesRequest,
) -> ReleaseResourcesResponse:
    raise NotImplementedError
