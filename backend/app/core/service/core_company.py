from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import CompanyInput, CompanyType
from app.core.models.core_company import CoreCompany
from app.core.repository.core_company import CompanyRepository
from app.core.repository.core_system import SystemRepository
from app.core.service.core_system import SystemService


class CompanyService:

    @staticmethod
    def _serialize(company: CoreCompany) -> CompanyType:
        return CompanyType(
            id=company.id,
            name=company.name,
            active=company.active,
            sequence=company.sequence,
            currency_id=company.currency_id,
            color=company.color,
            street=company.street,
            street2=company.street2,
            zip=company.zip,
            city=company.city,
            state_id=company.state_id,
            country_id=company.country_id,
            phone=company.phone,
            email=company.email,
            website=company.website,
            logo_url=company.logo_url,
            vat=company.vat,
            lang_id=company.lang_id,
            systems_ids=[system.id for system in company.systems_ids if system.id is not None],
        )

    @staticmethod
    def _normalize(payload: CompanyInput) -> dict:
        data = asdict(payload)
        data["name"] = data["name"].strip()
        data["systems_ids"] = SystemService._normalize_id_list(
            data.get("systems_ids"), "systems_ids"
        )
        if not data["name"]:
            raise HTTPException(status_code=400, detail="name is required")
        return data

    @staticmethod
    async def _validate_system_refs(system_ids: list[int]) -> None:
        systems = await SystemRepository.get_by_ids(system_ids)
        found_ids = {system.id for system in systems}
        missing_ids = [system_id for system_id in system_ids if system_id not in found_ids]
        if missing_ids:
            missing_text = ", ".join(str(system_id) for system_id in missing_ids)
            raise HTTPException(
                status_code=400,
                detail=f"systems do not exist: {missing_text}",
            )

    @staticmethod
    async def create(payload: CompanyInput) -> CompanyType:
        data = CompanyService._normalize(payload)
        system_ids = data.pop("systems_ids", [])
        await CompanyService._validate_system_refs(system_ids)
        created = await CompanyRepository.create(CoreCompany(**data), system_ids=system_ids)
        return CompanyService._serialize(created)

    @staticmethod
    async def get_all() -> list[CompanyType]:
        companies = await CompanyRepository.get_all()
        return [CompanyService._serialize(company) for company in companies]

    @staticmethod
    async def get_by_id(company_id: int) -> CompanyType | None:
        company = await CompanyRepository.get_by_id(company_id)
        return CompanyService._serialize(company) if company else None

    @staticmethod
    async def update(company_id: int, payload: CompanyInput) -> CompanyType:
        data = CompanyService._normalize(payload)
        system_ids = data.pop("systems_ids", [])
        await CompanyService._validate_system_refs(system_ids)
        updated = await CompanyRepository.update(company_id, data, system_ids=system_ids)
        if updated is None:
            raise HTTPException(status_code=404, detail="company not found")

        return CompanyService._serialize(updated)

    @staticmethod
    async def delete(company_id: int) -> bool:
        deleted = await CompanyRepository.delete(company_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="company not found")
        return True
