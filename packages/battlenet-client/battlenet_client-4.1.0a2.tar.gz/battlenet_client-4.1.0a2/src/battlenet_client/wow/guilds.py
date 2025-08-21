

"""World of Warcraft Guild and Banner

Disclaimer:
All rights reserved, Blizzard is the intellectual property owner of WoW and WoW Classic
and any api_data pertaining thereto

Author:
David "Gahd" Couples <gahdania@gahd.online>
"""
import os
import pendulum
from PIL import Image, ImageChops, ImageDraw, ImageFont

from wow_api.clients.client import WoWClient
from .realms import Realm
from battlenet_client.wow.regions import Region
from .characters import Character


class Guild:
    """World of Warcraft Guild

    Args:
        region_tag (str or :obj:`Region`): region abbreviation for use with the APIs
        realm (int, str, :obj:`Realm`): the ID or name of the realm
        name (str): the name or slug of the guild

    Keyword Args:
        release (str, optional): the release to use.  Currently 'classic' only.  The default of None, indicates to use
            the retail data
        locale (str, optional): the localization to use from the API, The default of None means all localizations
        scope (list of str, optional): the scope or scopes to use during the endpoints that require the
            Web Application Flow
        redirect_uri (str, optional): the URI to return after a successful authentication between the user and Blizzard
        client_id (str): the client ID from the developer portal
        client_secret (str): the client secret from the developer portal
    """
    def __init__(self, client: Union[OAuth2Session, OicClient], region_tag: str, realm: Union[str, int], name: str, *,
                 release: Optional[str] = None, locale: Optoinal[str] = None):

        self.region = Region(client, region_tag, release=release, locale=locale)
        self.realm = Realm(client, region_tag, api_data['realm']['id'], locale=locale, release=release)

        self.object_id = api_data['id']
        self.name = api_data['name']
        self.faction = api_data['faction']

        self.member_count = int(api_data['member_count'])
        self.achievement_points = int(api_data['achievement_points'])
        self._achievements_url = api_data['achievements']['href']
        self.crest = api_data['crest']
        
        self.created = pendulum.from_timestamp(api_data['created_timestamp'] / 1000, tz=self.realm.timezone)
        self.roster_list = self._client.guild_roster(self.realm.slug, self.slug)
        self.achievements = self._client.guild_achievements(self.realm.slug, self.slug)
        self.activities = self._client.guild_activities(self.realm.slug, self.slug)

        self.level = None if 'level' not in api_data.keys() else api_data['level']

    def __str__(self):
        return f"{self.name}-{self.realm.name} ({self.realm.region.tag.upper()})"

    @property
    def roster(self):
        return [Character('us', character['character']['realm']['slug'], character['character']['name'],
                locale=self.locale) for character in self.roster_list['members']]


class GuildBanner:

    def __init__(self, region, guild, *, release=None, locale=None, scope=None, redirect_uri=None,
                 client=None, client_id=None, client_secret=None):

        if client:
            self._client = client
        else:
            self._client = WoWClient(region, locale=locale, release=release, scope=scope, redirect_uri=redirect_uri,
                                     client_id=client_id, client_secret=client_secret)

        if locale:
            self.locale = locale
        else:
            self.locale = self._client.locale

        if isinstance(region, Region):
            self.region = region
        else:
            self.region = Region(region, locale=locale, release=release, scope=scope, redirect_uri=redirect_uri,
                                 client=self._client)

        self.guild_id = int(guild.id)
        self.faction = guild.faction
        self.level = guild.level

        self.emblem = dict(id=None, color=dict(r=None, g=None, b=None, a=None))
        self.border = dict(id=None, color=dict(r=None, g=None, b=None, a=None))
        self.banner = dict(r=None, g=None, b=None, a=None)

        self.emblem['id'] = guild.crest['emblem']['id']
        for key, value in guild.crest['emblem']['color']['rgba'].items():
            if key == 'a':
                value = int(value * 255)

            self.emblem['color'][key] = value

        self.border['id'] = guild.crest['border']['id']
        for key, value in guild.crest['border']['color']['rgba'].items():
            if key == 'a':
                value = int(value * 255)
            self.border['color'][key] = value

        for key, value in guild.crest['background']['color']['rgba'].items():
            if key == 'a':
                value = int(value * 255)
            self.banner[key] = value

    def show_crest(self, show_ring=True, show_level=False, width=215, path=None):

        if path and isinstance(path, str):
            path = os.path.dirname(path)

        if not path:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crest')

        crest_file = os.path.join(path, 'cache', f"{self.region.id}_{self.guild_id}.png")

        try:
            crest = Image.open(crest_file)
        except FileNotFoundError:
            crest = self.create_crest(show_ring=show_ring, show_level=show_level, width=width, path=path)
        except AttributeError:
            crest = self.create_crest(show_ring=show_ring, show_level=show_level, width=width, path=path)

        return crest

    def delete_crest(self, path=None):

        if path and isinstance(path, str):
            path = os.path.dirname(path)

        if not path:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crest')

        crest = os.path.join(path, 'cache', f"{self.region.id}_{self.guild_id}.png")

        try:
            os.unlink(crest)
        except OSError as error:
            print(error)
        else:
            return None

    def create_crest(self, show_ring=True, show_level=False, width=215, path=None):
        """Creates the guild emblem

        Args:
            show_ring (bool): show the faction (default) if True, else do not (False)
            show_level (bool): True to show the guild level, False otherwise (default)
            width (int): the overall width of the guild emblem
            path (:obj:`os.path`): the path to the segments

        Returns:
            (:obj:`Image`): the completed image of the emblem
        """

        def _blend(base, color):
            """builds the layer to be the next overlay of the images

            Args:
                base (:obj:`Image`): the image to use as the base of the overlay, ie the emblem, border, or flag
                    background converted to RGBA format
                color (dict): the color in red (r), green (g), blue (b), and alpha (a)

            Returns:
                (:obj:`Image`): completed layer to overlay onto the temporary image.
            """

            swatch = Image.new('RGB', base.size, (color['r'], color['g'], color['b']))
            # alpha = base.getchannel('A').convert('RGB')
            # need to find right modification to emulate a merge based on luminosity
            image = ImageChops.overlay(swatch, base.convert('RGB')).convert('RGBA')
            image.putalpha(base.getchannel('A'))
            return image

        x_offset = 20
        y_offset = 23
        height = int(width * 230 / 215)
        scale = width / 215

        if path and isinstance(path, str):
            path = os.path.dirname(path)

        if not path:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crest')

        static = os.path.join(path, 'static')
        save_path = os.path.join(path, 'cache', f"{self.region.id}_{self.guild_id}.png")

        # load the images
        output = Image.new('RGBA', (int(width), int(height)), (0, 0, 0, 0))
        ring = Image.open(os.path.join(static, f"ring-{self.faction['type'].lower()}.png")).convert('RGBA')
        shadow = Image.open(os.path.join(static, 'shadow_00.png')).convert('RGBA')
        flag = Image.open(os.path.join(static, 'bg_00.png')).convert('RGBA')
        emblem_data = self._client.guild_crest_emblem_media(self.emblem['id'])
        emblem = Image.open(self._client.get(emblem_data['assets'][0]['value']))
        border_data = self._client.guild_crest_border_media(self.border['id'])
        border = Image.open(self._client.get(border_data['assets'][0]['value'])).convert('RGBA')
        hooks = Image.open(os.path.join(static, 'hooks.png')).convert('RGBA')

        flag = _blend(flag, self.banner)

        overlay = Image.open(os.path.join(static, 'overlay_00.png')).convert('RGBA')

        emblem = _blend(emblem, self.emblem['color'])

        border = _blend(border, self.border['color'])

        # load the faction ring, and lowest shadow
        if show_ring:
            output.alpha_composite(ring)
            output.alpha_composite(shadow, (x_offset, y_offset))

        output.alpha_composite(flag, (x_offset, y_offset))
        output.alpha_composite(emblem, (x_offset + 17, y_offset + 22))
        output.alpha_composite(border, (x_offset + 13, y_offset + 14))
        output.alpha_composite(overlay, (x_offset, y_offset + 2))
        output.alpha_composite(hooks, (x_offset - 2, y_offset))

        if show_level and self.level:
            level_output = Image.new('RGBA', output.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(level_output)
            font = ImageFont.truetype(os.path.join(static, 'CantataOne-Regular.ttf'), 80)

            text_size = font.getsize(str(self.level))

            if show_ring:
                level_output.alpha_composite(ring)

            # add the flag shadow layer
            level_output.alpha_composite(shadow, (x_offset, y_offset))

            # add the flag
            level_output.alpha_composite(flag, (x_offset, y_offset))

            offsets = {
                'x1': int((ring.width - text_size[0]) / 2),
                'y1': int((ring.height - text_size[1]) / 2),
                'x2': int((ring.width - text_size[0]) / 2) + text_size[0],
                'y2': int((ring.height - text_size[1]) / 2) + text_size[1],
                'tx': font.getoffset(str(self.level))[0],
                'ty': font.getoffset(str(self.level))[1],
            }

            draw.text((offsets['x1'] - offsets['tx'] / 2, offsets['y1'] - offsets['ty'] / 2), str(self.level),
                      font=font,
                      fill=(self.emblem['color']['r'], self.emblem['color']['g'], self.emblem['color']['b'],
                            self.emblem['color']['a']),
                      outline=(self.border['color']['r'], self.border['color']['g'], self.border['color']['b'],
                               self.border['color']['a']),
                      width=5)

            # add the border
            level_output.alpha_composite(border, (x_offset + 13, y_offset + 15))
            level_output.alpha_composite(overlay, (x_offset, y_offset + 2))
            level_output.alpha_composite(hooks, (x_offset - 2, y_offset))
            level_output = level_output.resize((int(215 / 3), int(230 / 3)), resample=Image.BICUBIC)
            output.alpha_composite(level_output, (215 - level_output.width, 230 - level_output.height))

        if scale != 1:
            output.resize((output.width * scale, output.height * scale), resample=Image.BICUBIC)
        print(save_path)
        output.save(save_path)
