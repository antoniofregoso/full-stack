import json
from pathlib import Path
from typing import Any

from sqlmodel import select

from app.auth.service.authentication import AuthenticationService
from app.auth.models.auth_user import (
    AuthPermission,
    AuthRole,
    AuthRolePermission,
    AuthUser,
    AuthUserRole,
    ThemeMode,
    UserType,
)
from app.core.models.core_country import CoreCountry, CoreCountryState
from app.core.models.core_entity import CoreEntity
from app.core.models.core_page import CorePage
from config import db
from app.core.models.core_currency import CoreCurrency, CurrencyPosition
from app.core.models.core_lang import CoreLang
from app.core.models.core_seed_run import CoreSeedRun
from app.core.models.core_system import CoreSystem
from app.core.models.core_team import CoreTeam
from app.core.models.core_module import CoreModule
from app.core.models.core_user_assignment import CoreUserAssignment
from logging_config import get_logger

logger = get_logger(__name__)
CORE_CURRENCY_SEED_KEY = "core_currency:v1"
CORE_COUNTRY_SEED_KEY = "core_country:v1"
CORE_LANG_SEED_KEY = "core_lang:v1"
CORE_PAGE_SEED_KEY = "core_page:v1"
CORE_SYSTEM_SEED_KEY = "core_system:v1"
CORE_USER_ASSIGNMENT_SEED_KEY = "core_user_assignment:v1"
AUTH_USER_SEED_KEY = "auth_user:v1"
AUTH_ROLE_SEED_KEY = "auth_role:v1"
AUTH_PERMISSION_SEED_KEY = "auth_permission:v1"
AUTH_ROLE_PERMISSION_SEED_KEY = "auth_role_permission:v1"
SYSTEM_BOT_EMAIL = "bot@system.local"


def _country_code_to_flag(country_code: str) -> str:
    normalized = country_code.strip().upper()
    if len(normalized) != 2 or not normalized.isalpha():
        return ""
    base = 127397
    return "".join(chr(base + ord(char)) for char in normalized)


def _pick_translation(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return (
            value.get("es_MX")
            or value.get("en_US")
            or next((v for v in value.values() if isinstance(v, str)), "")
        )
    return ""


async def _get_system_bot_user(session) -> AuthUser:
    result = await session.execute(
        select(AuthUser).where(AuthUser.email == SYSTEM_BOT_EMAIL)
    )
    bot_user = result.scalars().first()
    if bot_user is None:
        raise ValueError(
            f"System bot user '{SYSTEM_BOT_EMAIL}' must exist before running this seed"
        )
    return bot_user


def _normalize_currency_row(row: dict[str, Any]) -> dict[str, Any]:
    code = (row.get("name") or "").strip().upper()
    iso_numeric = row.get("code")

    return {
        "code": code,
        "name": code,
        "iso_numeric": int(iso_numeric) if isinstance(iso_numeric, int) else 0,
        "symbol": (row.get("symbol") or "").strip(),
        "currency_unit_label": _pick_translation(row.get("currency_unit_label")) or code,
        "currency_subunit_label": _pick_translation(row.get("currency_subunit_label")),
        "rounding": 0.01,
        "position": CurrencyPosition.BEFORE,
        "active": True,
    }


async def seed_core_currencies() -> tuple[int, int]:
    data_file = Path(__file__).resolve().parents[1] / "data" / "core_currency.json"
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("core_currency.json must contain a list of currencies")

    inserted = 0
    updated = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == CORE_CURRENCY_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info("Seed %s already executed. Skipping load.", CORE_CURRENCY_SEED_KEY)
            return 0, 0
        bot_user = await _get_system_bot_user(session)

        result = await session.execute(select(CoreCurrency))
        existing_by_code = {currency.code: currency for currency in result.scalars().all()}

        for raw in raw_rows:
            payload = _normalize_currency_row(raw)
            code = payload["code"]
            if not code:
                continue

            existing = existing_by_code.get(code)
            if existing is None:
                session.add(CoreCurrency(**payload, create_by=bot_user.id))
                inserted += 1
                continue

            changed = False
            for field, value in payload.items():
                if getattr(existing, field) != value:
                    setattr(existing, field, value)
                    changed = True
            if existing.updated_by != bot_user.id:
                existing.updated_by = bot_user.id
                changed = True

            if changed:
                session.add(existing)
                updated += 1

        session.add(CoreSeedRun(seed_key=CORE_CURRENCY_SEED_KEY))
        await session.commit()

    logger.info(
        "Currency seed completed. Inserted=%s Updated=%s",
        inserted,
        updated,
    )
    return inserted, updated


def _normalize_auth_user_row(row: dict[str, Any]) -> dict[str, Any]:
    avatar_url = row.get("avatar_url")
    normalized_avatar_url = str(avatar_url).strip() if avatar_url is not None else None
    return {
        "name": str(row.get("name") or "").strip(),
        "email": str(row.get("email") or "").strip(),
        "password": str(row.get("password") or "").strip(),
        "avatar_url": normalized_avatar_url or None,
        "active": bool(row.get("active")) if row.get("active") is not None else True,
        "theme": ThemeMode(str(row.get("theme") or ThemeMode.system.value).strip().lower()),
        "user_type": UserType(str(row.get("user_type") or UserType.HUMAN.value).strip().upper()),
    }


async def seed_auth_users() -> tuple[int, int]:
    data_file = Path(__file__).resolve().parents[2] / "auth" / "data" / "auth_user.json"
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("auth_user.json must contain a list of users")

    inserted = 0
    updated = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == AUTH_USER_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info("Seed %s already executed. Skipping load.", AUTH_USER_SEED_KEY)
            return 0, 0

        result = await session.execute(select(AuthUser))
        existing_by_email = {user.email: user for user in result.scalars().all()}
        bot_user = existing_by_email.get(SYSTEM_BOT_EMAIL)

        normalized_rows = [_normalize_auth_user_row(raw) for raw in raw_rows]
        normalized_rows.sort(
            key=lambda payload: payload["user_type"] != UserType.SYSTEM
        )

        for payload in normalized_rows:
            email = payload["email"]
            password = payload.pop("password")
            if not email:
                continue

            hashed_password = AuthenticationService.pwd_context.hash(password)
            payload["password"] = hashed_password
            existing = existing_by_email.get(email)

            if existing is None:
                user = AuthUser(**payload)
                if bot_user is not None:
                    user.create_by = bot_user.id
                session.add(user)
                await session.flush()
                if email == SYSTEM_BOT_EMAIL:
                    if user.create_by is None:
                        user.create_by = user.id
                        session.add(user)
                    bot_user = user
                existing_by_email[email] = user
                inserted += 1
                continue

            changed = False
            for field, value in payload.items():
                if getattr(existing, field) != value:
                    setattr(existing, field, value)
                    changed = True

            if existing.password != hashed_password:
                existing.password = hashed_password
                changed = True

            if existing.email == SYSTEM_BOT_EMAIL:
                if existing.create_by is None:
                    existing.create_by = existing.id
                    changed = True
            elif bot_user is not None and existing.updated_by != bot_user.id:
                existing.updated_by = bot_user.id
                changed = True

            if changed:
                session.add(existing)
                updated += 1

        session.add(CoreSeedRun(seed_key=AUTH_USER_SEED_KEY))
        await session.commit()

    logger.info("Auth user seed completed. Inserted=%s Updated=%s", inserted, updated)
    return inserted, updated


def _normalize_auth_role_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": str(row.get("name") or "").strip(),
        "description": str(row.get("description") or "").strip() or None,
        "active": bool(row.get("active")) if row.get("active") is not None else True,
        "user_emails": [str(email).strip() for email in (row.get("user_emails") or []) if str(email).strip()],
    }


async def seed_auth_roles() -> tuple[int, int, int]:
    data_file = Path(__file__).resolve().parents[2] / "auth" / "data" / "auth_role.json"
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("auth_role.json must contain a list of roles")

    inserted = 0
    updated = 0
    assigned = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == AUTH_ROLE_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info("Seed %s already executed. Skipping load.", AUTH_ROLE_SEED_KEY)
            return 0, 0, 0
        bot_user = await _get_system_bot_user(session)

        roles_result = await session.execute(select(AuthRole))
        existing_roles = {role.name: role for role in roles_result.scalars().all()}

        users_result = await session.execute(select(AuthUser))
        users_by_email = {user.email: user for user in users_result.scalars().all()}

        mappings_result = await session.execute(select(AuthUserRole))
        existing_mappings = {
            (mapping.user_id, mapping.role_id) for mapping in mappings_result.scalars().all()
        }

        for raw in raw_rows:
            payload = _normalize_auth_role_row(raw)
            role_name = payload["name"]
            user_emails = payload.pop("user_emails")
            if not role_name:
                continue

            role = existing_roles.get(role_name)
            if role is None:
                role = AuthRole(**payload, create_by=bot_user.id)
                session.add(role)
                await session.flush()
                existing_roles[role_name] = role
                inserted += 1
            else:
                changed = False
                for field, value in payload.items():
                    if getattr(role, field) != value:
                        setattr(role, field, value)
                        changed = True
                if role.updated_by != bot_user.id:
                    role.updated_by = bot_user.id
                    changed = True
                if changed:
                    session.add(role)
                    updated += 1

            for email in user_emails:
                user = users_by_email.get(email)
                if user is None:
                    raise ValueError(f"User with email '{email}' was not found for role '{role_name}'")
                mapping_key = (user.id, role.id)
                if mapping_key in existing_mappings:
                    continue
                session.add(
                    AuthUserRole(
                        user_id=user.id,
                        role_id=role.id,
                        create_by=bot_user.id,
                    )
                )
                existing_mappings.add(mapping_key)
                assigned += 1

        session.add(CoreSeedRun(seed_key=AUTH_ROLE_SEED_KEY))
        await session.commit()

    logger.info(
        "Auth role seed completed. Inserted=%s Updated=%s Assigned=%s",
        inserted,
        updated,
        assigned,
    )
    return inserted, updated, assigned


def _normalize_auth_permission_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "code": str(row.get("code") or "").strip(),
        "description": str(row.get("description") or "").strip() or None,
        "active": bool(row.get("active")) if row.get("active") is not None else True,
    }


async def seed_auth_permissions() -> tuple[int, int]:
    data_file = Path(__file__).resolve().parents[2] / "auth" / "data" / "auth_permission.json"
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("auth_permission.json must contain a list of permissions")

    inserted = 0
    updated = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == AUTH_PERMISSION_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info("Seed %s already executed. Skipping load.", AUTH_PERMISSION_SEED_KEY)
            return 0, 0
        bot_user = await _get_system_bot_user(session)

        result = await session.execute(select(AuthPermission))
        existing_by_code = {permission.code: permission for permission in result.scalars().all()}

        for raw in raw_rows:
            payload = _normalize_auth_permission_row(raw)
            code = payload["code"]
            if not code:
                continue

            existing = existing_by_code.get(code)
            if existing is None:
                session.add(AuthPermission(**payload, create_by=bot_user.id))
                inserted += 1
                continue

            changed = False
            for field, value in payload.items():
                if getattr(existing, field) != value:
                    setattr(existing, field, value)
                    changed = True
            if existing.updated_by != bot_user.id:
                existing.updated_by = bot_user.id
                changed = True

            if changed:
                session.add(existing)
                updated += 1

        session.add(CoreSeedRun(seed_key=AUTH_PERMISSION_SEED_KEY))
        await session.commit()

    logger.info("Auth permission seed completed. Inserted=%s Updated=%s", inserted, updated)
    return inserted, updated


def _normalize_auth_role_permission_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "role_name": str(row.get("role_name") or "").strip(),
        "permission_codes": [
            str(code).strip()
            for code in (row.get("permission_codes") or [])
            if str(code).strip()
        ],
    }


async def seed_auth_role_permissions() -> tuple[int, int]:
    data_file = (
        Path(__file__).resolve().parents[2] / "auth" / "data" / "auth_role_permission.json"
    )
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("auth_role_permission.json must contain a list of role-permission mappings")

    assigned = 0
    skipped = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == AUTH_ROLE_PERMISSION_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info(
                "Seed %s already executed. Skipping load.",
                AUTH_ROLE_PERMISSION_SEED_KEY,
            )
            return 0, 0
        bot_user = await _get_system_bot_user(session)

        roles_result = await session.execute(select(AuthRole))
        roles_by_name = {role.name: role for role in roles_result.scalars().all()}

        permissions_result = await session.execute(select(AuthPermission))
        permissions_by_code = {
            permission.code: permission for permission in permissions_result.scalars().all()
        }

        mappings_result = await session.execute(select(AuthRolePermission))
        existing_mappings = {
            (mapping.role_id, mapping.permission_id)
            for mapping in mappings_result.scalars().all()
        }

        for raw in raw_rows:
            payload = _normalize_auth_role_permission_row(raw)
            role_name = payload["role_name"]
            if not role_name:
                continue

            role = roles_by_name.get(role_name)
            if role is None:
                raise ValueError(f"Role '{role_name}' was not found for role-permission seed")

            for permission_code in payload["permission_codes"]:
                permission = permissions_by_code.get(permission_code)
                if permission is None:
                    raise ValueError(
                        f"Permission '{permission_code}' was not found for role '{role_name}'"
                    )
                mapping_key = (role.id, permission.id)
                if mapping_key in existing_mappings:
                    skipped += 1
                    continue
                session.add(
                    AuthRolePermission(
                        role_id=role.id,
                        permission_id=permission.id,
                        create_by=bot_user.id,
                    )
                )
                existing_mappings.add(mapping_key)
                assigned += 1

        session.add(CoreSeedRun(seed_key=AUTH_ROLE_PERMISSION_SEED_KEY))
        await session.commit()

    logger.info(
        "Auth role-permission seed completed. Assigned=%s Skipped=%s",
        assigned,
        skipped,
    )
    return assigned, skipped


def _normalize_lang_row(row: dict[str, Any]) -> dict[str, Any]:
    week_start = row.get("week_start")
    try:
        normalized_week_start = int(week_start) if week_start is not None else None
    except (TypeError, ValueError) as exc:
        raise ValueError("core_lang.week_start must be an integer between 1 and 7") from exc

    if normalized_week_start is not None and normalized_week_start not in {1, 2, 3, 4, 5, 6, 7}:
        raise ValueError("core_lang.week_start must be an integer between 1 and 7")

    code = str(row.get("code") or "").strip()
    flag = str(row.get("flag") or "").strip()
    if not flag:
        parts = code.split("_")
        if len(parts) >= 2:
            flag = _country_code_to_flag(parts[-1])

    return {
        "name": str(row.get("name") or "").strip(),
        "code": code,
        "iso_code": str(row.get("iso_code") or "").strip(),
        "url_code": str(row.get("url_code") or "").strip(),
        "date_format": str(row.get("date_format") or "").strip() or None,
        "time_format": str(row.get("time_format") or "").strip() or None,
        "week_start": normalized_week_start,
        "flag": flag or None,
        "active": bool(row.get("active")) if row.get("active") is not None else False,
    }


async def seed_core_langs() -> tuple[int, int]:
    data_file = Path(__file__).resolve().parents[1] / "data" / "core_lang.json"
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("core_lang.json must contain a list of languages")

    inserted = 0
    updated = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == CORE_LANG_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info("Seed %s already executed. Skipping load.", CORE_LANG_SEED_KEY)
            return 0, 0
        bot_user = await _get_system_bot_user(session)

        result = await session.execute(select(CoreLang))
        existing_by_code = {lang.code: lang for lang in result.scalars().all()}

        for raw in raw_rows:
            payload = _normalize_lang_row(raw)
            code = payload["code"]
            if not code:
                continue

            existing = existing_by_code.get(code)
            if existing is None:
                session.add(CoreLang(**payload, create_by=bot_user.id))
                inserted += 1
                continue

            changed = False
            for field, value in payload.items():
                if getattr(existing, field) != value:
                    setattr(existing, field, value)
                    changed = True
            if existing.updated_by != bot_user.id:
                existing.updated_by = bot_user.id
                changed = True

            if changed:
                session.add(existing)
                updated += 1

        session.add(CoreSeedRun(seed_key=CORE_LANG_SEED_KEY))
        await session.commit()

    logger.info("Language seed completed. Inserted=%s Updated=%s", inserted, updated)
    return inserted, updated


def _normalize_translated_name(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object like {{'es_MX': 'Mexico'}}")

    normalized: dict[str, str] = {}
    for key, translation in value.items():
        locale = str(key).strip()
        text = str(translation).strip() if translation is not None else ""
        if locale and text:
            normalized[locale] = text

    if not normalized:
        raise ValueError(f"{field_name} must include at least one locale with text")

    return normalized


def _normalize_country_row(row: dict[str, Any]) -> dict[str, Any]:
    code = str(row.get("code") or "").strip().upper()
    phone_code = row.get("phone_code")
    currency_code = row.get("currency_code")

    return {
        "code": code,
        "name": _normalize_translated_name(row.get("name"), "country.name"),
        "phone_code": str(phone_code).strip() if phone_code else None,
        "currency_code": str(currency_code).strip().upper() if currency_code else None,
        "states": row.get("states") or [],
    }


def _normalize_state_row(row: dict[str, Any], country_id: int) -> dict[str, Any]:
    code = str(row.get("code") or "").strip().upper()
    if not code:
        raise ValueError("state.code is required")

    return {
        "code": code,
        "name": _normalize_translated_name(row.get("name"), f"state.name[{code}]"),
        "country_id": country_id,
    }


async def seed_core_countries() -> tuple[int, int, int, int]:
    data_file = Path(__file__).resolve().parents[1] / "data" / "core_country.json"
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("core_country.json must contain a list of countries")

    inserted_countries = 0
    updated_countries = 0
    inserted_states = 0
    updated_states = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == CORE_COUNTRY_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info("Seed %s already executed. Skipping load.", CORE_COUNTRY_SEED_KEY)
            return 0, 0, 0, 0
        bot_user = await _get_system_bot_user(session)

        currencies_result = await session.execute(select(CoreCurrency))
        currencies_by_code = {
            currency.code: currency for currency in currencies_result.scalars().all()
        }

        countries_result = await session.execute(select(CoreCountry))
        countries_by_code = {
            country.code: country for country in countries_result.scalars().all()
        }

        states_result = await session.execute(select(CoreCountryState))
        states_by_key = {
            (state.country_id, state.code): state for state in states_result.scalars().all()
        }

        for raw in raw_rows:
            payload = _normalize_country_row(raw)
            code = payload["code"]
            if not code:
                continue

            currency_id = None
            currency_code = payload.pop("currency_code")
            raw_states = payload.pop("states")

            if currency_code:
                currency = currencies_by_code.get(currency_code)
                if currency is None:
                    raise ValueError(
                        f"Currency with code '{currency_code}' was not found for country '{code}'"
                    )
                currency_id = currency.id

            payload["currency_id"] = currency_id

            existing_country = countries_by_code.get(code)
            if existing_country is None:
                country = CoreCountry(**payload, create_by=bot_user.id)
                session.add(country)
                await session.flush()
                countries_by_code[code] = country
                inserted_countries += 1
            else:
                country = existing_country
                changed = False
                for field, value in payload.items():
                    if getattr(country, field) != value:
                        setattr(country, field, value)
                        changed = True
                if country.updated_by != bot_user.id:
                    country.updated_by = bot_user.id
                    changed = True
                if changed:
                    session.add(country)
                    updated_countries += 1

            for raw_state in raw_states:
                state_payload = _normalize_state_row(raw_state, country.id)
                state_key = (country.id, state_payload["code"])
                existing_state = states_by_key.get(state_key)

                if existing_state is None:
                    state = CoreCountryState(**state_payload, create_by=bot_user.id)
                    session.add(state)
                    states_by_key[state_key] = state
                    inserted_states += 1
                    continue

                changed = False
                for field, value in state_payload.items():
                    if getattr(existing_state, field) != value:
                        setattr(existing_state, field, value)
                        changed = True
                if existing_state.updated_by != bot_user.id:
                    existing_state.updated_by = bot_user.id
                    changed = True

                if changed:
                    session.add(existing_state)
                    updated_states += 1

        session.add(CoreSeedRun(seed_key=CORE_COUNTRY_SEED_KEY))
        await session.commit()

    logger.info(
        "Country seed completed. Countries inserted=%s updated=%s. States inserted=%s updated=%s",
        inserted_countries,
        updated_countries,
        inserted_states,
        updated_states,
    )
    return inserted_countries, updated_countries, inserted_states, updated_states


def _normalize_system_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "code": str(row.get("code") or "").strip().lower(),
        "name": _normalize_translated_name(row.get("name"), "system.name"),
        "icon": row.get("icon") if isinstance(row.get("icon"), dict) else None,
        "description": (
            _normalize_translated_name(row.get("description"), "system.description")
            if row.get("description") is not None
            else None
        ),
        "active": bool(row.get("active")) if row.get("active") is not None else True,
        "sequence": int(row.get("sequence")) if row.get("sequence") is not None else 10,
        "color": str(row.get("color") or "").strip() or None,
        "teams": row.get("teams") or [],
    }


def _normalize_team_seed_row(row: dict[str, Any]) -> dict[str, Any]:
    raw_name = row.get("name")
    if raw_name is None:
        raw_name = row.get("name:")

    return {
        "code": str(row.get("code") or "").strip().lower(),
        "name": _normalize_translated_name(raw_name, "team.name"),
        "icon": row.get("icon") if isinstance(row.get("icon"), dict) else None,
        "description": (
            _normalize_translated_name(row.get("description"), "team.description")
            if row.get("description") is not None
            else None
        ),
        "active": bool(row.get("active")) if row.get("active") is not None else True,
        "sequence": int(row.get("sequence")) if row.get("sequence") is not None else 10,
        "color": str(row.get("color") or "").strip() or None,
    }


def _normalize_page_seed_row(row: dict[str, Any]) -> dict[str, Any]:
    page_name_value = row.get("name")
    page_description_value = row.get("description")

    # Backward-compatible fallback for legacy page seed shape:
    # name/description can live inside data.model.description.text.
    if page_name_value is None:
        model_description_text = (
            (((row.get("data") or {}).get("model") or {}).get("description") or {}).get("text")
        )
        if isinstance(model_description_text, dict):
            page_name_value = model_description_text

    if page_description_value is None:
        model_description_text = (
            (((row.get("data") or {}).get("model") or {}).get("description") or {}).get("text")
        )
        if isinstance(model_description_text, dict):
            page_description_value = model_description_text

    return {
        "name": _normalize_translated_name(page_name_value, "page.name"),
        "description": (
            _normalize_translated_name(page_description_value, "page.description")
            if page_description_value is not None
            else None
        ),
        "keys": row.get("keys") if isinstance(row.get("keys"), dict) else None,
        "view": row.get("view") if isinstance(row.get("view"), dict) else None,
        "active": bool(row.get("active")) if row.get("active") is not None else True,
        "sequence": int(row.get("sequence")) if row.get("sequence") is not None else 10,
        "color": str(row.get("color") or "").strip() or None,
        "public": bool(row.get("public")) if row.get("public") is not None else False,
    }


async def seed_core_pages() -> tuple[int, int]:
    data_file = Path(__file__).resolve().parents[1] / "data" / "core_page.json"
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("core_page.json must contain a list of pages")

    inserted = 0
    updated = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == CORE_PAGE_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info("Seed %s already executed. Skipping load.", CORE_PAGE_SEED_KEY)
            return 0, 0

        bot_user = await _get_system_bot_user(session)

        pages_result = await session.execute(select(CorePage))
        pages_by_name = {json.dumps(page.name, sort_keys=True): page for page in pages_result.scalars().all()}

        for raw in raw_rows:
            payload = _normalize_page_seed_row(raw)
            page_name = payload["name"]
            if not page_name:
                continue

            page_key = json.dumps(page_name, sort_keys=True)
            existing_page = pages_by_name.get(page_key)

            if existing_page is None:
                page = CorePage(**payload, create_by=bot_user.id)
                session.add(page)
                pages_by_name[page_key] = page
                inserted += 1
                continue

            changed = False
            for field, value in payload.items():
                if getattr(existing_page, field) != value:
                    setattr(existing_page, field, value)
                    changed = True
            if existing_page.updated_by != bot_user.id:
                existing_page.updated_by = bot_user.id
                changed = True
            if changed:
                session.add(existing_page)
                updated += 1

        session.add(CoreSeedRun(seed_key=CORE_PAGE_SEED_KEY))
        await session.commit()

    logger.info(
        "Core page seed completed. Inserted=%s Updated=%s",
        inserted,
        updated,
    )
    return inserted, updated


async def seed_core_systems() -> tuple[int, int, int, int]:
    data_file = Path(__file__).resolve().parents[1] / "data" / "core_system.json"
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("core_system.json must contain a list of systems")

    inserted_systems = 0
    updated_systems = 0
    inserted_teams = 0
    updated_teams = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == CORE_SYSTEM_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info("Seed %s already executed. Skipping load.", CORE_SYSTEM_SEED_KEY)
            return 0, 0, 0, 0

        bot_user = await _get_system_bot_user(session)

        systems_result = await session.execute(select(CoreSystem))
        systems_by_code = {system.code: system for system in systems_result.scalars().all()}

        teams_result = await session.execute(select(CoreTeam))
        teams_by_key = {
            (team.system_id, team.code): team for team in teams_result.scalars().all()
        }

        for raw in raw_rows:
            payload = _normalize_system_row(raw)
            code = payload["code"]
            if not code:
                continue

            raw_teams = payload.pop("teams")
            existing_system = systems_by_code.get(code)

            if existing_system is None:
                system = CoreSystem(**payload, create_by=bot_user.id)
                session.add(system)
                await session.flush()
                systems_by_code[code] = system
                inserted_systems += 1
            else:
                system = existing_system
                changed = False
                for field, value in payload.items():
                    if getattr(system, field) != value:
                        setattr(system, field, value)
                        changed = True
                if system.updated_by != bot_user.id:
                    system.updated_by = bot_user.id
                    changed = True
                if changed:
                    session.add(system)
                    updated_systems += 1

            for raw_team in raw_teams:
                team_payload = _normalize_team_seed_row(raw_team)
                team_code = team_payload["code"]
                if not team_code:
                    continue

                team_key = (system.id, team_code)
                existing_team = teams_by_key.get(team_key)

                if existing_team is None:
                    team = CoreTeam(
                        **team_payload,
                        system_id=system.id,
                        create_by=bot_user.id,
                    )
                    session.add(team)
                    teams_by_key[team_key] = team
                    inserted_teams += 1
                    continue

                changed = False
                for field, value in team_payload.items():
                    if getattr(existing_team, field) != value:
                        setattr(existing_team, field, value)
                        changed = True
                if existing_team.updated_by != bot_user.id:
                    existing_team.updated_by = bot_user.id
                    changed = True
                if changed:
                    session.add(existing_team)
                    updated_teams += 1

        session.add(CoreSeedRun(seed_key=CORE_SYSTEM_SEED_KEY))
        await session.commit()

    logger.info(
        "System seed completed. Systems inserted=%s updated=%s. Teams inserted=%s updated=%s",
        inserted_systems,
        updated_systems,
        inserted_teams,
        updated_teams,
    )
    return inserted_systems, updated_systems, inserted_teams, updated_teams


def _normalize_core_user_assignment_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "user_email": str(row.get("user_email") or "").strip().lower(),
        "system_code": str(row.get("system_code") or "").strip().lower() or None,
        "team_code": str(row.get("team_code") or "").strip().lower() or None,
        "module_code": str(row.get("module_code") or "").strip().lower() or None,
        "entity_code": str(row.get("entity_code") or "").strip().lower() or None,
        "assignment_role": str(row.get("assignment_role") or "").strip() or None,
        "is_manager": bool(row.get("is_manager")) if row.get("is_manager") is not None else False,
        "active": bool(row.get("active")) if row.get("active") is not None else True,
    }

    if not normalized["user_email"]:
        raise ValueError("core_user_assignment.user_email is required")

    scope_fields = ["system_code", "team_code", "module_code", "entity_code"]
    selected_scope = [field for field in scope_fields if normalized.get(field)]
    if len(selected_scope) != 1:
        raise ValueError(
            "core_user_assignment requires exactly one of system_code, team_code, module_code or entity_code"
        )

    return normalized


async def _resolve_single_scope_by_code(
    session,
    model,
    code_field,
    code: str,
    scope_name: str,
):
    result = await session.execute(select(model).where(code_field == code))
    matches = result.scalars().all()

    if not matches:
        raise ValueError(f"{scope_name} with code '{code}' was not found for core_user_assignment")

    if len(matches) > 1:
        raise ValueError(
            f"{scope_name} code '{code}' is ambiguous for core_user_assignment; provide a more specific seed format"
        )

    return matches[0]


async def seed_core_user_assignments() -> tuple[int, int]:
    data_file = Path(__file__).resolve().parents[1] / "data" / "core_user_assignment.json"
    raw_rows = json.loads(data_file.read_text(encoding="utf-8"))

    if not isinstance(raw_rows, list):
        raise ValueError("core_user_assignment.json must contain a list of assignments")

    inserted = 0
    updated = 0

    async with db as session:
        seed_run_result = await session.execute(
            select(CoreSeedRun).where(CoreSeedRun.seed_key == CORE_USER_ASSIGNMENT_SEED_KEY)
        )
        already_ran = seed_run_result.scalars().first() is not None
        if already_ran:
            logger.info("Seed %s already executed. Skipping load.", CORE_USER_ASSIGNMENT_SEED_KEY)
            return 0, 0

        bot_user = await _get_system_bot_user(session)

        users_result = await session.execute(select(AuthUser))
        users_by_email = {
            str(user.email).strip().lower(): user for user in users_result.scalars().all()
        }

        assignments_result = await session.execute(select(CoreUserAssignment))
        existing_assignments = {
            (
                assignment.user_id,
                assignment.system_id,
                assignment.team_id,
                assignment.module_id,
                assignment.entity_id,
            ): assignment
            for assignment in assignments_result.scalars().all()
        }

        for raw in raw_rows:
            payload = _normalize_core_user_assignment_row(raw)
            user = users_by_email.get(payload["user_email"])
            if user is None:
                raise ValueError(
                    f"User with email '{payload['user_email']}' was not found for core_user_assignment"
                )

            system_id = None
            team_id = None
            module_id = None
            entity_id = None

            if payload["system_code"]:
                system = await _resolve_single_scope_by_code(
                    session,
                    CoreSystem,
                    CoreSystem.code,
                    payload["system_code"],
                    "system",
                )
                system_id = system.id
            elif payload["team_code"]:
                team = await _resolve_single_scope_by_code(
                    session,
                    CoreTeam,
                    CoreTeam.code,
                    payload["team_code"],
                    "team",
                )
                team_id = team.id
            elif payload["module_code"]:
                module = await _resolve_single_scope_by_code(
                    session,
                    CoreModule,
                    CoreModule.code,
                    payload["module_code"],
                    "module",
                )
                module_id = module.id
            elif payload["entity_code"]:
                entity = await _resolve_single_scope_by_code(
                    session,
                    CoreEntity,
                    CoreEntity.code,
                    payload["entity_code"],
                    "entity",
                )
                entity_id = entity.id

            assignment_key = (user.id, system_id, team_id, module_id, entity_id)
            existing = existing_assignments.get(assignment_key)

            if existing is None:
                assignment = CoreUserAssignment(
                    user_id=user.id,
                    system_id=system_id,
                    team_id=team_id,
                    module_id=module_id,
                    entity_id=entity_id,
                    assignment_role=payload["assignment_role"],
                    is_manager=payload["is_manager"],
                    active=payload["active"],
                    create_by=bot_user.id,
                )
                session.add(assignment)
                existing_assignments[assignment_key] = assignment
                inserted += 1
                continue

            changed = False
            for field in ["assignment_role", "is_manager", "active"]:
                value = payload[field]
                if getattr(existing, field) != value:
                    setattr(existing, field, value)
                    changed = True
            if existing.updated_by != bot_user.id:
                existing.updated_by = bot_user.id
                changed = True

            if changed:
                session.add(existing)
                updated += 1

        session.add(CoreSeedRun(seed_key=CORE_USER_ASSIGNMENT_SEED_KEY))
        await session.commit()

    logger.info(
        "Core user assignment seed completed. Inserted=%s Updated=%s",
        inserted,
        updated,
    )
    return inserted, updated
