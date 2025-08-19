import logging
from datetime import datetime, timezone, timedelta
import os
from lasutils.settings import ConnectorSettings
from lasutils.api_poller import create_poller

CONF_LAS_API_URL = "api.url"
CONF_LAS_SITE_ID = "site.id"
API_SITE_ID = "site-id"

log = logging.getLogger(__name__)


class LasApi:
    # --- Internals ---
    def __init__(
        self,
        site_id: str = None,
        api_url: str = None,
        poll_retry_time: int = 30,
        las_config: dict = None,
        las_user: str = None,
        las_pwd: str = None,
    ):
        if las_config:
            self._api_url = las_config[CONF_LAS_API_URL]
            self._site_id = las_config[CONF_LAS_SITE_ID]
        else:
            self._site_id = site_id
            self._api_url = api_url

        if not las_user:
            self.las_user = os.getenv("LAS_USER")
        if not las_pwd:
            self.las_pwd = os.getenv("LAS_PWD")
        # if las_user and las_pwd:
        #     user = las_user
        #     pwd = las_pwd
        # else:
        #     user = os.getenv("LAS_USER")
        #     pwd = os.getenv("LAS_PWD")
        self._poll_retry_time = poll_retry_time
        self._poller = self._create_poller(
            self._api_url, las_usr=las_user, las_pwd=las_pwd
        )

    def _create_poller(self, api_url: str, las_usr: str, las_pwd: str):
        bo_auth_config = {
            "auth.token.url": f"{api_url}/user/login",
            "auth.content.type": "json",
            "auth.token.name": "jwt_token",
            "auth.payload": {
                "userName": f"{las_usr}",
                "password": f"{las_pwd}",
            },
        }
        bo_api_config = {
            "api.type": "rest",
            "api.format": "json",
            "api.url": f"{api_url}",
            "api.dataPath": "",
        }
        return create_poller(auth_config=bo_auth_config, api_config=bo_api_config)

    def _get_api_time_format(self, dt: datetime):
        if dt == None:
            return None
        utc = dt.astimezone(timezone.utc)

        iso_format = utc.isoformat(timespec="milliseconds") + "Z"
        custom_format = utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return custom_format

    def _remove_nulls(self, params: dict) -> dict:
        return {k: v for k, v in params.items() if v is not None}

    # Generic POST
    def post(self, resource: str = None, payload: dict = None, params: dict = None):
        return self._poller.post(
            resource,
            payload=payload,
            params=params,
            fail_retry_time=self._poll_retry_time,
        )

    def patch(self, resource: str = None, payload: dict = None, params: dict = None):
        return self._poller.patch(
            resource,
            payload=payload,
            params=params,
            fail_retry_time=self._poll_retry_time,
        )

    def put(self, resource: str = None, payload: dict = None, params: dict = None):
        return self._poller.put(
            resource,
            payload=payload,
            params=params,
            fail_retry_time=self._poll_retry_time,
        )

    def options(self, resource: str = None, params: dict = None):
        return self._poller.options(
            resource,
            params=params,
            fail_retry_time=self._poll_retry_time,
        )

    # Generic GET. Handles both paged and unpaged data
    def poll(self, resource: str = None, params: dict = None, page_size: int = 0):
        params = {} if not params else params
        if page_size == 0:
            # Get unpaged data
            return self._poller.poll(
                resource,
                params=params,
                fail_retry_time=self._poll_retry_time,
            )
        else:
            # Get paged data
            page_index = 0
            params = {"page-index": page_index, "page-size": page_size, **params}

            batch = self._poller.poll(
                resource,
                params=params,
                fail_retry_time=self._poll_retry_time,
            )
            result = batch
            while len(batch) >= page_size:
                page_index += 1
                params["page-index"] = page_index
                batch = self._poller.poll(
                    resource,
                    params=params,
                    fail_retry_time=self._poll_retry_time,
                )
                result.extend(batch)
            # log.info(f"Polled {len(result)} items")
            return result

    # --- API ---
    # Cloud producer
    # https://api.test.livearenasports.com/camera-controller/cloud-production/652550aedc5b6b07b707d251/status?site-id=SIF
    def get_cloud_producer_status(self, broadcast_id: str, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        params = {
            # API_SITE_ID: site_id,
        }
        return self.poll(
            f"camera-controller/cloud-production/{broadcast_id}/status", params=params
        )

    def set_cloud_producer_status(
        self,
        broadcast_id: str,
        status: bool,
    ):
        # broadcastId: "66cc73e3d144b57b0ff285ad", cloudProducer: {active: true}}
        params = {"broadcastId": broadcast_id, "cloudProducer": {"active": status}}
        return self.patch(f"broadcast/internal", payload=self._remove_nulls(params))

    # Broadcast
    def get_broadcasts(
        self,
        start_from: datetime = None,
        start_to: datetime = None,
        end_from: datetime = None,
        end_to: datetime = None,
        comp_id: str = None,
        site_id: str = None,
        group_ext_id: str = None,
    ):

        site_id = site_id if site_id else self._site_id
        sf = self._get_api_time_format(start_from) if start_from else None
        st = self._get_api_time_format(start_to) if start_to else None
        ef = self._get_api_time_format(end_from) if end_from else None
        et = self._get_api_time_format(end_to) if end_to else None
        params = {
            API_SITE_ID: site_id,
            "start-from": sf,
            "start-to": st,
            "end-from": ef,
            "end-to": et,
            "competition-id": comp_id,
            "external-group-id": group_ext_id,
            "hide-cancelled": True,
            "sort-column": "start",
            "sort-order": "Ascending",
            # "hide-cancelled": False,
            # "cache": False,
        }
        params = self._remove_nulls(params)
        return self.poll("broadcast", params=params, page_size=50000)

    def get_broadcasts_video(
        self,
        broadcast_id: str = None,
        start_from: datetime = None,
        start_to: datetime = None,
        end_from: datetime = None,
        end_to: datetime = None,
        comp_id: str = None,
        site_id: str = None,
    ):
        site_id = site_id if site_id else self._site_id
        sf = self._get_api_time_format(start_from) if start_from else None
        st = self._get_api_time_format(start_to) if start_to else None
        ef = self._get_api_time_format(end_from) if end_from else None
        et = self._get_api_time_format(end_to) if end_to else None
        params = {
            API_SITE_ID: site_id,
            "broadcast-id": broadcast_id,
            "start-from": sf,
            "start-to": st,
            "end-from": ef,
            "end-to": et,
            "competition-id": comp_id,
            "hide-cancelled": True,
        }
        params = self._remove_nulls(params)
        return self.poll("broadcast/video", params=params, page_size=50000)

    def get_broadcast_by_id(self, broadcast_id: str):
        params = {
            # API_SITE_ID: self._site_id,
            "broadcast-id": broadcast_id,
        }
        return self.poll("broadcast/internal", params=params)

    # Get broadcast with context
    def get_broadcast_with_context(self, broadcast_id: str, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: site_id,
            "broadcast-id": broadcast_id,
        }
        return self.poll("broadcast/internal/with-context", params=params)

    def get_broadcast_by_ext_id(self, match_id: str):
        params = {
            API_SITE_ID: self._site_id,
            "external-broadcast-id": match_id,
        }
        return self.poll("broadcast", params=params)

    def get_broadcast(self, broadcast_id: str):
        params = {
            API_SITE_ID: self._site_id,
        }
        return self.poll(f"broadcast/{broadcast_id}", params=params)

    def get_broadcast_start(self, broadcast_id: str):
        params = {
            # API_SITE_ID: self._site_id,
            "broadcastId": broadcast_id,
        }
        return self.options("broadcast/start")

    def update_broadcast(self, broadcast_id, kv: dict):
        date_keys = ["start", "end"]
        kv_date = {}
        for k, v in kv.items():
            kv_date[k] = v if k not in date_keys else self._get_api_time_format(v)
        # kv_date = kv | {
        #     k: self._get_api_time_format(v) for k, v in kv.items() if k in date_keys
        # }
        params = {"id": broadcast_id} | kv_date
        return self.patch(f"broadcast", payload=self._remove_nulls(params))

    def create_broadcast(
        self,
        site_id: str,
        broadcast_eid: str,
        venue_eid: str,
        competion_eid: str,
        start: datetime,
        name: str = None,
        home_team_eid: str = None,
        away_team_eid: str = None,
        end: datetime = None,
        cancelled: bool = None,
    ):
        sid = site_id if site_id else self._site_id
        params = {
            "name": name,
            "siteId": sid,
            "venueExtId": venue_eid,
            "start": self._get_api_time_format(start),
            "end": self._get_api_time_format(end),
            # "start": "2024-02-10T12:06:00.000Z",
            # "end": "2024-02-10T12:07:00.000Z",
            "extId": broadcast_eid,
            "competition": {"extId": competion_eid},
            "homeTeam": {"extId": home_team_eid},
            "awayTeam": {"extId": away_team_eid},
            "cancelled": str(cancelled).lower(),
        }
        return self.post(f"broadcast/ext", payload=self._remove_nulls(params))

    def start_broadcast(
        self, broadcast_id: str, venue_id: str, site_id: str, start=str
    ):
        params = {
            "id": broadcast_id,
            "venueId": venue_id,
            "siteId": site_id,
            "start": self._get_api_time_format(start),
        }
        return self.post(f"broadcast/start", payload=params)

    # Lineup
    def get_line_up(self, broadcast_id: str):
        params = {
            API_SITE_ID: self._site_id,
            "broadcast-id": broadcast_id,
        }
        return self.poll("match-event/lineup", params=params)

    # https://api.livearenasports.com/match-event/?broadcast-id=640825720ee95b4a16dcae35&site-id=SIF
    # Match events
    def get_match_events(self, broadcast_id: str):
        params = {
            API_SITE_ID: self._site_id,
            "broadcast-id": broadcast_id,
        }
        return self.poll("match-event", params=params)

    # def get_match_event_standings(self, start_date: str, competition_id: str):
    #     params = {
    #         API_SITE_ID: self._site_id,
    #         "start_date": start_date,
    #         "competition_id": competition_id,
    #     }
    #     return self.poll("match-event/standings", params=params)

    def get_match_event_standing(self, broadcast_id: str):
        params = {
            API_SITE_ID: self._site_id,
        }
        return self.poll(f"match-event/{broadcast_id}/standing", params=params)

    def get_match_event_clock(self, broadcast_id: str):
        params = {
            API_SITE_ID: self._site_id,
            "broadcast-id": broadcast_id,
        }
        return self.poll(f"match-event/clock-info", params=params)

    def get_officials(self, broadcast_id: str):
        params = {
            API_SITE_ID: self._site_id,
            "broadcast-id": broadcast_id,
        }
        officials = self.poll(f"match-event/officials", params=params)
        return officials[0] if officials else None

    # Logs
    def get_status_logs(self, broadcast_id: str):
        params = {
            API_SITE_ID: self._site_id,
            "broadcast-id": broadcast_id,
            "type": "INFO",
        }
        return self.poll(
            f"scheduler-broadcast/status-log", params=params, page_size=200
        )

    # Audit logs
    # https://api.test.livearenasports.com/api-docs/?urls.primaryName=audit-log#/Audit%20Log%20Resource/get_audit_log
    # Domain : BRO, BRO_CONF, CAM, CAM_CONF, COM, COM_SEA, FEA, FIL, GRP, INT, MEV, MRK, MSG, PAY, PAY_CONF, PRO, SIT, USR, USR_ACC, USR_ROLE, VEN
    # Type: CRE, DEL, ERR, INF, PUR_END, PUR_START, REG, REQ, UPD
    def get_audit_logs(
        self,
        from_date: datetime,
        to_date: datetime,
        search_string: str,
        domain: str,
        type: str,
        site_id: str = None,
    ):
        site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: site_id,
            "from": self._get_api_time_format(from_date),
            "to": self._get_api_time_format(to_date),
            "search-string": search_string,
            "domain": domain,
            "type": type,
            "sort-column": "date",
            "sort-order": "Descending",
        }
        return self.poll(f"audit-log", params=params, page_size=200)

    # Video
    def get_video(self, id: str):
        params = {
            API_SITE_ID: self._site_id,
        }
        return self.poll(f"broadcast/video/{id}", params=params)

    def get_download_list(
        self, access_token: str, competition_id: str, start_from: datetime
    ):
        if not start_from:
            log.error(f'Get download-list. Missing "start_from" param')
            return None
        params = {
            "competition-id": competition_id,
            "access-token": access_token,
            "start-to": self._get_api_time_format(start_from),
            "sort-column": "start",
            "sort-order": "Descending",
        }
        try:
            self._poller.set_header_field("site-id", self._site_id)
            result = self.poll(f"broadcast/download-list", params=params, page_size=25)
        except Exception as err:
            self._poller.set_header_field("site-id", "BACKOFFICE")
            log.error(f"Failed to get download list. Error: {err}")

    def get_download_access_token(self, competition_id: str):
        params = {
            "target-id": competition_id,
            "target": "COMP",
        }
        return self.poll(f"user/access-token", params=params)

    def create_download_access_token(self, competition_id: str):
        data = {
            "targetId": competition_id,
            "target": "COMP",
            "note": f"Python SDK",
            "anonymous": "true",
            "siteId": self._site_id,
        }
        return self.post(f"user/access-token", payload=data)

    # Competition/table
    def get_table(self, competition_id: str):
        params = {
            API_SITE_ID: self._site_id,
            "competition-id": competition_id,
            # "competition-id": "641ad0d11004dd5827fa5158",
            "sort-column": "created",
            "sort-order": "Descending",
        }
        return self.poll(f"competition/table", params=params)

    # Venue
    def get_venue(self, venue_id: str):
        params = {
            API_SITE_ID: self._site_id,
        }
        return self.poll(f"venue/{venue_id}", params=params)

    def get_venues(self, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: site_id,
        }
        return self.poll(f"venue", params=params, page_size=200)

    # Sites
    def get_sites(self):
        params = {
            "sort-column": "siteId",
            "sort-order": "Ascending",
        }
        return self.poll(f"site/config/settings", params=params, page_size=200)

    # https://api.livearenasports.com/site/config/settings/AU_FHWA?site-id=AU_FHWA
    def get_site_config(self, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: site_id,
        }
        return self.poll(
            f"site/config/settings/{site_id}", params=params, page_size=200
        )

    # Cameras
    def get_camera(self, cam_id):
        return self.poll(f"venue/camera/{cam_id}")

    def get_cameras(self):
        return self.poll(f"venue/camera", page_size=200)
        # return self.poll(f"venue/camera")

    # Comment
    # Competitions
    def get_competitions(self, ext_id: str = None, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: site_id,
            "external_id": ext_id,
            "sort-column": "name",
            "sort-order": "Ascending",
        }
        return self.poll(
            "competition", params=self._remove_nulls(params), page_size=200
        )

    def create_competition(
        self,
        ext_id: str,
        name: str,
        type: str,  # SERIES, CUP, TOURNAMENT, OFF_SEASON, PRE_SEASON, PRACTICE_MATCH
        start: datetime,
        end: datetime,
        site_id: str = None,
    ):
        sid = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: sid,
            "extId": ext_id,
            "name": name,
            "type": type,
            # "start": self._get_api_time_format(start),
            # "end": self._get_api_time_format(end),
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "siteId": sid,
        }
        return self.post(f"competition", payload=params)

    def update_competition(self, comp_id, updates: dict):
        date_keys = ["start", "end"]
        kv_date = {}
        for k, v in updates.items():
            kv_date[k] = v if k not in date_keys else self._get_api_time_format(v)
        # kv_date = kv | {
        #     k: self._get_api_time_format(v) for k, v in kv.items() if k in date_keys
        # }
        params = {"id": comp_id} | kv_date
        return self.patch(f"competition", payload=self._remove_nulls(params))

    # Groups
    def get_groups(self, site_id: str = None, external_id: str = None):
        site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: site_id,
            "external-id": external_id,
            "sort-column": "name",
            "sort-order": "Ascending",
        }
        return self.poll("group", params=self._remove_nulls(params), page_size=200)

    def get_group(self, group_id: str) -> list:
        if not group_id:
            return None
        params = {
            # API_SITE_ID: self._site_id,
        }
        return self.poll(f"group/{group_id}", params=params)

    def create_group(
        self,
        name: str,
        short_name: str,
        logo_url: str,
        secondary_logo_url: str = None,
        external_id: str = None,
        site_id: str = None,
    ):
        sid = site_id if site_id else self._site_id
        params = {
            "siteId": sid,
            "externalId": external_id,
            "name": name,
            "shortName": short_name,
            "type": "CLUB",
            "logo": {"url": logo_url},
            "secondaryLogo": {"url": secondary_logo_url},
        }
        # cleaned_params = {k: v for k, v in params.items() if v is not None}
        return self.post(f"group/ext", payload=params)

    def update_group(
        self,
        name: str,
        short_name: str,
        logo_url: str,
        secondary_logo_url: str = None,
        external_id: str = None,
        site_id: str = None,
    ):
        sid = site_id if site_id else self._site_id
        params = {
            "siteId": sid,
            "externalId": external_id,
            "name": name,
            "shortName": short_name,
            "type": "CLUB",
            "logo": {"url": logo_url},
            "secondaryLogo": {"url": secondary_logo_url},
        }
        return self.patch(f"group/ext", payload=self._remove_nulls(params))

    # Payment
    def get_payment_config(self, site_id: str = None):
        param_site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: param_site_id,
        }
        return self.poll(f"payment/v3/config", params=params)

    def get_payment_transactions(
        self,
        start: datetime,
        stop: datetime,
        site_id: str = None,
    ):
        param_site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: param_site_id,
            "from": self._get_api_time_format(start),
            "to": self._get_api_time_format(stop),
        }
        return self.poll(f"payment/v3/transactions", params=params, page_size=5000)

    def get_user_transactions(self, user_id: str):
        params = {
            API_SITE_ID: self._site_id,
            "user-id": user_id,
        }
        return self.poll(f"payment/v2/transactions", params=params, page_size=200)

    def get_user_session(self, user_id: str):
        params = {
            API_SITE_ID: self._site_id,
            "user-id": user_id,
        }
        return self.poll(f"session", params=params)

    # Products
    def get_products(self, site_id: str = None, archived: bool = False):
        param_site_id = site_id if site_id else self._site_id
        # Don't submit archived unless you really want archived products. PPV's are missing otherwise
        if archived == False:
            archived = None
        params = {
            API_SITE_ID: param_site_id,
            "archived": archived,
        }
        # return self.poll(f"payment/v2/product/subscriptions/{user_id}", params=params)
        return self.poll(f"product", params=self._remove_nulls(params), page_size=200)

    # Products
    def get_product_subscriptions(
        self, user_id: str = None, valid_from: datetime = None, site_id: str = None
    ):
        site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: site_id,
            "user-id": user_id,
            "valid-from": self._get_api_time_format(valid_from) if valid_from else None,
        }
        # return self.poll(f"payment/v2/product/subscriptions/{user_id}", params=params)
        return self.poll(f"user/access", params=self._remove_nulls(params))

    # ttps://api.livearenasports.com/user/access?site-id=SIF&user-id=64006cee28401b55db26418f&page-index=0

    # https://api.livearenasports.com/payment/v2/product/subscriptions/64ae8e5f6a1fe366d524d230?site-id=COM_META

    # Users
    def get_users(self, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        return self.poll(f"user/get-users-by-site-id/{site_id}", page_size=5000)

    def get_user(self, user_id):
        return self.poll(f"user/{user_id}")

    # Player Account
    def get_player_account(self, user_id, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        params = {API_SITE_ID: site_id, "user-id": user_id}

        return self.poll(
            f"player-account",
            params=params,
        )

    # CDN
    def set_cdn(self, cdn: str, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        body = {"siteId": site_id, "cdn": cdn}
        # body: siteId:SIF, cdnType:AZURE/GLOBAL
        return self.patch(f"site/config", payload=body)

    # Team Account
    # https://api.winnerheads.com/api/team-account/site-configs?site=SIF
    def get_feature_team_account(self, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        params = {API_SITE_ID: site_id, "type": "TEAM_ACCOUNT"}
        return self.poll(
            f"feature",
            params=params,
            page_size=50,
        )

    # Broadcast rules
    def get_broadcast_rules(self, site_id: str = None):
        site_id = site_id if site_id else self._site_id
        params = {
            API_SITE_ID: site_id,
        }
        return self.poll(
            f"broadcast/rules",
            params=params,
        )
