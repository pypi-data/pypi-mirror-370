"""Selection Data for common use cases."""

import json
from pathlib import Path
from typing import Dict, List

import structlog
from opentelemetry import trace

from inventree_common_data.datastructures import (
    FileSourceSelectionListModel,
)
from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin
from plugin.models import PluginConfig

try:
    from plugin.mixins import SettingsContentMixin
except ImportError:

    class SettingsContentMixin:
        """Dummy settings content."""


LOGGER = structlog.get_logger("inventree")
tracer = trace.get_tracer(__name__)


class SelectionListHandelingMixin:
    """Mixin for handling common Selection List behaviour."""

    @tracer.start_as_current_span("check_open_migration")
    def check_open_migration(self):
        """Check if there is an open data migrations."""
        if not self.is_active():
            return

        LOGGER.info("Checking if there is an open data migrations")

        # check if stettings enabled
        if not self.get_setting("AUTO_SYNC", cache=False):
            LOGGER.info(
                "skipping updates because as autoupdates are disabled in settings"
            )
            return

        # Get data
        cfg: PluginConfig = self.plugin_config()
        if cfg is None:
            LOGGER.warning("Failed to get plugin configuration")
            return

        metadata = cfg.get_metadata(self.slug, {})
        latest_versions = metadata.get("latest_versions", {})

        # Collect available sources
        all_sources = self.get_available_sources()

        # Compile the latest versions
        sources: Dict[str, FileSourceSelectionListModel] = {}
        for identifier, versions in all_sources.items():
            latest_version = max(versions.keys())
            sources[identifier] = versions[latest_version]
        self.sources = sources
        LOGGER.info(f"Sources: {sources}")

        # Check if lists are missing or outdated and provision them
        self.provision_missing_lists(latest_versions, sources, cfg)

        # Write data
        metadata["latest_versions"] = latest_versions
        cfg.set_metadata(self.slug, metadata)

    @tracer.start_as_current_span("provision_missing_lists")
    def provision_missing_lists(
        self,
        latest_versions,
        sources: Dict[str, FileSourceSelectionListModel],
        cfg: PluginConfig,
    ):
        """Provision missing or outdated Selection Lists in the database."""
        from common.models import SelectionList

        missing: List[FileSourceSelectionListModel] = []
        for identifier, obj in sources.items():
            if identifier not in latest_versions:
                missing.append(obj)
            else:
                if latest_versions[identifier] != obj.version:
                    missing.append(obj)
        LOGGER.info(f"Lists missing src: {missing}")

        # Get all Selection Lists from the source plugin
        slist = SelectionList.objects.filter(source_plugin=cfg.id).all()

        # Provision lists if missing
        for obj in missing:
            LOGGER.info(
                f"Provisioning Selection List '{obj.name}' from source '{obj.path}'"
            )
            data = obj.load()
            if data is None:
                LOGGER.warning(f"Failed to load data from source {obj.path}")
                continue

            # Provision the list
            el = self.find_existing_db_lists(obj, slist)
            if self.provision_list(obj, cfg, el):
                latest_versions[obj.identifier] = obj.version

    @tracer.start_as_current_span("find_existing_db_lists")
    def find_existing_db_lists(self, obj, slist):
        """Filter existing Selection List from database entries."""
        return next(
            (
                l
                for l in slist
                if "_" in l.source_string
                and l.source_string.split("_")[0] == obj.identifier
            ),
            None,
        )

    @tracer.start_as_current_span("provision_list")
    def provision_list(
        self, obj: FileSourceSelectionListModel, cfg: PluginConfig, exsiting_list=None
    ) -> bool:
        """Provision a Selection List from data.

        Returns True if the list was successfully provisioned.
        """
        from common.models import SelectionList, SelectionListEntry

        # Check if the list exists
        list_obj = None
        # If not, create it
        if not exsiting_list:
            list_obj = SelectionList.objects.create(
                source_plugin=cfg,
                name=obj.data.name,
                description=obj.data.description,
                locked=True,
                active=True,
                source_string=obj.get_source_string(),
            )
        # If it does, update it
        else:
            list_obj = exsiting_list
            list_obj.name = obj.data.name
            list_obj.description = obj.data.description
            list_obj.source_string = obj.get_source_string()
            list_obj.save()
        LOGGER.info(f"List: {list_obj}")

        # Update the list entries
        targets = {str(entry.value): entry for entry in obj.data.entries}
        existing_entries = SelectionListEntry.objects.filter(list=list_obj)

        # Bulk update existing entries
        objs = existing_entries.filter(value__in=targets.keys())
        if objs:
            for obj in objs:
                obj.label = targets[obj.value].label
                obj.description = targets[obj.value].description
            SelectionListEntry.objects.bulk_update(objs, ["label", "description"])

        # Remove entries that are no longer in the source
        existing_entries.exclude(value__in=targets.keys()).delete()

        # Create new entries
        new_entries = targets.keys() - {entry.value for entry in existing_entries}
        SelectionListEntry.objects.bulk_create([
            SelectionListEntry(
                list=list_obj,
                value=key,
                label=targets[key].label,
                description=targets[key].description,
            )
            for key in new_entries
        ])

        return True

    def get_available_sources(self):
        """Get available sources for Selection Lists in a passive manner.

        The data is not loaded, only basic information is extracted from filenames.
        """
        # Collect available sources:
        src = Path(__file__, "..", "sources").resolve()
        if not src.exists():
            LOGGER.warning(f"Sources directory {src} does not exist")
            return {}

        sources_files = list(src.glob("**/*.yaml"))

        all_sources: Dict[str, Dict[str, FileSourceSelectionListModel]] = {}
        # Iterate over all source files and extarct basic info without loading the data
        for source_file in sources_files:
            try:
                names = source_file.stem.split("_")
                obj = FileSourceSelectionListModel(
                    name=names[2],
                    version=names[1],
                    identifier=names[0],
                    path=source_file,
                )
                if obj.identifier not in all_sources:
                    all_sources[obj.identifier] = {}
                all_sources[obj.identifier][obj.version] = obj
            except Exception as e:
                # TODO: expose error to user
                LOGGER.warning(f"Error reading source file {source_file}: {e}")

        return all_sources


class InvenTreeCommonDataPlugin(
    SettingsContentMixin, SelectionListHandelingMixin, SettingsMixin, InvenTreePlugin
):
    """Selection Data for common use cases."""

    NAME = "InvenTree Common Data"
    SLUG = "inventree_common_data"
    MIN_VERSION = "0.16.0"
    SETTINGS = {
        "AUTO_SYNC": {
            "name": "Auto sync changes",
            "description": "Automatically apply changes in reference tables (when you update the plugin for example)",
            "validator": bool,
            "default": True,
        },
    }
    ADMIN_SOURCE = "ui_settings.js"

    def __init__(self):
        """Initialize the InvenTree Common Data plugin."""
        super().__init__()
        self.check_open_migration()

    def get_admin_context(self) -> dict:
        """Return custom context data which can be rendered in the admin panel."""
        meta = self.get_meta() or {}
        sources = self.get_available_sources()
        latest_sources = {}
        for ka, a in sources.items():
            for kb, b in a.items():
                sources[ka][kb] = json.loads(b.json())
                if ka in meta["latest_versions"].keys():
                    data = b.load()
                    latest_sources[ka] = {
                        "name": data.name,
                        "description": data.description,
                        "source": json.loads(data.source.json()),
                    }
        return {
            "sources": sources,
            "latest_sources": latest_sources,
            "meta": meta,
        }

    def get_settings_content(self, request):
        """Custom settings content for the plugin. Only needed for 0.17.x and earlier."""
        items = self.get_admin_context()

        overview_link = "/settings/#select-part-parameters"  # data.modelInformation?.partparametertemplate?.url_overview || '#';
        data_text = "".join([
            f'<li>{item["name"]}: {item["description"]} from <a href="{item["source"]["url"]}">{item["source"]["text"]}</a></li>'
            for key, item in items["latest_sources"].items()
        ])
        username = request.user.username or "unknown"
        superuser_text = "Superuser" if request.user.is_superuser else "not Superuser"

        return f"""
    <i>InvenTree Common Data</i> is a provider for commonly used data. It provides various locked SelectionLists, that can be used in part and part category <a href="{overview_link}">parameters</a>.

    <h5>Available Sources:</h5>
    In their latest version
    <ul>
    {data_text}
    </ul>

    User Info: <i>{username}</i> {superuser_text}
        """

    # region internal
    def get_meta(self):
        """Return metadata for the plugin."""
        cfg: PluginConfig = self.plugin_config()
        if cfg is None:
            return {}
        return cfg.get_metadata(self.slug, {})

    # endregion
