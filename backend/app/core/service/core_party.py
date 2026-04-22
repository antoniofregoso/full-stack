from dataclasses import asdict

from fastapi import HTTPException

from app.core.graphql.types import PartyInput, PartyType
from app.core.models.core_party import CoreParty
from app.core.repository.core_party import PartyRepository


class PartyService:

    @staticmethod
    def _serialize(party: CoreParty) -> PartyType:
        return PartyType(
            id=party.id,
            name=party.name,
            active=party.active,
            sequence=party.sequence,
            color=party.color,
            parent_id=party.parent_id,
            lang_id=party.lang_id,
            street=party.street,
            street2=party.street2,
            zip=party.zip,
            city=party.city,
            state_id=party.state_id,
            country_id=party.country_id,
            tz_id=party.tz_id,
            tz_offset=party.tz_offset,
            phone=party.phone,
            email=party.email,
            function=party.function,
            website=party.website,
            vat=party.vat,
            avatar_url=party.avatar_url,
            is_company=party.is_company,
            company_id=party.company_id,
            created_at=party.created_at,
            create_by=party.create_by,
            updated_at=party.updated_at,
            updated_by=party.updated_by,
        )

    @staticmethod
    def _normalize(payload: PartyInput) -> dict:
        data = asdict(payload)
        data["name"] = data["name"].strip()
        if not data["name"]:
            raise HTTPException(status_code=400, detail="name is required")
        return data

    @staticmethod
    async def create(payload: PartyInput) -> PartyType:
        data = PartyService._normalize(payload)
        created = await PartyRepository.create(CoreParty(**data))
        return PartyService._serialize(created)

    @staticmethod
    async def get_all() -> list[PartyType]:
        parties = await PartyRepository.get_all()
        return [PartyService._serialize(party) for party in parties]

    @staticmethod
    async def get_by_id(party_id: int) -> PartyType | None:
        party = await PartyRepository.get_by_id(party_id)
        return PartyService._serialize(party) if party else None

    @staticmethod
    async def update(party_id: int, payload: PartyInput) -> PartyType:
        data = PartyService._normalize(payload)
        updated = await PartyRepository.update(party_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="party not found")

        return PartyService._serialize(updated)

    @staticmethod
    async def delete(party_id: int) -> bool:
        deleted = await PartyRepository.delete(party_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="party not found")
        return True
