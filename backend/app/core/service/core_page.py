from dataclasses import asdict
from copy import deepcopy
import json
from pathlib import Path

from fastapi import HTTPException

from app.auth.repository.auth_user import AuthUserRepository
from app.core.graphql.types import PageInput, PageType
from app.core.repository.core_lang import LangRepository
from app.core.service.core_app import AppService
from app.core.models.core_page import CorePage
from app.core.repository.core_page import PageRepository
from app.core.service.core_party import PartyService
from app.core.service.core_system import SystemService
from app.infrastructure.i18n import filter_i18n_with_fallback


class PageService:
    DASHBOARD_TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "dash.json"

    @staticmethod
    def _to_type(page: CorePage) -> PageType:
        return PageType(
            id=page.id,
            name=page.name,
            description=page.description,
            keys=page.keys,
            view=page.view,
            active=page.active,
            sequence=page.sequence,
            color=page.color,
            public=page.public,
            created_at=page.created_at,
            create_by=page.create_by,
            updated_at=page.updated_at,
            updated_by=page.updated_by,
        )

    @staticmethod
    def _normalize(payload: PageInput) -> dict:
        data = asdict(payload)
        data["name"] = SystemService._normalize_json_name(data.get("name"), "name")
        if data.get("description") is not None:
            data["description"] = SystemService._normalize_json_name(
                data.get("description"), "description"
            )
        if data.get("keys") is not None:
            data["keys"] = SystemService._normalize_json_object(data.get("keys"), "keys")
        if data.get("view") is not None:
            data["view"] = SystemService._normalize_json_object(data.get("view"), "view")
        if data["name"] is None:
            raise HTTPException(status_code=400, detail="name is required")
        return data

    @staticmethod
    def _normalize_dashboard_keys(keys: dict) -> dict:
        if not isinstance(keys, dict) or not keys:
            raise HTTPException(status_code=400, detail="keys must be a non-empty JSON object")
        return {key: value for key, value in keys.items() if value is not None}

    @staticmethod
    def _load_dashboard_template() -> dict:
        with PageService.DASHBOARD_TEMPLATE_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _merge_dashboard_view(
        template: dict,
        page: CorePage | None,
        page_view: dict | None,
        controls: dict | None,
        items: list[dict],
        page_size: int | None,
        context: dict,
        lang_options: dict[str, str],
    ) -> dict:
        dashboard = deepcopy(template)
        dashboard["context"] = context
        props = dashboard.setdefault("props", {})
        props["title"] = page.name if page else props.get("title", {})
        props["description"] = page.description if page else props.get("description", {})

        components = props.get("components") or [{}]
        component = deepcopy(components[0]) if components else {}

        controls_data = controls or {}
        view_data = page_view or {}
        component["menu"] = view_data.get(
            "menu",
            controls_data.get("menu", component.get("menu", [])),
        )
        component["settings"] = view_data.get(
            "settings",
            controls_data.get("settings", component.get("settings", [])),
        )
        component["breadcrumb"] = view_data.get(
            "breadcrumb",
            controls_data.get("breadcrumb", component.get("breadcrumb", {})),
        )
        component["calendar"] = view_data.get(
            "calendar",
            controls_data.get("calendar", component.get("calendar", {})),
        )
        component["activities"] = view_data.get(
            "activities",
            controls_data.get("activities", component.get("activities", {})),
        )
        component["form"] = view_data.get(
            "form",
            controls_data.get("form", component.get("form", {})),
        )
        actions = deepcopy(controls_data.get("actions", component.get("actions", {})))
        actions.update(deepcopy(view_data.get("actions", {})))
        actions_i18n = deepcopy(actions.get("i18n", {}))
        actions_i18n["lang"] = lang_options
        actions["i18n"] = actions_i18n
        component["actions"] = actions

        base_data = controls_data.get("data", component.get("data", {}))
        page_data = view_data.get("data", {})
        merged_data = {**base_data, **page_data}
        merged_data["records"] = items
        if page_size is not None:
            merged_data["page_size"] = page_size
        component["data"] = merged_data

        props["components"] = [component]
        return dashboard

    @staticmethod
    def _pick_page_by_keys(pages: list[CorePage], keys: dict) -> CorePage | None:
        if not pages:
            return None

        exact_match = next((page for page in pages if (page.keys or {}) == keys), None)
        if exact_match is not None:
            return exact_match

        return max(
            pages,
            key=lambda page: len(page.keys or {}),
        )

    @staticmethod
    async def _get_entity_items(entity: str) -> list[dict]:
        if entity == "core.app":
            return [asdict(app) for app in await AppService.get_all()]

        if entity == "core.party":
            return [asdict(party) for party in await PartyService.get_all()]

        return []

    @staticmethod
    async def _get_user_page_size(user_id: int | None) -> int | None:
        if user_id is None:
            return None

        user = await AuthUserRepository.get_by_id(user_id, include_system=True)
        return user.page_size if user else None

    @staticmethod
    async def _get_dashboard_i18n(
        user_id: int | None,
        lang_code: str | None = None,
    ) -> tuple[dict, dict[str, str]]:
        default_context = {"lang": "es"}
        default_lang_options = {"es": "ES"}

        langs = await LangRepository.get_all()
        active_langs = [lang for lang in langs if lang.active]
        lang_options = {
            lang.code: (lang.flag or lang.code.upper())
            for lang in active_langs
        } or default_lang_options

        normalized_lang_code = (lang_code or "").strip().lower()
        if normalized_lang_code:
            selected_lang = next(
                (lang for lang in active_langs if lang.code.strip().lower() == normalized_lang_code),
                None,
            )
            if selected_lang is not None:
                return {"lang": selected_lang.code}, lang_options

        if user_id is None:
            return default_context, lang_options

        user = await AuthUserRepository.get_by_id(user_id, include_system=True)
        if user is None or user.lang_id is None:
            return default_context, lang_options

        user_lang = next((lang for lang in active_langs if lang.id == user.lang_id), None)
        if user_lang is None:
            return default_context, lang_options

        return {"lang": user_lang.code}, lang_options

    @staticmethod
    async def create(payload: PageInput) -> PageType:
        data = PageService._normalize(payload)
        created = await PageRepository.create(CorePage(**data))
        return PageService._to_type(created)

    @staticmethod
    async def get_all() -> list[PageType]:
        pages = await PageRepository.get_all()
        return [PageService._to_type(page) for page in pages]

    @staticmethod
    async def get_by_id(page_id: int) -> PageType | None:
        page = await PageRepository.get_by_id(page_id)
        return PageService._to_type(page) if page else None

    @staticmethod
    async def get_by_name(name: dict) -> PageType | None:
        normalized_name = SystemService._normalize_json_name(name, "name")
        if normalized_name is None:
            raise HTTPException(status_code=400, detail="name is required")

        page = await PageRepository.get_by_name(normalized_name)
        return PageService._to_type(page) if page else None

    @staticmethod
    async def get_by_keys(keys: dict) -> list[PageType]:
        if not isinstance(keys, dict) or not keys:
            raise HTTPException(status_code=400, detail="keys must be a non-empty JSON object")

        pages = await PageRepository.get_by_keys(keys)
        return [PageService._to_type(page) for page in pages]

    @staticmethod
    async def get_dashboard(
        keys: dict,
        user_id: int | None = None,
        lang_code: str | None = None,
    ) -> dict:
        normalized_keys = PageService._normalize_dashboard_keys(keys)
        controls_keys = {"common": "dashboard"}
        controls_pages = await PageRepository.get_by_keys(controls_keys)
        controls_page = PageService._pick_page_by_keys(controls_pages, controls_keys)
        controls = controls_page.view if controls_page else None
        pages = await PageRepository.get_by_keys(normalized_keys)
        page = PageService._pick_page_by_keys(pages, normalized_keys)
        page_view = page.view if page else None
        items = await PageService._get_entity_items(str(normalized_keys.get("entity", "")))
        page_size = await PageService._get_user_page_size(user_id)
        context, lang_options = await PageService._get_dashboard_i18n(user_id, lang_code)
        dashboard = PageService._merge_dashboard_view(
            template=PageService._load_dashboard_template(),
            page=page,
            page_view=page_view,
            controls=controls,
            items=items,
            page_size=page_size,
            context=context,
            lang_options=lang_options,
        )
        allowed_langs = {"en", str(context.get("lang", "")).strip().lower()}
        return filter_i18n_with_fallback(dashboard, allowed_langs=allowed_langs, fallback="en")

    @staticmethod
    async def update(page_id: int, payload: PageInput) -> PageType:
        data = PageService._normalize(payload)
        updated = await PageRepository.update(page_id, data)
        if updated is None:
            raise HTTPException(status_code=404, detail="page not found")

        return PageService._to_type(updated)

    @staticmethod
    async def delete(page_id: int) -> bool:
        deleted = await PageRepository.delete(page_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="page not found")
        return True
