"""
"""

# todo: Finish non-account modules first.


from operator import attrgetter
import pendulum
from battlenet_client.wow.profile import profile, specializations_summary, media_summary, encounters
from battlenet_client.wow.profile import achievement_summary, achievement_statistics, pvp
from battlenet_client.wow.realms import Realm
from battlenet_client.wow.playables import PlayableClass, PlayableSpecialization
from battlenet_client.wow.races import PlayableRace


MAX_LEVEL = {'classic1x': 60, 'classic': 80, 'retail': 70}


class Character:
    """Defines a character in World of Warcraft

    Args:
        region_tag (str): region abbreviation for use with the APIs
        realm_tag (str or int): the realm of the character's creation
        name (str): the character name

    Keyword Args:
        release (str, optional): the release to use.  Currently 'classic' only.  The default of None, indicates to use
            the retail data
        locale (str, optional): the localization to use from the API, The default of None means all localizations
        scope (list of str, optional): the scope or scopes to use during the endpoints that require the
            Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal


    Attributes:
        realm (:obj:`Realm`): the realm instance
        playable_class (:obj:`PlayableClass`): the class of the character
        active_specialization (:obj:`PlayableSpecialization`): the current specialization in use
        race (:obj:`PlayableRace`): the race of the character
        id (int): the ID of the character
        name (str): the properly capitalized name of the character
        gender (str): the gender of the character
        faction (str): the faction the character belongs
        level (int): the level of the character
        experience (int or None): the experience remaining until the next level
        last_login (:obj:`datetime`): the last time the character was active
        achievement_points (int): the total achievement points acquired by the character
            (may include account wide achievement points as well)
        avg_ilevel (int): The average item level (ilevel) with the highest gear either equipped
            or in the character's bags
        equipped_ilevel (int): the item level (ilevel) of the all of the equipped gear
        available_specs (list of :obj:`PlayableSpecialization`): a list of the other
            possible specializations
    """

    def __init__(self, region_tag, realm_tag, name, *, release=None, locale=None, client=None):

        self.playable_class = None
        self.active_specialization = None
        self.race = None
        self.object_id = None
        self.name = name
        self.realm_tag = realm_tag
        self.gender = None
        self.faction = None
        self.level = None
        self._specs = None
        self.equipped_ilevel = None
        self.avg_ilevel = None
        self.achievement_points = None
        self.last_login = None
        self.experience = None
        self.realm = None
        self._media = None
        self.available_specs = None
        self._dungeons = None
        self._raids = None
        self.pvp = None
        self.achievement_summary = None
        self.achievement_statistics = None

        (url, params) = profile(region_tag, realm_tag, name, status=False, release=release, locale=locale)

        if client:
            self.get(client)
        
    def __repr__(self):
        return f"{self.name} ({self.realm.name} {self.realm.region.name})"

    def __str__(self):
        return f"{self.name} ({self.realm.name} {self.realm.region.name})"

    def media(self, media_type='avatar'):
        try:
            return self._media[f'{media_type}_url']
        except KeyError:
            print("media_type needs to be 'avatar', 'bust', 'render', or no value")

    def raid_progression(self, tier=None):
        if not tier:
            try:
                return self._raids['expansions'][-1]
            except KeyError:
                return 'no raid progression'

    def get(self, client):

        api_data = client.get(url, params=params)
        release = "retail"

        if params['namespace'].count("-") > 1:
            start = params['namespace'].find('-')
            end = params['namespace'].find('-', -1)
            release = params['namespace'][start:end]

        self.realm = Realm(region_tag, realm_tag, release=release, locale=params['locale'], client=client)

        self.playable_class = PlayableClass(region_tag, class_id=api_data['character_class']['id'],
                                            release=release, locale=params['locale'], client=client)

        self.active_specialization = PlayableSpecialization(region_tag, spec_id=api_data['active_spec']['id'],
                                                            release=release, locale=params['locale'],
                                                            client=client)
        self.race = PlayableRace(region_tag, race_id=api_data['race']['id'], release=release,
                                 locale=params['locale'], client=client)
        self.object_id = int(api_data['id'])
        self.name = api_data['name']
        self.gender = api_data['gender']['name']
        self.faction = api_data['faction']['name']
        self.level = int(api_data['level'])

        if self.level < MAX_LEVEL[client.release]:
            self.experience = int(api_data['experience'])
        else:
            self.experience = 0

        self.last_login = pendulum.from_timestamp(api_data['last_login_timestamp'] / 1000, tz=self.realm.timezone)
        self.achievement_points = api_data['achievement_points']
        self.avg_ilevel = int(api_data['average_item_level'])
        self.equipped_ilevel = int(api_data['equipped_item_level'])
        self._specs = specializations_summary(client, realm_tag, self.name)
        self._media = media_summary(client, realm_tag, self.name)
        self.available_specs = sorted(
            [PlayableSpecialization(region_tag, spec_id=spec['specialization']['id'], release=release,
                                    locale=params['locale'], client=client)
             for spec in self._specs['specializations']
                if spec['specialization']['id'] != self.active_specialization.id], key=attrgetter('name'))

        # for now, keep these to the API returned endpoints
        self._dungeons = encounters(realm_tag, self.name, 'dungeons')
        self._raids = encounters(realm_tag, self.name, 'raids')
        self.achievement_summary = achievement_summary(client, self.realm.slug, self.name)
        self.achievement_statistics = achievement_statistics(client, self.realm.slug, self.name)
        self.pvp = pvp(client, self.realm.slug, self.name)