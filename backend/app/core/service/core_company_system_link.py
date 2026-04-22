from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import CompanySystemLinkInput, CompanySystemLinkType
from app.core.models.core_company import CoreCompanySystemLink
from app.core.repository.core_company import CompanyRepository
from app.core.repository.core_company_system_link import CompanySystemLinkRepository
from app.core.repository.core_system import SystemRepository


class CompanySystemLinkService:
    @staticmethod
    def _to_type(link: CoreCompanySystemLink) -> CompanySystemLinkType:
        return CompanySystemLinkType(
            company_id=link.company_id,
            system_id=link.system_id,
            description=link.description,
        )

    @staticmethod
    def _normalize(payload: CompanySystemLinkInput) -> dict:
        data = asdict(payload)

        company_id = data.get("company_id")
        system_id = data.get("system_id")
        description = data.get("description")

        if company_id is None:
            raise HTTPException(status_code=400, detail="company_id is required")
        if system_id is None:
            raise HTTPException(status_code=400, detail="system_id is required")
        if description is not None and not isinstance(description, dict):
            raise HTTPException(status_code=400, detail="description must be a JSON object")

        return data

    @staticmethod
    async def _validate_references(company_id: int, system_id: int) -> None:
        company = await CompanyRepository.get_by_id(company_id)
        if company is None:
            raise HTTPException(status_code=400, detail="company does not exist")

        system = await SystemRepository.get_by_id(system_id)
        if system is None:
            raise HTTPException(status_code=400, detail="system does not exist")

    @staticmethod
    async def create(payload: CompanySystemLinkInput) -> CompanySystemLinkType:
        data = CompanySystemLinkService._normalize(payload)
        await CompanySystemLinkService._validate_references(
            data["company_id"],
            data["system_id"],
        )

        existing = await CompanySystemLinkRepository.get_by_ids(
            data["company_id"],
            data["system_id"],
        )
        if existing is not None:
            raise HTTPException(status_code=400, detail="company system link already exists")

        created = await CompanySystemLinkRepository.create(CoreCompanySystemLink(**data))
        return CompanySystemLinkService._to_type(created)

    @staticmethod
    async def get_all() -> list[CompanySystemLinkType]:
        links = await CompanySystemLinkRepository.get_all()
        return [CompanySystemLinkService._to_type(link) for link in links]

    @staticmethod
    async def get_by_ids(company_id: int, system_id: int) -> CompanySystemLinkType | None:
        link = await CompanySystemLinkRepository.get_by_ids(company_id, system_id)
        return CompanySystemLinkService._to_type(link) if link else None

    @staticmethod
    async def get_by_company(company_id: int) -> list[CompanySystemLinkType]:
        links = await CompanySystemLinkRepository.get_by_company(company_id)
        return [CompanySystemLinkService._to_type(link) for link in links]

    @staticmethod
    async def get_by_system(system_id: int) -> list[CompanySystemLinkType]:
        links = await CompanySystemLinkRepository.get_by_system(system_id)
        return [CompanySystemLinkService._to_type(link) for link in links]

    @staticmethod
    async def update(
        company_id: int,
        system_id: int,
        payload: CompanySystemLinkInput,
    ) -> CompanySystemLinkType:
        data = CompanySystemLinkService._normalize(payload)
        await CompanySystemLinkService._validate_references(
            data["company_id"],
            data["system_id"],
        )

        existing = await CompanySystemLinkRepository.get_by_ids(
            data["company_id"],
            data["system_id"],
        )
        if existing is not None and (
            data["company_id"] != company_id or data["system_id"] != system_id
        ):
            raise HTTPException(status_code=400, detail="company system link already exists")

        updated = await CompanySystemLinkRepository.update(company_id, system_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="company system link not found")

        return CompanySystemLinkService._to_type(updated)

    @staticmethod
    async def delete(company_id: int, system_id: int) -> bool:
        deleted = await CompanySystemLinkRepository.delete(company_id, system_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="company system link not found")
        return True
