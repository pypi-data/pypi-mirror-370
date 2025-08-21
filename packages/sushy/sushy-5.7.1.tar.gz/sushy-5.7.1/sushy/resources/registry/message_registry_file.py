# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This is referred from Redfish standard schema.
# https://redfish.dmtf.org/schemas/v1/MessageRegistryFileCollection.json
# https://redfish.dmtf.org/schemas/v1/MessageRegistryFile.v1_1_0.json

import logging

from sushy.resources import base
from sushy.resources.registry import attribute_registry
from sushy.resources.registry import message_registry

LOG = logging.getLogger(__name__)


class LocationListField(base.ListField):
    """Location for each registry file of languages supported

    There are 3 options where the file can be hosted:

    * locally as a single file,
    * locally as a part of archive (zip or other),
    * publicly on the Internet.
    """

    language = base.Field('Language')
    """File's RFC5646 language code or the string 'default'"""

    uri = base.Field('Uri')
    """Location URI for co-located registry file with the Redfish service"""

    archive_uri = base.Field('ArchiveUri')
    """Location URI for  archive file"""

    archive_file = base.Field('ArchiveFile')
    """File name for registry if using archive_uri"""

    publication_uri = base.Field('PublicationUri')
    """Location URI of publicly available schema"""


class RegistryType(base.ResourceBase):
    _odata_type = base.Field('@odata.type', required=True)


class MessageRegistryFile(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """Identity of Message Registry file resource"""

    description = base.Field('Description')
    """Description of Message Registry file resource"""

    name = base.Field('Name', required=True)
    """Name of Message Registry file resource"""

    languages = base.Field('Languages', required=True)
    """List of RFC 5646 language codes supported by this resource"""

    registry = base.Field('Registry', required=True, default='UNKNOWN.0.0')
    """Prefix for MessageId used for messages from this resource

    This attribute is in form Registry_name.Major_version.Minor_version
    """

    location = LocationListField('Location', required=True)
    """List of locations of Registry files for each supported language"""

    def get_message_registry(self, language, public_connector):
        """Get a Message Registry from the location

        :param language: RFC 5646 language code for registry files
        :param public_connector: connector to use when downloading registry
            from the Internet
        :returns: a MessageRegistry or None if not found
        """
        return self._get_registry(language, public_connector,
                                  'MessageRegistry',
                                  message_registry.MessageRegistry)

    def get_attribute_registry(self, language, public_connector):
        """Get an Attribute Registry from the location

        :param language: RFC 5646 language code for registry files
        :param public_connector: connector to use when downloading registry
            from the Internet
        :returns: an AttributeRegistry or None if not found
        """
        return self._get_registry(language, public_connector,
                                  'AttributeRegistry',
                                  attribute_registry.AttributeRegistry)

    def _get_registry(self, language, public_connector, requested_type,
                      registry_class):
        """Load registry file depending on the registry type

        Will try to find requested_type based on `odata.type` property,
        location, and provided language. If desired language is not found,
        will pick a registry that has 'default' language.

        :param language: RFC 5646 language code for registry files
        :param public_connector: connector to use when downloading registry
            from the Internet
        :param requested_type: string identifying registry
        :param registry_class: registry class
        :returns: registry or None if not found
        """

        # NOTE (etingof): as per RFC5646, languages are case-insensitive
        language = language.lower()

        # NOTE(iurygregory): some registries may have "en-US" as their
        # language, in this case we can check if the registry language
        # starts with the requested language.
        locations = [
            loc for loc in self.location
            if loc.language.lower().split('-', 1)[0] == language
            or loc.language == language
        ]

        locations += [
            loc for loc in self.location if loc.language.lower() == 'default']

        for location in locations:
            if location.uri:
                args = self._conn,
                kwargs = {
                    'path': location.uri,
                    'reader': None,
                    'redfish_version': self.redfish_version
                }

            elif location.archive_uri:
                args = self._conn,
                kwargs = {
                    'path': location.archive_uri,
                    'reader': base.JsonArchiveReader(location.archive_file),
                    'redfish_version': self.redfish_version
                }

            elif location.publication_uri:
                args = public_connector,
                kwargs = {
                    'path': location.publication_uri,
                    'reader': base.JsonPublicFileReader(),
                    'redfish_version': self.redfish_version
                }

            else:
                LOG.warning('Incomplete location for language %(language)s',
                            {'language': language})
                continue

            try:
                registry_type = RegistryType(*args, **kwargs)

            except Exception as exc:
                LOG.warning(
                    'Cannot load registry type from location '
                    '%(location)s: %(error)s', {
                        'location': kwargs['path'],
                        'error': exc})
                continue

            if registry_type._odata_type.endswith(requested_type):
                try:
                    return registry_class(*args, **kwargs)

                except Exception as exc:
                    LOG.warning(
                        'Cannot load registry %(type)s from location '
                        '%(location)s: %(error)s', {
                            'type': requested_type,
                            'location': kwargs['path'],
                            'error': exc})
                    continue

            LOG.debug('Ignoring unsupported flavor of registry %(registry)s',
                      {'registry': registry_type._odata_type})
            return

        LOG.warning('No registry found for %(language)s or default',
                    {'language': language})


class MessageRegistryFileCollection(base.ResourceCollectionBase):
    """Collection of Message Registry Files"""

    @property
    def _resource_type(self):
        return MessageRegistryFile
